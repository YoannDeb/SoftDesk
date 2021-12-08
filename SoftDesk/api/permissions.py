from rest_framework.permissions import BasePermission


class IsProjectContributor(BasePermission):
    def has_permission(self, request, view):
        project_pk = int(request.resolver_match.kwargs['project_pk'])
        user_is_contributor_projects_pks = list(request.user.project_set.all().values_list('pk', flat=True))
        return project_pk in user_is_contributor_projects_pks


class IsProjectAuthor(BasePermission):
    def has_permission(self, request, view):
        project_pk = int(request.resolver_match.kwargs['project_pk'])
        user_is_author_project_pks = list(request.user.project_set.filter(author_user_id=request.user).values_list('pk', flat=True))
        return project_pk in user_is_author_project_pks


class IsCurrentUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.pk == int(request.resolver_match.kwargs['user_pk'])


class IsIssueAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.pk in list(request.user.issues.all().values_list('pk', flat=True))


class IsCommentAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.pk in list(request.user.comments.all().values_list('pk', flat=True))
