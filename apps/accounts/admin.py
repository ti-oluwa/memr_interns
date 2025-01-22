from django.contrib import admin as django_admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import GroupAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import display as unfold_display
from imagekit.admin import AdminThumbnail
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from imagekit.cachefiles import ImageCacheFile

from django.http import HttpRequest

from .models import UserAccount


class AdminThumbnailSpec(ImageSpec):
    # processors = [ResizeToFill(100, 100)]
    format = "JPEG"
    options = {"quality": 60}


def cached_admin_thumb(instance: UserAccount):
    if not instance.image:
        return None

    cached = ImageCacheFile(AdminThumbnailSpec(instance.image))
    # only generates the first time, subsequent calls use cache
    cached.generate()
    return cached


@django_admin.register(UserAccount)
class UserAccountModelAdmin(UnfoldModelAdmin):
    """Custom UserAccount model admin."""

    search_fields = ["first_name", "last_name", "email", "account_type"]
    list_display = [
        "image_preview",
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
    
    image_preview = AdminThumbnail(image_field=cached_admin_thumb)
    image_preview = unfold_display(description=_("Image"))(image_preview)


django_admin.site.unregister(Group)
@django_admin.register(Group)
class GroupModelAdmin(GroupAdmin, UnfoldModelAdmin):
    """Custom Group model admin."""

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser
