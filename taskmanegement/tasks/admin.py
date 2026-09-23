from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(role='employee')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
