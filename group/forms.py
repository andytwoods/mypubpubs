from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms

from group.models import Group


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
        fields = ["title", "description", "members", ]

    members = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=None)
    invite_people = forms.CharField(widget=forms.Textarea,
                                    max_length=1024, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['members'].queryset = kwargs['instance'].members.all()
        self.fields['description'].widget.attrs = {'rows': 2}
        self.fields['invite_people'].widget.attrs = {'rows': 2, 'placeholder': 'enter comma/tab/line seperated email '
                                                                               'addresses to invite people to this group'}

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("title", css_class="col-md-12"),
                Column("description", rows='2', css_class="col-md-12"),
                Column("invite_people", css_class="col-md-12"),
                Column(InlineCheckboxes("members"), css_class="col-md-12"),
            ),
            Row(
                Column(
                    Submit("submit", "Update", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
