from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


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
    BACK_END = 'BE'
    FRONT_END = 'FE'
    IOS = 'IO'
    ANDROID = 'AN'

    TYPE_CHOICES = [
        (BACK_END, 'back-end'),
        (FRONT_END, 'front-end'),
        (IOS, 'IOS'),
        (ANDROID, 'Android'),
    ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Contributor')

    def __str__(self):
        return self.title

    @property
    def author_user_id(self):
        return User.objects.get(projects__project_id=self, projects__permission=Contributor.AUTHOR).pk


class Issue(models.Model):
    BUG = 'BU'
    AMELIORATION = 'AM'
    TACHE = 'TA'

    TAG_CHOICES = [
        (BUG, 'BUG'),
        (AMELIORATION, 'AMÉLIORATION'),
        (TACHE, 'TÂCHE'),
    ]

    A_FAIRE = 'AF'
    EN_COURS = 'EC'
    TERMINE = 'TE'

    STATUS_CHOICES = [
        (A_FAIRE, 'À faire'),
        (EN_COURS, 'En cours'),
        (TERMINE, 'Terminé'),
    ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    tag = models.CharField(max_length=50, choices=TAG_CHOICES)
    priority = models.CharField(max_length=50)
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='issues')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
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
