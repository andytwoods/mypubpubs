from django.db import models
from mailauth.contrib.user.models import AbstractEmailUser


class User(AbstractEmailUser):
    pass
