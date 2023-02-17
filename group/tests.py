from django.test import TestCase
from django.urls import reverse

from group.factories import GroupUserThruFactory, GroupFactory, GroupAdminThruFactory
from group.model_choices import StatusChoices
from group.models import GroupUserThru, GroupAdminThru
from group.views import home_context_info
from users.factories import UserFactory


class TestHome(TestCase):

    def test_logged_in(self):
        response = self.client.get(reverse('home'))
        home_context_vars = [x[0] for x in home_context_info]
        for key in home_context_vars:
            self.assertTrue(key not in response.context)

        user = UserFactory()
        user.save()
        self.client.force_login(user)
        response = self.client.get(reverse('home'))
        for key in home_context_vars:
            self.assertTrue(key in response.context)

    def test_group_via_status(self):
        user = UserFactory()
        group = GroupFactory()

        found = GroupUserThru.retrieve_groups_given_status(user=user, status=StatusChoices.ACTIVE)
        self.assertEqual(found.count(), 0)

        gu: GroupUserThru = GroupUserThruFactory(user=user, group=group, status=StatusChoices.ACTIVE)

        self.assertEqual(found.count(), 1)

        gu.status = StatusChoices.INVITED
        gu.save()
        self.assertEqual(found.count(), 0)

    def test_admin_of(self):
        user = UserFactory()
        group = GroupFactory()

        found = GroupAdminThru.admin_of_which_groups(user=user)
        self.assertEqual(found.count(), 0)

        GroupAdminThruFactory(user=user, group=group)

        self.assertEqual(found.count(), 1)

    def test_admin_edit_group(self):
        response = self.client.get(reverse('admin-group-edit', kwargs={'uuid': '79adfebf-4305-4cea-a016-f0b58a2228b7'}))
        self.assertRedirects(response, reverse('home'))

        group = GroupFactory()
        response = self.client.get(reverse('admin-group-edit', kwargs={'uuid': group.uuid}))
        self.assertRedirects(response, reverse('home'))

        user = UserFactory()
        group.admins.add(user)
        self.client.force_login(user)
        response = self.client.get(reverse('admin-group-edit', kwargs={'uuid': group.uuid}))
        self.assertEqual(response.status_code, 200)
