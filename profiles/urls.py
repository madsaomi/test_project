from django.urls import path
from . import views

urlpatterns = [
    path("student/", views.StudentDashboardView.as_view(), name="student_dashboard"),
    path("student/profile/", views.StudentProfileUpdateView.as_view(), name="student_profile_update"),
    path("employer/", views.EmployerDashboardView.as_view(), name="employer_dashboard"),
    path("employer/profile/", views.EmployerProfileUpdateView.as_view(), name="employer_profile_update"),
]
