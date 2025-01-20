from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path("", RedirectView.as_view(url="interns/dashboard/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("interns/", include("apps.interns.urls", namespace="interns")),
]

admin.site.site_header = f"{settings.APPLICATION_NAME}"
admin.site.site_title = f"{settings.APPLICATION_NAME}"
admin.site.index_title = f"{settings.APPLICATION_NAME}"
