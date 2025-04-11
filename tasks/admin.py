from django.contrib import admin
from .models import UserProfile,Task
# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'assignee', 'status', 'priority', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'deadline')
    search_fields = ('title', 'description', 'assignee__username')
    ordering = ('-created_at',)
