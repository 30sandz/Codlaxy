from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import logout
from .models import Project, UserProfile, Investor, Comment, Application, ProjectUpdate, Notification
from django.contrib.auth.models import User
import json
from django.db import models

def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('projects:landing')

def landing_page(request):
    """Landing page view with featured projects"""
    featured_projects = Project.objects.all()[:6]
    return render(request, 'projects/landing.html', {'featured_projects': featured_projects})

class ProjectListView(ListView):
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
        return context

class ProjectDetailView(DetailView):
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
            
            # Handle required roles and their vacancies
            if isinstance(required_roles, str):
                roles = [role.strip() for role in required_roles.split(',') if role.strip()]
                form.instance.required_roles = roles
                
                # Get role vacancies from POST data
                vacancies_dict = {}
                for role in roles:
                    vacancy = self.request.POST.get(f'vacancy_{role}', '1')
                    try:
                        vacancies_dict[role] = max(1, int(vacancy))  # Ensure at least 1 vacancy
                    except (ValueError, TypeError):
                        vacancies_dict[role] = 1  # Default to 1 if invalid
                
                form.instance.role_vacancies = vacancies_dict
            
            response = super().form_valid(form)
            messages.success(self.request, 'Project created successfully!')
            return response
            
        except Exception as e:
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
            
            # Handle required roles and their vacancies
            if isinstance(required_roles, str):
                roles = [role.strip() for role in required_roles.split(',') if role.strip()]
                form.instance.required_roles = roles
                
                # Get role vacancies from POST data
                vacancies_dict = {}
                for role in roles:
                    vacancy = self.request.POST.get(f'vacancy_{role}', '1')
                    try:
                        vacancies_dict[role] = max(1, int(vacancy))  # Ensure at least 1 vacancy
                    except (ValueError, TypeError):
                        # Keep existing vacancy number or default to 1
                        existing_vacancy = form.instance.role_vacancies.get(role, 1)
                        vacancies_dict[role] = existing_vacancy
                
                form.instance.role_vacancies = vacancies_dict
            
            response = super().form_valid(form)
            messages.success(self.request, 'Project updated successfully!')
            return response
            
        except Exception as e:
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


class UserProfileView(DetailView):
    """User profile view"""
    model = UserProfile
    template_name = 'projects/profile.html'
    context_object_name = 'profile'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object.user
        context['owned_projects'] = user.owned_projects.all()
        context['team_projects'] = user.team_projects.all()
        return context

@login_required
def profile_edit(request):
    """View for editing user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
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
        return redirect('projects:profile', pk=profile.pk)
    return render(request, 'projects/profile_edit.html', {'profile': profile})

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
                'profile_url': reverse('projects:profile', kwargs={'pk': comment.user.userprofile.pk}),
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
            # Add applicant to project team members
            project.team_members.add(application.applicant)
            
            # Create notification for applicant
            Notification.objects.create(
                recipient=application.applicant,
                sender=request.user,
                project=project,
                notification_type='application_accepted',
                message=f'Your application for the {application.role} role in "{project.title}" has been accepted!'
            )
            
            # Update application status
            application.status = 'accepted'
            application.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Application accepted successfully',
                'user': {
                    'username': application.applicant.username,
                    'profile_url': reverse('projects:profile', kwargs={'pk': application.applicant.userprofile.pk}),
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
