import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from group.exceptions import InvitedBannedUser
from group.helpers.email_link import generate_message, compose_email_link, encode
from group.model_choices import StatusChoices

User = get_user_model()

from group.helpers.email import let_new_user_know_added
from group.helpers.list_tools import make_list


class AbstractGroupUserThru(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class GroupUserThru(AbstractGroupUserThru):
    status = models.CharField(
        max_length=2,
        choices=StatusChoices.choices,
        default=StatusChoices.WAITING_FOR_OK,
    )

    @classmethod
    def accept_invitation(cls, user: User, group_uuid):
        found = GroupUserThru.objects.get(user=user, group__uuid=group_uuid)
        found.status = StatusChoices.ACTIVE
        found.save()

    @classmethod
    def check_new_people_needing_permission(cls, group_uuid):
        found = GroupUserThru.objects.filter(group__uuid=group_uuid, status=StatusChoices.WAITING_FOR_OK)
        return found.count()

    @classmethod
    def cancel_join_request(cls, user: User, group_uuid):
        cls.objects.get(group__uuid=group_uuid, user=user).delete()

    @classmethod
    def decline_invitation(cls, user, group_uuid):
        cls.objects.get(group__uuid=group_uuid, user=user).delete()

    @classmethod
    def retrieve_groups_given_status(cls, user: User, status: StatusChoices):
        return GroupUserThru. \
            objects. \
            filter(user=user, status=status). \
            select_related('group')


class GroupAdminThru(AbstractGroupUserThru):
    @classmethod
    def admin_of_which_groups(cls, user: User):
        return GroupAdminThru. \
            objects. \
            filter(user=user). \
            select_related('group'). \
            prefetch_related('user')


class DomainNames(models.Model):
    domain = models.TextField(max_length=64, blank=False, null=False)

    def __str__(self):
        return self.domain


class Group(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64)
    description = models.TextField()
    members = models.ManyToManyField('users.User', related_name='members', through=GroupUserThru)
    admins = models.ManyToManyField('users.User', related_name='admins', through=GroupAdminThru)

    members_can_email_all = models.BooleanField(default=False)

    safe_domains = models.ManyToManyField(DomainNames, blank=True)

    class FieldChoices(models.TextChoices):
        BCC = 'BC', _('BCC')
        CC = 'CC', _('CC')
        TO = 'TO', _('TO')

    field = models.CharField(
        max_length=2,
        choices=FieldChoices.choices,
        default=FieldChoices.BCC,
    )

    def admins_emails(self):
        return [member.email for member in self.admins.all()]

    def members_emails(self):
        return [admin.email for admin in self.members.all()]

    def make_admin_email(self, subject='trip to pub', message=''):
        admin_list = self.admins_emails()
        return "mailto:?subject=" + encode(subject) + \
            "&body=" + encode(message) + \
            "&to=" + ','.join(admin_list)

    def make_email(self, subject='trip to pub', message=None):

        email_list = self.members_emails()
        admin_list = self.admins_emails()

        if message is None:
            message = generate_message(self)

        field_txt = ''
        match self.field:
            case Group.FieldChoices.BCC:
                field_txt = 'bcc'
            case Group.FieldChoices.CC:
                field_txt = 'cc'
            case Group.FieldChoices.TO:
                field_txt = 'to'

        if self.field is Group.FieldChoices.TO:
            email_list = admin_list + email_list
            admin_list.clear()

        mailto_txt = compose_email_link(subject, message, field_txt, email_list)

        if self.field is not Group.FieldChoices.TO:
            mailto_txt += f"&to={','.join(admin_list)}"

        return mailto_txt

    def authorise_users(self, user_ids):
        for user_id in user_ids:
            gu: GroupUserThru = GroupUserThru.objects.get(group=self, user__id=user_id)
            gu.status = StatusChoices.ACTIVE
            gu.save()

    def add_safe_domains(self, new_safe_domains_str):
        new_safe_domains = make_list(new_safe_domains_str)
        if not new_safe_domains:
            return
        already_exists = list(self.safe_domains.all())
        for new_safe_domain in new_safe_domains:
            if new_safe_domain not in already_exists:
                dm = DomainNames(domain=new_safe_domain)
                dm.save()
                self.safe_domains.add(dm)

    def ban_users(self, banned_emails_str):
        banned_emails = make_list(banned_emails_str)
        for email in banned_emails:
            gu: GroupUserThru
            gu, created = GroupUserThru.objects.get_or_create(group=self, user__email=email)
            gu.status = StatusChoices.BANNED
            gu.save()
        pass

    def remove_users_not_in_this_list(self, user_ids):
        to_remove = GroupUserThru.objects.filter(group=self).exclude(user__in=user_ids).select_related('user')
        found = [groupuser.user.email for groupuser in to_remove]
        to_remove.delete()
        return found

    def add_people(self, invite_emails_str):
        for email in make_list(invite_emails_str):
            self.add_user(email, StatusChoices.ACTIVE)

    def add_user(self, email, status: StatusChoices):
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.save()
        group_user, joined_group = GroupUserThru.objects.get_or_create(user=user, group=self)
        if created:
            group_user.status = status
            group_user.save()
            let_new_user_know_added(self, email, status)
        else:
            if group_user.status is StatusChoices.BANNED:
                raise InvitedBannedUser(email)
            elif group_user.status is StatusChoices.ACTIVE:
                return

        return group_user, joined_group

    def check_is_admin(self, user: User):
        exists = GroupAdminThru.objects.filter(user=user, group=self).exists()
        return exists

    def check_is_active_user(self, user: User):
        exists = GroupUserThru.objects.filter(user=user, group=self, status=StatusChoices.ACTIVE).exists()
        return exists

    def linked_with_group(self, user: User):
        return GroupUserThru.objects.filter(group=self, user=user).exists() or \
            GroupAdminThru.objects.filter(group=self, user=user).exists()

