from rest_framework.permissions import BasePermission


class IsProjectContributor(BasePermission):
    def has_permissions(self, request, view):
        return bool(request.user and request.user.is_authhenticated and request.project in request.user.projects)


class IsProjectAuthor(BasePermission):
    def has_permissions(self, request, view):
        return bool(request.user and request.user.is_authhenticated and request.project.author_user_id == request.user)