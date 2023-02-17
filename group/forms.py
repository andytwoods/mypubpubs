from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, HTML
from django import forms

from group.model_choices import StatusChoices
from group.models import Group, GroupUserThru


class JoinGroupForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("email", css_class="col-md-4"),
            ),
            Row(
                Column(
                    Submit("submit", "Update", css_class="my-4 btn-lg"),
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

    invite_people = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)
    add_banned = forms.CharField(widget=forms.Textarea, max_length=1024, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group: Group = kwargs['instance']

        self.fields['description'].widget.attrs = {'rows': 2}

        my_members = group.members.filter(groupuserthru__status=StatusChoices.ACTIVE)
        self.fields['members'].choices = [(u.id, u.email) for u in my_members]
        self.fields['members'].help_text = 'Select those who you want to stop being members'

        my_asked = group.members.filter(groupuserthru__status=StatusChoices.WAITING_FOR_OK)
        asked_users = [(u.id, u.email) for u in my_asked]
        self.fields['requested_to_join'].choices = asked_users
        self.fields['requested_to_join'].help_text = 'Select those who you want to become active members'
        self.fields['invite_people'].widget.attrs = {'rows': 2, 'placeholder': 'enter comma/tab/line seperated email '
                                                                               'addresses to invite people to this '
                                                                               'group'}

        self.fields['safe_domains'].queryset = group.safe_domains.all()
        self.fields['add_safe_domains'].widget.attrs = {'rows': 2,
                                                        'placeholder': 'enter comma/tab/line seperated domains '
                                                                       '(e.g. rhul.ac.uk). People with emails ending '
                                                                       'in these domains will be automatically added'}

        self.fields['add_banned'].widget.attrs = {'rows': 2,
                                                        'placeholder': 'enter comma/tab/line seperated email addresses'
                                                                       ' to ban.'}

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
                Column("invite_people", css_class="col-md-12"),
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
                    Submit("submit", "Update", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
