from django.urls import path

from .views import (
    PostListCreateView,
    PostDetailView,
    BookmarkToggleView,
    PinToggleView,
    RepostView,
    PollVoteView,
    PostReportView,
)


urlpatterns = [

    path(
        "",
        PostListCreateView.as_view(),
        name="post-list-create"
    ),

    path("<int:pk>/bookmark/", BookmarkToggleView.as_view(), name="post-bookmark"),
    path("<int:pk>/pin/", PinToggleView.as_view(), name="post-pin"),
    path("<int:pk>/repost/", RepostView.as_view(), name="post-repost"),
    path("<int:pk>/report/", PostReportView.as_view(), name="post-report"),
    path("<int:pk>/poll/<int:option_id>/vote/", PollVoteView.as_view(), name="poll-vote"),
    path(
        "<int:pk>/",
        PostDetailView.as_view(),
        name="post-detail"
    ),
]