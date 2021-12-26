from rest_framework.permissions import BasePermission


class IsProjectContributor(BasePermission):
    message = "Access forbidden: You are not contributor of the project"

    def has_permission(self, request, view):
        try:
            project_pk = int(request.resolver_match.kwargs['project_pk'])
        except:
            project_pk = int(request.resolver_match.kwargs['pk'])
        projects_of_which_user_is_contributor = list(request.user.project_set.all().values_list('pk', flat=True))
        return project_pk in projects_of_which_user_is_contributor


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
        try:
            issue = int(request.resolver_match.kwargs['pk'])
            issues_of_which_user_is_the_author = list(request.user.created_issues.all().values_list('pk', flat=True))
            return issue in issues_of_which_user_is_the_author
        except AttributeError:
            return False


class IsCommentAuthor(BasePermission):
    message = "Access forbidden: You are not the author of the comment"

    def has_permission(self, request, view):
        try:
            comment = int(request.resolver_match.kwargs['pk'])
            comments_of_which_user_is_the_author = list(request.user.comments.all().values_list('pk', flat=True))
            return comment in comments_of_which_user_is_the_author
        except AttributeError:
            return False
