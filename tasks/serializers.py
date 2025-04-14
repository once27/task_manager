from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile,Task,TaskActivity,TaskComment,Project

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

def create(self, validated_data):
    user = User.objects.create_user(
        username=validated_data['username'],
        email=validated_data['email'],
        password=validated_data['password']
    )
    # Explicitly create UserProfile
    UserProfile.objects.create(user=user)
    return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='profile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

# only for admin to get roles
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
    queryset=User.objects.all(), required=True
)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline', 'created_at', 'assignee', 'status_note', 'project']


class TaskActivitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskActivity
        fields = ['id', 'user', 'action', 'message', 'timestamp']

class TaskCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'user', 'message', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    manager = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager', 'start_date', 'deadline']

from .models import Task, TaskComment, TaskActivity, Project

class TaskCommentMiniSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = TaskComment
        fields = ['user', 'message', 'created_at']


class TaskActivityMiniSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = TaskActivity
        fields = ['user', 'action', 'message', 'timestamp']


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = serializers.StringRelatedField()
    project = serializers.StringRelatedField()
    comments = TaskCommentMiniSerializer(many=True, read_only=True)
    activity_log = TaskActivityMiniSerializer(source='activities', many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 'deadline',
            'created_at', 'assignee', 'project',
            'comments', 'activity_log'
        ]


class ProjectTaskMiniSerializer(serializers.ModelSerializer):
    assignee = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'assignee', 'deadline']


class ProjectDetailSerializer(serializers.ModelSerializer):
    manager = serializers.StringRelatedField()
    tasks = ProjectTaskMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'manager',
            'start_date', 'deadline', 'tasks'
        ]

