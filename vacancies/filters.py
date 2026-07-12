import django_filters
from .models import Vacancy


class VacancyFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search_filter", label="Поиск")
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    work_type = django_filters.ChoiceFilter(choices=Vacancy.WorkType.choices)
    city = django_filters.CharFilter(lookup_expr="icontains")
    salary_min = django_filters.NumberFilter(field_name="salary", lookup_expr="icontains")

    class Meta:
        model = Vacancy
        fields = ["q", "category", "work_type", "city"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(title__icontains=value)
