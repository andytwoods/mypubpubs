from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.db import models


class ChartBase:
    dv = ''

class Histogram(ChartBase):
    min = 10
    max = 80
    bins = 'auto'

class Pie(ChartBase):
    pass


class HtmxFormHelper(FormHelper):

    form_class = "fade-me-out"

    def __init__(self, form=None):
        super().__init__(form)
        self.attrs['hx-post'] = f'{form.__class__.__name__}'
        self.attrs['hx-swap'] ="outerHTML swap:1s"


class DemographicsForm(forms.Form, Histogram):
    age = forms.IntegerField(min_value=18, max_value=45, help_text='What is your age')

    dv = 'age'

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


class SurveyForm(forms.Form, Pie):
    class Q1Choices(models.TextChoices):
        BAR = "a", 'my a'
        PIE = "b", 'my b'
        HISTOGRAM = 'my c'

    q1 = forms.ChoiceField(choices=Q1Choices.choices, help_text='Q1...')

    dv = 'q1'

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
