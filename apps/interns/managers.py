from django.db import models
from django.utils import timezone


class InternshipQuerySet(models.QuerySet):
    def with_ongoing(self):
        """
        Return annotated queryset with new field `ongoing`
        indicating if an intern's internship is still ongoing or not
        """
        return self.annotate(
            ongoing=models.Case(
                models.When(
                    end_date__gte=timezone.now().date(),
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
