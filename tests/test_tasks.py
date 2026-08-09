import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from core.tasks import send_new_application_email, send_new_message_email


EMAIL_BACKEND = override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)


@pytest.mark.django_db
class TestNewApplicationEmail:
    def test_task_sends_email_to_employer(self, vacancy, student_profile):
        application = vacancy.applications.create(
            student=student_profile,
            cover_letter="Хочу стажироваться",
        )
        with EMAIL_BACKEND:
            send_new_application_email(
                application.pk,
                vacancy.employer.user.email,
                "https://example.com/employer/vacancies/1/",
            )
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [vacancy.employer.user.email]
        assert vacancy.title in email.subject
        assert "Хочу стажироваться" in email.body

    def test_apply_view_sends_email(self, api_client, student_user, student_profile, vacancy):
        api_client.force_login(user=student_user)
        with EMAIL_BACKEND:
            response = api_client.post(
                reverse("apply_to_vacancy", kwargs={"pk": vacancy.pk}),
                {"cover_letter": "Интересуюсь позицией"},
            )
        assert response.status_code == 302
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [vacancy.employer.user.email]


@pytest.mark.django_db
class TestNewMessageEmail:
    def test_task_sends_email_to_recipient(self, application, employer_user):
        conversation = application.conversations.create()
        message = conversation.messages.create(
            sender=employer_user,
            text="Приглашаем на собеседование",
        )
        with EMAIL_BACKEND:
            send_new_message_email(
                message.pk,
                application.student.user.email,
                "https://example.com/messages/1/",
            )
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to == [application.student.user.email]
        assert "Приглашаем на собеседование" in email.body

    def test_send_message_view_sends_email_to_other_party(
        self, api_client, student_user, application
    ):
        api_client.force_login(user=student_user)
        with EMAIL_BACKEND:
            response = api_client.post(
                reverse("send_message", kwargs={"application_pk": application.pk}),
                {"text": "Здравствуйте!"},
            )
        assert response.status_code == 302
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [application.vacancy.employer.user.email]
