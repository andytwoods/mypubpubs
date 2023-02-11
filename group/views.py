from email._header_value_parser import Domain

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views.generic import UpdateView
from mailauth.forms import EmailLoginForm

from group.forms import GroupAdminForm, JoinGroupForm
from group.helpers.add_user_to_group import add_user_to_group
from group.helpers.email import tell_admin_signup
from group.models import Group, GroupUserThru, GroupAdminThru, DomainNames


def send_login_email(user, request):
    login_form = EmailLoginForm(None)
    login_form.cleaned_data = {"next": reverse('home')}
    context = login_form.get_mail_context(request, user)
    login_form.send_mail(user.email, context)


def group(request, uuid):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    my_group: Group = Group.objects.get(uuid=uuid)
    if request.POST:
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            # requested_to_join = form.data.get('requested_to_join')
            # print(requested_to_join,33)

            email = form.data.get('email')
            domain_info = email.split('@')
            safe_domains = [domain[0] for domain in my_group.safe_domains.all().values_list('domain')]

            def on_active_member(groupuser, message):
                message += " You've been emailed a link you can use to log in (expires in 5 minutes)."
                send_login_email(groupuser.user, request)
                messages.success(request, message)

            if domain_info[1] in safe_domains:
                groupuser, joined_group = add_user_to_group(email, my_group, GroupUserThru.StatusChoices.ACTIVE)
                if joined_group:
                    on_active_member(groupuser, "Congrats, you've been added to the group!")
                else:
                    on_active_member(groupuser, "You already are a part of this group!")
            else:
                groupuser, joined_group = add_user_to_group(email, my_group, GroupUserThru.StatusChoices.WAITING_FOR_OK)
                if groupuser.status is GroupUserThru.StatusChoices.ACTIVE:
                    on_active_member(groupuser, "You already are a part of this group!")
                else:
                    tell_admin_signup(email, my_group)
                    messages.success(request, 'We have sent your details to the admins :)')
            return redirect(reverse('home'))
    context = {'group': my_group,
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


def make_list(val: str):
    val = ','.join(val.splitlines())
    val = ','.join(val.split(';'))
    val = ''.join(val.split(' '))
    return [x for x in val.split(',') if len(x) > 0]


def add_safe_domains(new_safe_domains, group: Group):
    already_exists = list(group.safe_domains.all())
    for new_safe_domain in new_safe_domains:
        if new_safe_domain not in already_exists:
            dm = DomainNames(domain=new_safe_domain)
            dm.save()
            group.safe_domains.add(dm)


class GroupPrefs(UpdateView):
    model = Group
    form_class = GroupAdminForm
    template_name = 'group/edit_group.html'

    def get_success_url(self):
        return reverse('admin-group-edit', kwargs={'uuid': self.kwargs.get('uuid')})

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.error(self.request, 'Oops, you are not logged in.')
            return redirect('home')
        try:
            GroupAdminThru.objects.get(user=self.request.user, group__uuid=self.kwargs.get('uuid'))
        except GroupAdminThru.DoesNotExist:
            messages.error(self.request, 'Oops, you are not an admin of this group, or this group does not exist!')
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        uuid = self.kwargs.get('uuid')
        return Group.objects.get(uuid=uuid)

    def form_valid(self, form):
        outcome = super().form_valid(form)

        new_safe_domains = make_list(form.data['add_safe_domains'])
        add_safe_domains(new_safe_domains, self.get_object())

        invited = make_list(form.data['invite_people'])

        return outcome


@login_required
def add_person(request, uuid, email):
    group = Group.objects.get(uuid=uuid)
    if request.user not in group.admins:
        messages.error(request, 'You are not an admin of this group')
    else:
        add_user_to_group(email, group, GroupUserThru.StatusChoices.ACTIVE)
        messages.success(request, f'added {email} to the group!')
    return None
