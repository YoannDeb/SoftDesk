from rest_framework.serializers import ModelSerializer, SerializerMethodField, ValidationError, CharField, IntegerField

from models import Project, Issue, Comment, Contributor


class ContributorListSerializer(ModelSerializer):
    user_username = CharField(read_only=True, source='user.username')
    project_title = CharField(read_only=True, source='project.title')

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'user_username', 'project_id', 'project_title', 'permission', 'role']


class ContributorDetailSerializer(ModelSerializer):
    user_username = CharField(read_only=True, source='user.username')
    project_title = CharField(read_only=True, source='project.title')

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'user_username', 'project_id', 'project_title', 'permission', 'role']


class CommentListSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user_id', 'issue_id', 'created_time']


class CommentDetailSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user_id', 'issue_id', 'created_time']


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'created_time']


class IssueDetailSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'project_id', 'status', 'author_user_id', 'assignee_user_id', 'created_time']


class ProjectListSerializer(ModelSerializer):

    contributors = SerializerMethodField()
    author_user_id = SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id', 'contributors']

    def get_author_user_id(self, instance):
        return instance.contributors.get(permission=Contributor.AUTHOR)['user_id']

    # def get_contributors(self, instance):
    #     queryset = instance.contributors.all()
    #     serializer = ContributorSerializer(queryset, many=True)
    #     return serializer.data


class ProjectDetailSerializer(ModelSerializer):

    contributors = SerializerMethodField()
    author_user_id = SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id', 'contributors']

    def get_author_user_id(self, instance):
        return instance.contributors.get(permission=Contributor.AUTHOR)['user_id']


class ProjectUsersListSerializer(ModelSerializer):
    pass


class ProjectUsersDetailSerializer(ModelSerializer):
    pass


class ProjectIssuesListSerializer(ModelSerializer):
    pass


class ProjectIssuesDetailSerializer(ModelSerializer):
    pass


class ProjectIssueCommentsListSerializer(ModelSerializer):
    pass


class ProjectIssueCommentsDetailSerializer(ModelSerializer):
    pass
