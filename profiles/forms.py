from django import forms
from .models import StudentProfile, EmployerProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = (
            "city", "desired_position", "resume_text", "skills",
            "education", "experience", "languages",
            "telegram", "linkedin", "github", "portfolio",
        )

    def clean_skills(self):
        value = self.cleaned_data.get("skills")
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        return value or []


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ("company_name", "company_description", "company_logo", "website")
