from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from graffiti.models import GraffitiImage, Headset
from graffiti.tasks import every_five_mins, _every_five_mins


# Create your tests here.

class TasksTest(TestCase):
    def test_every_five_mins(self):
        headset = Headset(vr_id='my_id')
        headset.save()
        image = GraffitiImage(headset=headset)
        image.save()

        self.assertEquals(GraffitiImage.objects.count(), 1)
        _every_five_mins(now())
        self.assertEquals(GraffitiImage.objects.count(), 1)

        _every_five_mins(now() - timedelta(minutes=4, seconds=59))
        self.assertEquals(GraffitiImage.objects.count(), 1)

        _every_five_mins(now() - timedelta(minutes=5, seconds=1))
        self.assertEquals(GraffitiImage.objects.count(), 0)
