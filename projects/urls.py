from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView

app_name = 'projects'

urlpatterns = [
    # Landing and main pages
    path('', views.landing_page, name='landing'),
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    
    # Authentication URLs
    path('logout/', views.logout_view, name='logout'),
    
    # Project related URLs
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    
    # Profile related URLs
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/connections/', views.user_connections, name='connections'),
    path('profile/<int:pk>/connect/', views.send_connection_request, name='send-connection-request'),
    path('profile/<int:pk>/accept-connection/', views.accept_connection, name='accept-connection'),
    path('profile/<int:pk>/reject-connection/', views.reject_connection, name='reject-connection'),
    path('profile/<int:pk>/cancel-connection/', views.cancel_connection, name='cancel-connection'),
    
    # AJAX endpoints
    path('project/<int:pk>/like/', views.like_project, name='like-project'),
    path('project/<int:pk>/apply/', views.apply_for_role, name='apply-for-role'),
    path('project/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('application/<int:pk>/handle/', views.handle_application, name='handle-application'),
    
    # Project management
    path('project/<int:pk>/delete/', views.delete_project, name='project-delete'),
    
    # Comment management
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='comment-edit'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='comment-delete'),
    
    # Account management
    path('accounts/delete/', views.delete_account, name='account-delete'),

    # Notification URLs
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear-all-notifications'),

    # Team member management
    path('project/<int:project_id>/remove-member/<int:user_id>/', views.remove_team_member, name='remove-team-member'),
    path('project/<int:project_id>/leave/', views.leave_project, name='leave-project'),
] 