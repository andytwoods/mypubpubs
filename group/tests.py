from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from group.factories import GroupUserThruFactory, GroupFactory, GroupAdminThruFactory
from group.helpers.email import tell_admin_signup
from group.model_choices import StatusChoices
from group.models import GroupUserThru, GroupAdminThru, Group
from group.views import home_context_info
from users.factories import UserFactory

User = get_user_model()


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

    def test_admin_of(self):
        user = UserFactory()
        group = GroupFactory()

        found = GroupAdminThru.admin_of_which_groups(user=user)
        self.assertEqual(found.count(), 0)

        GroupAdminThruFactory(user=user, group=group)

        self.assertEqual(found.count(), 1)

    def test_check_is_admin(self):
        user = UserFactory()
        group:Group = GroupFactory()
        self.assertFalse(group.check_is_admin(user))

        GroupAdminThru(user=user, group=group).save()

        self.assertTrue(group.check_is_admin(user))

    def test_check_is_active_user(self):
        user = UserFactory()
        group: Group = GroupFactory()
        self.assertFalse(group.check_is_active_user(user))

        gu:GroupUserThru = GroupUserThru(user=user, group=group)

        self.assertFalse(group.check_is_active_user(user))

        gu.status = StatusChoices.ACTIVE
        gu.save()
        self.assertTrue(group.check_is_active_user(user))



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


class TestModels(TestCase):

    def test_remove_users(self):
        group: Group = GroupFactory()

        safe_user = UserFactory()
        bad_user1 = UserFactory()
        bad_user2 = UserFactory()

        for user in [safe_user, bad_user1, bad_user2]:
            u = GroupUserThruFactory(group=group, user=user)
            u.save()

        self.assertEqual(GroupUserThru.objects.filter(group=group).count(), 3)

        removed = group.remove_users_not_in_this_list([safe_user.id, ])
        self.assertEqual(len(removed), 2)
        self.assertCountEqual(removed, [bad_user1.email, bad_user2.email, ])


class TestGroupUserThru(TestCase):

    def test_accept_invitation(self):
        group: Group = GroupFactory()
        user: User = UserFactory()
        gu: GroupUserThru = GroupUserThruFactory(group=group, user=user)

        self.assertEqual(gu.status, GroupUserThru._meta.get_field('status').get_default())

        gu.accept_invitation(user, group.uuid)
        gu.refresh_from_db()

        self.assertEqual(gu.status, StatusChoices.ACTIVE)

    def test_check_new_people_needing_permission(self):
        group: Group = GroupFactory()

        self.assertEqual(GroupUserThru.check_new_people_needing_permission(group.uuid), 0)

        for _ in range(3):
            GroupUserThruFactory(group=group, user=UserFactory(), status=StatusChoices.WAITING_FOR_OK)

        self.assertEqual(GroupUserThru.check_new_people_needing_permission(group.uuid), 3)

    def test_cancel_join_request(self):
        group: Group = GroupFactory()
        user: User = UserFactory()
        GroupUserThruFactory(user=user, group=group)

        GroupUserThru.cancel_join_request(group_uuid=group.uuid, user=user)
        self.assertFalse(GroupUserThru.objects.filter(group=group, user=user).exists())

    def test_decline_invitation(self):
        group: Group = GroupFactory()
        user: User = UserFactory()
        GroupUserThruFactory(user=user, group=group)

        GroupUserThru.decline_invitation(group_uuid=group.uuid, user=user)
        self.assertFalse(GroupUserThru.objects.filter(group=group, user=user).exists())

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


class TestGroupAdminThru(TestCase):
    def test_add_admin(self):
        group: Group = GroupFactory()
        user = UserFactory()

        self.assertFalse(group.check_is_admin(user))

        group.add_admin(user.email)
        self.assertTrue(group.check_is_admin(user))


class TestIntegration(TestCase):

    def test_user_invited(self):
        group: Group = GroupFactory()

        invited_email = 'invited@example.com'

        group.add_people(invited_email)

        # check sends invite email
        self.assertEqual(len(mail.outbox), 1)
        print(mail.outbox[0].message())

        # check creates the user
        users = User.objects.filter(email=invited_email)
        self.assertTrue(users.exists())

        # check GroupUserThru is ACTIVE status
        # Note, changed this from INVITED status, for simplification
        gu: GroupUserThru = GroupUserThru.objects.get(user__email=invited_email)
        self.assertEqual(gu.status, StatusChoices.ACTIVE)

class TestEmails(TestCase):
    def test_tell_admin_signup(self):
        group: Group = GroupFactory()
        admin = UserFactory()
        GroupAdminThru(group=group, user=admin).save()

        email = 'test@test.com'
        self.assertEqual(len(mail.outbox), 0)

        self.signup = tell_admin_signup(email=email, group=group)
        self.assertEqual(len(mail.outbox), 1)



