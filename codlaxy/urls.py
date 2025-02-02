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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
import os

def health_check(request):
    try:
        # Basic environment checks
        env_vars = {
            'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE'),
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS'),
            'DATABASE_URL': 'Set' if os.getenv('DATABASE_URL') else 'Not Set',
            'DEBUG': os.getenv('DEBUG'),
            'PORT': os.getenv('PORT')
        }
        
        # Request information
        request_info = {
            'host': request.get_host(),
            'scheme': request.scheme,
            'path': request.path,
            'method': request.method,
        }
        
        return JsonResponse({
            'status': 'healthy',
            'environment': env_vars,
            'request': request_info,
            'settings': {
                'allowed_hosts': settings.ALLOWED_HOSTS,
                'debug': settings.DEBUG,
                'static_root': str(settings.STATIC_ROOT),
                'database_config': 'configured' if 'default' in settings.DATABASES else 'not configured'
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=200)  # Still return 200 for health check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),
    path('accounts/', include('allauth.urls')),
    re_path(r'^health/?$', health_check, name='health_check'),  # This will match both /health and /health/
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
