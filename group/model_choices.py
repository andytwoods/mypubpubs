from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.TextChoices):
    WAITING_FOR_OK = 'WA', _('Waiting for admins to OK')
    ACTIVE = 'AC', _('Active member')
    BANNED = 'BA', _('Banned')
    INVITED = 'IN', _('Invited to join by Admin')
    DECLINED = 'DE', _('User declines membership')
