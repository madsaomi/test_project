from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.DashboardRedirectView.as_view(), name="dashboard_redirect"),
]
