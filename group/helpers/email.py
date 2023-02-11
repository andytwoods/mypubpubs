from django.core.mail import send_mail
from django.urls import reverse

from group.models import Group
from django.conf import settings


def tell_admin_signup(email: str, group: Group):
    admins_emails = group.admins_emails()

    link = reverse('accept_person', kwargs={'email': email})
    message = f'To accept them, please follow this link: {link}.'
    html_message = f'To accept them, please follow this <a href="{link}">link</a>.'
    send_mail(
        subject=f"{email} requested to join '{group.title}'",
        message=message,
        from_email=settings.EMAIL_SITE,
        recipient_list=admins_emails,
        html_message=html_message,
        fail_silently=False,
    )


def let_new_user_know_added(group, email):
    message = 'Yay :) Visit www.pubpubs.pub to edit your membership, or delete your account.'
    send_mail(
        subject=f"Admins have added you to: '{group.title}'",
        message=message,
        from_email=settings.EMAIL_SITE,
        recipient_list=[email],
        html_message=message,
        fail_silently=False,
    )
