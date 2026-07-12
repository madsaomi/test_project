from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class DashboardRedirectView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard_redirect.html"

    def get(self, request, *args, **kwargs):
        if request.user.role == "student":
            return redirect("student_dashboard")
        return redirect("employer_dashboard")
