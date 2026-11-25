
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message, GroupConversation, GroupMembership
from .serializers import MessageSerializer, GroupConversationSerializer
from .utils import conversation_group_name
from notifications.utils import create_notification
from social.access import blocked_user_ids, can_chat_between

User = get_user_model()


class GroupConversationView(generics.ListCreateAPIView):
    serializer_class = GroupConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupConversation.objects.filter(memberships__user=self.request.user).distinct()

    max_other_members = 50

    def perform_create(self, serializer):
        member_ids = self.request.data.get("member_ids", [])
        if not isinstance(member_ids, list):
            raise ValidationError({"member_ids": "Expected a list of user IDs."})
        try:
            member_ids = {
                int(member_id)
                for member_id in member_ids
                if int(member_id) != self.request.user.id
            }
        except (TypeError, ValueError):
            raise ValidationError({"member_ids": "User IDs must be integers."})
        if len(member_ids) > self.max_other_members:
            raise ValidationError({
                "member_ids": f"A group can have at most {self.max_other_members} other members."
            })

        candidates = list(User.objects.filter(id__in=member_ids))
        if len(candidates) != len(member_ids):
            raise ValidationError({"member_ids": "One or more users do not exist."})
        for candidate in candidates:
            if not can_chat_between(self.request.user, candidate):
                raise ValidationError({
                    "member_ids": "One or more of these users cannot be added to this group."
                })

        with transaction.atomic():
            group = serializer.save(created_by=self.request.user)
            GroupMembership.objects.create(group=group, user=self.request.user, role="admin")
            GroupMembership.objects.bulk_create([
                GroupMembership(group=group, user=candidate)
                for candidate in candidates
            ])


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        message = get_object_or_404(Message, pk=pk, sender=request.user, deleted_at__isnull=True)
        content = (request.data.get("content") or "").strip()
        if not content:
            return Response({"detail": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        message.content = content
        message.edited_at = timezone.now()
        message.save(update_fields=["content", "edited_at"])
        self.broadcast(
            message,
            {
                "type": "message_updated",
                "message_id": message.id,
                "content": message.content,
                "edited_at": message.edited_at.isoformat(),
            },
        )
        return Response(MessageSerializer(message, context={"request": request}).data)

    def delete(self, request, pk):
        message = get_object_or_404(Message, pk=pk, sender=request.user, deleted_at__isnull=True)
        message.deleted_at = timezone.now()
        message.save(update_fields=["deleted_at"])
        self.broadcast(
            message,
            {
                "type": "message_deleted",
                "message_id": message.id,
                "deleted_at": message.deleted_at.isoformat(),
            },
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def broadcast(message, event):
        if not message.receiver_id:
            return
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        async_to_sync(channel_layer.group_send)(
            conversation_group_name(message.sender_id, message.receiver_id),
            event,
        )


class GroupMessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        get_object_or_404(GroupMembership, group_id=self.kwargs["group_id"], user=self.request.user)
        return Message.objects.filter(
            group_id=self.kwargs["group_id"],
            deleted_at__isnull=True,
        ).exclude(
            sender_id__in=blocked_user_ids(self.request.user)
        ).select_related("sender", "receiver")

    def perform_create(self, serializer):
        membership = get_object_or_404(GroupMembership, group_id=self.kwargs["group_id"], user=self.request.user)
        serializer.save(sender=self.request.user, group=membership.group)


class ConversationView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        other_user = get_object_or_404(
            User,
            id=self.kwargs["user_id"]
        )
        if not can_chat_between(self.request.user, other_user):
            raise Http404

        return Message.objects.filter(
            Q(sender=self.request.user, receiver=other_user)
            | Q(sender=other_user, receiver=self.request.user),
            deleted_at__isnull=True,
        ).select_related("sender", "receiver")

    def perform_create(self, serializer):
        receiver = get_object_or_404(
            User,
            id=self.kwargs["user_id"]
        )

        if receiver == self.request.user:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                "You cannot message yourself."
            )
        if not can_chat_between(self.request.user, receiver):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This conversation is unavailable.")

        message = serializer.save(
            sender=self.request.user,
            receiver=receiver
        )
        create_notification(
            recipient=receiver,
            sender=self.request.user,
            notification_type="message",
        )
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                conversation_group_name(self.request.user.id, receiver.id),
                {
                    "type": "chat_message",
                    "message": message.content,
                    "sender_id": message.sender_id,
                    "receiver_id": message.receiver_id,
                    "id": message.id,
                    "created_at": message.created_at.isoformat(),
                    "is_read": message.is_read,
                },
            )


class MarkConversationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        if not can_chat_between(request.user, other_user):
            raise Http404

        unread_messages = Message.objects.filter(
            sender=other_user,
            receiver=request.user,
            is_read=False,
            deleted_at__isnull=True,
        )
        message_ids = list(unread_messages.values_list("id", flat=True))
        updated_count = unread_messages.update(is_read=True)

        if message_ids:
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    conversation_group_name(request.user.id, other_user.id),
                    {
                        "type": "read_receipt",
                        "reader_id": request.user.id,
                        "message_ids": message_ids,
                    },
                )

        return Response({
            "message": "Conversation marked as read.",
            "updated_count": updated_count,
        })


class UnreadMessageCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(
            receiver=request.user,
            is_read=False,
            deleted_at__isnull=True,
        ).exclude(sender_id__in=blocked_user_ids(request.user)).count()
        return Response({"unread_count": count})


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blocked_ids = blocked_user_ids(request.user)
        messages = (
            Message.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user),
                receiver__isnull=False,
                group__isnull=True,
                deleted_at__isnull=True,
            )
            .exclude(sender_id__in=blocked_ids)
            .exclude(receiver_id__in=blocked_ids)
            .select_related(
                "sender",
                "receiver",
                "sender__profile",
                "receiver__profile",
            )
            .order_by("-created_at")
        )
        unread_counts = {
            row["sender_id"]: row["total"]
            for row in (
                Message.objects.filter(
                    receiver=request.user,
                    is_read=False,
                    deleted_at__isnull=True,
                )
                .exclude(sender_id__in=blocked_ids)
                .values("sender_id")
                .annotate(total=Count("id"))
            )
        }
        conversations = {}
        for message in messages:
            other = message.receiver if message.sender_id == request.user.id else message.sender
            if other.id in conversations:
                continue
            profile_picture = None
            profile = getattr(other, "profile", None)
            if profile and profile.profile_picture:
                profile_picture = request.build_absolute_uri(
                    profile.profile_picture.url
                )
            unread = unread_counts.get(other.id, 0)
            conversations[other.id] = {
                "id": other.id,
                "username": other.username,
                "first_name": other.first_name,
                "last_name": other.last_name,
                "profile_picture": profile_picture,
                "last_message": message.content,
                "last_message_at": message.created_at,
                "unread_count": unread,
            }
        return Response(list(conversations.values()))
