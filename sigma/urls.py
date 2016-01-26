"""sigma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from sigma_core.views.user import UserViewSet
from sigma_core.views.group import GroupViewSet
from sigma_core.views.school import SchoolViewSet
from sigma_core.views.group_user import GroupUserViewSet
from sigma_core.views.group_member import GroupMemberViewSet

router = routers.DefaultRouter()

router.register(r'user', UserViewSet)
router.register(r'group', GroupViewSet)
router.register(r'school', SchoolViewSet)
router.register(r'group-member', GroupMemberViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^', include(router.urls)),
]
