from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models, transaction
from django.conf import settings


class CustomUserManager(BaseUserManager):
    """
    Custom user manager is necessary for custom user with custom fields (notably email as username) to work.
    """
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        with transaction.atomic():
            user = self.model(email=self.normalize_email(email), **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user, notably for email as username.
    Declared in settings.py
    """
    email = models.EmailField(max_length=255, unique=True, verbose_name='email address', error_messages={'unique':'A user with this email already exists.'})
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        return self.is_superuser

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Contributor(models.Model):
    """
    Contributor model. Contributor is a through table between Projects and Users.
    It stores permissions and roles in addition to foreign keys.
    """
    AUTHOR = 'AU'
    CONTRIBUTOR = 'CO'

    PERMISSION_CHOICES = [
        (AUTHOR, 'Author'),
        (CONTRIBUTOR, 'Contributor'),
    ]

    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='users')
    permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES)
    role = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user_id', 'project_id')


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

    title = models.CharField(max_length=120, blank=False, unique=True)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, error_messages={
        'invalid_choice': f'Type must be between those choices: {BACK_END} for Back-end; {FRONT_END} for front-end; '
                          f'{IOS} for IOS; {ANDROID} for Android'
    })
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Contributor')

    def __str__(self):
        return self.title

    @property
    def author_user_id(self):
        return CustomUser.objects.get(projects__project_id=self, projects__permission=Contributor.AUTHOR).pk


class Issue(models.Model):
    """
    Issues are bound to a project.
    """
    BUG = 'BU'
    AMELIORATION = 'AM'
    TACHE = 'TA'

    TAG_CHOICES = [
        (BUG, 'BUG'),
        (AMELIORATION, 'AMÉLIORATION'),
        (TACHE, 'TÂCHE'),
    ]

    FAIBLE = 'FA'
    MOYENNE = 'MO'
    ELEVEE = 'EL'

    PRIORITY_CHOICES = [
        (FAIBLE, 'FAIBLE'),
        (MOYENNE, 'MOYENNE'),
        (ELEVEE, 'ÉLEVÉE')
    ]

    A_FAIRE = 'AF'
    EN_COURS = 'EC'
    TERMINE = 'TE'

    STATUS_CHOICES = [
        (A_FAIRE, 'À faire'),
        (EN_COURS, 'En cours'),
        (TERMINE, 'Terminé'),
    ]

    title = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    tag = models.CharField(max_length=2, choices=TAG_CHOICES)
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES)
    project_id = models.ForeignKey('api.Project', on_delete=models.CASCADE, related_name='issues')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_issues')
    assignee_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, default=author_user_id, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'project_id')


class Comment(models.Model):
    """
    Comments are bound to an issue.
    """
    description = models.CharField(max_length=300)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    issue_id = models.ForeignKey('api.Issue', on_delete=models.CASCADE, related_name='comments')
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('description', 'issue_id')
