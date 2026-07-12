from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages as django_messages
from django.urls import reverse
from django.db.models import Q, Count
from .models import Conversation, Message
from applications.models import Application


class InboxView(LoginRequiredMixin, ListView):
    template_name = "messaging/inbox.html"
    context_object_name = "conversations"

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            Q(application__vacancy__employer__user=user) |
            Q(application__student__user=user)
        ).annotate(
            unread=Count("messages", filter=Q(messages__is_read=False, messages__sender=user)),
        ).select_related(
            "application", "application__vacancy",
            "application__student__user",
            "application__vacancy__employer",
        ).order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unread = 0
        for c in context["conversations"]:
            if c.messages.filter(is_read=False).exclude(sender=self.request.user).exists():
                unread += 1
        context["unread_count"] = unread
        return context


class ConversationView(LoginRequiredMixin, DetailView):
    template_name = "messaging/conversation.html"
    model = Conversation

    def get_object(self, queryset=None):
        conv = super().get_object(queryset)
        user = self.request.user
        can_access = (
            conv.application.vacancy.employer.user == user or
            conv.application.student.user == user
        )
        if not can_access:
            from django.http import Http404
            raise Http404()
        return conv

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conv = self.object
        conv.messages.filter(~Q(sender=self.request.user), is_read=False).update(is_read=True)
        return context


class SendMessageView(LoginRequiredMixin, View):
    def get(self, request, application_pk):
        application = get_object_or_404(Application, pk=application_pk)
        user = request.user
        can_message = (
            application.vacancy.employer.user == user or
            application.student.user == user
        )
        if not can_message:
            django_messages.error(request, "Доступ запрещён")
            return redirect("dashboard_redirect")
        conversation, _ = Conversation.objects.get_or_create(application=application)
        return redirect("conversation", pk=conversation.pk)

    def post(self, request, application_pk):
        application = get_object_or_404(Application, pk=application_pk)
        user = request.user
        can_message = (
            application.vacancy.employer.user == user or
            application.student.user == user
        )
        if not can_message:
            django_messages.error(request, "Доступ запрещён")
            return redirect("dashboard_redirect")

        text = request.POST.get("text", "").strip()
        if not text:
            django_messages.error(request, "Сообщение не может быть пустым")
            return redirect("employer_applications", pk=application.vacancy.pk)

        conversation, _ = Conversation.objects.get_or_create(application=application)
        Message.objects.create(
            conversation=conversation,
            sender=user,
            text=text,
        )
        return redirect("conversation", pk=conversation.pk)
