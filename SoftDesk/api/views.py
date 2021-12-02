from django.conf import settings
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, CommentSerializer, IssueSerializer

# class SignUpAPIView(views.APIView):
#     permission_classes = (AllowAny,)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(contributors=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])



