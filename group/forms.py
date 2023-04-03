from captcha.fields import CaptchaField
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django import forms
from django.contrib.auth import get_user_model
from django.forms import HiddenInput
from django.utils.safestring import mark_safe

from group.helpers.email_link import compose_email_link, generate_message
from group.model_choices import StatusChoices
from group.models import Group

User = get_user_model()


class PreferencesForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["email"].help_text = 'Be careful changing your address! If you enter an incorrect address you' \
                                         'will be locked out of your account.'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("email", css_class='col-md-4')),
            Row(
                Column(
                    Submit("submit", "Update", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )


class JoinGroupForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField()
    def __init__(self, *args, **kwargs):
        self.user:User = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if self.user.is_authenticated:
            email_field = self.fields['email']
            email_field.widget.attrs['readonly'] = True
            email_field.widget = HiddenInput()
            email_field.initial = self.user.email

        self.fields['captcha'].help_text = 'We need to check you are not a robot. ' \
                                           'Please type the letters you see in the image ' \
                                           'into the box above.'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row( Column("email", css_class="col-md-4"),),
            Row(Column("captcha", css_class="col-md-5"), ),
            Row(
                Column(
                    Submit("submit", "Join", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["title", "description", "safe_domains", ]

    safe_domains = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=None, required=False)
    add_safe_domains = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    members = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)
    requested_to_join = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)

    add_people = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    add_banned = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group: Group = kwargs['instance']

        self.fields['description'].widget.attrs = {'rows': 2}

        my_members = group.members.filter(groupuserthru__status=StatusChoices.ACTIVE)
        members = self.fields['members']
        members.choices = [(u.id, u.email) for u in my_members]
        if len(members.choices) == 0:
            members.widget = HiddenInput()
        else:
            members.initial = [u.id for u in my_members]
            members.help_text = 'Deselect those who you want to stop being members'

        my_asked = group.members.filter(groupuserthru__status=StatusChoices.WAITING_FOR_OK)
        asked_users = [(u.id, u.email) for u in my_asked]
        requested_to_join = self.fields['requested_to_join']
        if len(asked_users) == 0:
            requested_to_join.widget = HiddenInput()
        else:
            requested_to_join.choices = asked_users
            requested_to_join.help_text = 'Select those who you want to become active members'
        self.fields['add_people'].widget.attrs = {'rows': 2, 'placeholder': 'enter comma/tab/line seperated email '
                                                                               'addresses to add people to this '
                                                                               'group'}
        link = compose_email_link(subject='Link to join group',
                                  message=generate_message(group),
                                  field_txt='', email_list=[])
        self.fields['add_people'].label = mark_safe(f'Add people <small class="text-primary">'
                                                    f'or <a href="{link}" target="_blank">'
                                                    f'generate</a> an email to forward with a one-click '
                                                    f'joining link</a></small>')

        self.fields['safe_domains'].queryset = group.safe_domains.all()
        self.fields['add_safe_domains'].widget.attrs = {'rows': 2,
                                                        'placeholder': 'enter comma/tab/line seperated domains '
                                                                       '(e.g. rhul.ac.uk). People with emails ending '
                                                                       'in these domains will join automatically'}

        self.fields['add_banned'].widget.attrs = {'rows': 2,
                                                  'placeholder': 'enter comma/tab/line seperated email addresses'
                                                                 ' to ban'}

        self.helper = FormHelper()
        row_css = 'bg-light rounded shadow mb-3'
        self.helper.layout = Layout(
            Row(
                Column("title", css_class="col-md-12"),
                Column("description", rows='2', css_class="col-md-12"),
                css_class=row_css,
            ),
            Row(
                HTML('<h4>Members</h2>'),
                Column(InlineCheckboxes("members"), css_class="col-md-12"),
                Column(InlineCheckboxes("requested_to_join"), css_class="col-md-12"),
                Column("add_people", css_class="col-md-12"),
                css_class=row_css,
            ),
            Row(
                HTML('<h4>Let people join automatically if their email address has a specific ending</h2>'),
                Column(InlineCheckboxes("safe_domains"), css_class="col-md-12"),
                Column("add_safe_domains", css_class="col-md-12"),
                css_class=row_css,
            ),
            Row(
                HTML('<h4>Ban people</h2>'),
                Column("add_banned", css_class="col-md-12"),
                css_class=row_css,
            ),
            Row(
                Column(
                    Submit("submit", "Save", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
