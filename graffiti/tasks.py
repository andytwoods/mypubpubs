from datetime import timedelta

from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from huey import crontab
from huey.contrib.djhuey import periodic_task

from graffiti.models import GraffitiImage

expires_after_x_minutes = 5


@periodic_task(crontab(minute=f'*/{expires_after_x_minutes}'))
def every_five_mins():
    older_than_five = now() - timedelta(minutes=expires_after_x_minutes)
    expired = GraffitiImage.objects.filter(created__gte=older_than_five)
    expired.delete()
