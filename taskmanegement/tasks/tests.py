from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tasks.models import Task

User = get_user_model()


class JWTAuthMixin:
    """Register + login a user, store JWT tokens."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'
        self.login_url = '/api/login/'

        self.user_data = {
            'username': 'taskuser',
            'email': 'taskuser@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 'employee',
        }
        self.register()

    def register(self):
        response = self.client.post(
            self.register_url, self.user_data, format='json'
        )
        self.access_token = response.data['tokens']['access']
        self.refresh_token = response.data['tokens']['refresh']
        self.user_id = response.data['user']['id']

    def login(self, username='taskuser', password='StrongPass123!'):
        response = self.client.post(
            self.login_url,
            {'username': username, 'password': password},
            format='json',
        )
        self.access_token = response.data['tokens']['access']
        self.refresh_token = response.data['tokens']['refresh']

    def auth_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')


# ──────────────────────────────────────────────
#  Model Tests
# ──────────────────────────────────────────────


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='m1', email='m1@test.com', password='Pass123!'
        )

    def test_create_task(self):
        task = Task.objects.create(
            user=self.user, title='Task1', description='desc',
            status='pending', priority='high',
        )
        self.assertEqual(task.title, 'Task1')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.user, self.user)

    def test_str(self):
        task = Task.objects.create(user=self.user, title='Hello')
        self.assertEqual(str(task), 'Hello')

    def test_defaults(self):
        task = Task.objects.create(user=self.user, title='Def')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'medium')

    def test_ordering_newest_first(self):
        t1 = Task.objects.create(user=self.user, title='First')
        t2 = Task.objects.create(user=self.user, title='Second')
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], t2)
        self.assertEqual(tasks[1], t1)

    def test_status_choices(self):
        for val in ['pending', 'in_progress', 'completed']:
            t = Task.objects.create(user=self.user, title=val, status=val)
            self.assertEqual(t.status, val)

    def test_priority_choices(self):
        for val in ['low', 'medium', 'high']:
            t = Task.objects.create(user=self.user, title=val, priority=val)
            self.assertEqual(t.priority, val)


# ──────────────────────────────────────────────
#  Authentication Tests (JWT)
# ──────────────────────────────────────────────


class TaskAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post('/api/register/', {
            'username': 'authuser',
            'email': 'auth@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 'employee',
        }, format='json')

    def test_login_returns_tokens(self):
        response = self.client.post('/api/login/', {
            'username': 'authuser', 'password': 'StrongPass123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_refresh_token(self):
        login = self.client.post('/api/login/', {
            'username': 'authuser', 'password': 'StrongPass123!'
        }, format='json')
        refresh = login.data['tokens']['refresh']
        response = self.client.post('/api/token/refresh/', {
            'refresh': refresh
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


# ──────────────────────────────────────────────
#  Create Task
# ──────────────────────────────────────────────


class TaskCreateTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()

    def test_create_task(self):
        data = {
            'title': 'New Task',
            'description': 'Learn testing',
            'status': 'pending',
            'priority': 'high',
            'due_date': '2026-12-31',
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_minimal(self):
        response = self.client.post('/api/tasks/', {
            'title': 'Minimal'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['priority'], 'medium')

    def test_create_task_belongs_to_logged_in_user(self):
        self.client.post('/api/tasks/', {'title': 'Mine'}, format='json')
        task = Task.objects.first()
        self.assertEqual(task.user.username, 'taskuser')


# ──────────────────────────────────────────────
#  List Tasks
# ──────────────────────────────────────────────


class TaskListTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()

    def test_list_empty(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list_own_tasks(self):
        user = User.objects.get(username='taskuser')
        Task.objects.create(user=user, title='T1')
        Task.objects.create(user=user, title='T2')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data['count'], 2)

    def test_list_excludes_other_users(self):
        user = User.objects.get(username='taskuser')
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        Task.objects.create(user=user, title='Mine')
        Task.objects.create(user=other, title='Theirs')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Mine')


# ──────────────────────────────────────────────
#  Retrieve Task
# ──────────────────────────────────────────────


class TaskRetrieveTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')

    def test_get_task(self):
        task = Task.objects.create(user=self.user, title='Get Me')
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Get Me')


# ──────────────────────────────────────────────
#  Update Task
# ──────────────────────────────────────────────


class TaskUpdateTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')
        self.task = Task.objects.create(
            user=self.user, title='Old', description='old desc',
            status='pending', priority='low',
        )

    def test_full_update(self):
        response = self.client.put(f'/api/tasks/{self.task.id}/', {
            'title': 'New',
            'description': 'new desc',
            'status': 'in_progress',
            'priority': 'high',
            'due_date': '2026-12-31',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'New')
        self.assertEqual(self.task.status, 'in_progress')

    def test_partial_update(self):
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            {'priority': 'high'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.priority, 'high')
        self.assertEqual(self.task.title, 'Old')


# ──────────────────────────────────────────────
#  Delete Task
# ──────────────────────────────────────────────


class TaskDeleteTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')

    def test_delete_task(self):
        task = Task.objects.create(user=self.user, title='Delete Me')
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


# ──────────────────────────────────────────────
#  Complete Task
# ──────────────────────────────────────────────


class TaskCompleteTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')

    def test_complete_task(self):
        task = Task.objects.create(
            user=self.user, title='Done', status='pending'
        )
        response = self.client.patch(f'/api/tasks/{task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')

    def test_complete_already_completed(self):
        task = Task.objects.create(
            user=self.user, title='Done', status='completed'
        )
        response = self.client.patch(f'/api/tasks/{task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, 'completed')


# ──────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────


class DashboardTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')

    def test_empty_dashboard(self):
        response = self.client.get('/api/tasks/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_tasks'], 0)
        self.assertEqual(response.data['pending'], 0)
        self.assertEqual(response.data['in_progress'], 0)
        self.assertEqual(response.data['completed'], 0)

    def test_dashboard_counts(self):
        Task.objects.create(user=self.user, title='P1', status='pending')
        Task.objects.create(user=self.user, title='P2', status='pending')
        Task.objects.create(user=self.user, title='IP', status='in_progress')
        Task.objects.create(user=self.user, title='C1', status='completed')
        response = self.client.get('/api/tasks/dashboard/')
        self.assertEqual(response.data['total_tasks'], 4)
        self.assertEqual(response.data['pending'], 2)
        self.assertEqual(response.data['in_progress'], 1)
        self.assertEqual(response.data['completed'], 1)

    def test_dashboard_only_own_tasks(self):
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        Task.objects.create(user=self.user, title='Mine', status='pending')
        Task.objects.create(user=other, title='Theirs', status='completed')
        response = self.client.get('/api/tasks/dashboard/')
        self.assertEqual(response.data['total_tasks'], 1)


# ──────────────────────────────────────────────
#  Pagination (30 tasks, PAGE_SIZE=10)
# ──────────────────────────────────────────────


class TaskPaginationTest(JWTAuthMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.auth_header()
        self.user = User.objects.get(username='taskuser')
        for i in range(30):
            Task.objects.create(
                user=self.user,
                title=f'Task {i+1:02d}',
                status=['pending', 'in_progress', 'completed'][i % 3],
                priority=['low', 'medium', 'high'][i % 3],
            )

    def test_total_count_is_30(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data['count'], 30)

    def test_first_page(self):
        response = self.client.get('/api/tasks/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_last_page(self):
        response = self.client.get('/api/tasks/?page=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_middle_page(self):
        response = self.client.get('/api/tasks/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_all_30_tasks_across_pages(self):
        all_tasks = []
        for page in range(1, 4):
            response = self.client.get(f'/api/tasks/?page={page}')
            all_tasks.extend(response.data['results'])
        titles = [t['title'] for t in all_tasks]
        self.assertEqual(len(all_tasks), 30)
        self.assertIn('Task 01', titles)
        self.assertIn('Task 15', titles)
        self.assertIn('Task 30', titles)

    def test_no_page_param_returns_first_page(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data['results']), 10)


# ──────────────────────────────────────────────
#  Exception Tests
# ──────────────────────────────────────────────


class ExceptionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post('/api/register/', {
            'username': 'exuser',
            'email': 'ex@test.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 'employee',
        }, format='json')
        login = self.client.post('/api/login/', {
            'username': 'exuser', 'password': 'StrongPass123!'
        }, format='json')
        self.token = login.data['tokens']['access']
        self.user = User.objects.get(username='exuser')

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    # --- Auth exceptions ---
    def test_wrong_password_401(self):
        res = self.client.post('/api/login/', {
            'username': 'exuser', 'password': 'WrongPass!'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token_returns_401(self):
        res = self.client.get('/api/tasks/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_returns_401(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken123')
        res = self.client.get('/api/tasks/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Create task exceptions ---
    def test_create_completed_not_allowed(self):
        self.auth()
        res = self.client.post('/api/tasks/', {
            'title': 'Bad', 'status': 'completed'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_title(self):
        self.auth()
        res = self.client.post('/api/tasks/', {
            'description': 'no title'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)

    # --- Retrieve task exceptions ---
    def test_get_nonexistent_task_404(self):
        self.auth()
        res = self.client.get('/api/tasks/9999/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_other_users_task_404(self):
        self.auth()
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        task = Task.objects.create(user=other, title='Secret')
        res = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Update task exceptions ---
    def test_cannot_update_other_users_task(self):
        self.auth()
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        task = Task.objects.create(user=other, title='Secret')
        res = self.client.patch(
            f'/api/tasks/{task.id}/', {'title': 'Hacked'}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Delete task exceptions ---
    def test_cannot_delete_other_users_task(self):
        self.auth()
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        task = Task.objects.create(user=other, title='Protected')
        res = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.filter(user=other).count(), 1)

    # --- Complete task exceptions ---
    def test_complete_nonexistent_404(self):
        self.auth()
        res = self.client.patch('/api/tasks/9999/complete/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_complete_other_users_task(self):
        self.auth()
        other = User.objects.create_user(
            username='other', email='o@t.com', password='Pass123!'
        )
        task = Task.objects.create(user=other, title='Secret', status='pending')
        res = self.client.patch(f'/api/tasks/{task.id}/complete/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # --- Pagination exceptions ---
    def test_out_of_range_page(self):
        self.auth()
        for i in range(12):
            Task.objects.create(user=self.user, title=f'T{i}')
        res = self.client.get('/api/tasks/?page=99')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
