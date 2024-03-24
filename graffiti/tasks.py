from datetime import timedelta

from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from huey import crontab
from huey.contrib.djhuey import periodic_task

from graffiti.models import GraffitiImage, image_expires_after_x_minutes, headset_expires_after_x_minutes, Headset

check_every_x_mins = 1


@periodic_task(crontab(minute=f'*/{check_every_x_mins}'))
def every_five_mins():
    # doing this so can more easily test below function
    _every_five_mins()


def _every_five_mins(current_time=now()):
    older_than_x = current_time + timedelta(minutes=image_expires_after_x_minutes)
    images_expired = GraffitiImage.objects.filter(created__gte=older_than_x)
    images_expired.delete()

    older_than_x = current_time + timedelta(minutes=headset_expires_after_x_minutes)
    headsets_expired = Headset.objects.filter(created__gte=older_than_x)
    headsets_expired.delete()
