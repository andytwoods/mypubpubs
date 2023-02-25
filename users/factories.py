from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    first_name = Faker("name")
    last_name = Faker("name")
    email = Faker("email")

    class Meta:
        model = get_user_model()
