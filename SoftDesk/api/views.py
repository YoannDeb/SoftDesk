from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import viewsets, views, permissions, status, decorators

from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import ProjectSerializer, CommentSerializer, IssueSerializer, UserSerializer, ContributorSerializer, CreateContributorSerializer, CreateIssueSerializer, CreateCommentSerializer
from .permissions import IsProjectContributor, IsProjectAuthor, IsCurrentUser, IsIssueAuthor, IsCommentAuthor


class SignUpAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user = request.data
            serializer = UserSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response({"Message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "There was an integrity error."}, status=status.HTTP_400_BAD_REQUEST)


# @decorators.permission_classes([permissions.IsAuthenticated()])
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        if self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor()]
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes = [permissions.IsAuthenticated(), IsProjectAuthor()]
        return permission_classes

    def get_queryset(self):
        return Project.objects.filter(contributors=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'create':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor()]
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor(), IsIssueAuthor()]
        return permission_classes

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project_pk'])

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateIssueSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(project_id=Project.objects.get(pk=int(self.kwargs['project_pk'])), author_user_id=request.user,)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response({"Message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response({"Message": "Multiple objects returned"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response({"Message": "An issue with this title already exists for this project."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "There was an integrity error."}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated()]

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'create':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor()]
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor(), IsCommentAuthor()]
        return permission_classes

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(issue_id=Issue.objects.get(pk=int(self.kwargs['issue_pk'])), author_user_id=request.user,)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response({"Message": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response({"Message": "Multiple objects returned"}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response({"Message": "A comment with this description already exists for this issue."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "There was an integrity error."}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated()]
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated(), IsProjectContributor()]
        elif self.action == 'create' or self.action == 'destroy' or self.action == 'update':
            permission_classes = [permissions.IsAuthenticated(), IsProjectAuthor()]
        return permission_classes

    def get_queryset(self):
        return Contributor.objects.filter(project_id=int(self.kwargs['project_pk']))

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
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response({"Message": "This user is already contributor or author of the project."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "There was an integrity error."}, status=status.HTTP_400_BAD_REQUEST)


class RGPDViewSet(viewsets.ViewSet):
    permission_classes = [IsCurrentUser]

    def retrieve(self, request, pk=None):
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            queryset = CustomUser.objects.all()
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response({"Message": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Message": "There was an integrity error."}, status=status.HTTP_400_BAD_REQUEST)

    # def partial_update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)

    def destroy(self, request, pk=None):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

