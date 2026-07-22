from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Schema
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
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
    path("vacancies/<uuid:pk>/delete/", views.VacancyDeleteAV.as_view(), name="api_vacancy_delete"),
    path("vacancies/categories/", views.CategoryListAV.as_view(), name="api_categories"),
    # Profiles
    path("student/profile/", views.StudentProfileAV.as_view(), name="api_student_profile"),
    path("employer/profile/", views.EmployerProfileAV.as_view(), name="api_employer_profile"),
    # Applications
    path("applications/", views.CreateApplicationAV.as_view(), name="api_create_application"),
    path("applications/student/", views.StudentApplicationsAV.as_view(), name="api_student_applications"),
    path("applications/employer/", views.EmployerApplicationsAV.as_view(), name="api_employer_applications"),
    path("applications/<uuid:pk>/status/", views.UpdateApplicationStatusAV.as_view(), name="api_update_application_status"),
    path("applications/<uuid:pk>/delete/", views.ApplicationDeleteAV.as_view(), name="api_delete_application"),
]
