from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db import IntegrityError
from django.views import View
from .models import Application
from .forms import ApplicationForm
from vacancies.models import Vacancy
from profiles.models import StudentProfile


class ApplyToVacancyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != "student":
            messages.error(request, "Только студенты могут откликаться")
            return redirect("dashboard_redirect")

        vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
        student = get_object_or_404(StudentProfile, user=request.user)
        form = ApplicationForm(request.POST)

        if form.is_valid():
            try:
                Application.objects.create(
                    vacancy=vacancy,
                    student=student,
                    cover_letter=form.cleaned_data["cover_letter"],
                )
                messages.success(request, "Отклик отправлен!")
            except IntegrityError:
                messages.warning(request, "Вы уже откликались на эту вакансию")
        else:
            messages.error(request, "Ошибка в форме")

        return redirect("vacancy_detail", pk=pk)


class StudentApplicationsView(LoginRequiredMixin, ListView):
    template_name = "applications/student_applications.html"
    context_object_name = "applications"

    def get_queryset(self):
        profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Application.objects.filter(student=profile).select_related(
            "vacancy", "vacancy__employer", "vacancy__employer__user"
        )


class UpdateApplicationStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(
            Application, pk=pk, vacancy__employer__user=request.user
        )

        new_status = request.POST.get("status")
        if new_status in dict(Application.Status.choices):
            application.status = new_status
            application.save(update_fields=["status"])
            messages.success(request, f"Статус изменён на {application.get_status_display()}")

        return redirect("employer_applications", pk=application.vacancy.pk)


class VacancyApplicationsView(LoginRequiredMixin, ListView):
    template_name = "applications/vacancy_applications.html"
    context_object_name = "applications"

    def get_queryset(self):
        self.vacancy = get_object_or_404(
            Vacancy, pk=self.kwargs["pk"], employer__user=self.request.user
        )
        return Application.objects.filter(vacancy=self.vacancy).select_related(
            "student", "student__user"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vacancy"] = self.vacancy
        return context
