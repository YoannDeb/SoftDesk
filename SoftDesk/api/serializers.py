from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import Project, Issue, Comment, Contributor, CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password']

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.
        Apparently necessary with custom user.
        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

    def validate_email(self, value: str) -> str:
        """
        Overload of validate_email method, converting email and
        checking existence of the email in the database EXCEPT for current user.
        Necessary cause by default for an update, if the mail was the same, the user wasn't updated.
        """
        email = value.lower()
        if self.instance and CustomUser.objects.exclude(pk=self.instance.pk).filter(email=value):
            raise serializers.ValidationError('A user with this email already exists.')
        return email

    def validate_first_name(self, value: str) -> str:
        """
        Overload of validate_first_name method, capitalizing first name.
        """
        return value.capitalize()

    def validate_last_name(self, value: str) -> str:
        """
        Overload of validate_last_name method, capitalizing last name.
        """
        return value.capitalize()


class ContributorSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(read_only=True, source='project.title')

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'project_id', 'project_title', 'permission', 'role']


class CreateContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'role']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user_id', 'issue_id', 'created_time']


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description']


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'tag', 'priority', 'project_id',
            'status', 'author_user_id', 'assignee_user_id', 'created_time'
        ]


class CreateIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'tag', 'priority',
            'status', 'assignee_user_id'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id', 'contributors']

    def create(self, validated_data):
        """
        Overloaded Create method to automatically create contributor with user creating the project as author.
        """
        with transaction.atomic():
            project_instance = super().create(validated_data)
            contributor = Contributor.objects.create(
                permission=Contributor.AUTHOR, project_id=project_instance, user_id=self.context['request'].user
            )
            contributor.save()
            return project_instance
