
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from .models import User, Story, StoryView, StoryReaction
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    PublicProfileSerializer,
    StorySerializer,
    StoryReactionSerializer,
)

from posts.models import Post
from posts.serializers import PostSerializer
from social.access import (
    blocked_user_ids,
    friend_ids,
    is_blocked_between,
    visible_posts,
    with_post_serializer_prefetches,
)
from social.models import Follow
from notifications.utils import create_notification


def revoke_user_refresh_tokens(user):
    """Blacklist every outstanding refresh token for a user."""
    outstanding = OutstandingToken.objects.filter(user=user)
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=token) for token in outstanding],
        ignore_conflicts=True,
    )


def visible_stories(viewer):
    friends = friend_ids(viewer)
    followed = Follow.objects.filter(follower=viewer).values("following_id")
    privacy_rules = (
        Q(author_id=viewer.id)
        | Q(privacy=Story.Privacy.PUBLIC)
        | Q(privacy=Story.Privacy.FOLLOWERS, author_id__in=followed)
        | Q(privacy=Story.Privacy.FRIENDS, author_id__in=friends)
    )
    profile_visibility = (
        Q(author_id=viewer.id)
        | Q(author__profile__isnull=True)
        | Q(author__profile__is_private=False)
        | Q(author_id__in=friends)
    )
    return (
        Story.objects.filter(expires_at__gt=timezone.now())
        .filter(privacy_rules, profile_visibility)
        .exclude(author_id__in=blocked_user_ids(viewer))
        .select_related("author", "author__profile")
        .distinct()
    )


# =====================================
# User Registration
# =====================================

class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response({
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================
# User Login
# =====================================

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful.",

                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },

                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }

            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password", "")
        new_password = request.data.get("new_password", "")
        if not request.user.check_password(current_password):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password, request.user)
        except Exception as exc:
            messages = getattr(exc, "messages", [str(exc)])
            return Response({"detail": messages}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            request.user.set_password(new_password)
            request.user.save(update_fields=["password"])
            revoke_user_refresh_tokens(request.user)
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Password changed successfully."})


class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        with transaction.atomic():
            request.user.is_active = False
            request.user.save(update_fields=["is_active"])
            revoke_user_refresh_tokens(request.user)
        return Response({"detail": "Account deactivated."})


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        user = get_user_model().objects.filter(email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = (
                f"{settings.FRONTEND_URL.rstrip('/')}/password-reset-confirm/"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                subject="Reset your SocialConnect password",
                message=(
                    "Use the following link to choose a new SocialConnect password:\n"
                    f"{reset_url}\n\n"
                    "If you did not request this, you can ignore this message."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        return Response({
            "detail": "If the account exists, password reset instructions were sent."
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = force_str(urlsafe_base64_decode(request.data.get("uid", "")))
            user = get_user_model().objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)
        token = request.data.get("token", "")
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired reset link."}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get("password", "")
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(password, user)
        except Exception as exc:
            return Response({"detail": getattr(exc, "messages", [str(exc)])}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            user.set_password(password)
            user.save(update_fields=["password"])
            revoke_user_refresh_tokens(user)
        return Response({"detail": "Password reset successfully."})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid or expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Logout successful."})


# =====================================
# Own Profile View
# =====================================

class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        profile = user.profile

        serializer = ProfileSerializer(
            profile,
            context={"request": request},
        )

        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "profile": serializer.data
        }, status=status.HTTP_200_OK)


    def patch(self, request):

        user = request.user
        profile = user.profile

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():

            with transaction.atomic():

                user.first_name = request.data.get(
                    "first_name",
                    user.first_name
                )

                user.last_name = request.data.get(
                    "last_name",
                    user.last_name
                )

                user.save(
                    update_fields=["first_name", "last_name"]
                )

                serializer.save()

            return Response({
                "message": "Profile updated successfully.",

                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,

                "profile": serializer.data

            }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =====================================
# User Search
# =====================================

class StoryListCreateView(generics.ListCreateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return visible_stories(self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, expires_at=timezone.now() + timedelta(hours=24))


class StoryViewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        story = get_object_or_404(visible_stories(request.user), pk=pk)
        StoryView.objects.get_or_create(story=story, viewer=request.user)
        return Response({"viewed": True})


# =====================================
# Story Reactions
# =====================================

class StoryReactionView(APIView):
    """Create or update a reaction on a story."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        story = get_object_or_404(visible_stories(request.user), pk=pk)

        # Prevent users from reacting to their own stories
        if story.author_id == request.user.id:
            return Response(
                {"detail": "You cannot react to your own story."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reaction_type = (request.data.get("reaction_type") or "").lower()
        allowed = {choice[0] for choice in StoryReaction.ReactionType.choices}
        if reaction_type not in allowed:
            return Response(
                {"detail": f"Invalid reaction type. Allowed: {', '.join(sorted(allowed))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            reaction, created = StoryReaction.objects.update_or_create(
                user=request.user,
                story=story,
                defaults={"reaction_type": reaction_type},
            )

        # Notify story owner (skip if the reactor is the owner - already checked above)
        create_notification(
            recipient=story.author,
            sender=request.user,
            notification_type="story_reaction",
        )

        serializer = StoryReactionSerializer(
            reaction, context={"request": request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        story = get_object_or_404(visible_stories(request.user), pk=pk)

        deleted, _ = StoryReaction.objects.filter(
            user=request.user,
            story=story,
        ).delete()

        if not deleted:
            return Response(
                {"detail": "You have not reacted to this story."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "Reaction removed."},
            status=status.HTTP_204_NO_CONTENT,
        )


class StoryReactionListView(generics.ListAPIView):
    """List all reactions on a story, with counts by type."""

    serializer_class = StoryReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        self.story = get_object_or_404(
            visible_stories(self.request.user), pk=self.kwargs["pk"]
        )
        return (
            StoryReaction.objects.filter(story=self.story)
            .select_related("user", "user__profile")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Build reaction counts by type
        counts = {}
        for choice in StoryReaction.ReactionType.choices:
            counts[choice[0]] = 0
        for reaction in queryset:
            counts[reaction.reaction_type] = counts.get(reaction.reaction_type, 0) + 1

        # Current user's reaction
        current_user_reaction = None
        if request.user.is_authenticated:
            own = queryset.filter(user=request.user).first()
            if own:
                current_user_reaction = own.reaction_type

        return Response(
            {
                "story_id": self.story.id,
                "total_reactions": queryset.count(),
                "counts_by_type": counts,
                "user_reaction": current_user_reaction,
                "reactions": serializer.data,
            }
        )


class UserSearchView(generics.ListAPIView):

    serializer_class = PublicProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get("suggested") == "true":
            following = self.request.user.following.values_list(
                "following_id",
                flat=True,
            )
            return (
                User.objects.exclude(id=self.request.user.id)
                .exclude(id__in=blocked_user_ids(self.request.user))
                .exclude(id__in=following)
                .select_related("profile")
                .order_by("-date_joined", "id")[:5]
            )

        search = (
            self.request.query_params.get("search")
            or self.request.query_params.get("q")
            or ""
        )

        return User.objects.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        ).exclude(
            id=self.request.user.id
        ).exclude(
            id__in=blocked_user_ids(self.request.user)
        ).select_related("profile").order_by("username", "id")[:50]


# =====================================
# Public Profile View
# =====================================

class PublicProfileView(generics.RetrieveAPIView):

    serializer_class = PublicProfileSerializer

    permission_classes = [IsAuthenticated]

    lookup_field = "id"
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return User.objects.exclude(
            id__in=blocked_user_ids(self.request.user)
        )


# =====================================
# User Posts View
# =====================================

class UserPostsView(generics.ListAPIView):

    serializer_class = PostSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user_id = self.kwargs.get("user_id")

        return with_post_serializer_prefetches(
            self.request.user,
            visible_posts(self.request.user).filter(author_id=user_id),
        ).order_by("-created_at", "-pk")
