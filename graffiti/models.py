from django.db import models
from django_extensions.db.models import TimeStampedModel
# Create your models here.


from django.core.exceptions import ValidationError

# https://stackoverflow.com/a/35321718/960471
def file_size(value):
    limit = 8 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(f'File too large. Size should not exceed {limit}MB.')

class GraffitiImage(TimeStampedModel):
    image = models.ImageField(validators=[file_size])
    vr_id = models.CharField(max_length=20, primary_key=True)

    # https://stackoverflow.com/a/58542283/960471
    def delete(self, using=None, keep_parents=False):
        # assuming that you use same storage for all files in this model:
        storage = self.image.storage

        if storage.exists(self.image.name):
            storage.delete(self.image.name)

        super().delete()