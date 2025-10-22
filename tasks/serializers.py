from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
from .models import UserProfile,Task,TaskActivity,TaskComment,Project,Notification
from .models import Task, TaskComment, TaskActivity, Project
from datetime import date

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
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
        #UserProfile.objects.create(user=user)
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
#     assignee = serializers.PrimaryKeyRelatedField(
#     queryset=User.objects.all(), required=True
# )
#     project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    assignee = serializers.CharField(write_only=True)
    project = serializers.CharField(write_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline', 'created_at', 'assignee', 'status_note', 'project']

    def validate(self, data):
        if self.instance is None:
            assignee_name = data.pop('assignee')
            project_name = data.pop('project')

            try:
                assignee_user = User.objects.get(username=assignee_name)
                data['assignee'] = assignee_user
            except User.DoesNotExist:
                raise serializers.ValidationError({'assignee': f"User '{assignee_name}' does not exist."})

            try:
                project = Project.objects.get(title=project_name)
                data['project'] = project
            except Project.DoesNotExist:
                raise serializers.ValidationError({'project': f"Project '{project_name}' does not exist."})
            return data
        else:
            if 'assignee' in data:
                assignee_name = data.pop('assignee')    
                try:
                    assignee_user = User.objects.get(username=assignee_name)
                    data['assignee'] = assignee_user
                except User.DoesNotExist:
                    raise serializers.ValidationError({'assignee': f"User '{assignee_name}' does not exist."})
            return data

    validators = [UniqueTogetherValidator(queryset = Task.objects.all(),fields=['title','assignee'])]


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
    #start_date = serializers.DateTimeField(read_only=True,default=date.today)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager', 'start_date', 'deadline']
        validators = [UniqueTogetherValidator(queryset = Project.objects.all(),fields=['title','description'])]

    def validate(self,data):
            start_date = data.get('start_date',date.today())
            deadline = data.get('deadline')
            if deadline <= start_date:
                raise serializers.ValidationError("Deadline must be after the start date")
            return data


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

class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(read_only=True,source='task.title')
    task_description = serializers.CharField(read_only=True,source='task.description')
    project_name = serializers.CharField(read_only=True,source='project.title')
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'task_title', 'task_description' , 'project_name']
