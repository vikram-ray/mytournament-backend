from rest_framework import permissions

class UpdateOwnProfile(permissions.BasePermission): 
    """ Permission for updating CustomUser """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id



class ChangeUserPasswordPermission(permissions.BasePermission): 
    """ Permission for updating own password """
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id



