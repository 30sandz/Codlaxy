from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from projects.models import Project, ProjectRole, Application
from django.utils import timezone

User = get_user_model()

class ProjectTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project description',
            owner=self.user,
            category='STARTUP',
            status='ACTIVE'
        )
        self.role = ProjectRole.objects.create(
            project=self.project,
            title='Developer',
            description='Backend developer needed',
            skills_required=['Python', 'Django']
        )

    def test_project_creation(self):
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.owner, self.user)
        self.assertEqual(self.project.status, 'ACTIVE')

    def test_project_list_view(self):
        response = self.client.get(reverse('project-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_detail_view(self):
        response = self.client.get(
            reverse('project-detail', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Developer')

    def test_project_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'title': 'New Project',
            'description': 'New project description',
            'category': 'STARTUP',
            'status': 'ACTIVE'
        }
        response = self.client.post(reverse('project-create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Project.objects.filter(title='New Project').exists())

    def test_role_application(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'role': self.role.id,
            'message': 'I would like to join this project',
            'experience': '2 years of Python development'
        }
        response = self.client.post(
            reverse('apply-role', kwargs={'pk': self.role.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Application.objects.filter(
                applicant=self.user,
                role=self.role
            ).exists()
        ) 