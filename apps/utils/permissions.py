from rest_framework import permissions


class CustomReadonlyPermission(permissions.BasePermission): 
    """ Permission for reading """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
