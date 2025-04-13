import re
from string import ascii_letters
from random import choice
from typing import Dict, Any

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

from core.settings import EMAIL_CONFIRM_TOKEN_LENGTH
from users.tasks import send_email_verify


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name: str, max_length: int = None) -> str:
        self.delete(name)
        return name


def avatar_path(instance: 'User', filename: str) -> str:
    if instance.pk:
        return f'users/user_{instance.pk}/avatar.webp'

    last = User.objects.last()
    if last:
        return f'users/user_{last.id + 1}/avatar.webp'
    return f'users/user_1/avatar.webp'


def validate_phone_number(phone: str) -> None:
    pattern = re.compile(
        r"^((8|\+374|\+994|\+995|\+375|\+7|\+380|\+38|\+996|\+998|\+993)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$")
    if not re.match(pattern, phone):
        raise ValidationError("Wrong phone number format")


class CustomUserManager(UserManager):
    def _create_user(self, email: str, password: str, **extra_fields: Dict[str, Any]) -> 'User':
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.full_clean()
        user.set_password(user.password)
        user.save(using=self._db)
        token = self.create_email_and_token(email, user)
        send_email_verify.apply_async(args=[email, token])
        return user

    def create(self, email: str = None, password: str = None, **extra_fields: Dict[str, Any]) -> 'User':
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str = None, password: str = None, **extra_fields: Dict[str, Any]) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

    @staticmethod
    def create_email_and_token(email: str, user: 'User') -> str:
        email_address = EmailAddress.objects.create(email, user)
        return EmailVerifyToken.objects.create(email_address)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=128)
    phone = models.CharField(unique=True, null=True, blank=True, validators=[validate_phone_number])
    name = models.CharField(max_length=254, default="Пользователь")
    avatar = models.ImageField(upload_to=avatar_path, default="users/default_avatar.webp", storage=OverwriteStorage)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self) -> str:
        return self.name

    def get_short_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class EmailAddressManager(models.Manager):
    def create(self, email_address: str, user: User, **kwargs) -> 'EmailAddress':
        email_address = self.model(email_address=email_address, user=user, **kwargs)
        email_address.save(using=self._db)
        return email_address


class EmailAddress(models.Model):
    email_address = models.EmailField(unique=True, max_length=128)
    verified = models.BooleanField(default=False)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='email_address')

    objects = EmailAddressManager()


class EmailVerifyTokenManager(models.Manager):
    def create(self, email_address: EmailAddress) -> str:
        token = "".join([choice(ascii_letters) for _ in range(EMAIL_CONFIRM_TOKEN_LENGTH)])
        evt = self.model(token=token, email_address=email_address)
        evt.save(using=self._db)
        return token


class EmailVerifyToken(models.Model):
    token = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    email_address = models.ForeignKey('EmailAddress', on_delete=models.CASCADE, related_name='tokens')
    duplicated = models.BooleanField(default=False)

    objects = EmailVerifyTokenManager()


class PasswordResetTokenManager(models.Manager):
    def create(self, user: User) -> 'PasswordResetToken':
        token = "".join([choice(ascii_letters) for _ in range(EMAIL_CONFIRM_TOKEN_LENGTH)])
        prt = self.model(token=token, user=user)
        prt.save(using=self._db)
        return prt


class PasswordResetToken(models.Model):
    token = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='password_tokens')
    duplicated = models.BooleanField(default=False)

    objects = PasswordResetTokenManager()
