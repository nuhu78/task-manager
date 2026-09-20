from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='task_complete'),
    path('tasks/dashboard/', views.dashboard, name='task_dashboard'),
]
