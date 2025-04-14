from django.urls import path
from .views import RegisterAPIView, LoginAPIView,LogoutAPIView,UserListView,TaskCreateView,TaskListView,TaskUpdateView,TaskActivityListView,TaskCommentListCreateView,ProjectListCreateView,MyTasksView,TaskDetailView,ProjectDetailView,NotificationListView,NotificationMarkAsReadView,NotificationMarkAllAsReadView


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/', UserListView.as_view(), name='user-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:task_id>/activity/', TaskActivityListView.as_view(), name='task-activity'),
    path('tasks/<int:task_id>/comments/', TaskCommentListCreateView.as_view(), name='task-comments'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('my-tasks/', MyTasksView.as_view(), name='my-tasks'),
    path('tasks/<int:pk>/detail/', TaskDetailView.as_view(), name='task-detail'),
    path('projects/<int:pk>/detail/', ProjectDetailView.as_view(), name='project-detail'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', NotificationMarkAsReadView.as_view(), name='mark-notification-read'),
    path('notifications/read-all/', NotificationMarkAllAsReadView.as_view(), name='mark-all-read'),


]
