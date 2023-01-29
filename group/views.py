from django.shortcuts import render

# Create your views here.
from group.models import Group


def group(request, uuid):
    group = Group.objects.get(uuid=uuid)
    context = {'group': group}
    return render(request, 'group/group.html', context=context)