from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from rest_framework import viewsets, views, permissions, status
from rest_framework.response import Response

from .models import Project, Contributor, Issue, Comment, CustomUser
from .serializers import ProjectSerializer, CommentSerializer, IssueSerializer, UserSerializer, ContributorSerializer,\
    CreateContributorSerializer, CreateIssueSerializer, CreateCommentSerializer
from .permissions import IsProjectContributor, IsProjectAuthor, IsCurrentUser, IsIssueAuthor, IsCommentAuthor


class SignUpAPIView(views.APIView):
    """
    Using APIView inheritance as we only need post in this endpoint.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user = request.data
            serializer = UserSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = serializer.data.copy()
            data.pop('password')
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "A user with this email already exists.", status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)


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
        """
        Overload of update method authorizing partial update with put HTTP method.
        """
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
        """
        Overload of create method.
        - Automatically add the project pk from url as the project_id of the issue,
        and the current user's pk as author_user_id.
        - Error catching if an issue with the same title already exists for the current project,
        delivering proper API response.
        """
        try:
            serializer = CreateIssueSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                project_id=Project.objects.get(pk=int(self.kwargs['project_pk'])), author_user_id=request.user
            )
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response("Project does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "An issue with this title already exists for this project.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Overload of update method.
        - Authorize partial update with put HTTP method.
        - Error catching if an issue with the same title already exists for the current project,
        delivering proper API response.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response("Project does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response("An issue with this title already exists for this project.",
                                status=status.HTTP_400_BAD_REQUEST)
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)


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
        """
        Overload of create method.
        - Automatically add the issue pk from url as the issue_id of the comment,
        and the current user's pk as author_user_id.
        - Error catching if a comment with the same title already exists for the current issue,
        delivering proper API response.
        """
        try:
            serializer = CreateCommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(issue_id=Issue.objects.get(pk=int(self.kwargs['issue_pk'])), author_user_id=request.user,)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response("Project does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except Issue.DoesNotExist:
            return Response("Issue does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "A comment with this description already exists for this issue.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Overload of update method.
        - Authorize partial update with put HTTP method.
        - Error catching if a comment with the same title already exists for the current issue,
        delivering proper API response.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response("Project does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except Issue.DoesNotExist:
            return Response("Issue does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "A comment with this description already exists for this issue.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)


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
        """
        Overload of create method.
        - Automatically add the project pk from url as the project_id of the comment,
        and the permission to 'CO' (contributor only as the author is the only user allowed to add other contributors,
        and there can be only one author to a project).
        - Error catching if a comment with the same title already exists for the current issue,
        delivering proper API response.
        """
        try:
            serializer = CreateContributorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(project_id=Project.objects.get(pk=int(self.kwargs['project_pk'])), permission='CO',)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Project.DoesNotExist:
            return Response("Project does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Project.MultipleObjectsReturned:
            return Response("Multiple objects returned.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "This user is already contributor or author of the project.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)


class RGPDViewSet(viewsets.ViewSet):
    """
    RGPD Viewset, allowing consultation and modification of the user according to RGPD laws.
    Viewset is used as we don't need all endpoints given by ModelViewSet.
    """
    permission_classes = [IsCurrentUser]

    def retrieve(self, request, pk=None):
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Error catching if another user with the same email already exists in database,
        delivering proper API response.
        Partial update is allowed.
        """
        try:
            queryset = CustomUser.objects.all()
            user = get_object_or_404(queryset, pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            if 'UNIQUE constraint' in e.args[0]:
                return Response(
                    "A user with this email already exists.", status=status.HTTP_400_BAD_REQUEST
                )
            return Response("There was an integrity error.", status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        - Deletes user and all projects of which user is the author
        (got to be handled manually cause there is no direct foreign_keys between users and projects).
        - Contributors, issues and comments objects of which user is the author are automatically deleted
        because on_delete=cascade in respective models' foreign keys.
        """
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        projects_of_which_user_is_contributor = user.project_set.all()
        with transaction.atomic():
            for project in projects_of_which_user_is_contributor:
                if project.author_user_id == int(pk):
                    project.delete()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
