from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Team, TeamMember
from .tasks import send_team_assignment_email

User = get_user_model()


class ExceptionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager1', email='manager1@test.com',
            password='Test@1234', role='manager'
        )
        self.employee = User.objects.create_user(
            username='employee1', email='employee1@test.com',
            password='Test@1234', role='employee'
        )
        self.team = Team.objects.create(name='Team A', manager=self.manager)

    # --- Register exceptions ---
    def test_register_password_mismatch(self):
        res = self.client.post('/api/register/', {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'Test@1234', 'password2': 'Wrong@1234', 'role': 'employee'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        res = self.client.post('/api/register/', {
            'username': 'manager1', 'email': 'another@test.com',
            'password': 'Test@1234', 'password2': 'Test@1234', 'role': 'employee'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        res = self.client.post('/api/register/', {
            'username': 'unique_name', 'email': 'manager1@test.com',
            'password': 'Test@1234', 'password2': 'Test@1234', 'role': 'employee'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        res = self.client.post('/api/register/', {
            'username': 'weakuser', 'email': 'weak@test.com',
            'password': '123', 'password2': '123', 'role': 'employee'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        res = self.client.post('/api/register/', {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Login exceptions ---
    def test_login_invalid_credentials(self):
        res = self.client.post('/api/login/', {
            'username': 'manager1', 'password': 'WrongPassword'
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        res = self.client.post('/api/login/', {
            'username': 'nouser', 'password': 'Test@1234'
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        res = self.client.post('/api/login/', {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Change password exceptions ---
    def test_change_password_wrong_old_password(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post('/api/change-password/', {
            'old_password': 'WrongOld', 'new_password': 'NewPass@1234'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_new_password(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post('/api/change-password/', {
            'old_password': 'Test@1234', 'new_password': '123'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        res = self.client.post('/api/change-password/', {
            'old_password': 'Test@1234', 'new_password': 'NewPass@1234'
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- IsManager permission exceptions ---
    def test_employee_access_employee_list(self):
        self.client.force_authenticate(user=self.employee)
        res = self.client.get('/api/employees/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_employee_list(self):
        res = self.client.get('/api/employees/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_access_team_list(self):
        self.client.force_authenticate(user=self.employee)
        res = self.client.get('/api/teams/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_create_team(self):
        self.client.force_authenticate(user=self.employee)
        res = self.client.post('/api/teams/', {'name': 'Hack Team'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # --- Team assign exceptions ---
    def test_assign_team_not_found(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post('/api/teams/2/assign/', {'employee_id': self.employee.pk})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_assign_missing_employee_id(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post(f'/api/teams/{self.team.pk}/assign/', {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_employee_not_found(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post(f'/api/teams/{self.team.pk}/assign/', {'employee_id': 2})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_assign_employee_already_in_team(self):
        self.client.force_authenticate(user=self.manager)
        TeamMember.objects.create(team=self.team, employee=self.employee)
        res = self.client.post(f'/api/teams/{self.team.pk}/assign/', {'employee_id': self.employee.pk})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_manager_as_employee(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.post(f'/api/teams/{self.team.pk}/assign/', {'employee_id': self.manager.pk})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Team delete member exceptions ---
    def test_remove_team_not_found(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.delete('/api/teams/2/assign/', {'employee_id': self.employee.pk})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_missing_employee_id(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.delete(f'/api/teams/{self.team.pk}/assign/', {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_employee_not_in_team(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.delete(f'/api/teams/{self.team.pk}/assign/', {'employee_id': self.employee.pk})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Team detail exceptions ---
    def test_team_detail_not_found(self):
        self.client.force_authenticate(user=self.manager)
        res = self.client.get('/api/teams/2/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_employee_access_team_detail(self):
        self.client.force_authenticate(user=self.employee)
        res = self.client.get(f'/api/teams/{self.team.pk}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_access_other_manager_team(self):
        other_manager = User.objects.create_user(
            username='manager2', email='m2@test.com',
            password='Test@1234', role='manager'
        )
        self.client.force_authenticate(user=other_manager)
        res = self.client.get(f'/api/teams/{self.team.pk}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Profile exceptions ---
    def test_profile_unauthenticated(self):
        res = self.client.get('/api/profile/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ──────────────────────────────────────────────
#  Celery Configuration Tests
# ──────────────────────────────────────────────


class CeleryConfigTest(TestCase):
    def test_celery_app_is_configured(self):
        from taskmanegement.celery import app
        self.assertEqual(app.main, 'taskmanegement')

    def test_celery_app_uses_json_serialization(self):
        from taskmanegement.celery import app
        self.assertIn('json', app.conf.accept_content)

    def test_task_autodiscovery(self):
        from taskmanegement.celery import app
        registered = app.tasks.keys()
        self.assertIn('accounts.tasks.send_team_assignment_email', registered)

    def test_eager_mode_enabled(self):
        from django.conf import settings
        self.assertTrue(settings.CELERY_TASK_ALWAYS_EAGER)

    def test_eager_propagation_enabled(self):
        from django.conf import settings
        self.assertTrue(settings.CELERY_TASK_EAGER_PROPAGATES)


# ──────────────────────────────────────────────
#  Send Team Assignment Email Tests
# ──────────────────────────────────────────────


class SendTeamAssignmentEmailTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager1', email='manager1@test.com',
            password='Test@1234', role='manager',
            first_name='John', last_name='Manager'
        )
        self.employee = User.objects.create_user(
            username='employee1', email='employee1@test.com',
            password='Test@1234', role='employee',
            first_name='Jane', last_name='Employee'
        )
        self.team = Team.objects.create(
            name='Engineering',
            description='Software engineering team',
            manager=self.manager
        )

    def test_sends_email_to_employee(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['employee1@test.com'])

    def test_email_subject_contains_team_name(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertIn('Engineering', mail.outbox[0].subject)

    def test_email_body_contains_manager_full_name(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertIn('John Manager', mail.outbox[0].body)

    def test_email_body_contains_employee_name(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertIn('Jane Employee', mail.outbox[0].body)

    def test_email_body_contains_team_description(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertIn('Software engineering team', mail.outbox[0].body)

    def test_returns_success_message(self):
        result = send_team_assignment_email(self.team.id, self.employee.id)
        self.assertEqual(result, 'Email sent to employee1@test.com')

    def test_email_from_address(self):
        send_team_assignment_email(self.team.id, self.employee.id)
        self.assertEqual(mail.outbox[0].from_email, 'noreply@taskmanager.com')


class SendTeamAssignmentEmailNoDescriptionTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager1', email='manager1@test.com',
            password='Test@1234', role='manager',
            first_name='John', last_name='Manager'
        )
        self.employee = User.objects.create_user(
            username='employee1', email='employee1@test.com',
            password='Test@1234', role='employee',
            first_name='Jane', last_name='Employee'
        )
        self.team = Team.objects.create(
            name='Engineering',
            description='',
            manager=self.manager
        )

    def test_works_without_description(self):
        result = send_team_assignment_email(self.team.id, self.employee.id)
        self.assertEqual(result, 'Email sent to employee1@test.com')
        self.assertEqual(len(mail.outbox), 1)


class SendTeamAssignmentEmailEdgeCasesTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager1', email='manager1@test.com',
            password='Test@1234', role='manager'
        )
        self.employee = User.objects.create_user(
            username='employee1', email='employee1@test.com',
            password='Test@1234', role='employee'
        )
        self.team = Team.objects.create(name='Team A', manager=self.manager)

    def test_missing_team_returns_error(self):
        result = send_team_assignment_email(9999, self.employee.id)
        self.assertEqual(result, 'Team 9999 not found')
        self.assertEqual(len(mail.outbox), 0)

    def test_missing_employee_returns_error(self):
        result = send_team_assignment_email(self.team.id, 9999)
        self.assertEqual(result, 'Employee 9999 not found')
        self.assertEqual(len(mail.outbox), 0)


# ──────────────────────────────────────────────
#  Team Assign View + Celery Integration Tests
# ──────────────────────────────────────────────


class TeamAssignViewCeleryIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager1', email='manager1@test.com',
            password='Test@1234', role='manager'
        )
        self.employee = User.objects.create_user(
            username='employee1', email='employee1@test.com',
            password='Test@1234', role='employee'
        )
        self.team = Team.objects.create(name='Team A', manager=self.manager)
        self.client.force_authenticate(user=self.manager)

    @patch('accounts.tasks.send_team_assignment_email.delay')
    def test_assign_triggers_celery_task(self, mock_delay):
        mock_delay.return_value = None
        res = self.client.post(
            f'/api/teams/{self.team.pk}/assign/',
            {'employee_id': self.employee.pk},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mock_delay.assert_called_once_with(self.team.id, self.employee.id)

    def test_api_response_not_blocked_by_email(self):
        res = self.client.post(
            f'/api/teams/{self.team.pk}/assign/',
            {'employee_id': self.employee.pk},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TeamMember.objects.count(), 1)

    def test_email_sent_on_successful_assign(self):
        res = self.client.post(
            f'/api/teams/{self.team.pk}/assign/',
            {'employee_id': self.employee.pk},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['employee1@test.com'])
