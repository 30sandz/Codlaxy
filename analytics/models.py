from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)  # e.g., 'view', 'like', 'comment'
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)  # Additional activity data

    class Meta:
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', 'activity_type', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

class PageView(models.Model):
    path = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    referrer = models.URLField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True)  # Duration in seconds

    class Meta:
        indexes = [
            models.Index(fields=['path', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

class MarketingMetrics(models.Model):
    date = models.DateField(unique=True)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    project_views = models.PositiveIntegerField(default=0)
    applications_submitted = models.PositiveIntegerField(default=0)
    successful_matches = models.PositiveIntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(default=0.0)
    average_session_duration = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = 'Marketing Metrics'
        ordering = ['-date'] 