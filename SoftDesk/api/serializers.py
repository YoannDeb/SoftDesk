from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import Project, Issue, Comment, Contributor, CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'email', 'password']
        # extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return make_password(value)

    # def create(self, validated_data):
    #     user = CustomUser.objects.create_user(
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name'],
    #         email=validated_data['email'],
    #         password=validated_data['password'],
    #     )
    #     return user


class ContributorSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(read_only=True, source='project.title')

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'project_id', 'project_title', 'permission', 'role']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user_id', 'issue_id', 'created_time']


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'tag', 'priority', 'project_id',
            'status', 'author_user_id', 'assignee_user_id', 'created_time'
        ]


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id', 'contributors']

    def create(self, validated_data):
        with transaction.atomic():
            project_instance = super().create(validated_data)
            contributor = Contributor.objects.create(
                permission=Contributor.AUTHOR, project_id=project_instance, user_id=self.context['request'].user
            )
            contributor.save()
            return project_instance
