import datetime
import typing
from django.contrib import admin as django_admin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from imagekit.admin import AdminThumbnail
from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from imagekit.cachefiles import ImageCacheFile
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import action as unfold_action, display as unfold_display

from .models import Internship
from .helpers import queryset_to_csv_response, queryset_to_xlsx_response


class InSessionFilter(django_admin.SimpleListFilter):
    """Custom filter for interns in session."""

    title = "in session"
    parameter_name = "in_session"

    def lookups(self, request, model_admin: django_admin.ModelAdmin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset: models.QuerySet[Internship]):
        if self.value() == "yes":
            return queryset.ongoing()
        if self.value() == "no":
            return queryset.completed()


class DateFieldListFilter(django_admin.DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        self.links = (
            *self.links,
            *self.custom_links(),
        )

    def custom_links(self):
        """
        Add custom date filters like Past Month, Past 2 Weeks, etc.
        """
        today = timezone.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        return [
            (
                _("Past Month"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=30),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past 2 Weeks"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=14),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past 3 Months"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=90),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past 6 Months"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=180),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past Year"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=365),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
        ]


def generate_search_help_text(search_fields: list[str]) -> str:
    """Generate search help text."""
    fields = [
        field.split("__")[-1].replace("_", " ").lower() for field in search_fields
    ]
    return f"Search by {', '.join(fields[:-1])} or {fields[-1]}"


class AdminThumbnailSpec(ImageSpec):
    # processors = [ResizeToFill(100, 100)]
    format = "JPEG"
    options = {"quality": 60}


def cached_admin_thumb(instance: Internship):
    if not instance.image:
        return None

    cached = ImageCacheFile(AdminThumbnailSpec(instance.image))
    # only generates the first time, subsequent calls use cache
    cached.generate()
    return cached


@django_admin.register(Internship)
class InternshipModelAdmin(UnfoldModelAdmin):
    """Custom Internship model admin."""

    list_display = [
        "image_preview",
        "__str__",
        "internship_type",
        "in_session",
        "department",
        "age",
        "start_date",
        "end_date",
        "duration",
    ]
    list_display_links = ["__str__"]
    list_editable = [
        "internship_type",
        "department",
        "start_date",
        "end_date",
    ]
    list_filter = [
        "department",
        "internship_type",
        InSessionFilter,
        ("start_date", DateFieldListFilter),
        ("end_date", DateFieldListFilter),
    ]
    search_fields = [
        "account__first_name",
        "account__last_name",
        "account__email",
        "account__phone1",
        "account__phone2",
        "internship_type",
        "department",
    ]
    search_help_text = generate_search_help_text(search_fields)
    save_as = False
    save_as_continue = True
    save_on_top = False
    list_per_page = 200
    list_max_show_all = 1000
    actions_on_top = True
    actions = [
        "end_internship",
        "download_as_csv",
        "download_as_xlsx",
    ]
    date_hierarchy = "start_date"
    ordering = [
        "start_date",
        "account__first_name",
    ]
    readonly_fields = []

    def get_queryset(self, request):
        # Returns annotated queryset with `ongoing` fields
        return super().get_queryset(request).select_related("account").with_ongoing()

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj: Internship = None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_admin

    def has_change_permission(self, request, obj: Internship = None):
        return request.user.is_admin

    def has_delete_permission(self, request, obj: Internship = None):
        return request.user.is_admin

    #################
    # CUSTOM FIELDS #
    #################
    image_preview = AdminThumbnail(image_field=cached_admin_thumb)
    image_preview = unfold_display(description=_("Intern Image"))(image_preview)

    
    @unfold_display(boolean=True, description="In Session", ordering="ongoing")
    def in_session(self, obj: Internship) -> bool:
        return obj.check_ongoing()

    @unfold_display(description="Intern Age", ordering="account__date_of_birth")
    def age(self, obj: Internship) -> typing.Optional[int]:
        return obj.account.age

    ########################
    # CUSTOM ADMIN ACTIONS #
    ########################

    @unfold_action(description=_("End selected internships"))
    def end_internship(self, request, queryset: models.QuerySet[Internship]):
        """End selected internships"""
        queryset.update(end_date=timezone.now().date())

    @unfold_action(
        description=_("Download selected interns as a CSV file"),
        attrs={"target": "_blank"},
    )
    def download_as_csv(self, request, queryset: models.QuerySet[Internship]):
        """Download selected interns as CSV file"""
        return queryset_to_csv_response(queryset)

    @unfold_action(
        description=_("Download selected interns as an Excel file"),
        attrs={"target": "_blank"},
    )
    def download_as_xlsx(self, request, queryset: models.QuerySet[Internship]):
        """Download selected interns as Excel file"""
        return queryset_to_xlsx_response(queryset)
