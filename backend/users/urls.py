
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    UserSearchView,
    PublicProfileView,
    UserPostsView,
    ChangePasswordView,
    DeactivateAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    StoryListCreateView,
    StoryViewView,
    StoryReactionView,
    StoryReactionListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),

    path("login/", LoginView.as_view(), name="login"),
    path("password/change/", ChangePasswordView.as_view(), name="password-change"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("account/deactivate/", DeactivateAccountView.as_view(), name="account-deactivate"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    path("profile/", ProfileView.as_view(), name="profile"),

    path("search/", UserSearchView.as_view(), name="user-search"),
    path("stories/", StoryListCreateView.as_view(), name="story-list-create"),
    path("stories/<int:pk>/view/", StoryViewView.as_view(), name="story-view"),
    path(
        "stories/<int:pk>/react/",
        StoryReactionView.as_view(),
        name="story-react",
    ),
    path(
        "stories/<int:pk>/reactions/",
        StoryReactionListView.as_view(),
        name="story-reactions",
    ),

    path("<int:user_id>/posts/", UserPostsView.as_view(), name="user-posts"),
    path("<int:pk>/", PublicProfileView.as_view(), name="public-profile"),
]
