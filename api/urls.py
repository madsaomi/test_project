from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="api_register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="api_token_refresh"),
    path("auth/me/", views.MeView.as_view(), name="api_me"),
    # Vacancies
    path("vacancies/", views.VacancyListAV.as_view(), name="api_vacancy_list"),
    path("vacancies/<uuid:pk>/", views.VacancyDetailAV.as_view(), name="api_vacancy_detail"),
    path("vacancies/create/", views.VacancyCreateAV.as_view(), name="api_vacancy_create"),
    path("vacancies/<uuid:pk>/update/", views.VacancyUpdateAV.as_view(), name="api_vacancy_update"),
    path("vacancies/categories/", views.CategoryListAV.as_view(), name="api_categories"),
    # Profiles
    path("student/profile/", views.StudentProfileAV.as_view(), name="api_student_profile"),
    path("employer/profile/", views.EmployerProfileAV.as_view(), name="api_employer_profile"),
    # Applications
    path("applications/", views.CreateApplicationAV.as_view(), name="api_create_application"),
    path("applications/student/", views.StudentApplicationsAV.as_view(), name="api_student_applications"),
    path("applications/employer/", views.EmployerApplicationsAV.as_view(), name="api_employer_applications"),
    path("applications/<uuid:pk>/status/", views.UpdateApplicationStatusAV.as_view(), name="api_update_application_status"),
]
