from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer, DashboardSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def complete_task(request, pk):
    try:
        task = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    task.status = 'completed'
    task.save()
    return Response(TaskSerializer(task).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    data = tasks.aggregate(
        total_tasks=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        completed=Count('id', filter=Q(status='completed')),
    )
    return Response(data)
