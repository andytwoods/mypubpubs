import factory
from factory.django import DjangoModelFactory

from group.models import Group, GroupUserThru, GroupAdminThru
from users.factories import UserFactory


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group

    title = factory.Faker("text")
    description = factory.Faker("text")


class AbstractGroupUserThruFactory:
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)


class GroupUserThruFactory(DjangoModelFactory, AbstractGroupUserThruFactory):
    class Meta:
        model = GroupUserThru


class GroupAdminThruFactory(GroupUserThruFactory, AbstractGroupUserThruFactory):
    class Meta:
        model = GroupAdminThru
