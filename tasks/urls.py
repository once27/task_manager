from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView,UserListView,TaskCreateView,TaskListView


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/', UserListView.as_view(), name='user-list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
]
