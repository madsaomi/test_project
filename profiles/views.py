from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from .models import StudentProfile, EmployerProfile
from .forms import StudentProfileForm, EmployerProfileForm
from applications.models import Application


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        applications = Application.objects.filter(student=profile).select_related("vacancy")
        context.update({
            "profile": profile,
            "applications": applications,
            "total_applications": applications.count(),
            "viewed_applications": applications.filter(status="viewed").count(),
            "invited_applications": applications.filter(status="invited").count(),
        })
        return context


class StudentProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = "profiles/student_profile_form.html"
    success_url = reverse_lazy("student_dashboard")

    def get_object(self, queryset=None):
        obj, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

    def form_valid(self, form):
        user = self.request.user
        user.first_name = self.request.POST.get("first_name", "")
        user.last_name = self.request.POST.get("last_name", "")
        user.save()
        messages.success(self.request, "Профиль сохранён")
        return super().form_valid(form)


class EmployerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/employer_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        vacancies = profile.vacancies.annotate(
            app_count=Count("applications"),
        )
        total_applications = sum(v.app_count for v in vacancies)
        recent_applications = Application.objects.filter(
            vacancy__employer=profile, status="sent"
        ).count()
        context.update({
            "profile": profile,
            "vacancies": vacancies,
            "total_vacancies": vacancies.count(),
            "total_applications": total_applications,
            "new_applications_today": recent_applications,
        })
        return context


class EmployerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployerProfile
    form_class = EmployerProfileForm
    template_name = "profiles/employer_profile_form.html"
    success_url = reverse_lazy("employer_dashboard")

    def get_object(self, queryset=None):
        obj, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Профиль сохранён")
        return super().form_valid(form)
