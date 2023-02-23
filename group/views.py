from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView
from django_htmx.http import HttpResponseClientRefresh
from mailauth.forms import EmailLoginForm

from group.forms import GroupAdminForm, JoinGroupForm, PreferencesForm
from group.helpers.email import tell_admin_signup
from group.model_choices import StatusChoices
from group.models import Group, GroupUserThru, GroupAdminThru


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

            email = form.data.get('email')
            domain_info = email.split('@')
            safe_domains = [domain[0] for domain in my_group.safe_domains.all().values_list('domain')]

            def on_active_member(groupuser, message):
                message += " You've been emailed a link you can use to log in (expires in 5 minutes)."
                send_login_email(groupuser.user, request)
                messages.success(request, message)

            if domain_info[1] in safe_domains:
                groupuser, joined_group = my_group.add_user(email, StatusChoices.ACTIVE)
                if joined_group:
                    on_active_member(groupuser, "Congrats, you've been added to the group!")
                else:
                    on_active_member(groupuser, "You already are a part of this group!")
            else:
                groupuser, joined_group = my_group.add_user(email, StatusChoices.WAITING_FOR_OK)
                if groupuser.status is StatusChoices.ACTIVE:
                    on_active_member(groupuser, "You already are a part of this group!")
                else:
                    tell_admin_signup(email, my_group)
                    messages.success(request, 'We have sent your details to the admins :)')
            return request.path
    context = {'group': my_group,
               'form': JoinGroupForm()}
    return render(request, 'group/group.html', context=context)


home_context_info = [('group_memberships', StatusChoices.ACTIVE),
                     ('waiting_memberships', StatusChoices.WAITING_FOR_OK),
                     ('ok_invitation', StatusChoices.INVITED)]


def home(request):
    context = {}
    if request.user.is_authenticated:

        context['admin_of_groups'] = GroupAdminThru.admin_of_which_groups(request.user)

        for label, status in home_context_info:
            context[label] = GroupUserThru.retrieve_groups_given_status(request.user, status)

    return render(request, 'home.html', context=context)


class GroupPrefs(UpdateView):
    model = Group
    form_class = GroupAdminForm
    template_name = 'group/edit_group.html'

    def get_success_url(self):
        return reverse('admin-group-edit', kwargs={'uuid': self.kwargs.get('uuid')})

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            messages.error(self.request, 'Oops, yÏou are not logged in.')
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

        group: Group = self.get_object()
        group.add_safe_domains(form.cleaned_data['add_safe_domains'])
        group.authorise_users(form.cleaned_data['requested_to_join'])
        group.ban_users(form.cleaned_data['add_banned'])

        group.invite(form.data['invite_people'])

        return outcome


@login_required
def add_person(request, uuid, email):
    group = Group.objects.get(uuid=uuid)
    if request.user not in group.admins:
        messages.error(request, 'You are not an admin of this group')
    else:
        group.add_user(email, StatusChoices.ACTIVE)
        messages.success(request, f'added {email} to the group!')
    return None


@login_required
@require_http_methods(['POST'])
def htmx_home_commands(request):
    match request.POST.get('command'):
        case 'accept-invitation':
            GroupUserThru.accept_invitation(request.user, request.POST.get('group_uuid'))
            messages.success(request, 'Successfully added you to group!')
        case 'decline-invitation':
            GroupUserThru.decline_invitation(request.user, request.POST.get('group_uuid'))
        case 'check-new-people':
            group_uuid = request.POST.get('group_uuid')
            my_group: Group = Group.objects.get(uuid=group_uuid)
            if not my_group.check_is_admin(request.user):
                raise Http404
            found = GroupUserThru.check_new_people_needing_permission(group_uuid)
            if found:
                context = {
                    'group_uuid': group_uuid,
                    'found': found
                }
                return render(request, template_name='partials/waiting_to_join.html', context=context)
            else:
                return HttpResponse('')
        case 'cancel-join-request':
            group_uuid = request.POST.get('group_uuid')
            GroupUserThru.cancel_join_request(request.user, group_uuid)
            return HttpResponseClientRefresh()
        case 'leave-group':
            group_uuid = request.POST.get('group_uuid')
            GroupUserThru.objects.get(user=request.user, group__uuid=group_uuid).delete()
            messages.success(request, 'Successfully removed you from the group')
            return HttpResponseClientRefresh()
        case 'delete-account':
            user = request.user
            logout(request)
            user.delete()
            return HttpResponseClientRefresh()
            #
        case _:
            raise Exception('unknown htmx command')
    return HttpResponseClientRefresh()


@login_required
def preferences(request):
    if request.POST:
        form = PreferencesForm(request.POST)

    else:
        form = PreferencesForm(instance=request.user)

    context = {'form': form, }
    return render(request, template_name='group/preferences.html', context=context)


@require_http_methods(['GET'])
def htmx_modal(request):
    match request.GET.get('command'):
        case 'login':
            return redirect('mailauth:login')

    raise Exception('unknown htmx modal request')
