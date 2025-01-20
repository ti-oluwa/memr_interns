from django.contrib import admin as django_admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from django.http import HttpRequest

from .models import UserAccount


@django_admin.register(UserAccount)
class UserAccountModelAdmin(UnfoldModelAdmin):
    """Custom UserAccount model admin."""

    search_fields = ["first_name", "last_name", "email", "account_type"]
    list_display = [
        "full_name",
        "email",
        "phone1",
        "phone2",
        "account_type",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "account_type",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    ]
    date_hierarchy = "date_joined"
    save_as = False

    def save_model(self, request, obj, form, change):
        # If password is set, then set it using the set_password method
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data["password"])
        obj.save()
        return None

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser


django_admin.site.unregister(Group)
@django_admin.register(Group)
class GroupModelAdmin(GroupAdmin, UnfoldModelAdmin):
    """Custom Group model admin."""

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser
