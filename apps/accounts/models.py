import typing
import functools
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from timezone_field.fields import TimeZoneField
from phonenumber_field.modelfields import PhoneNumberField
from uuid_extensions import uuid7

from .managers import UserAccountManager
from helpers.django.utils.uploads import make_upload_directory_for_user


class AccountType(models.TextChoices):
    INTERN = "intern", _("Intern")
    STAFF = "staff", _("Staff")


def image_directory(instance, filename) -> str:
    return functools.partial(
        make_upload_directory_for_user("id"), parent_dir="images"
    )(instance, filename)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """Model representing a user account"""

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    other_name = models.CharField(max_length=120, blank=True, null=True)
    account_type = models.CharField(
        max_length=120, choices=AccountType.choices, default=AccountType.INTERN
    )
    email = models.EmailField(
        unique=True, db_index=True, verbose_name=_("Email address")
    )
    phone1 = PhoneNumberField(unique=True, verbose_name=_("Phone number 1"))
    phone2 = PhoneNumberField(blank=True, null=True, verbose_name=_("Phone number 2"))
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(blank=False, null=True, upload_to=image_directory)
    timezone = TimeZoneField(default="UTC", blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone1"]

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("User account")
        verbose_name_plural = _("User accounts")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.get_username()

    @property
    def full_name(self) -> str:
        if self.other_name:
            return f"{self.first_name} {self.other_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @property
    def is_intern(self) -> bool:
        return self.account_type == AccountType.INTERN

    @property
    def age(self) -> typing.Optional[int]:
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None
