from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Team, TeamMember

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
