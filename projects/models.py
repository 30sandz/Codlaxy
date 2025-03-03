from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    college = models.CharField(max_length=200, blank=True)
    most_recognized_role = models.CharField(max_length=100, blank=True)
    awards = models.TextField(blank=True)
    github_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    portfolio_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    investment_focus = models.TextField()
    past_startups_funded = models.IntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Investor: {self.user.username}"

class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'On-going'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    CATEGORY_CHOICES = [
        ('startup', 'Startup'),
        ('skill_improvement', 'Improvement'),
        ('recognition', 'Recognition'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    technologies = ArrayField(models.CharField(max_length=50), blank=True)
    required_roles = ArrayField(models.CharField(max_length=100), blank=True)
    role_vacancies = models.JSONField(default=dict, blank=True)  # Store role vacancies as {"role": number}
    team_members = models.ManyToManyField(User, related_name='team_projects', blank=True)
    likes = models.ManyToManyField(User, related_name='liked_projects', blank=True)
    project_logo = models.ImageField(upload_to='project_logos/', null=True, blank=True)
    github_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    demo_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    role = models.CharField(max_length=100)
    experience = models.TextField()
    portfolio = models.URLField(blank=True, null=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'applicant', 'role']

    def __str__(self):
        return f"{self.applicant.username}'s application for {self.role} in {self.project.title}"

class ProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.project.title}: {self.title}"

class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    requester = models.ForeignKey(User, related_name='sent_connections', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_connections', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('requester', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.username} -> {self.receiver.username} ({self.status})"

    @property
    def is_mutual(self):
        return self.status == 'accepted'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application', 'Project Application'),
        ('like', 'Project Like'),
        ('comment', 'Project Comment'),
        ('application_accepted', 'Application Accepted'),
        ('application_rejected', 'Application Rejected'),
        ('team_update', 'Team Update'),
        ('project_update', 'Project Update'),
        ('system', 'System Notification'),
        ('connection_request', 'Connection Request'),
        ('connection_accepted', 'Connection Accepted'),
        ('connection_rejected', 'Connection Rejected'),
        ('connected_new_project', 'Connection New Project'),
        ('connected_joined_project', 'Connection Joined Project'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @property
    def get_notification_icon(self):
        icon_map = {
            'application': 'fa-user-plus',
            'like': 'fa-heart',
            'comment': 'fa-comment',
            'application_accepted': 'fa-check-circle',
            'application_rejected': 'fa-times-circle',
            'team_update': 'fa-users',
            'project_update': 'fa-project-diagram',
            'connection_request': 'fa-user-plus',
            'connection_accepted': 'fa-check-circle',
            'connection_rejected': 'fa-times-circle',
            'connected_new_project': 'fa-project-diagram',
            'connected_joined_project': 'fa-users',
        }
        return f"fas {icon_map.get(self.notification_type, 'fa-bell')}"

    @property
    def get_notification_color(self):
        color_map = {
            'application': 'blue',
            'like': 'red',
            'comment': 'green',
            'application_accepted': 'green',
            'application_rejected': 'red',
            'team_update': 'purple',
            'project_update': 'indigo',
            'connection_request': 'blue',
            'connection_accepted': 'green',
            'connection_rejected': 'red',
            'connected_new_project': 'blue',
            'connected_joined_project': 'purple',
        }
        return color_map.get(self.notification_type, 'gray')
