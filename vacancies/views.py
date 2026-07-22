from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Vacancy, Category
from .filters import VacancyFilter
from .forms import VacancyForm
from profiles.models import EmployerProfile, StudentProfile
from applications.models import Application
from applications.forms import ApplicationForm


class HomeView(ListView):
    template_name = "vacancies/home.html"
    context_object_name = "latest_vacancies"

    def get_queryset(self):
        return Vacancy.objects.filter(is_active=True).select_related(
            "employer", "category", "employer__user"
        )[:8]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["popular_categories"] = Category.objects.annotate(
            vacancy_count=models.Count("vacancies", filter=models.Q(vacancies__is_active=True))
        ).order_by("-vacancy_count")[:6]
        return context


class VacancyListView(ListView):
    template_name = "vacancies/vacancy_list.html"
    context_object_name = "vacancies"
    paginate_by = 12

    def get_queryset(self):
        qs = Vacancy.objects.filter(is_active=True).select_related(
            "employer", "category", "employer__user"
        )
        self.filterset = VacancyFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        context["categories"] = Category.objects.all()
        context["work_types"] = Vacancy.WorkType.choices
        return context


class VacancyDetailView(DetailView):
    template_name = "vacancies/vacancy_detail.html"
    context_object_name = "vacancy"
    queryset = Vacancy.objects.filter(is_active=True).select_related(
        "employer", "category", "employer__user"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancy = self.object
        session_key = f"viewed_vacancy_{vacancy.pk}"
        if not self.request.session.get(session_key, False):
            Vacancy.objects.filter(pk=vacancy.pk).update(views_count=models.F("views_count") + 1)
            self.request.session[session_key] = True
        if self.request.user.is_authenticated and self.request.user.role == "student":
            profile = get_object_or_404(StudentProfile, user=self.request.user)
            already_applied = Application.objects.filter(
                vacancy=vacancy, student=profile
            ).exists()
            context["form"] = ApplicationForm()
            context["already_applied"] = already_applied
        return context


class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = "vacancies/vacancy_form.html"
    success_url = reverse_lazy("employer_dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "employer":
            messages.error(request, "Только работодатели могут создавать вакансии")
            from django.shortcuts import redirect
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        form.instance.employer = profile
        messages.success(self.request, "Вакансия опубликована")
        return super().form_valid(form)


class VacancyUpdateView(LoginRequiredMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = "vacancies/vacancy_form.html"
    success_url = reverse_lazy("employer_dashboard")

    def get_queryset(self):
        return Vacancy.objects.filter(employer__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Вакансия обновлена")
        return super().form_valid(form)
