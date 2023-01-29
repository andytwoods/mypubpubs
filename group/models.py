from django.db import models
from django_extensions.db.models import TimeStampedModel
import uuid


class Group(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=64)
    description = models.TextField()
    members = models.ManyToManyField('users.User', related_name='members')
    admins = models.ManyToManyField('users.User', related_name='admins')
