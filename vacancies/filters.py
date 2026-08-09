import django_filters
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import connection
from django.db.models import Q
from functools import reduce
from operator import or_

from .models import Vacancy


class VacancyFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search_filter", label="Поиск")
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    work_type = django_filters.ChoiceFilter(choices=Vacancy.WorkType.choices)
    city = django_filters.CharFilter(lookup_expr="icontains")
    salary_min = django_filters.CharFilter(
        field_name="salary", lookup_expr="icontains",
        label="Зарплата содержит",
    )

    class Meta:
        model = Vacancy
        fields = ["q", "category", "work_type", "city"]

    SEARCH_FIELDS = ("title", "description", "requirements", "conditions", "city")

    def search_filter(self, queryset, name, value):
        if connection.vendor == "postgresql":
            vector = SearchVector(*self.SEARCH_FIELDS)
            query = SearchQuery(value)
            return (
                queryset
                .annotate(search=vector, rank=SearchRank(vector, query))
                .filter(search=query)
                .order_by("-rank", "-created_at")
            )
        terms = [Q(**{f"{field}__icontains": value}) for field in self.SEARCH_FIELDS]
        return queryset.filter(reduce(or_, terms))
