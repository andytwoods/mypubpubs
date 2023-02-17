from django.test import TestCase

from group.factories import GroupUserThruFactory, GroupFactory
from group.model_choices import StatusChoices
from group.models import GroupUserThru
from users.factories import UserFactory


class TestHome(TestCase):

    def test_group_via_status(self):
        user = UserFactory()

        found = GroupUserThru.retrieve_groups_given_status(user=user, status=StatusChoices.ACTIVE)
        self.assertEqual(found.count(), 0)

        group = GroupFactory()
        gu: GroupUserThru = GroupUserThruFactory(user=user, group=group, status=StatusChoices.ACTIVE)

        self.assertEqual(found.count(), 1)

        gu.status = StatusChoices.INVITED
        gu.save()
        self.assertEqual(found.count(), 0)

