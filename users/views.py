from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from mailauth.views import LoginView

from .forms import SignUpForm, MyEmailLoginForm
from .helpers.login_email import send_login_email

User = get_user_model()


class MyLoginView(LoginView):
    form_class = MyEmailLoginForm

    def form_valid(self, form):

        email = form.cleaned_data[form.field_name]
        users = list(form.get_users(email))
        if users:
            for user in users:
                context = form.get_mail_context(self.request, user)
                form.send_mail(email, context)
            return super().form_valid(form)
        else:
            messages.error(self.request, f'{email} is not yet a member of this site')
            return redirect(reverse('login'))


        return outcome


def signup_view(request):
    form = None
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.save()
                messages.success(request, f'Welcome! We have sent you an email to {email} with a link '
                                          f'that will log you in')
            else:
                messages.error(request, f'You already have an account! An email has'
                                        f' been sent to {email} with a link to log in')
            send_login_email(user, request)
            return redirect(reverse('home'))

    if not form:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'registration/signup.html', context)
