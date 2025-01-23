from django import forms
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.formfields import PhoneNumberField as PhoneNumberFormField
from timezone_field.forms import TimeZoneFormField

from helpers.django.validators import max_file_size_validator_factory


class SignInForm(forms.Form):
    """Form for user sign in"""

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class EmailVerificationInitiationForm(forms.Form):
    """Form for verifying registration email"""

    email = forms.EmailField(required=True)
    event = forms.CharField(required=True, widget=forms.HiddenInput)


class EmailVerificationCompletionForm(forms.Form):
    """Form for verifying registration email"""

    otp = forms.CharField(required=True, max_length=settings.OTP_LENGTH)
    verification_token = forms.CharField(required=True, widget=forms.HiddenInput)


max_size_100KB = max_file_size_validator_factory(100)


def validate_date_of_birth(date_of_birth):
    if date_of_birth:
        if date_of_birth.year < 1900:
            raise forms.ValidationError(["Date of birth cannot be earlier than 1900"])
        if (timezone.now().date() - date_of_birth) < timezone.timedelta(days=365 * 16):
            raise forms.ValidationError(["You must be at least 16 years old."])
    return date_of_birth


class AccountCreationForm(forms.Form):
    email_token = forms.CharField(required=True, widget=forms.HiddenInput)
    token_event = forms.CharField(required=True, widget=forms.HiddenInput)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    other_name = forms.CharField(required=False)
    phone1 = PhoneNumberFormField(required=True)
    phone2 = PhoneNumberFormField(required=False)
    date_of_birth = forms.DateField(required=False, validators=[validate_date_of_birth])
    image = forms.ImageField(
        allow_empty_file=False, required=True, validators=[max_size_100KB]
    )
    password = forms.CharField(
        widget=forms.PasswordInput, required=True, validators=[validate_password]
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    timezone = TimeZoneFormField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.pop("confirm_password", None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({"confirm_password": "Passwords do not match."})

        return cleaned_data


class PasswordResetForm(forms.Form):
    email_token = forms.CharField(required=True, widget=forms.HiddenInput)
    token_event = forms.CharField(required=True, widget=forms.HiddenInput)
    password = forms.CharField(
        widget=forms.PasswordInput, required=True, validators=[validate_password]
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.pop("confirm_password", None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({"confirm_password": "Passwords do not match."})

        return cleaned_data


class ProfileUpdateForm(forms.Form):
    """Form for updating user profile"""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    other_name = forms.CharField(required=False)
    phone1 = PhoneNumberFormField(required=True)
    phone2 = PhoneNumberFormField(required=False)
    date_of_birth = forms.DateField(required=False, validators=[validate_date_of_birth])
    timezone = TimeZoneFormField(required=False)
    image = forms.ImageField(
        allow_empty_file=False, required=False, validators=[max_size_100KB]
    )
