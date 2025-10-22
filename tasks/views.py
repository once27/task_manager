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
from .permissions import IsAdminOrManager,IsAdminOrManagerOrAssignee,IsProjectMemberOrAdmin
from .serializers import UserSerializer,TaskSerializer,TaskActivitySerializer,TaskCommentSerializer,ProjectSerializer,TaskDetailSerializer,ProjectDetailSerializer,NotificationSerializer,ProjectMemberSerializer
from .models import Task,TaskActivity,TaskActivity,TaskComment,Project,Notification
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from django.utils.dateparse import parse_date
from rest_framework.response import Response

# Create your views here.

def dashboard_view(request):
    return render(request, 'dashboard.html')
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


class TaskCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManager]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()

            Notification.objects.create(# Send notification to assignee
                recipient=task.assignee,
                message=f"You've been assigned a new task: {task.title}",
                task=task,
                project=task.project
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TaskListView(ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()

        project_id = self.request.query_params.get('project')# Filter by project ID
        if project_id:
            queryset = queryset.filter(project__id=project_id)
 
        status_filter = self.request.query_params.get('status')# Filter by task status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        deadline_before = self.request.query_params.get('deadline_before')# Filter by deadline before or after
        deadline_after = self.request.query_params.get('deadline_after')

        if deadline_before:
            queryset = queryset.filter(deadline__lte=parse_date(deadline_before))

        if deadline_after:
            queryset = queryset.filter(deadline__gte=parse_date(deadline_after))

        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['admin', 'manager']):# Role-based visibility
            return queryset

        return queryset.filter(assignee=user)
    
class MyTasksView(ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(assignee=user)

        status_filter = self.request.query_params.get('status')# Filter by status
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        priority_filter = self.request.query_params.get('priority')# Filter by priority
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        ordering = self.request.query_params.get('order_by')
        if ordering in ['deadline', 'priority', '-deadline', '-priority']:
            queryset = queryset.order_by(ordering)

        return queryset

    
class TaskUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManagerOrAssignee]

    def patch(self, request, pk):
        user = request.user
        task = get_object_or_404(Task, pk=pk)

        self.check_object_permissions(request, task)

        valid_transitions = {# Status transition control
            'todo': ['in_progress'],
            'in_progress': ['done', 'todo'],
            'done': [],
        }

        new_status = request.data.get('status')
        if new_status:
            current_status = task.status

            if new_status != current_status:
                allowed = valid_transitions.get(current_status, [])
                if new_status not in allowed:
                    if not (user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['admin', 'manager'])):# admin/manager can break the flow
                        return Response(
                            {"detail": f"Invalid status transition from '{current_status}' to '{new_status}'"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

        if hasattr(user, 'profile') and user.profile.role in ['admin', 'manager']:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            update_data = request.data
        else:
            allowed_fields = {'status', 'status_note'}
            update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

            if 'status' in update_data and 'status_note' not in update_data:
                return Response(
                    {"detail": "Please provide a status note when updating task status."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = TaskSerializer(task, data=update_data, partial=True)

        if serializer.is_valid():
            old_values = {field: getattr(task, field) for field in update_data.keys()}  # Save old values

            serializer.save()  # Save new updated values
            task.refresh_from_db()

            changed_fields = []
            for field in update_data.keys():
                old = old_values.get(field)
                new = getattr(task, field)
                if str(old) != str(new):
                    changed_fields.append(f"{field} changed from '{old}' to '{new}'")

            message = "; ".join(changed_fields) if changed_fields else ''

            TaskActivity.objects.create(
                task=task,
                user=user,
                action='status_change' if 'status' in update_data else 'updated',
                message=message
            )
            
            if 'status' in update_data:# Send status update notification to assignee
                Notification.objects.create(
                recipient=task.assignee,
                message=f"Status of task '{task.title}' changed to '{task.status}'",
                task=task,
                project=task.project
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
    permission_classes = [IsAuthenticated,IsProjectMemberOrAdmin]

    def get(self, request, task_id):
        comments = TaskComment.objects.filter(task__id=task_id).order_by('created_at')
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        self.check_object_permissions(request, task)    
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(task=task, user=request.user)

            if task.assignee != request.user: # Notify assignee 
                Notification.objects.create(
                    recipient=task.assignee,
                    message=f"{request.user.username} commented on task: {task.title}",
                    task=task,
                    project=task.project
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectListCreateView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManager]

    def get_queryset(self):
        return Project.objects.all()

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

class TaskDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManagerOrAssignee]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        self.check_object_permissions(request, task)
       
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

class ProjectDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        # Optional: Only manager/admin sees all, others need to be involved
        if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['admin', 'manager'])):
            if not project.tasks.filter(assignee=request.user).exists():
                return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)

class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        serializer = self.get_serializer(queryset, many=True)
    
        queryset.update(is_read=True)
        
        return Response(serializer.data)
    
class ProjectMemberView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManager]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        self.check_object_permissions(request, project) # Run permission check
        
        usernames = request.data.get('usernames', []) # Get usernames as a list
        if not usernames:
            return Response({"error": "List of usernames is required"}, status=status.HTTP_400_BAD_REQUEST)

        added_users = []
        not_found_users = []
        for username in usernames:
            try:
                user_to_add = User.objects.get(username=username)
                project.members.add(user_to_add)
                added_users.append(username)
            except User.DoesNotExist:
                not_found_users.append(username)

        response_data = {}
        if added_users:
            response_data["added"] = f"Users '{', '.join(added_users)}' added to project '{project.title}'"
        if not_found_users:
            response_data["not_found"] = f"Users '{', '.join(not_found_users)}' not found"

        return Response(response_data)
    
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        members = project.members.all()
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        self.check_object_permissions(request, project) # Run permission check

        usernames = request.data.get('usernames', [])
        if not usernames:
            return Response({"error": "List of usernames is required"}, status=status.HTTP_400_BAD_REQUEST)

        removed_users = []
        not_found_users = []
        for username in usernames:
            try:
                user_to_remove = User.objects.get(username=username)
                project.members.remove(user_to_remove)
                removed_users.append(username)
            except User.DoesNotExist:
                not_found_users.append(username)

        response_data = {}
        if removed_users:
            response_data["removed"] = f"Users '{', '.join(removed_users)}' removed from project '{project.title}'"
        if not_found_users:
            response_data["not_found"] = f"Users '{', '.join(not_found_users)}' not found"

        return Response(response_data)