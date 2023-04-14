from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Row, Submit
from django import forms

from graffiti.models import GraffitiImage


class UploadImageForm(forms.Form):
    image = forms.ImageField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column("image", css_class='col-md-6')),
            Row(
                Column(
                    Submit("submit", "Upload", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
