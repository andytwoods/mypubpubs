import random
import string

from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.conf import settings

from django.core.exceptions import ValidationError


# https://stackoverflow.com/a/35321718/960471
def file_size(value):
    limit = 8 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(f'File too large. Size should not exceed {limit}MB.')


def randcode():
    return random.sample(string.digits + string.ascii_lowercase, 5)


class Headset(TimeStampedModel):
    vr_id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    temp_code = models.CharField(max_length=10, default=randcode)


class GraffitiImage(TimeStampedModel):
    image = models.ImageField(validators=[file_size])
    headset = models.ForeignKey(Headset, on_delete=models.CASCADE)

    # https://stackoverflow.com/a/58542283/960471
    def delete(self, using=None, keep_parents=False):
        # assuming that you use same storage for all files in this model:
        storage = self.image.storage

        if storage.exists(self.image.name):
            storage.delete(self.image.name)

        super().delete()

    @classmethod
    def get_or_generate_code(cls, vr_id: str):
        headset, created = Headset.objects.get_or_create(vr_id=vr_id)
        return headset.temp_code
