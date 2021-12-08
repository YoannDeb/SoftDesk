from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, permissions, status, generics

from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import ProjectSerializer, CommentSerializer, IssueSerializer, UserSerializer, ContributorSerializer, CreateContributorSerializer
from .permissions import IsProjectContributor, IsProjectAuthor, IsCurrentUser, IsIssueAuthor


class SignUpAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class SignupApiView(generics.CreateAPIView):
#     model = User
#     permission_classes = [permissions.AllowAny]
#     serializer_class = UserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(contributors=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsProjectContributor]
        elif self.action == 'delete' or self.action == 'update':
            permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsIssueAuthor]
        return permission_classes

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classe = [IsProjectContributor]

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsProjectContributor]

    def get_queryset(self):
        return Contributor.objects.filter(project_id=self.kwargs['project_pk'])

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateContributorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(project_id=Project.objects.get(pk=int(self.kwargs['project_pk'])), permission='CO',)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response({"Message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response({"Message": "Multiple objects returned"}, status=status.HTTP_404_NOT_FOUND)


class RGPDViewSet(viewsets.ViewSet):
    permission_classes = [IsCurrentUser]

    def retrieve(self, request, pk=None):
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request):
        pass

    def destroy(self, request):
        request.user.delete()
