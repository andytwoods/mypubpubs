from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from group.models import Group, GroupUserThru
from users.factories import UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates users'

    def handle(self, *args, **options):
        user = UserFactory()
        user.save()
        group = Group.objects.first()
        if not group:
            try:
                andy:User = User.objects.get(email='andytwoods@gmail.com')
            except User.DoesNotExist:
                andy = UserFactory(email='andytwoods@gmail.com')
                andy.is_superuser = True
                andy.is_staff = True
                andy.save()

            group = Group()
            group.save()
            group.admins.add(andy)
        user = GroupUserThru(group=group, user=user)
        user.save()
        self.stdout.write(self.style.SUCCESS('Successfully created some users'))
