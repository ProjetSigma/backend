from django.http import Http404
from django.db.models import Q

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissionFiltersBase

from sigma_core.models.user import User
from sigma_chat.models.chat import Chat
from sigma_chat.models.chat_member import ChatMember
from sigma_chat.serializers.chat import ChatSerializer
from sigma_chat.models.message import Message
from sigma_chat.serializers.message import MessageSerializer


class MessageFilterBackend(DRYPermissionFiltersBase):
    filter_q = {
        'chat': lambda c: Q(chat_id=c)
    }

    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        user_chat_ids = request.user.user_chatmember.filter(is_member=True).values_list('chat_id', flat=True)
        queryset = queryset.prefetch_related('chat_id', 'chatmember_id') \
            .filter(chat_id__in=user_chat_ids)

        for (param, q) in self.filter_q.items():
            x = request.query_params.get(param, None)
            if x is not None:
                queryset = queryset.filter(q(x))

        return queryset.distinct()


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = (MessageFilterBackend, )
