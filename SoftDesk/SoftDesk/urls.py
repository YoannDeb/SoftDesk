"""SoftDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import ProjectViewSet, IssueViewSet, ContributorViewSet, CommentViewSet, SignUpAPIView, RGPDViewSet


"""
Use of rest_framework_nested for nested routers.
"""
router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('rgpd', RGPDViewSet, basename='rgpd')

project_router = routers.NestedSimpleRouter(router, 'projects', lookup='project')
project_router.register('issues', IssueViewSet, basename='issues')
project_router.register('users', ContributorViewSet, basename='users')

issue_router = routers.NestedSimpleRouter(project_router, 'issues', lookup='issue')
issue_router.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignUpAPIView.as_view()),
    path('rgpd/', RGPDViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('', include(router.urls)),
    path('', include(project_router.urls)),
    path('', include(issue_router.urls))
]
