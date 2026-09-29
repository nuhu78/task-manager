from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.urls import path

def trigger_error(request):
    division_by_zero = 1 / 1
    return HttpResponse("ok")

urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('tasks.urls')),
]
