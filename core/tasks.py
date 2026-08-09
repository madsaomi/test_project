from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_new_application_email(application_id, employer_email, applications_url):
    from applications.models import Application

    application = Application.objects.select_related(
        "vacancy", "student__user"
    ).get(pk=application_id)
    subject = f"Новый отклик на вакансию «{application.vacancy.title}»"
    message = (
        f"Студент {application.student.user.email} откликнулся на вакансию "
        f"«{application.vacancy.title}».\n\n"
        f"Сопроводительное письмо:\n{application.cover_letter}\n\n"
        f"Просмотреть отклики: {applications_url}"
    )
    send_mail(
        subject,
        message,
        None,
        [employer_email],
        fail_silently=False,
    )


@shared_task
def send_new_message_email(message_id, recipient_email, conversation_url):
    from messaging.models import Message

    message = Message.objects.select_related("conversation__application__vacancy", "sender").get(
        pk=message_id
    )
    subject = f"Новое сообщение: {message.conversation.application.vacancy.title}"
    body = (
        f"{message.sender.email} написал вам:\n\n"
        f"{message.text}\n\n"
        f"Ответить: {conversation_url}"
    )
    send_mail(
        subject,
        body,
        None,
        [recipient_email],
        fail_silently=False,
    )
