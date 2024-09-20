import random
import string
from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django_extensions.db.models import TimeStampedModel
from django.conf import settings

from django.core.exceptions import ValidationError

mb_limit = 8
limit = mb_limit * 1024 * 1024


# https://stackoverflow.com/a/35321718/960471
def file_size(value):
    if value.size > limit:
        raise ValidationError(f'File too large. Size should not exceed {limit}MB.')


code_length = 6


def randcode():
    # I HATE mixing up 0o and i1
    code_alphabet = list('23456789abcdefghjkmnpqrstuvwxyz')
    code_str = ''.join(random.sample(code_alphabet, code_length))
    return code_str


class Headset(TimeStampedModel):
    vr_id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    temp_code = models.CharField(max_length=10, unique=True)

    @classmethod
    def get_or_generate_code(cls, vr_id: str):
        headset, created = Headset.objects.get_or_create(vr_id=vr_id)
        if created:
            headset.save()
        return headset

    def save(self, **kwargs):
        if self._state.adding:
            while True:
                temp_code = randcode()
                if not Headset.objects.filter(temp_code=temp_code).exists():
                    self.temp_code = temp_code
                    break
        super().save(**kwargs)

    @classmethod
    def check_short_code(cls, temp_code):
        return len(temp_code) == code_length


image_expires_after_x_minutes = 10
headset_expires_after_x_minutes = 5


class GraffitiImage(TimeStampedModel):
    url = models.URLField(null=True, blank=True)
    image = models.ImageField(validators=[file_size], null=True, blank=True)
    headset = models.ForeignKey(Headset, on_delete=models.CASCADE)

    # https://stackoverflow.com/a/58542283/960471
    def delete(self, using=None, keep_parents=False):
        # assuming that you use same storage for all files in this model:

        if self.image:
            storage = self.image.storage
            if storage.exists(self.image.name):
                storage.delete(self.image.name)

        super().delete()

    @classmethod
    def check_valid(cls, image, current_datetime=now()):
        if image is None:
            raise NoImage()
        older_than_x = current_datetime + timedelta(minutes=image_expires_after_x_minutes)
        if image.created >= older_than_x:
            image.delete()
            raise NoImage()
        return image

    @classmethod
    def retrieve_and_check_valid(cls, headset: Headset):
        print(cls.objects.filter(headset=headset),22)
        image = cls.objects.filter(headset=headset).first()
        return GraffitiImage.check_valid(image)


class NoImage(BaseException):
    pass
