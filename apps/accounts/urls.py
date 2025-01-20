from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("sign-in/", views.user_signin_view, name="signin"),
    path("sign-out/", views.user_signout_view, name="signout"),
    path(
        "email-verification/initiate/",
        views.email_verification_initiation_view,
        name="email_verification_initiation",
    ),
    path(
        "email-verification/completion/",
        views.email_verification_completion_view,
        name="email_verification_completion",
    ),
    path(
        "register/",
        views.account_creation_view,
        name="registration",
    ),
    path(
        "reset-password/",
        views.password_reset_view,
        name="password_reset",
    ),
    path(
        "profile/",
        views.account_profile_view,
        name="profile",
    ),
    path(
        "profile/update/",
        views.account_profile_update_view,
        name="profile_update",
    ),
]
