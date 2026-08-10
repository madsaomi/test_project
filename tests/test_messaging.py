import pytest
from django.urls import reverse

from messaging.models import Conversation, Message


@pytest.mark.django_db
class TestConversationModel:
    def test_str(self, application):
        conversation = Conversation.objects.create(application=application)
        assert conversation.application.vacancy.title in str(conversation)

    def test_message_str(self, application, employer_user):
        conversation = Conversation.objects.create(application=application)
        message = Message.objects.create(
            conversation=conversation,
            sender=employer_user,
            text="Приглашаем на собеседование",
        )
        assert str(message) == f"{employer_user.email}: Приглашаем на собеседование"


@pytest.mark.django_db
class TestInboxView:
    def test_login_required(self, api_client, application):
        response = api_client.get(reverse("inbox"))
        assert response.status_code in (302, 200)
        assert "login" in response.url

    def test_student_sees_conversation(self, api_client, student_user, application):
        api_client.force_login(user=student_user)
        application.conversations.create()
        response = api_client.get(reverse("inbox"))
        assert response.context["conversations"].count() == 1

    def test_unrelated_user_sees_nothing(self, api_client, student_user, vacancy):
        api_client.force_login(user=student_user)
        response = api_client.get(reverse("inbox"))
        assert response.context["conversations"].count() == 0

    def test_unread_count(self, api_client, student_user, application, employer_user):
        conversation = application.conversations.create()
        conversation.messages.create(sender=employer_user, text="Привет")
        api_client.force_login(user=student_user)
        response = api_client.get(reverse("inbox"))
        conversation = response.context["conversations"].get()
        assert conversation.unread_count == 1
        assert response.context["unread_count"] == 1


@pytest.mark.django_db
class TestConversationView:
    def test_participant_marks_messages_read(
        self, api_client, student_user, application, employer_user
    ):
        conversation = application.conversations.create()
        message = conversation.messages.create(sender=employer_user, text="Привет")
        assert message.is_read is False
        api_client.force_login(user=student_user)
        response = api_client.get(reverse("conversation", kwargs={"pk": conversation.pk}))
        assert response.status_code == 200
        message.refresh_from_db()
        assert message.is_read is True

    def test_non_participant_404(self, api_client, application, student_user):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        outsider = User.objects.create_user(
            email="outsider@example.com",
            password="testpass123",
            role="student",
        )
        conversation = application.conversations.create()
        api_client.force_login(user=outsider)
        response = api_client.get(reverse("conversation", kwargs={"pk": conversation.pk}))
        assert response.status_code == 404

    def test_own_message_not_marked_read(
        self, api_client, student_user, application
    ):
        conversation = application.conversations.create()
        message = conversation.messages.create(sender=student_user, text="Я согласен")
        api_client.force_login(user=student_user)
        api_client.get(reverse("conversation", kwargs={"pk": conversation.pk}))
        message.refresh_from_db()
        assert message.is_read is False


@pytest.mark.django_db
class TestSendMessageView:
    def test_get_creates_conversation(self, api_client, student_user, application):
        api_client.force_login(user=student_user)
        response = api_client.get(
            reverse("send_message", kwargs={"application_pk": application.pk})
        )
        assert response.status_code == 302
        assert response.url == reverse(
            "conversation", kwargs={"pk": application.conversations.get().pk}
        )

    def test_post_creates_message(self, api_client, student_user, application):
        api_client.force_login(user=student_user)
        response = api_client.post(
            reverse("send_message", kwargs={"application_pk": application.pk}),
            {"text": "Здравствуйте"},
        )
        assert response.status_code == 302
        message = Message.objects.get(conversation=application.conversations.get())
        assert message.text == "Здравствуйте"
        assert message.sender == student_user

    def test_empty_message_not_created(self, api_client, student_user, application):
        api_client.force_login(user=student_user)
        response = api_client.post(
            reverse("send_message", kwargs={"application_pk": application.pk}),
            {"text": "   "},
        )
        assert response.status_code == 302
        assert not Message.objects.filter(conversation__application=application).exists()

    def test_login_required(self, api_client, application):
        response = api_client.get(
            reverse("send_message", kwargs={"application_pk": application.pk})
        )
        assert response.status_code in (302, 200)
        assert "login" in response.url