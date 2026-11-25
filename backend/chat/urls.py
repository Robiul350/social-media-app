
from django.urls import path
from .views import (
    ConversationView,
    MarkConversationReadView,
    UnreadMessageCountView,
    ConversationListView,
    GroupConversationView,
    GroupMessageView,
    MessageDetailView,
)

urlpatterns = [
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message-detail"),
    path("groups/", GroupConversationView.as_view(), name="group-list-create"),
    path("groups/<int:group_id>/messages/", GroupMessageView.as_view(), name="group-message-list-create"),
    path(
        "conversations/<int:user_id>/",
        ConversationView.as_view(),
        name="conversation"
    ),
    path(
        "conversations/<int:user_id>/read/",
        MarkConversationReadView.as_view(),
        name="conversation-read"
    ),
    path(
        "unread-count/",
        UnreadMessageCountView.as_view(),
        name="unread-message-count"
    ),
    path(
        "conversations/",
        ConversationListView.as_view(),
        name="conversation-list"
    ),
]
