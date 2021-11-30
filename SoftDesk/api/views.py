from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Project, Contributor, Issue, Comment
# from .serializers import ProjectListSerializer, ProjectDetailSerializer
from .serializers import ProjectSerializer, CommentSerializer, IssueSerializer


# class ProjectViewSet(ModelViewSet):
#     serializer_class = ProjectListSerializer
#     detail_serializer_class = ProjectDetailSerializer
#     queryset = Project.objects.all()  #TODO to change in something like Project.objects.filter(contributors.user_id=settings.AUTH_USER_MODEL) when auth is done
#
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return self.detail_serializer_class
#         return super().get_serializer_class()

class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()  #TODO to change in something like Project.objects.filter(contributors.user_id=settings.AUTH_USER_MODEL) when auth is done


class IssueViewSet(ModelViewSet):
    serializer_class = IssueSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])



