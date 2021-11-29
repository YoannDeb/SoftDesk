from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Comment, Issue

admin.site.register(User, UserAdmin)
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Issue)
