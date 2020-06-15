from rest_framework import permissions


class TournamentUpdatePermission(permissions.BasePermission): 
    """ Permission for updating Tournament """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.id == obj.created_by.id


    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
