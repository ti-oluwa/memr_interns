import json
from urllib.parse import urlencode as urllib_urlencode
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from helpers.django.exceptions import capture
from helpers.django.response.decorators import redirect_authenticated
from helpers.django.utils.requests import parse_query_params_from_request
from helpers.django.utils.mailing import send_smtp_mail
from helpers.django.response import shortcuts as response
from .forms import (
    SignInForm,
    EmailVerificationInitiationForm,
    EmailVerificationCompletionForm,
    AccountCreationForm,
    PasswordResetForm,
    ProfileUpdateForm,
)
from apps.tokens.totp import (
    InvalidToken,
    generate_totp_for_identifier,
    get_totp_by_identifier,
    exchange_data_for_token,
    exchange_token_for_data,
)
from .models import UserAccount, AccountType
from dcrypt import TextCrypt, CryptKey

crypt_key = CryptKey()
text_crypt = TextCrypt(crypt_key)


@capture.enable
@capture.capture(content="An error occurred while signing you in.")
class SignInView(generic.TemplateView):
    template_name = "accounts/signin.html"
    form_class = SignInForm
    http_method_names = ["get", "post"]

    @redirect_authenticated("interns:dashboard")
    def get(self, request, *args: str, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = self.form_class(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return response.validation_error(
            detail="An error occurred",
            errors=form.errors,
        )

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user_account = authenticate(
            self.request,
            username=email,
            password=password,
        )

        if user_account:
            login(self.request, user_account)
            timezone = form.cleaned_data.get("timezone", None)
            if timezone:
                user_account.timezone = form.cleaned_data["timezone"]
                user_account.save(update_fields=["timezone"])

            if self.request.user.is_staff:
                # Just redirect to admin index page if user is staff
                next_url = reverse("admin:index")
            else:
                query_params = parse_query_params_from_request(self.request)
                next_url = query_params.pop("next", None)
                if next_url and query_params:
                    other_query_params = urllib_urlencode(query_params)
                    next_url = f"{next_url}?{other_query_params}"

            return response.success(
                message=f"Hello {user_account.full_name}!",
                data={
                    "redirect_url": next_url or reverse("interns:dashboard"),
                },
            )
        return response.bad_request(
            "Invalid credentials! Check the details provided and try again."
        )


class SignOutView(LoginRequiredMixin, generic.View):
    """View for user sign out"""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("accounts:signin")


@capture.enable
@capture.capture(content="An error occurred while verifying email.")
class EmailVerificationInitiationView(generic.View):
    http_method_names = ["post"]
    form_class = EmailVerificationInitiationForm

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = self.form_class(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return response.validation_error(
            detail="An error occurred",
            errors=form.errors,
        )

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        query_params = parse_query_params_from_request(self.request)
        check_unique = query_params.get("check_unique", False)
        check_exists = query_params.get("check_exists", False)
        if check_unique:
            if UserAccount.objects.filter(email=email).exists():
                return response.bad_request("Account with email already exists!")
        if check_exists:
            if not UserAccount.objects.filter(email=email).exists():
                return response.bad_request("Account with email does not exists!")

        event = form.cleaned_data["event"]
        identifier = f"{event}:{email}"
        totp = generate_totp_for_identifier(identifier)
        send_smtp_mail(
            subject="Verify your email",
            message=f"Your email verification code is {totp.token()}",
            to_email=email,
        )
        verification_token = f"{identifier}:{totp.id}"
        return response.success(
            message="An OTP has been sent to your email. Please check your inbox.",
            data={"verification_token": text_crypt.encrypt(verification_token)},
        )


@capture.enable
@capture.capture(content="Oops! An error occurred while verifying OTP.")
class EmailVerificationCompletionView(generic.View):
    http_method_names = ["post"]
    form_class = EmailVerificationCompletionForm

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = self.form_class(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        otp = form.cleaned_data["otp"]
        verification_token = text_crypt.decrypt(form.cleaned_data["verification_token"])
        token_event, email, totp_obj_id = verification_token.split(":")[:3]
        identifier = f"{token_event}:{email}"

        with transaction.atomic():
            totp = get_totp_by_identifier(identifier)
            if not totp or totp.id != int(totp_obj_id):
                return response.bad_request("Invalid OTP!")

            if not totp.verify_token(otp):
                return response.bad_request("Invalid OTP!")

            totp.delete()
            token = exchange_data_for_token(
                data={
                    "event": token_event,
                    "email": email,
                },
                expires_after=60 * 15,
            )
        return response.success(message="OTP Valid!", data={"token": token})

    def form_invalid(self, form):
        return response.validation_error(detail="An error occurred", errors=form.errors)


@redirect_authenticated("interns:dashboard", method="get")
@capture.enable
@capture.capture(content="Oops! An error occurred while completing registration.")
class AccountCreationView(generic.TemplateView):
    template_name = "accounts/registration.html"
    form_class = AccountCreationForm
    http_method_names = ["get", "post"]

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return response.validation_error(
            detail="An error occurred",
            errors=form.errors,
        )

    def form_valid(self, form):
        form_data = form.cleaned_data.copy()
        email_token = form_data.pop("email_token")
        token_event = form_data.pop("token_event")

        with (
            capture.capture(
                InvalidToken,
                content="Invalid or expired token! Please try again",
                code=400,
                prioritize_content=True,
            ),
            capture.capture(
                IntegrityError,
                content="Account with given details already exists",
                code=400,
                prioritize_content=True,
            ),
        ):
            with transaction.atomic():
                token_data = exchange_token_for_data(email_token)
                if token_event != token_data.get("event", None):
                    return response.bad_request("Invalid token!")

                account = UserAccount.objects.create_user(
                    email=token_data["email"],
                    **form_data,
                    account_type=AccountType.INTERN,
                )

        login(self.request, account)
        return response.success(
            message="Account created successfully!",
            data={"redirect_url": reverse("interns:dashboard")},
        )


@redirect_authenticated("interns:dashboard", method="get")
@capture.enable
@capture.capture(content="Oops! An error occurred while resetting password.")
class PasswordResetView(generic.TemplateView):
    template_name = "accounts/password_reset.html"
    form_class = PasswordResetForm
    http_method_names = ["get", "post"]

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = self.form_class(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return response.validation_error(
            detail="An error occurred",
            errors=form.errors,
        )

    def form_valid(self, form):
        form_data = form.cleaned_data
        email_token = form_data.get("email_token")
        token_event = form_data.get("token_event")

        with capture.capture(
            (InvalidToken, UserAccount.DoesNotExist),
            content="Invalid or expired token! Please try again",
            code=400,
        ):
            with transaction.atomic():
                token_data = exchange_token_for_data(email_token)
                if token_event != token_data.get("event", None):
                    return response.bad_request("Invalid token!")

                account = UserAccount.objects.get(email=token_data["email"])
                account.set_password(form_data["password"])

        login(self.request, account)
        return response.success(
            message="Password reset successful!",
            data={"redirect_url": reverse("interns:dashboard")},
        )


class AccountProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/profile.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["account"] = self.request.user
        return context_data


class AccountProfileUpdateView(LoginRequiredMixin, generic.View):
    http_method_names = ["post"]
    form_class = ProfileUpdateForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        return response.validation_error(
            detail="An error occurred",
            errors=form.errors,
        )

    def form_valid(self, form):
        form_data = form.cleaned_data
        user_account = self.request.user

        for key, value in form_data.items():
            if key == "image" and not value:
                continue
            setattr(user_account, key, value)
        user_account.save(update_fields=list(form_data.keys()))
        return response.success(
            message="Profile updated!",
            data={"redirect_url": reverse("accounts:profile")},
        )


user_signin_view = SignInView.as_view()
user_signout_view = SignOutView.as_view()
email_verification_initiation_view = EmailVerificationInitiationView.as_view()
email_verification_completion_view = EmailVerificationCompletionView.as_view()
account_creation_view = AccountCreationView.as_view()
password_reset_view = PasswordResetView.as_view()
account_profile_view = AccountProfileView.as_view()
account_profile_update_view = AccountProfileUpdateView.as_view()
