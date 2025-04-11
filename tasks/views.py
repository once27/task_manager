from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from .serializers import RegisterSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.decorators import authentication_classes, permission_classes
from .serializers import UserSerializer,TaskSerializer,TaskActivitySerializer,TaskCommentSerializer
from .models import Task,TaskActivity,TaskActivity,TaskComment
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404

# Create your views here.

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user_id": user.id,
            "username": user.username,
            "token": token.key
        })


class LoginAPIView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            "user_id": token.user_id,
            "username": token.user.username,
            "token": token.key
        })

class LogoutAPIView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except:
            raise AuthenticationFailed("Invalid or missing token.")
        logout(request)
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

# class LogoutAPIView(generics.GenericAPIView):
#     def post(self, request, *args, **kwargs):
#         request.user.auth_token.delete()
#         logout(request)
#         return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class UserListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get('role', None)

        if role:
            users = User.objects.filter(userprofile__role=role)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

# only for admin access 
# class UserListView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class TaskCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Only admin and manager allowed to create tasks
        if not (user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['admin', 'manager'])):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# currently not working
class TaskListView(ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins and managers can see all tasks
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['admin', 'manager']):
            return Task.objects.all()
        
        # Team members see only their assigned tasks
        return Task.objects.filter(assignee=user)
    
class TaskUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        task = get_object_or_404(Task, pk=pk)

        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['admin', 'manager']):
            serializer = TaskSerializer(task, data=request.data, partial=True)
            update_data = request.data
        else:
            if task.assignee != user:
                return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            allowed_fields = {'status', 'status_note'}
            update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

            if 'status' in update_data and 'status_note' not in update_data:
                return Response(
                    {"detail": "Please provide a status note when updating task status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = TaskSerializer(task, data=update_data, partial=True)

        if serializer.is_valid():
            old_values = {field: getattr(task, field) for field in update_data.keys()}#Save old values BEFORE saving

            serializer.save()             # 2. Save new updated values
            task.refresh_from_db()

            changed_fields = [] 
            for field in update_data.keys():
                old = old_values.get(field)
                new = getattr(task, field)
                if str(old) != str(new):
                    changed_fields.append(f"{field} changed from '{old}' to '{new}'") #Compare and generate message to display

            message = "; ".join(changed_fields) if changed_fields else ''
 
            TaskActivity.objects.create( #Log activity
                task=task,
                user=user,
                action='status_change' if 'status' in update_data else 'updated',
                message=message
            )

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskActivityListView(ListAPIView):
    serializer_class = TaskActivitySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskActivity.objects.filter(task__id=task_id).order_by('-timestamp')
    
class TaskCommentListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        comments = TaskComment.objects.filter(task__id=task_id).order_by('created_at')
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
