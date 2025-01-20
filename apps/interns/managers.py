from django.db import models
from django.utils import timezone


class InternshipQuerySet(models.QuerySet):
    def with_expected_end_date(self):
        """
        Return annotated queryset with new field `expected_end_date`
        indicating the expected end date of an internship calculated
        from `start_date` and `duration`
        """
        return self.annotate(
            expected_end_date=models.ExpressionWrapper(
                models.F("start_date") + models.F("duration"),
                output_field=models.DateField(),
            )
        )

    def with_ongoing(self):
        """
        Return annotated queryset with new field `ongoing`
        indicating if an intern's internship is still ongoing or not
        """
        return self.with_expected_end_date().annotate(
            ongoing=models.Case(
                models.When(
                    models.Q(end_date__isnull=True)
                    | models.Q(expected_end_date__gt=timezone.now().date()),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(),
            )
        )

    def ongoing(self):
        """Return only interns with ongoing internships"""
        return self.with_ongoing().filter(ongoing=True)

    def completed(self):
        """Return only interns with completed internships"""
        return self.with_ongoing().filter(ongoing=False)


class InternshipManager(models.Manager.from_queryset(InternshipQuerySet)):
    pass
