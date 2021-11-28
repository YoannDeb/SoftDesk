from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


class Contributor(models.Model):

    AUTHOR = 'AU'
    CONTRIBUTOR = 'CO'

    PERMISSION_CHOICES = [
        (AUTHOR, 'Author'),
        (CONTRIBUTOR, 'Contributor'),
    ]

    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contributors')
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='contributors')

    permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES)  # Unique author? a priori yes
    role = models.CharField(max_length=300)


class Project(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=50)
    # Use something like project.Contributors.objects.filter(project_id=pk).filter(permission=AUTHOR)
    # or
    # author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Projects')

    def __str__(self):
        return self.title


class Issue(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    tag = models.CharField(max_length=50)
    priority = models.CharField(max_length=50)
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='issues')
    status = models.CharField(max_length=50)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_issues')
    assignee_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_issues')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    description = models.CharField(max_length=300)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    issue_id = models.ForeignKey('api.Issue', on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)
