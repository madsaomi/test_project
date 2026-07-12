from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import BaseSignupForm
from django import forms


class CustomSignupForm(BaseSignupForm):
    role = forms.ChoiceField(
        choices=(("student", "Я студент"), ("employer", "Я работодатель")),
        widget=forms.RadioSelect,
        label="Кто вы?",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].required = False

    def signup(self, request, user):
        user.role = self.cleaned_data["role"]
        user.username = user.email.split("@")[0]
        user.save()


class AccountAdapter(DefaultAccountAdapter):
    def get_signup_form_class(self, request):
        return CustomSignupForm

    def is_open_for_signup(self, request):
        return True
