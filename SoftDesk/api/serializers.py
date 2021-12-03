from rest_framework import serializers
from django.db import transaction

from .models import Project, Issue, Comment, Contributor, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class ContributorSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(read_only=True, source='user.username')
    project_title = serializers.CharField(read_only=True, source='project.title')

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'user_username', 'project_id', 'project_title', 'permission', 'role']


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
