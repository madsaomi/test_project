from django.urls import path
from . import views

urlpatterns = [
    path("vacancies/<uuid:pk>/apply/", views.ApplyToVacancyView.as_view(), name="apply_to_vacancy"),
    path("student/", views.StudentApplicationsView.as_view(), name="student_applications"),
    path(
        "employer/vacancies/<uuid:pk>/",
        views.VacancyApplicationsView.as_view(),
        name="employer_applications",
    ),
    path(
        "employer/application/<uuid:pk>/status/",
        views.UpdateApplicationStatusView.as_view(),
        name="update_application_status",
    ),
]
