from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView,UserListView


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('user/', UserListView.as_view(), name='user-list'),
]
