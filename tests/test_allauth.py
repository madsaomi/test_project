import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from allauth.account.models import EmailAddress


@pytest.mark.django_db
class TestAllauthSignup:
    def test_signup_creates_user_without_email_verification(self, client):
        url = reverse("account_signup")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "role": "student",
            },
        )
        assert response.status_code == 302
        # Верификация email отключена (ACCOUNT_EMAIL_VERIFICATION = "none"):
        # подтверждающее письмо не отправляется, вход разрешён без подтверждения
        assert EmailAddress.objects.filter(email="newuser@example.com").exists()

        # Пользователь создан и может войти сразу
        login_url = reverse("account_login")
        login_response = client.post(
            login_url,
            {"login": "newuser@example.com", "password": "StrongPass123!"},
        )
        assert login_response.status_code == 302

    def test_signup_password_mismatch_fails(self, client):
        url = reverse("account_signup")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "DifferentPass123!",
                "role": "student",
            },
        )
        assert response.status_code == 200
        assert not EmailAddress.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
class TestAllauthEmailConfirmation:
    @pytest.fixture
    def unverified_user(self, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            email="confirm@example.com",
            password="StrongPass123!",
            role="student",
        )
        EmailAddress.objects.create(
            user=user, email="confirm@example.com", verified=False, primary=True
        )
        return user

    def test_unverified_email_shows_unverified(self, unverified_user):
        email_obj = EmailAddress.objects.get(email="confirm@example.com")
        assert email_obj.verified is False

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_send_confirmation_email(self, client, unverified_user):
        from allauth.account.adapter import get_adapter
        from allauth.account.models import EmailConfirmation

        adapter = get_adapter()
        email_obj = EmailAddress.objects.get(email="confirm@example.com")
        key = adapter.generate_emailconfirmation_key(email_obj.email)
        confirmation = EmailConfirmation.objects.create(email_address=email_obj, key=key)
        assert len(confirmation.key) > 0
        assert EmailConfirmation.objects.filter(email_address=email_obj).exists()


@pytest.mark.django_db
class TestAllauthLogin:
    @pytest.fixture
    def verified_user(self, db):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            email="login@example.com",
            password="StrongPass123!",
            role="student",
        )
        EmailAddress.objects.create(
            user=user, email="login@example.com", verified=True, primary=True
        )
        return user

    def test_login_with_valid_credentials(self, client, verified_user):
        url = reverse("account_login")
        response = client.post(
            url,
            {"login": "login@example.com", "password": "StrongPass123!"},
        )
        assert response.status_code == 302

    def test_login_with_wrong_password(self, client, verified_user):
        url = reverse("account_login")
        response = client.post(
            url,
            {"login": "login@example.com", "password": "WrongPass123!"},
        )
        assert response.status_code == 200
