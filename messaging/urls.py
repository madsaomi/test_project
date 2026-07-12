from django.urls import path
from . import views

urlpatterns = [
    path("", views.InboxView.as_view(), name="inbox"),
    path("<uuid:pk>/", views.ConversationView.as_view(), name="conversation"),
    path(
        "send/<uuid:application_pk>/",
        views.SendMessageView.as_view(),
        name="send_message",
    ),
]
