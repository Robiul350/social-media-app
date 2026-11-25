
from notifications.utils import create_notification
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
import re

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from posts.models import Post
from posts.serializers import PostSerializer

from .access import (
    blocked_user_ids,
    can_comment_on_profile,
    friend_ids,
    is_blocked_between,
    visible_posts,
    with_post_serializer_prefetches,
)
from .models import Block, Like, Comment, Follow, FriendRequest, CommentReaction, Mention
from .serializers import (
    CommentSerializer,
    FriendRequestSerializer,
    UserSummarySerializer,
)
from .permissions import IsCommentOwnerOrReadOnly


User = get_user_model()


# =====================================
# Like Toggle
# =====================================

class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(visible_posts(request.user), id=post_id)

        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )

        if created:
            create_notification(
                recipient=post.author,
                sender=request.user,
                notification_type="like",
                post=post
            )

        if not created:
            like.delete()

            return Response({
                "message": "Like removed",
                "liked": False,
                "like_count": post.likes.count()
            })

        return Response({
            "message": "Post liked",
            "liked": True,
            "like_count": post.likes.count()
        }, status=status.HTTP_201_CREATED)


# =====================================
# Comment List and Create
# =====================================

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post = get_object_or_404(
            visible_posts(self.request.user),
            id=self.kwargs["post_id"]
        )

        return Comment.objects.filter(
            post=post
        ).exclude(
            user_id__in=blocked_user_ids(self.request.user)
        ).select_related(
            "user",
            "user__profile",
        ).order_by("created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["post_id"] = self.kwargs["post_id"]
        return context

    def perform_create(self, serializer):
        post = get_object_or_404(
            Post.objects.filter(is_draft=False)
            .filter(Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now()))
            .exclude(author_id__in=blocked_user_ids(self.request.user)),
            id=self.kwargs["post_id"],
        )
        if (
            post.audience != Post.Audience.PUBLIC
            and not visible_posts(self.request.user).filter(pk=post.pk).exists()
        ):
            raise Http404
        if is_blocked_between(self.request.user, post.author):
            raise PermissionDenied("This action is unavailable.")
        if not can_comment_on_profile(self.request.user, post.author):
            raise PermissionDenied("You cannot comment on this post.")
        comment = serializer.save(
            post=post,
            user=self.request.user
        )
        parent = comment.parent
        for username in set(re.findall(r"@([A-Za-z0-9_.-]+)", comment.content)):
            mentioned = User.objects.filter(username__iexact=username).first()
            if mentioned:
                Mention.objects.get_or_create(comment=comment, mentioned=mentioned)
                create_notification(recipient=mentioned, sender=self.request.user, notification_type="mention", post=post, comment=comment)
        parent = comment.parent
        create_notification(
            recipient=parent.user if parent else post.author,
            sender=self.request.user,
            notification_type="reply" if parent else "comment",
            post=post,
            comment=comment
        )


# =====================================
# Comment Detail
# =====================================

class CommentReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment.objects.filter(post__in=visible_posts(request.user)).exclude(user_id__in=blocked_user_ids(request.user)), pk=pk)
        reaction = (request.data.get("reaction") or "like").lower()
        allowed = {choice[0] for choice in CommentReaction.Reaction.choices}
        if reaction not in allowed:
            return Response({"detail": "Invalid reaction."}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = CommentReaction.objects.get_or_create(comment=comment, user=request.user, defaults={"reaction": reaction})
        if not created:
            if obj.reaction == reaction:
                obj.delete()
                return Response({"reacted": False})
            obj.reaction = reaction
            obj.save(update_fields=["reaction"])
        return Response({"reacted": True, "reaction": reaction})


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer

    permission_classes = [
        IsAuthenticated,
        IsCommentOwnerOrReadOnly
    ]

    def get_queryset(self):
        return Comment.objects.filter(
            post__in=visible_posts(self.request.user)
        ).exclude(
            user_id__in=blocked_user_ids(self.request.user)
        ).select_related("user", "user__profile")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["post_id"] = self.get_object().post_id
        return context


# =====================================
# Follow Toggle
# =====================================

class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)

        if target.id == request.user.id:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_blocked_between(request.user, target):
            raise PermissionDenied("This action is unavailable.")

        _, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target
        )

        if not created:
            return Response({
                "message": "Already following this user.",
                "following": True,
            })
        create_notification(
            recipient=target,
            sender=request.user,
            notification_type="follow"
        )

        return Response(
            {"message": f"Now following {target.username}."},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, user_id):
        target = get_object_or_404(User, id=user_id)

        if is_blocked_between(request.user, target):
            raise PermissionDenied("This action is unavailable.")

        deleted, _ = Follow.objects.filter(
            follower=request.user,
            following=target
        ).delete()

        if deleted:
            return Response({
                "message": "Unfollowed successfully."
            })

        return Response(
            {"message": "You do not follow this user."},
            status=status.HTTP_404_NOT_FOUND
        )


class FriendRequestSendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        if target.id == request.user.id:
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if is_blocked_between(request.user, target):
            raise PermissionDenied("This action is unavailable.")

        with transaction.atomic():
            list(
                User.objects.select_for_update()
                .filter(pk__in=[request.user.pk, target.pk])
                .order_by("pk")
                .values_list("pk", flat=True)
            )

            existing_friendship = FriendRequest.objects.filter(
                Q(sender=request.user, receiver=target)
                | Q(sender=target, receiver=request.user),
                status=FriendRequest.Status.ACCEPTED,
            ).first()
            if existing_friendship:
                return Response(
                    {"detail": "You are already friends."},
                    status=status.HTTP_409_CONFLICT,
                )

            incoming_request = FriendRequest.objects.filter(
                sender=target,
                receiver=request.user,
                status=FriendRequest.Status.PENDING,
            ).first()
            if incoming_request:
                return Response(
                    {
                        "detail": "This user has already sent you a request.",
                        "friend_request_id": incoming_request.id,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            friend_request, created = FriendRequest.objects.get_or_create(
                sender=request.user,
                receiver=target,
                defaults={"status": FriendRequest.Status.PENDING},
            )
            if friend_request.status == FriendRequest.Status.ACCEPTED:
                return Response(
                    {"detail": "You are already friends."},
                    status=status.HTTP_409_CONFLICT,
                )
            if not created and friend_request.status == FriendRequest.Status.PENDING:
                return Response(
                    FriendRequestSerializer(
                        friend_request,
                        context={"request": request},
                    ).data,
                    status=status.HTTP_200_OK,
                )

            if not created:
                friend_request.status = FriendRequest.Status.PENDING
                friend_request.save(update_fields=["status", "updated_at"])

            create_notification(
                recipient=target,
                sender=request.user,
                notification_type="friend_request",
            )

        return Response(
            FriendRequestSerializer(
                friend_request,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        direction = request.query_params.get("direction", "incoming")
        if direction == "incoming":
            queryset = FriendRequest.objects.filter(receiver=request.user)
        elif direction == "outgoing":
            queryset = FriendRequest.objects.filter(sender=request.user)
        else:
            return Response(
                {"direction": "Choose either 'incoming' or 'outgoing'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.filter(
            status=FriendRequest.Status.PENDING
        ).select_related(
            "sender",
            "receiver",
            "sender__profile",
            "receiver__profile",
        ).exclude(
            sender_id__in=blocked_user_ids(request.user)
        ).exclude(
            receiver_id__in=blocked_user_ids(request.user)
        ).order_by("-created_at")
        return Response(
            FriendRequestSerializer(
                queryset,
                many=True,
                context={"request": request},
            ).data
        )


class FriendRequestRespondView(APIView):
    permission_classes = [IsAuthenticated]
    response_status = None

    def post(self, request, pk):
        with transaction.atomic():
            friend_request = get_object_or_404(
                FriendRequest.objects.select_for_update(),
                pk=pk,
                receiver=request.user,
                status=FriendRequest.Status.PENDING,
            )
            if is_blocked_between(friend_request.sender, friend_request.receiver):
                raise Http404
            friend_request.status = self.response_status
            friend_request.save(update_fields=["status", "updated_at"])

        return Response({
            "id": friend_request.id,
            "status": friend_request.status,
        })


class FriendRequestAcceptView(FriendRequestRespondView):
    response_status = FriendRequest.Status.ACCEPTED


class FriendRequestRejectView(FriendRequestRespondView):
    response_status = FriendRequest.Status.REJECTED


class FriendRequestCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        friend_request = get_object_or_404(
            FriendRequest,
            pk=pk,
            sender=request.user,
            status=FriendRequest.Status.PENDING,
        )
        friend_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _friend_ids(user):
    return friend_ids(user)


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = User.objects.filter(
            id__in=_friend_ids(request.user)
        ).exclude(
            id__in=blocked_user_ids(request.user)
        ).select_related("profile").order_by("username")
        return Response(
            UserSummarySerializer(
                friends,
                many=True,
                context={"request": request},
            ).data
        )


class UnfriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        deleted, _ = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=target)
            | Q(sender=target, receiver=request.user),
            status=FriendRequest.Status.ACCEPTED,
        ).delete()
        if not deleted:
            return Response(
                {"detail": "You are not friends with this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MutualFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        if is_blocked_between(request.user, target):
            raise Http404
        mutual_ids = _friend_ids(request.user) & _friend_ids(target)
        mutual_friends = User.objects.filter(
            id__in=mutual_ids
        ).exclude(
            id__in=blocked_user_ids(request.user)
        ).select_related("profile").order_by("username")
        return Response(
            UserSummarySerializer(
                mutual_friends,
                many=True,
                context={"request": request},
            ).data
        )


# =====================================
# Following List
# =====================================

class FollowingListView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            followers__follower=self.request.user
        ).exclude(
            id__in=blocked_user_ids(self.request.user)
        ).select_related("profile").distinct()


# =====================================
# Followers List
# =====================================

class FollowersListView(generics.ListAPIView):
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            following__following=self.request.user
        ).exclude(
            id__in=blocked_user_ids(self.request.user)
        ).select_related("profile").distinct()


class NewsFeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# =====================================
# News Feed
# =====================================

class NewsFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NewsFeedPagination

    def list(self, request, *args, **kwargs):
        if "page" not in request.query_params:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return with_post_serializer_prefetches(self.request.user).order_by(
            "-created_at", "-pk"
        )


class BlockListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blocks = Block.objects.filter(
            blocker=request.user
        ).select_related("blocked", "blocked__profile").order_by("-created_at")
        return Response(
            UserSummarySerializer(
                [block.blocked for block in blocks],
                many=True,
                context={"request": request},
            ).data
        )


class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        if target.id == request.user.id:
            return Response(
                {"detail": "You cannot block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        _, created = Block.objects.get_or_create(
            blocker=request.user,
            blocked=target,
        )
        return Response(
            {"blocked": True},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        deleted, _ = Block.objects.filter(
            blocker=request.user,
            blocked=target,
        ).delete()
        if not deleted:
            return Response(
                {"detail": "This user is not in your blocked list."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
