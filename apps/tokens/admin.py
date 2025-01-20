from django.contrib import admin as django_admin
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import display as unfold_display

from .models import UserRelatedTOTP, IdentifierRelatedTOTP


@django_admin.register(UserRelatedTOTP)
class UserRelatedTOTPModelAdmin(UnfoldModelAdmin):
    """Model admin for the UserRelatedTOTP model"""

    list_display = [
        "owner",
        "validity_period",
        "requestor_ip_address",
        "is_valid",
        "created_at",
    ]
    search_fields = [
        "owner__email",
        "owner__firstname",
        "owner__lastname",
        "requestor_ip_address",
        "created_at",
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser
    
    @unfold_display(
        description=_("Valid"),
        boolean=True,
    )
    def is_valid(self, obj: UserRelatedTOTP) -> bool:
        return obj.is_valid


@django_admin.register(IdentifierRelatedTOTP)
class IdentifierRelatedTOTPModelAdmin(UnfoldModelAdmin):
    """Model admin for the IdentifierRelatedTOTP model"""

    list_display = [
        "identifier",
        "validity_period",
        "requestor_ip_address",
        "is_valid",
        "created_at",
    ]
    search_fields = ["identifier", "requestor_ip_address"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_module_permission(self, request, obj=None):
        return request.user.is_superuser
    
    @unfold_display(
        description=_("Valid"),
        boolean=True,
    )
    def is_valid(self, obj: IdentifierRelatedTOTP) -> bool:
        return obj.is_valid
