from rest_framework.permissions import BasePermission


class IsProjectContributor(BasePermission):
    message = "Access forbidden: You are not contributor of the project"

    def has_permission(self, request, view):
        try:
            project_pk = int(request.resolver_match.kwargs['project_pk'])
        except:
            project_pk = int(request.resolver_match.kwargs['pk'])

        # project = request.user.project_set.get(pk=project_pk)
        projects_pks_of_which_user_is_contributor = list(request.user.project_set.all().values_list('pk', flat=True))
        return project_pk in projects_pks_of_which_user_is_contributor
    #todo: returning not allowed when project does not exist


class IsProjectAuthor(BasePermission):
    message = "Access forbidden: You are not the author of the project"

    def has_permission(self, request, view):
        try:
            project_pk = int(request.resolver_match.kwargs['project_pk'])
        except:
            project_pk = int(request.resolver_match.kwargs['pk'])
        project = request.user.project_set.get(pk=project_pk)
        return project.author_user_id == request.user.pk


class IsCurrentUser(BasePermission):
    message = "Access forbidden: You are not the user concerned"

    def has_permission(self, request, view):
        return request.user.pk == int(request.resolver_match.kwargs['pk'])


class IsIssueAuthor(BasePermission):
    message = "Access forbidden: You are not the author of the issue"

    def has_permission(self, request, view):
        return request.user.pk in list(request.user.issues.all().values_list('pk', flat=True))


class IsCommentAuthor(BasePermission):
    message = "Access forbidden: You are not the author of the comment"

    def has_permission(self, request, view):
        return request.user.pk in list(request.user.comments.all().values_list('pk', flat=True))
