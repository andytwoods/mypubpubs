from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from factory.faker import faker

fake = faker.Faker()


class UserFactory(DjangoModelFactory):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()

    class Meta:
        model = get_user_model()
