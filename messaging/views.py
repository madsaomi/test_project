from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages as django_messages
from django.http import Http404
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
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            ),
            last_message_text=Count("messages"),
        ).select_related(
            "application", "application__vacancy",
            "application__student__user",
            "application__vacancy__employer",
            "application__vacancy__employer__user",
        ).prefetch_related(
            "messages",
        ).order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unread_count"] = sum(
            c.unread_count for c in context["conversations"]
        )
        return context


class ConversationView(LoginRequiredMixin, DetailView):
    template_name = "messaging/conversation.html"
    queryset = Conversation.objects.select_related(
        "application__vacancy__employer__user",
        "application__student__user",
    )

    def get_object(self, queryset=None):
        conv = super().get_object(queryset)
        user = self.request.user
        can_access = (
            conv.application.vacancy.employer.user == user or
            conv.application.student.user == user
        )
        if not can_access:
            raise Http404()
        return conv

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conv = self.object
        conv.messages.select_related("sender").filter(
            ~Q(sender=self.request.user), is_read=False
        ).update(is_read=True)
        context["messages_list"] = conv.messages.select_related("sender").all()
        return context


class SendMessageView(LoginRequiredMixin, View):
    def get(self, request, application_pk):
        application = get_object_or_404(
            Application, pk=application_pk,
            Q(vacancy__employer__user=request.user) | Q(student__user=request.user),
        )
        conversation, _ = Conversation.objects.get_or_create(application=application)
        return redirect("conversation", pk=conversation.pk)

    def post(self, request, application_pk):
        application = get_object_or_404(
            Application, pk=application_pk,
            Q(vacancy__employer__user=request.user) | Q(student__user=request.user),
        )

        text = request.POST.get("text", "").strip()
        if not text:
            django_messages.error(request, "Сообщение не может быть пустым")
            return redirect("conversation", pk=Conversation.objects.get(application=application).pk)

        conversation, _ = Conversation.objects.get_or_create(application=application)
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text[:5000],
        )
        return redirect("conversation", pk=conversation.pk)
