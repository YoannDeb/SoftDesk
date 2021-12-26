from rest_framework.permissions import BasePermission
from django.core.exceptions import ObjectDoesNotExist
from .models import Project, Contributor, Issue, Comment, CustomUser


class IsProjectContributor(BasePermission):
    """
    - Checking if the user is contributor by checking if project pk in url
    is in the set of the projects of which the authenticated user is contributor or author.
    - Message is changed if the project does not exist.
    """
    message = "Access forbidden: You are not contributor of the project"

    def has_permission(self, request, view):
        try:
            project_pk = int(request.resolver_match.kwargs['project_pk'])
        except KeyError:
            project_pk = int(request.resolver_match.kwargs['pk'])

        # Adapted message if project does not exist:
        try:
            Project.objects.get(pk=project_pk)
        except ObjectDoesNotExist:
            self.message = "Project does not exist"

        projects_of_which_user_is_contributor = list(request.user.project_set.all().values_list('pk', flat=True))
        return project_pk in projects_of_which_user_is_contributor


class IsProjectAuthor(BasePermission):
    """
    - Checking if the user is the author of the project comparing the project's author_user_id and
    the authenticated user's pk.
    - Message is changed if the project does not exist at all.
    """
    message = "Access forbidden: You are not the author of the project"

    def has_permission(self, request, view):
        try:
            project_pk = int(request.resolver_match.kwargs['project_pk'])
        except KeyError:
            project_pk = int(request.resolver_match.kwargs['pk'])

        # Adapted message if project does not exist at all:
        try:
            Project.objects.get(pk=project_pk)
        except ObjectDoesNotExist:
            self.message = "Project does not exist"

        project = request.user.project_set.get(pk=project_pk)
        return project.author_user_id == request.user.pk


class IsCurrentUser(BasePermission):
    """
    - Checking if the current user is the user concerned by checking if user pk in url is the user authenticated.
    - Message is changed if the user does not exist at all.
    """
    message = "Access forbidden: You are not the user concerned"

    def has_permission(self, request, view):
        user_pk_in_url = int(request.resolver_match.kwargs['pk'])

        # Adapted message if project does not exist at all:
        try:
            CustomUser.objects.get(pk=user_pk_in_url)
        except ObjectDoesNotExist:
            self.message = "User does not exist"

        return request.user.pk == user_pk_in_url


class IsIssueAuthor(BasePermission):
    """
    - Checking if the user is the author of the issue by checking if issue pk in url
    is in the set of the issues of which the authenticated user is the author.
    - Message is changed if the issue does not exist at all.
    """
    message = "Access forbidden: You are not the author of the issue"

    def has_permission(self, request, view):
        try:
            issue_pk = int(request.resolver_match.kwargs['pk'])
            issues_of_which_user_is_the_author = list(request.user.created_issues.all().values_list('pk', flat=True))

            # Adapted message if issue does not exist:
            Issue.objects.get(pk=issue_pk)

            return issue_pk in issues_of_which_user_is_the_author
        except AttributeError:
            return False

        # Adapted message if issue does not exist at all:
        except ObjectDoesNotExist:
            self.message = "Issue does not exist"
            return False


class IsCommentAuthor(BasePermission):
    """
    - Checking if the user is the author of the comment by checking if comment pk in url
    is in the set of the comments of which the authenticated user is the author.
    - Message is changed if the issue does not exist at all.
    """
    message = "Access forbidden: You are not the author of the comment"

    def has_permission(self, request, view):
        try:
            comment_pk = int(request.resolver_match.kwargs['pk'])
            comments_of_which_user_is_the_author = list(request.user.comments.all().values_list('pk', flat=True))

            # Adapted message if comment does not exist:
            Comment.objects.get(pk=comment_pk)
            return comment_pk in comments_of_which_user_is_the_author

        except AttributeError:
            return False

        # Adapted message if comment does not exist at all:
        except ObjectDoesNotExist:
            self.message = "Issue does not exist"
            return False
