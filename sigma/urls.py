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
from django.conf import settings
from django.views import static

router = routers.DefaultRouter()

from sigma_core.views.user import UserViewSet
from sigma_core.views.group import GroupViewSet
from sigma_core.views.cluster import ClusterViewSet
from sigma_core.views.group_member import GroupMemberViewSet
from sigma_core.views.group_member_value import GroupMemberValueViewSet
from sigma_core.views.group_field import GroupFieldViewSet
from sigma_core.views.validator import ValidatorViewSet
from sigma_chat.views.chat_member import ChatMemberViewSet
from sigma_chat.views.chat import ChatViewSet
from sigma_chat.views.message import MessageViewSet

router.register(r'group', GroupViewSet)
router.register(r'group-field', GroupFieldViewSet)
router.register(r'group-member', GroupMemberViewSet)
router.register(r'group-member-value', GroupMemberValueViewSet)
router.register(r'cluster', ClusterViewSet)
router.register(r'user', UserViewSet)
router.register(r'validator', ValidatorViewSet)
router.register(r'chatmember', ChatMemberViewSet)
router.register(r'chat', ChatViewSet)
router.register(r'message', MessageViewSet)

from sigma_files.views import ImageViewSet

router.register(r'image', ImageViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$',
            static.serve,
            {'document_root': settings.MEDIA_ROOT, }),
    )
