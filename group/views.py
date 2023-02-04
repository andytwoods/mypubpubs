from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views.generic import UpdateView

from group.forms import GroupAdminForm, JoinGroupForm
from group.helpers.add_user_to_group import add_user_to_group
from group.helpers.email import tell_admin_signup
from group.models import Group, GroupUserThru, GroupAdminThru


def group(request, uuid):
    group = Group.objects.get(uuid=uuid)
    if request.POST:
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            email = form.email
            tell_admin_signup(email, group)
            messages.success(request, 'We past on your details to the admins :)')
            return reverse('home')
    context = {'group': group,
               'form': JoinGroupForm()}
    return render(request, 'group/group.html', context=context)


def home(request):
    context = {}
    if request.user.is_authenticated:
        context['group_memberships'] = GroupUserThru.objects.filter(user=request.user). \
            select_related('group')
        context['admin_of_groups'] = GroupAdminThru.objects.filter(user=request.user). \
            select_related('group'). \
            prefetch_related('user')
    return render(request, 'home.html', context=context)


class GroupPrefs(UpdateView):
    model = Group
    form_class = GroupAdminForm
    template_name = 'group/edit_group.html'

    def get_success_url(self):
        return reverse('home')

    def dispatch(self, *args, **kwargs):
        try:
            GroupAdminThru.objects.get(user=self.request.user, group__uuid=self.kwargs.get('uuid'))
        except GroupAdminThru.DoesNotExist:
            messages.error(self.request, 'Oops, you are not an admin of this group, or this group does not exist!')
            redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return Group.objects.get(uuid=uuid)

    def form_valid(self, form):
        outcome = super().form_valid(form)

        invited = form.data['invite_people']

        return outcome

@login_required
def add_person(request, uuid, email):
    group = Group.objects.get(uuid=uuid)
    if request.user not in group.admins:
        messages.error(request, 'You are not an admin of this group')
    else:
        add_user_to_group(email, group)
        messages.success(request, f'added {email} to the group!')
    return None