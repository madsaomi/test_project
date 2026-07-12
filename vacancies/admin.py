from django.contrib import admin
from .models import Category, Vacancy


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "category", "city", "is_active", "created_at")
    list_filter = ("is_active", "work_type", "category")
    search_fields = ("title", "description")
