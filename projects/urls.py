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
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    
    # AJAX endpoints
    path('project/<int:pk>/like/', views.like_project, name='like-project'),
    path('project/<int:pk>/apply/', views.apply_for_role, name='apply-for-role'),
    path('project/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('application/<int:pk>/handle/', views.handle_application, name='handle-application'),
] 