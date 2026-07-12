from django.contrib import admin
from .models import StudentProfile, EmployerProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "created_at")
    search_fields = ("user__email", "city")


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "website")
    search_fields = ("company_name", "user__email")
