from django.utils import timezone
from .models import PageView
import time

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer for page load duration
        request.start_time = time.time()
        
        # Get the response
        response = self.get_response(request)
        
        # Skip tracking for static files and admin pages
        if (not request.path.startswith('/static/') and 
            not request.path.startswith('/admin/') and 
            not request.path.startswith('/media/')):
            
            # Calculate page load duration
            duration = int((time.time() - request.start_time) * 1000)  # Convert to milliseconds
            
            # Create page view record
            PageView.objects.create(
                path=request.path,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                referrer=request.META.get('HTTP_REFERER'),
                duration=duration,
                timestamp=timezone.now()
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 