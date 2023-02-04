from urllib import parse

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
import uuid


class AbstractGroupUserThru(TimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class GroupUserThru(AbstractGroupUserThru):
    enabled = models.BooleanField(default=True)


class GroupAdminThru(AbstractGroupUserThru):
    pass


def generate_message(group):
    message = f"""
    
    ******POWERED BY www.PubPubs.Pub******
    ***Visit www.pubpubs.pub/group/{group.uuid}/ to join this group if you were forwarded this message***
    ***You can delete your link to this group there too, or set up a SNOOZE period***
    """
    return message #'%0D'.join(message.splitlines())


class Group(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64)
    description = models.TextField()
    members = models.ManyToManyField('users.User', related_name='members', through=GroupUserThru)
    admins = models.ManyToManyField('users.User', related_name='admins', through=GroupAdminThru)

    members_can_email_all = models.BooleanField(default=False)

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

        mailto_txt = "mailto:?subject=" + encode(subject) + \
                     "&body=" + encode(message) + \
                     f"&{field_txt}={','.join(email_list)}"

        if self.field is not Group.FieldChoices.TO:
            mailto_txt += f"&to={','.join(admin_list)}"

        return mailto_txt


def encode(str):
    return parse.quote(str, safe='~()*!\'')
