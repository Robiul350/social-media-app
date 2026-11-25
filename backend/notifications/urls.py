
from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    MarkAllNotificationsReadView,
    NotificationUnreadCountView,
    NotificationPreferenceView,
)

urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list"
    ),
    path("preferences/", NotificationPreferenceView.as_view(), name="notification-preferences"),
    path(
        "read-all/",
        MarkAllNotificationsReadView.as_view(),
        name="notification-read-all"
    ),
    path(
        "unread-count/",
        NotificationUnreadCountView.as_view(),
        name="notification-unread-count"
    ),
    path(
        "<int:pk>/read/",
        NotificationReadView.as_view(),
        name="notification-read"
    ),
]
