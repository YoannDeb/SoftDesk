from rest_framework.permissions import BasePermission


class IsProjectContributor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.project in request.user.projects)


class IsProjectAuthor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.project.author_user_id == request.user)


class IsCurrentUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user == request.context.user)


class IsIssueAuthor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user == request.issue.author_user_id)
