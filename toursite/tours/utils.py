from django.core.mail import EmailMessage
from django.utils.translation import gettext as _


def send_email(email):
    message = EmailMessage(
        to=[email],
        subject=_('Traversal - туристическая компания'),
        body=_(f'Вы успешно забронировали тур!'),
        from_email='noreply@traversal.kg'
    )

    message.send()
    return True