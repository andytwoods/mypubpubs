from group.helpers.email import let_new_user_know_added
from group.models import Group, GroupUserThru
from django.contrib.auth import get_user_model

User = get_user_model()


def add_user_to_group(email, group: Group):
    user, created = User.objects.get_or_create(email=email)
    if created:
        user.save()
    groupuser, created = GroupUserThru.objects.get_or_create(user=user, group=group)
    if created:
        groupuser.save()
        let_new_user_know_added(group, email)
