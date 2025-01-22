from django import forms
from django.conf import settings
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


max_size_200KB = max_file_size_validator_factory(200)


class AccountCreationForm(forms.Form):
    email_token = forms.CharField(required=True, widget=forms.HiddenInput)
    token_event = forms.CharField(required=True, widget=forms.HiddenInput)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    other_name = forms.CharField(required=False)
    phone1 = PhoneNumberFormField(required=True)
    phone2 = PhoneNumberFormField(required=False)
    date_of_birth = forms.DateField(required=False)
    image = forms.ImageField(
        allow_empty_file=False, required=True, validators=[max_size_200KB]
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
    date_of_birth = forms.DateField(required=False)
    timezone = TimeZoneFormField(required=False)
    image = forms.ImageField(
        allow_empty_file=False, required=True, validators=[max_size_200KB]
    )
