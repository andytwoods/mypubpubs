from django.urls import reverse
from mailauth.forms import EmailLoginForm


def send_login_email(user, request):
    login_form = EmailLoginForm(None)
    login_form.cleaned_data = {"next": reverse('home')}
    context = login_form.get_mail_context(request, user)
    login_form.send_mail(user.email, context)
