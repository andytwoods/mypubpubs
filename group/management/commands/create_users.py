from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from group.models import Group
from users.factories import UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates users'

    def handle(self, *args, **options):
        user = UserFactory()
        user.save()
        group = Group.objects.first()
        group.members.add(user)
        print(user)
        self.stdout.write(self.style.SUCCESS('Successfully created some users'))
