import os

from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanegement.settings')

# Create the Celery application
app = Celery('taskmanegement')

# Read configuration from Django settings (CELERY_ namespace)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()