from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
import re

from .models import Post, Bookmark, Poll, PollOption, PollVote, PostReport, Hashtag
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly
from social.access import (
    posts_for_detail,
    visible_posts,
    with_post_serializer_prefetches,
)


def sync_hashtags(post):
    """Keep a post's hashtag links in sync with its current content."""
    names = {name.lower() for name in re.findall(r"#([A-Za-z0-9_]+)", post.content or "")}
    current = set(post.hashtags.values_list("name", flat=True))
    for name in current - names:
        hashtag = Hashtag.objects.filter(name=name).first()
        if hashtag:
            hashtag.posts.remove(post)
    for name in names - current:
        hashtag, _ = Hashtag.objects.get_or_create(name=name)
        hashtag.posts.add(post)


class PostListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = PostSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):
        if self.request.query_params.get("drafts") == "true":
            queryset = Post.objects.filter(author=self.request.user)
        else:
            queryset = visible_posts(self.request.user).filter(is_draft=False).filter(
                Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=timezone.now())
            )
            if self.request.query_params.get("bookmarked") == "true":
                queryset = queryset.filter(bookmarks__user=self.request.user)
        return with_post_serializer_prefetches(self.request.user, queryset).order_by(
            "-created_at", "-pk"
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            post = serializer.save(author=self.request.user)
            sync_hashtags(post)


class BookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(visible_posts(request.user).filter(is_draft=False), pk=pk)
        bookmark, created = Bookmark.objects.get_or_create(post=post, user=request.user)
        if not created:
            bookmark.delete()
            return Response({"bookmarked": False})
        return Response({"bookmarked": True}, status=status.HTTP_201_CREATED)


class PinToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, author=request.user)
        post.is_pinned = not post.is_pinned
        post.save(update_fields=["is_pinned", "updated_at"])
        return Response({"pinned": post.is_pinned})


class RepostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        original = get_object_or_404(visible_posts(request.user).filter(is_draft=False), pk=pk)
        if original.author_id == request.user.id:
            raise ValidationError("You cannot repost your own post.")
        repost, created = Post.objects.get_or_create(
            author=request.user,
            repost_of=original,
            defaults={"content": ""},
        )
        return Response(
            PostSerializer(repost, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class PollVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, option_id):
        post = get_object_or_404(visible_posts(request.user).filter(is_draft=False), pk=pk)
        option = get_object_or_404(PollOption, pk=option_id, poll__post=post)
        if option.poll.expires_at and option.poll.expires_at <= timezone.now():
            return Response({"detail": "This poll has ended."}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            poll = Poll.objects.select_for_update().get(pk=option.poll_id)
            PollVote.objects.filter(option__poll=poll, user=request.user).delete()
            PollVote.objects.create(option=option, user=request.user)
        return Response({"voted": True, "option_id": option.id})


class PostReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(visible_posts(request.user).filter(is_draft=False), pk=pk)
        reason = (request.data.get("reason") or "").strip()
        if not reason:
            return Response({"detail": "A reason is required."}, status=status.HTTP_400_BAD_REQUEST)
        report = PostReport.objects.create(post=post, reporter=request.user, reason=reason)
        return Response({"reported": True, "report_id": report.id}, status=status.HTTP_201_CREATED)


class PostDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = PostSerializer

    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        return with_post_serializer_prefetches(
            self.request.user,
            posts_for_detail(self.request.user),
        )

    def perform_update(self, serializer):
        with transaction.atomic():
            post = serializer.save()
            sync_hashtags(post)