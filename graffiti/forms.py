from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Row, Submit, Field
from django import forms

from graffiti.models import GraffitiImage


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = GraffitiImage

        fields = ["url",]



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['url'].help_text = 'Remember to include https://'

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Field('url')),
            Row(
                Column(
                    Submit("submit", "Save", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
