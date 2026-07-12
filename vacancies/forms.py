from django import forms
from .models import Vacancy


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            "title", "description", "requirements", "conditions",
            "salary", "city", "work_type", "category", "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "conditions": forms.Textarea(attrs={"rows": 4}),
        }
