from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Row, Submit, Field
from django import forms

class UploadImageForm(forms.Form):
    image = forms.ImageField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = ''
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column(Field("image", accept='image/*;capture=camera'), css_class='col-md-6')),
            Row(
                Column(
                    Submit("submit", "Upload", css_class="my-4 btn-lg"),
                ),
                css_class="justify-content-center",
            ),
        )
