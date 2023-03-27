from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.generic import UpdateView
from django_htmx.http import HttpResponseClientRefresh

from group.forms import GroupAdminForm, JoinGroupForm, PreferencesForm
from group.helpers.email import tell_admin_signup
from group.helpers.email_link import compose_email_link
from group.model_choices import StatusChoices
from group.models import Group, GroupUserThru, GroupAdminThru
from users.helpers.login_email import send_login_email


def group(request, uuid):
    my_group: Group = Group.objects.get(uuid=uuid)

    if request.user.is_authenticated:
        if my_group.linked_with_group(request.user):
            return redirect(reverse('home'))

    if request.POST:
        form = JoinGroupForm(request.POST, user=request.user)
        if form.is_valid():

            email = request.user.email if request.user.is_authenticated else form.data.get('email')
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
                    messages.success(request,
                                     'As soon as the admins accept your request, you will be a member of this group :)')
            return redirect('home')
    context = {'group': my_group,
               'form': JoinGroupForm(user=request.user)}

    return render(request, 'group/group.html', context=context)


home_context_info = [('group_memberships', StatusChoices.ACTIVE),
                     ('waiting_memberships', StatusChoices.WAITING_FOR_OK),
                     ('ok_invitation', StatusChoices.INVITED)]

@cache_page(20 * 1) # 20s cache
def home(request):
    if request.user.is_authenticated:
        context = {'admin_of_groups': GroupAdminThru.admin_of_which_groups(request.user)}

        for label, status in home_context_info:
            context[label] = GroupUserThru.retrieve_groups_given_status(request.user, status)
        return render(request, 'home.html', context=context)

    message = '''This is an example email! Just add whatever text you want here, and then click send.
    
    'WHY DO WE NEED AN APP FOR THIS??!' I hear you ask. There's a stack of good reasons.  For example, letting people signup/leave your group via an app means you will never forget someone. You can make it that ANYONE in the group can generate an email. You can have emails automatically CC/BCC people, helping avoid embarrassing mistakes. 
    
    This app ONLY saves email addresses in its database. We don't collect any other information. We don't do cookies. It's birthplace was in Academia, with the goal of emailing and managing an ever growing list of researchers who enjoyed a pint after work.
    
    At the bottom of the email we provide information (if desired) about others signing up to the email,
     leaving the group etc.'''

    context = {'email_link': compose_email_link('greetings!',
                                                message=message,
                                                field_txt='cc',
                                                email_list=['example@example.com',
                                                            'example2@example.com',
                                                            'example3@example.com'])}

    return render(request, 'landing_page.html', context=context)


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

        group: Group = self.get_object()
        group.remove_users_not_in_this_list(form.cleaned_data['members'])
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
        case _:
            raise Exception('unknown htmx command')
    return HttpResponseClientRefresh()


@login_required
def user_preferences(request):
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


def htmx_generate_email(request, uuid: str, usertype: str):
    _group: Group = Group.objects.get(uuid=uuid)
    match usertype:
        case 'user':
            if not _group.check_is_active_user(request.user):
                raise Exception(f'non admin user ({request.user.id}) tried to request admin email (group: {uuid})')
            a_record_url = _group.make_admin_email()
            pass
        case 'admin':
            if not _group.check_is_admin(request.user):
                raise Exception(f'non admin user ({request.user.id}) tried to request admin email (group: {uuid})')
            a_record_url = _group.make_email()
        case _:
            raise Exception(f'unknown htmx htmx_generate_email command: {usertype}')

    context = {'a_record_url': a_record_url, 'my_id': f'{_group.uuid}-{usertype}' }
    return render(request, 'group/generate_email.html', context=context)
