from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Team, TeamMember


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('phone', 'profile_picture', 'bio', 'role')}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']
    list_filter = ['manager']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['team', 'employee', 'joined_at']
    list_filter = ['team']
