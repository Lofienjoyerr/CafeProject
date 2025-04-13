import os

from celery import shared_task
from django.core.mail import send_mail
from PIL import Image

from core.settings import MEDIA_ROOT


@shared_task
def send_email_verify(email: str, token: str) -> None:
    send_mail("Подтверждение электронной почты", f"""От вашего адреса электронной почты была проведена попытка активации электронной почты.
Если это были Вы, то перейдите по следующему адресу, чтобы подтвердить почту
http://127.0.0.1:8000/api/v1/email/verify/{token}/
Если это были не Вы, проигнорируйте данное сообщение.""", from_email=None,
              recipient_list=[email], fail_silently=False)


@shared_task
def send_password_reset(email: str, token: 'PasswordResetToken') -> None:
    send_mail("Смена пароля", f"""От вашего адреса электронной почты была проведена попытка смены пароля.
Если это были Вы, то перейдите по следующему адресу, чтобы сменить пароль
http://127.0.0.1:8000/api/v1/password/reset/verify/{token.token}/
Если это были не Вы, проигнорируйте данное сообщение.""", from_email=None,
              recipient_list=[email], fail_silently=False)


@shared_task
def crop_avatar(img_path: str) -> None:
    with Image.open(os.path.join(MEDIA_ROOT, img_path)) as im:
        im = im.resize((220, 220))
        im.save(os.path.join(MEDIA_ROOT, img_path))
