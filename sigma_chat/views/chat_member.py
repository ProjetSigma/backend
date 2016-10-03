from django.http import Http404
from django.db.models import Prefetch, Q

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import BaseFilterBackend
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_chat.models.chat_member import ChatMember
from sigma_chat.serializers.chat_member import ChatMemberSerializer
from sigma_chat.models.chat import Chat
from sigma_chat.models.message import Message
from sigma_chat.serializers.message import MessageSerializer


class ChatMemberFilterBackend(BaseFilterBackend):
    filter_q = {
        'user': lambda u: Q(user=u),
        'chat': lambda c: Q(chat=c)
    }

    def filter_queryset(self, request, queryset, view):
        """
        Limits all list requests w.r.t the Normal Rules of Visibility.
        """
        user_chat_ids = request.user.user_chatmember.filter(is_member=True).values_list('chat_id', flat=True)
        # I can see a ChatMember if and only I am member of the chat
        queryset = queryset.prefetch_related(
            Prefetch('user', queryset=ChatMember.objects.filter(is_member=True))
        ).filter(Q(user_id=request.user.id) | Q(chat_id__in=user_chat_ids)
        )

        for (param, q) in self.filter_q.items():
            x = request.query_params.get(param, None)
            if x is not None:
                queryset = queryset.filter(q(x))

        return queryset.distinct()


class ChatMemberViewSet(viewsets.ModelViewSet):
    queryset = ChatMember.objects.select_related('chat', 'user')
    serializer_class = ChatMemberSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_backends = (ChatMemberFilterBackend, )

    def list(self, request):
        """
        ---
        parameters_strategy:
            query: replace
        parameters:
            - name: user
              type: integer
              paramType: query
            - name: chat
              type: integer
              paramType: query
        """
        return super().list(request)

    @decorators.detail_route(methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message for the ChatMember pk.
        ---
        omit_serializer: true
        parameters_strategy:
            form: replace
        parameters:
            - name: text
              type: integer
              required: true
        """
        try:
            chatmember = ChatMember.objects.get(pk=pk)
            if not chatmember.is_member :
                return Response(status=status.HTTP_403_FORBIDDEN)

            request.data['chat_id'] = chatmember.chat.id
            request.data['chatmember_id'] = chatmember.id
            message = MessageSerializer(data=request.data)
            if message.is_valid():
                message.save()
                return Response(message.data, status=status.HTTP_201_CREATED)
            else:
                return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)

        except ChatMember.DoesNotExist:
            raise Http404("ChatMember %d not found" % request.data.get('chatmember_id', None))
        return False
