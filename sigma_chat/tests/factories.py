import factory
from faker import Factory as FakerFactory

from sigma_core.tests.factories import UserFactory

from sigma_chat.models.chat import Chat
from sigma_chat.models.chat_member import ChatMember
from sigma_chat.models.message import Message

faker = FakerFactory.create('fr_FR')

class ChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chat

    name = factory.LazyAttribute(lambda obj: faker.name())


class ChatMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMember

    is_creator = False
    is_admin = False
    user = factory.SubFactory(UserFactory)
    chat = factory.SubFactory(ChatFactory)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    text = factory.LazyAttribute(lambda obj: faker.text())
    chatmember_id = factory.SubFactory(ChatMemberFactory)
    chat_id = factory.SubFactory(ChatFactory)
    date = factory.LazyAttribute(lambda obj: faker.date())
    attachment = ""
