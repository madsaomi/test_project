from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("vacancies/", views.VacancyListView.as_view(), name="vacancy_list"),
    path("vacancies/<uuid:pk>/", views.VacancyDetailView.as_view(), name="vacancy_detail"),
    path(
        "dashboard/employer/vacancies/new/",
        views.VacancyCreateView.as_view(),
        name="vacancy_create",
    ),
    path(
        "dashboard/employer/vacancies/<uuid:pk>/edit/",
        views.VacancyUpdateView.as_view(),
        name="vacancy_update",
    ),
]
