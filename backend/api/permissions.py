from rest_framework.permissions import BasePermission


class AuthorOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
