"""
URL configuration for codlaxy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse

def health_check(request):
    try:
        # Check if we can access settings
        allowed_hosts = settings.ALLOWED_HOSTS
        debug = settings.DEBUG
        
        # Get request information
        host = request.get_host()
        scheme = request.scheme
        
        return JsonResponse({
            'status': 'healthy',
            'host': host,
            'scheme': scheme,
            'allowed_hosts': allowed_hosts,
            'debug': debug
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=200)  # Still return 200 for health check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),
    path('accounts/', include('allauth.urls')),
    path('health/', health_check, name='health_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
