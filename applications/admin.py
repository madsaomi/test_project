from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("vacancy", "student", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("vacancy__title", "student__user__email")
