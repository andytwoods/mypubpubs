from typing import Sequence, Any

from django.contrib.auth import get_user_model
from factory import post_generation, Faker
from factory.django import DjangoModelFactory
from faker import factory
from factory.faker import faker

fake = faker.Faker()

class UserFactory(DjangoModelFactory):

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    username = fake.user_name()

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
