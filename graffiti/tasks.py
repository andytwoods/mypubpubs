from datetime import timedelta

from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from huey import crontab
from huey.contrib.djhuey import periodic_task

from graffiti.models import GraffitiImage, expires_after_x_minutes


@periodic_task(crontab(minute=f'*/{expires_after_x_minutes}'))
def every_five_mins():
    # doing this so can more easily test below function
    _every_five_mins()


def _every_five_mins(current_time=now()):
    older_than_five = current_time + timedelta(minutes=expires_after_x_minutes)
    expired = GraffitiImage.objects.filter(created__gte=older_than_five)
    expired.delete()
