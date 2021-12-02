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

    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='users')
    permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES)
    role = models.CharField(max_length=300)


class Project(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=50)
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Contributor')

    def __str__(self):
        return self.title

    @property
    def author_user_id(self):
        return User.objects.get(projects__project_id=self, projects__permission=Contributor.AUTHOR).pk


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
