from django.contrib import admin
from .models import UserProfile,Task,TaskActivity,TaskComment,Project

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

@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'action', 'message', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('task__title', 'user__username', 'message')
    ordering = ('-timestamp',)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'message', 'created_at')
    search_fields = ('task__title', 'user__username', 'message')
    ordering = ('-created_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'manager', 'start_date', 'deadline')
    search_fields = ('title', 'description')
    list_filter = ('start_date', 'deadline')    