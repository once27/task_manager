from rest_framework.permissions import BasePermission

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role in ['admin', 'manager']
        )
    
class IsAdminOrManagerOrAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if (hasattr(request.user, 'profile') and
                request.user.profile.role in ['admin', 'manager']):
            return True
        
        return obj.assignee == request.user
    
class IsProjectMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if (hasattr(request.user, 'profile') and
                request.user.profile.role in ['admin', 'manager']):
            return True

        project = obj.project

        if project and request.user in project.members.all():
            return True
        
        return False