import csv
import datetime
import typing
import uuid
import openpyxl
from django.db import models
from django.http import HttpResponse

from .models import Internship, Departments, InternshipType
from apps.accounts.models import UserAccount
from helpers.generics.utils.datetime import display_timedelta


def _queryset_to_rows(qs: models.QuerySet[Internship]):
    """Yields data rows for a queryset of Interns."""
    yield (
        "Full Name",
        "Email",
        "Phone Number",
        "Alternative Phone Number",
        "Internship Type",
        "Department",
        "Intern Age",
        "Internship Start Date",
        "Internship Duration",
        "Internship End Date",
        "In Session",
    )

    for intern in qs.iterator(chunk_size=100):
        yield (
            intern.account.full_name,
            intern.account.email,
            str(intern.account.phone1.as_e164) if intern.account.phone1 else "",
            str(intern.account.phone2.as_e164) if intern.account.phone2 else "",
            str(InternshipType(intern.internship_type).label),
            str(Departments(intern.department).label),
            intern.account.age,
            intern.start_date,
            display_timedelta(intern.duration),
            intern.end_date,
            "YES" if intern.check_ongoing() else "NO",
        )


def queryset_to_csv_response(qs: models.QuerySet[Internship]):
    """Converts a queryset of interns to a downloadable CSV response."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="interns.csv"'

    writer = csv.writer(response)
    for row in _queryset_to_rows(qs):
        writer.writerow(row)
    return response


def queryset_to_xlsx_response(qs: models.QuerySet[Internship]):
    """Converts a queryset of interns to a downloadable XLSX response."""
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="interns.xlsx"'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    for row in _queryset_to_rows(qs):
        worksheet.append(row)

    workbook.save(response)
    return response


def check_internship_overlap(
    account: UserAccount,
    start_date: datetime.date,
    end_date: typing.Optional[datetime.date] = None,
    exclude_pks: typing.Optional[typing.List[uuid.UUID]] = None,
) -> bool:
    """Check if an internship overlaps with another internship."""
    queries = [
        models.Q(account=account),
        models.Q(end_date__gte=start_date),
    ]
    if end_date:
        queries.append(models.Q(start_date__lte=end_date))
    if exclude_pks:
        queries.append(~models.Q(pk__in=exclude_pks))

    internship_period_overlap = Internship.objects.select_related("account").filter(
        *queries
    )
    return internship_period_overlap.exists()
