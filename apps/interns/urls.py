from django.urls import path

from . import views

app_name = "interns"


urlpatterns = [
    path("dashboard/", views.intern_dashboard_view, name="dashboard"),
    path("internships/new/", views.internship_create_view, name="create_internship"),
    path(
        "internships/<uuid:internship_id>/",
        views.internship_detail_view,
        name="internship_detail",
    ),
    path(
        "internships/<uuid:internship_id>/update/",
        views.internship_update_view,
        name="update_internship",
    ),
    path(
        "internships/<uuid:internship_id>/delete/",
        views.internship_delete_view,
        name="delete_internship",
    ),
]
