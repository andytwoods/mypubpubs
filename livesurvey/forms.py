from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.db import models
from django.utils.safestring import mark_safe


class HtmxFormHelper(FormHelper):

    def __init__(self, form=None):
        super().__init__(form)
        self.attrs['hx-post'] = f'{form.__class__.__name__}/'





class DemographicsForm(forms.Form):

    age = forms.IntegerField(min_value=18, max_value=45, help_text='What is your  age')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = HtmxFormHelper(self)
        self.helper.layout = Layout(
            Row(Column("age", css_class="col-md-4"), ),
            Row(
                Column(
                    Submit("submit", "Join", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )


class SurveyForm(forms.Form):

    class Q1Choices(models.TextChoices):
        BAR = "a", 'my a'
        PIE = "b", 'my b'
        HISTOGRAM = 'my c'

    q1 = forms.ChoiceField(choices=Q1Choices.choices, help_text='Q1...')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = HtmxFormHelper(self)

        self.helper.layout = Layout(
            Row(Column("q1", css_class="col-md-4"), ),
            Row(
                Column(
                    Submit("submit", "Join", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
