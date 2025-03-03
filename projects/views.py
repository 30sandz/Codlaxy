from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Project, UserProfile, Investor, Comment, Application, ProjectUpdate, Notification, Connection
import json
from django.db import models

def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('projects:landing')

def landing_page(request):
    """Landing page view with featured projects"""
    context = {
        'featured_projects': Project.objects.all()[:6],
        **get_notification_context(request.user)
    }
    return render(request, 'projects/landing.html', context)

class ProjectListView(LoginRequiredMixin, ListView):
    """Main page with project listings"""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Handle category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Handle search query
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query) |
                models.Q(technologies__contains=[search_query]) |
                models.Q(required_roles__contains=[search_query])
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add search query to context for form persistence
        context['search_query'] = self.request.GET.get('search', '')
        context.update(get_notification_context(self.request.user))
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a single project"""
    model = Project
    template_name = 'projects/project_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all().select_related('user', 'user__userprofile')
        if self.request.user.is_authenticated:
            context['has_liked'] = self.object.likes.filter(id=self.request.user.id).exists()
            context['has_applied'] = self.object.applications.filter(applicant=self.request.user).exists()
        context['updates'] = self.object.updates.all()
        context['applications'] = self.object.applications.all()
        context.update(get_notification_context(self.request.user))
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new project"""
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'category', 'technologies', 'required_roles', 
              'project_logo', 'github_link', 'linkedin_link', 'demo_link']
    
    def form_valid(self, form):
        try:
            form.instance.owner = self.request.user
            
            # Convert comma-separated strings to lists for array fields
            technologies = form.cleaned_data.get('technologies', '')
            required_roles = form.cleaned_data.get('required_roles', '')
            
            # Handle technologies
            if isinstance(technologies, str):
                form.instance.technologies = [tech.strip() for tech in technologies.split(',') if tech.strip()]
            
            # Handle required roles
            if isinstance(required_roles, str):
                roles = [role.strip() for role in required_roles.split(',') if role.strip()]
                form.instance.required_roles = roles
            
            # Save the project first
            self.object = form.save()
            
            # Handle role vacancies separately
            role_vacancies_data = self.request.POST.get('role_vacancies')
            if role_vacancies_data:
                try:
                    vacancies_dict = json.loads(role_vacancies_data)
                    self.object.role_vacancies = vacancies_dict
                    self.object.save()
                except json.JSONDecodeError:
                    print("Invalid JSON format for role_vacancies")
            
            # Notify connections about the new project
            connections = Connection.objects.filter(
                models.Q(requester=self.request.user) | models.Q(receiver=self.request.user),
                status='accepted'
            )
            
            for connection in connections:
                recipient = connection.receiver if connection.requester == self.request.user else connection.requester
                Notification.objects.create(
                    recipient=recipient,
                    sender=self.request.user,
                    project=self.object,
                    notification_type='connected_new_project',
                    message=f'{self.request.user.username} created a new project: {self.object.title}'
                )
            
            messages.success(self.request, 'Project created successfully!')
            return redirect(self.get_success_url())
            
        except Exception as e:
            print(f"Error in form_valid: {str(e)}")
            messages.error(self.request, f'Error creating project: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing project"""
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['title', 'description', 'category', 'technologies', 'required_roles',
              'project_logo', 'github_link', 'linkedin_link', 'demo_link']
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def form_valid(self, form):
        try:
            # Convert comma-separated strings to lists for array fields
            technologies = form.cleaned_data.get('technologies', '')
            required_roles = form.cleaned_data.get('required_roles', '')
            
            # Handle technologies
            if isinstance(technologies, str):
                form.instance.technologies = [tech.strip() for tech in technologies.split(',') if tech.strip()]
            
            # Handle required roles
            if isinstance(required_roles, str):
                roles = [role.strip() for role in required_roles.split(',') if role.strip()]
                form.instance.required_roles = roles
            
            # Save the form first to update other fields
            self.object = form.save()
            
            # Handle role vacancies separately
            role_vacancies_data = self.request.POST.get('role_vacancies')
            if role_vacancies_data:
                try:
                    vacancies_dict = json.loads(role_vacancies_data)
                    self.object.role_vacancies = vacancies_dict
                    self.object.save()
                except json.JSONDecodeError:
                    print("Invalid JSON format for role_vacancies")
            
            messages.success(self.request, 'Project updated successfully!')
            return redirect(self.get_success_url())
            
        except Exception as e:
            print(f"Error in form_valid: {str(e)}")
            messages.error(self.request, f'Error updating project: {str(e)}')
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.object.pk})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object:
            # Convert lists to comma-separated strings for display
            form.initial['technologies'] = ', '.join(self.object.technologies or [])
            form.initial['required_roles'] = ', '.join(self.object.required_roles or [])
        return form


class UserProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = User
    template_name = 'projects/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Get user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        
        # Get connection status
        connection = Connection.objects.filter(
            models.Q(requester=self.request.user, receiver=user) |
            models.Q(requester=user, receiver=self.request.user)
        ).first()
        
        connection_status = None
        if connection:
            connection_status = connection.status
            context['connection_direction'] = 'received' if connection.receiver == self.request.user else 'sent'
        
        context.update({
            'owned_projects': user.owned_projects.all(),
            'team_projects': user.team_projects.all(),
            'connection_status': connection_status,
            'connections_count': Connection.objects.filter(
                models.Q(requester=user) | models.Q(receiver=user),
                status='accepted'
            ).count(),
            **get_notification_context(self.request.user)
        })
        return context

@login_required
def profile_edit(request):
    """View for editing user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'profile': profile,
        **get_notification_context(request.user)
    }
    if request.method == 'POST':
        # Handle username change
        new_username = request.POST.get('username')
        if new_username and new_username != request.user.username:
            # Check if username is available
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'This username is already taken.')
                return render(request, 'projects/profile_edit.html', context)
            try:
                request.user.username = new_username
                request.user.save()
                messages.success(request, 'Username updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating username: {str(e)}')
                return render(request, 'projects/profile_edit.html', context)

        # Handle other profile fields
        profile.college = request.POST.get('college')
        profile.most_recognized_role = request.POST.get('most_recognized_role')
        profile.awards = request.POST.get('awards')
        profile.github_link = request.POST.get('github_link')
        profile.linkedin_link = request.POST.get('linkedin_link')
        profile.portfolio_link = request.POST.get('portfolio_link')
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('projects:profile', username=request.user.username)
    return render(request, 'projects/profile_edit.html', context)

@login_required
@require_POST
def like_project(request, pk):
    """AJAX view for liking/unliking a project"""
    project = get_object_or_404(Project, pk=pk)
    if request.user in project.likes.all():
        project.likes.remove(request.user)
        liked = False
    else:
        project.likes.add(request.user)
        liked = True
    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': project.likes.count()
    })

@login_required
@require_POST
def apply_for_role(request, pk):
    """View for applying to a project role"""
    try:
        project = get_object_or_404(Project, pk=pk)
        
        # Check if user is the project owner
        if request.user == project.owner:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot apply to your own project'
            })
        
        # Parse JSON data from request
        data = json.loads(request.body)
        role = data.get('role')
        experience = data.get('experience')
        portfolio = data.get('portfolio')
        message = data.get('message')
        
        # Validate required fields
        if not role or not experience or not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Please fill in all required fields'
            })
        
        # Check if role exists in project
        if role not in project.required_roles:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid role selected'
            })
        
        # Check if user has already applied
        if Application.objects.filter(project=project, applicant=request.user, role=role).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'You have already applied for this role'
            })
        
        # Create the application
        application = Application.objects.create(
            project=project,
            applicant=request.user,
            role=role,
            experience=experience,
            portfolio=portfolio,
            message=message
        )
        
        # Send notification to project owner
        Notification.objects.create(
            recipient=project.owner,
            sender=request.user,
            project=project,
            notification_type='application',
            message=f'{request.user.username} applied for the {role} role in your project "{project.title}"'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Application submitted successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request format'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_POST
def add_comment(request, pk):
    """AJAX view for adding comments"""
    try:
        project = get_object_or_404(Project, pk=pk)
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Comment cannot be empty'
            })
        
        if len(content) > 500:
            return JsonResponse({
                'status': 'error',
                'message': 'Comment must be 500 characters or less'
            })
        
        comment = Comment.objects.create(
            project=project,
            user=request.user,
            content=content
        )
        
        # Send notification to project owner if commenter is not the owner
        if request.user != project.owner:
            Notification.objects.create(
                recipient=project.owner,
                sender=request.user,
                project=project,
                notification_type='comment',
                message=f'{request.user.username} commented on your project "{project.title}"'
            )
        
        return JsonResponse({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'username': comment.user.username,
                'content': comment.content,
                'profile_url': reverse('projects:profile', kwargs={'username': comment.user.username}),
                'profile_picture': comment.user.userprofile.profile_picture.url if comment.user.userprofile.profile_picture else None,
                'created_at': comment.created_at.strftime('%B %d, %Y %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request format'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_POST
def handle_application(request, pk):
    """View for handling project role applications (accept/reject)"""
    try:
        application = get_object_or_404(Application, pk=pk)
        project = application.project
        
        # Check if user is the project owner
        if request.user != project.owner:
            return JsonResponse({
                'status': 'error',
                'message': 'Only project owner can handle applications'
            })
        
        # Parse JSON data from request
        data = json.loads(request.body)
        action = data.get('action')
        
        if action not in ['accept', 'reject']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid action'
            })
        
        if action == 'accept':
            # Update role vacancy count
            role = application.role
            if role in project.role_vacancies:
                project.role_vacancies[role] = max(0, project.role_vacancies[role] - 1)
                # If vacancy becomes 0, remove the role from required_roles
                if project.role_vacancies[role] == 0 and role in project.required_roles:
                    project.required_roles.remove(role)
                project.save(update_fields=['role_vacancies', 'required_roles'])
            
            # Add applicant to project team members
            project.team_members.add(application.applicant)
            
            # Update application status
            application.status = 'accepted'
            application.save()
            
            # Create notification for applicant
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                project=project,
                notification_type='application_accepted',
                message=f'Your application for the {application.role} role in "{project.title}" has been accepted!'
            )
            
            # Notify connections about joining the project
            connections = Connection.objects.filter(
                models.Q(requester=application.applicant) | models.Q(receiver=application.applicant),
                status='accepted'
            )
            
            for connection in connections:
                recipient = connection.receiver if connection.requester == application.applicant else connection.requester
                Notification.objects.create(
                    recipient=recipient,
                    sender=application.applicant,
                    project=project,
                    notification_type='connected_joined_project',
                    message=f'{application.applicant.username} joined the project {project.title}'
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Application accepted successfully',
                'user': {
                    'username': application.applicant.username,
                    'profile_url': reverse('projects:profile', kwargs={'username': application.applicant.username}),
                    'profile_picture': application.applicant.userprofile.profile_picture.url if application.applicant.userprofile.profile_picture else None,
                }
            })
        else:
            # Reject application
            application.status = 'rejected'
            application.save()
            
            # Create notification for applicant
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                project=project,
                notification_type='application_rejected',
                message=f'Your application for the {application.role} role in "{project.title}" has been declined.'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Application rejected successfully'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request format'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
@require_POST
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        comment.content = data.get('content', '').strip()
        if not comment.content:
            return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
        comment.save()
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    comment.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def delete_account(request):
    if request.user.is_authenticated:
        try:
            user = request.user

            from allauth.account.models import EmailAddress
            from .models import UserProfile
            EmailAddress.objects.filter(user=user).delete()
            UserProfile.objects.filter(user=user).delete()
            
            # Delete user profile
            if hasattr(user, 'userprofile'):
                user.userprofile.delete()

            # Finally, delete the user account itself
            # This will cascade delete related data in auth_user table
            user.delete()
            
            messages.success(request, 'Your account and all related data have been permanently deleted.')

            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error deleting account: {str(e)}'
            }, status=500)
            
    return JsonResponse({'error': 'Unauthorized'}, status=403)

class NotificationListView(LoginRequiredMixin, ListView):
    """View for listing all notifications"""
    model = Notification
    template_name = 'projects/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context

@login_required
@require_POST
def mark_notification_read(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    if request.headers.get('HX-Request'):  # If it's an HTMX request
        return HttpResponse('')  # Return empty response for HTMX
    return redirect('projects:notifications')

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('HX-Request'):  # If it's an HTMX request
        return HttpResponse('')
    return redirect('projects:notifications')

@login_required
@require_POST
def clear_all_notifications(request):
    """Delete all notifications for the current user"""
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications have been cleared.')
    return redirect('projects:notifications')

def get_notification_context(user):
    """Helper function to get notification context for templates"""
    if user.is_authenticated:
        recent_notifications = Notification.objects.filter(recipient=user)[:5]
        unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
        return {
            'recent_notifications': recent_notifications,
            'unread_notifications_count': unread_count
        }
    return {
        'recent_notifications': [],
        'unread_notifications_count': 0
    }

class BaseContextMixin:
    """Mixin to add notification context to all views"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request.user))
        return context

@login_required
@require_POST
def send_connection_request(request, pk):
    """View for sending a connection request"""
    try:
        user_to_connect = get_object_or_404(User, pk=pk)
        
        # Can't connect with yourself
        if request.user == user_to_connect:
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot connect with yourself'
            }, status=400)
        
        # Check if connection already exists
        existing_connection = Connection.objects.filter(
            models.Q(requester=request.user, receiver=user_to_connect) |
            models.Q(requester=user_to_connect, receiver=request.user)
        ).first()
        
        if existing_connection:
            if existing_connection.status == 'pending':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Connection request already sent'
                }, status=400)
            elif existing_connection.status == 'accepted':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You are already connected'
                }, status=400)
        
        # Create connection request
        connection = Connection.objects.create(
            requester=request.user,
            receiver=user_to_connect,
            status='pending'
        )
        
        # Create notification for the receiver
        Notification.objects.create(
            recipient=user_to_connect,
            sender=request.user,
            notification_type='connection_request',
            message=f'{request.user.username} sent you a connection request'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Connection request sent to {user_to_connect.username}',
            'connection_status': 'pending'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def accept_connection(request, pk):
    """View for accepting a connection request"""
    try:
        connection = get_object_or_404(Connection, receiver=request.user, requester_id=pk, status='pending')
        connection.status = 'accepted'
        connection.save()
        
        # Create notification for the requester
        Notification.objects.create(
            recipient=connection.requester,
            sender=request.user,
            notification_type='connection_accepted',
            message=f'{request.user.username} accepted your connection request'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'You are now connected with {connection.requester.username}',
            'connection_status': 'accepted'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def reject_connection(request, pk):
    """View for rejecting a connection request"""
    try:
        connection = get_object_or_404(Connection, receiver=request.user, requester_id=pk, status='pending')
        connection.status = 'rejected'
        connection.save()
        
        # Create notification for the requester
        Notification.objects.create(
            recipient=connection.requester,
            sender=request.user,
            notification_type='connection_rejected',
            message=f'{request.user.username} declined your connection request'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Connection request from {connection.requester.username} declined',
            'connection_status': 'rejected'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def cancel_connection(request, pk):
    """View for canceling a connection request or removing a connection"""
    try:
        connection = get_object_or_404(
            Connection,
            models.Q(requester=request.user, receiver_id=pk) |
            models.Q(receiver=request.user, requester_id=pk)
        )
        connection.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Connection removed',
            'connection_status': None
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def user_connections(request, username):
    """View for displaying user connections"""
    user = get_object_or_404(User, username=username)
    connections = Connection.objects.filter(
        models.Q(requester=user) | models.Q(receiver=user),
        status='accepted'
    ).select_related('requester', 'receiver', 'requester__userprofile', 'receiver__userprofile')
    
    connected_users = []
    for connection in connections:
        connected_user = connection.receiver if connection.requester == user else connection.requester
        connected_users.append(connected_user)
    
    context = {
        'profile_user': user,
        'connected_users': connected_users,
        **get_notification_context(request.user)
    }
    return render(request, 'projects/connections.html', context)

@login_required
@require_POST
def remove_team_member(request, project_id, user_id):
    """View for project owner to remove a team member"""
    project = get_object_or_404(Project, id=project_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Check if the request user is the project owner
    if request.user != project.owner:
        messages.error(request, "Only the project owner can remove team members.")
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    # Check if the user is actually a team member
    if not project.team_members.filter(id=user_id).exists():
        messages.error(request, "User is not a team member.")
        return JsonResponse({'status': 'error', 'message': 'User is not a team member'}, status=400)
    
    # Remove the user from team members
    project.team_members.remove(user_to_remove)
    
    # Create notification for the removed user
    Notification.objects.create(
        recipient=user_to_remove,
        sender=request.user,
        project=project,
        notification_type='team_update',
        message=f'You have been removed from the project "{project.title}"'
    )
    
    messages.success(request, f'{user_to_remove.username} has been removed from the project.')
    return JsonResponse({
        'status': 'success',
        'message': f'{user_to_remove.username} has been removed from the project'
    })

@login_required
@require_POST
def leave_project(request, project_id):
    """View for team member to leave a project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user is actually a team member
    if not project.team_members.filter(id=request.user.id).exists():
        messages.error(request, "You are not a team member of this project.")
        return JsonResponse({'status': 'error', 'message': 'Not a team member'}, status=400)
    
    # Check if the user is not the project owner
    if request.user == project.owner:
        messages.error(request, "Project owner cannot leave the project.")
        return JsonResponse({'status': 'error', 'message': 'Project owner cannot leave'}, status=400)
    
    # Remove the user from team members
    project.team_members.remove(request.user)
    
    # Create notification for the project owner
    Notification.objects.create(
        recipient=project.owner,
        sender=request.user,
        project=project,
        notification_type='team_update',
        message=f'{request.user.username} has left the project "{project.title}"'
    )
    
    messages.success(request, f'You have left the project "{project.title}".')
    return JsonResponse({
        'status': 'success',
        'message': f'You have left the project successfully'
    })
