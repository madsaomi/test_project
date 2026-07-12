from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("cover_letter",)
        widgets = {
            "cover_letter": forms.Textarea(attrs={"rows": 4, "placeholder": "Расскажите, почему вы подходите на эту позицию..."}),
        }
