from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='What email address do you want to use?')
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['captcha'].help_text = 'We need to check you are not a robot. ' \
                                           'Please type the letters you see in the image ' \
                                           'into the box above.'
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row(
                Column("email", css_class="col-md-5"),
            ),
            Row(
                Column("captcha", css_class="col-md-5"),
            ),
            Row(
                Column(
                    Submit("submit", "Sign Up", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
