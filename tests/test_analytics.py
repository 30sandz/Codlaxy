from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from analytics.models import PageView, UserActivity, MarketingMetrics
from analytics.middleware import AnalyticsMiddleware
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.middleware = AnalyticsMiddleware(lambda r: None)

    def test_page_view_tracking(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        
        # Check if page view was recorded
        page_view = PageView.objects.first()
        self.assertIsNotNone(page_view)
        self.assertEqual(page_view.path, '/')
        self.assertEqual(page_view.user, self.user)

    def test_user_activity_tracking(self):
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='view',
            content_type_id=1,  # Assuming content type ID for User model
            object_id=self.user.id
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'view')

    def test_marketing_metrics_aggregation(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Create some test data
        MarketingMetrics.objects.create(
            date=yesterday,
            new_users=10,
            active_users=50,
            project_views=100,
            applications_submitted=5,
            successful_matches=2,
            conversion_rate=0.1,
            bounce_rate=0.3,
            average_session_duration=120
        )
        
        # Test metrics retrieval
        metrics = MarketingMetrics.objects.get(date=yesterday)
        self.assertEqual(metrics.new_users, 10)
        self.assertEqual(metrics.active_users, 50)
        self.assertEqual(metrics.project_views, 100)

    def test_middleware_ip_detection(self):
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_skip_static_files_tracking(self):
        response = self.client.get('/static/css/style.css')
        
        # Should not create a page view for static files
        self.assertEqual(PageView.objects.count(), 0) 