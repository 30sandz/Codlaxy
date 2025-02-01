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
        ('skill_improvement', 'Skill Improvement'),
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

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('application', 'New Application'),
        ('acceptance', 'Application Accepted'),
        ('rejection', 'Application Rejected'),
        ('comment', 'New Comment'),
        ('like', 'New Like'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notifications', null=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} from {self.sender.username}"

    class Meta:
        ordering = ['-created_at']
