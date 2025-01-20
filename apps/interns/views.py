import json
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Internship, InternshipType, Departments
from .forms import InternshipForm
from .access_mixins import InternOnlyMixin
from .helpers import check_internship_overlap
from helpers.django.exceptions import capture
from helpers.django.response import shortcuts as response


class InternDashboardView(InternOnlyMixin, LoginRequiredMixin, generic.TemplateView):
    """View for the intern dashboard"""

    template_name = "interns/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["internships"] = Internship.objects.select_related(
            "account"
        ).filter(account=self.request.user)
        context_data["internship_types"] = InternshipType
        context_data["departments"] = Departments
        return context_data


class InternshipDetailView(InternOnlyMixin, LoginRequiredMixin, generic.DetailView):
    """View for the intern dashboard"""

    template_name = "interns/internship_detail.html"
    model = Internship
    context_object_name = "internship"
    pk_url_kwarg = "internship_id"

    def get_queryset(self):
        return Internship.objects.select_related("account").filter(
            account=self.request.user
        )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["internship_types"] = InternshipType
        context_data["departments"] = Departments
        return context_data


@capture.capture(content="Oops! An error occurred")
class InternshipCreateView(InternOnlyMixin, LoginRequiredMixin, generic.View):
    """View for creating an internship"""

    http_method_names = ["post"]
    form_class = InternshipForm

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        form = self.form_class(data)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form: InternshipForm):
        return response.validation_error(
            errors=form.errors,
            detail="An error occurred",
        )

    def form_valid(self, form: InternshipForm):
        internship = form.save(commit=False)
        overlap_exists = check_internship_overlap(
            account=self.request.user,
            start_date=internship.start_date,
            end_date=internship.end_date,
        )
        if overlap_exists:
            return response.validation_error(
                errors={
                    "start_date": "Internship period overlaps with an existing internship"
                },
                detail="An error occurred",
            )

        internship.account = self.request.user
        internship.save()
        return response.created(
            "Internship created", data={"redirect_url": reverse("interns:dashboard")}
        )


@capture.capture(content="Oops! An error occurred")
class InternshipUpdateView(InternOnlyMixin, LoginRequiredMixin, generic.View):
    """View for creating an internship"""

    http_method_names = ["post", "put", "patch"]
    form_class = InternshipForm

    def get_queryset(self):
        return Internship.objects.select_related("account").filter(
            account=self.request.user
        )

    def post(self, request, *args, **kwargs):
        internship = get_object_or_404(self.get_queryset(), pk=kwargs["internship_id"])
        data = json.loads(request.body)
        form = self.form_class(data, instance=internship)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form: InternshipForm):
        return response.validation_error(
            errors=form.errors,
            detail="An error occurred",
        )

    def form_valid(self, form: InternshipForm):
        internship = form.instance
        overlap_exists = check_internship_overlap(
            account=internship.account,
            start_date=internship.start_date,
            end_date=internship.end_date,
            exclude_pks=[internship.pk,],
        )
        if overlap_exists:
            return response.validation_error(
                errors={
                    "start_date": "Internship period overlaps with an existing internship"
                },
                detail="An error occurred",
            )

        form.save()
        return response.success(
            "Internship details updated",
            data={
                "redirect_url": reverse(
                    "interns:internship_detail",
                    kwargs={"internship_id": form.instance.pk},
                )
            },
        )


class InternshipDeleteView(InternOnlyMixin, LoginRequiredMixin, generic.View):
    """View for creating an internship"""

    http_method_names = ["get"]

    def get_queryset(self):
        return Internship.objects.select_related("account").filter(
            account=self.request.user
        )

    def get(self, request, *args, **kwargs):
        internship = get_object_or_404(self.get_queryset(), pk=kwargs["internship_id"])
        internship.delete()
        return redirect("interns:dashboard")


intern_dashboard_view = InternDashboardView.as_view()
internship_create_view = InternshipCreateView.as_view()
internship_detail_view = InternshipDetailView.as_view()
internship_update_view = InternshipUpdateView.as_view()
internship_delete_view = InternshipDeleteView.as_view()
