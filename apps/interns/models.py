import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from uuid_extensions import uuid7
from django.core.exceptions import ValidationError

from .managers import InternshipManager


class InternshipType(models.TextChoices):
    """Choices for internship types"""

    INDUSTRIAL_TRAINING = "industrial_training", _("Industrial Training")
    NYSC = "nysc", _("NYSC")
    VOLUNTEERING = "volunteering", _("Volunteering")


class Departments(models.TextChoices):
    """Choices for departments in MEMR"""

    OIL_AND_GAS = "oil_and_gas", _("Oil and Gas Department")
    SOLID_MINERALS = "solid_minerals", _("Solid Minerals Department")
    GEOLOGICAL_SERVICES = "geological_services", _("Geological Services Department")
    POWER = "power", _("Power Department")
    PROCUREMENT = "procurement", _("Procurement Department")
    ADMIN_HR = "admin_hr", _("Admin and HR")
    ACCOUNTS = "accounts", _("Accounts Department")
    PUBLIC_RELATIONS = "public_relations", _("Public Relations Unit")
    PS_OFFICE = "ps_office", _("Permanent Secretary's Office")
    DREDGING_UNIT = "dredging_unit", _("Dredging Unit")


class Internship(models.Model):
    """Model representing an intern"""

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="internships",
        db_index=True,
    )
    internship_type = models.CharField(
        max_length=120,
        db_index=True,
        choices=InternshipType.choices,
    )
    department = models.CharField(
        max_length=120, db_index=True, choices=Departments.choices
    )
    start_date = models.DateField(db_index=True, blank=False, null=False)
    end_date = models.DateField(
        db_index=True, blank=False, null=False, default=timezone.now
    )

    objects = InternshipManager()

    class Meta:
        verbose_name = "Internship"
        verbose_name_plural = "Internships"
        ordering = ["start_date"]

    def __str__(self) -> str:
        return f"{self.account.full_name} - {InternshipType(self.internship_type).label} @ {Departments(self.department).label}"

    @property
    def display_label(self) -> str:
        return f"{InternshipType(self.internship_type).label} @ {Departments(self.department).label}"

    @property
    def image(self):
        return self.account.image

    @property
    def duration(self):
        return (self.end_date - self.start_date) or datetime.timedelta(days=1)

    def check_ongoing(self) -> bool:
        """
        Check if the intern's internship is still ongoing.

        An internship is considered to be ongoing if it has no end date or
        if the expected end date has not been reached.
        """
        if hasattr(self, "ongoing"):
            return self.ongoing

        today = timezone.now().date()
        return self.end_date >= today

    def end_internship(self) -> None:
        """End internship"""
        self.end_date = timezone.now().date()
        self.save(update_fields=["end_date"])

    def save(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be greater than start date.")
        super().save(*args, **kwargs)
