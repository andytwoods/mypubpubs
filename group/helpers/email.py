from django.core.mail import send_mail
from django.urls import reverse

from group.model_choices import StatusChoices
from django.conf import settings


def tell_admin_signup(email: str, group):
    admins_emails = group.admins_emails()
ISSUE HERE WHEN TRYING TO JOIN
    link = reverse('accept_person', kwargs={'email': email, 'uuid':str(group.uuid)})
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


def let_new_user_know_added(group, email, status: StatusChoices):

    match status:
        case StatusChoices.ACTIVE:
            subject = f"A message about the group: '{group.title}'"
            message = f'Yay :) Visit { settings.WEBSITE } to edit your membership, or delete your account.'
        case StatusChoices.INVITED:
            subject = f"You have been invited to join this group: '{group.title}'"
            message = f'Hi! Admin have invited you to join the group {group.title}. To accept or decline, or stop ' \
                      f'receiving any messages about groups in the future, please visit { settings.WEBSITE }.'
        case _:
            raise Exception()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_SITE,
        recipient_list=[email],
        html_message=message,
        fail_silently=False,
    )
