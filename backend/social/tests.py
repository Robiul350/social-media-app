from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from posts.models import Post
from notifications.models import Notification
from social.models import Block, Comment, Follow, FriendRequest

User = get_user_model()


class SocialFeatureTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="StrongPass!2026")
        self.other = User.objects.create_user(username="other", email="other@example.com", password="StrongPass!2026")
        self.post = Post.objects.create(author=self.owner, content="Test post")
        self.client.force_authenticate(user=self.other)

    def test_like_and_follow_create_notifications(self):
        like = self.client.post(f"/api/social/posts/{self.post.id}/like/")
        follow = self.client.post(f"/api/social/users/{self.owner.id}/follow/")
        comment = self.client.post(f"/api/social/posts/{self.post.id}/comments/", {"content": "Nice"})
        self.assertEqual(like.status_code, status.HTTP_201_CREATED)
        self.assertIn(follow.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertEqual(comment.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(Notification.objects.filter(recipient=self.owner).count(), 3)

    def test_followers_and_following_lists_return_the_authenticated_users_connections(self):
        self.client.post(f"/api/social/users/{self.owner.id}/follow/")

        following = self.client.get("/api/social/users/following/")
        self.assertEqual(following.status_code, status.HTTP_200_OK)
        self.assertEqual([person["id"] for person in following.data], [self.owner.id])

        self.client.force_authenticate(user=self.owner)
        followers = self.client.get("/api/social/users/followers/")
        self.assertEqual(followers.status_code, status.HTTP_200_OK)
        self.assertEqual([person["id"] for person in followers.data], [self.other.id])

    def test_feed_pagination_is_opt_in_and_returns_next_page(self):
        Post.objects.bulk_create(
            [
                Post(author=self.other, content=f"Feed post {index}")
                for index in range(12)
            ]
        )

        unpaginated = self.client.get("/api/social/feed/")
        first_page = self.client.get("/api/social/feed/?page=1")
        second_page = self.client.get("/api/social/feed/?page=2")

        self.assertEqual(unpaginated.status_code, status.HTTP_200_OK)
        self.assertIsInstance(unpaginated.data, list)
        self.assertEqual(len(unpaginated.data), 13)
        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.data["count"], 13)
        self.assertEqual(len(first_page.data["results"]), 10)
        self.assertIsNotNone(first_page.data["next"])
        self.assertEqual(len(second_page.data["results"]), 3)

    def test_feed_shows_three_unfollowed_authors_in_newest_order_with_interaction_metadata(self):
        self.other.first_name = "Avery"
        self.other.last_name = "One"
        self.other.save(update_fields=["first_name", "last_name"])
        second = User.objects.create_user(
            username="second",
            email="second@example.com",
            first_name="Blair",
            last_name="Two",
            password="StrongPass!2026",
        )
        third = User.objects.create_user(
            username="third",
            email="third@example.com",
            first_name="Casey",
            last_name="Three",
            password="StrongPass!2026",
        )
        posts = [
            Post.objects.create(author=user, content=f"Update from {user.username}")
            for user in (self.other, second, third)
        ]
        base_time = timezone.now()
        for index, post in enumerate(posts):
            Post.objects.filter(pk=post.pk).update(
                created_at=base_time - timedelta(minutes=2 - index)
            )

        self.client.post(f"/api/social/posts/{posts[2].id}/like/")
        self.client.post(f"/api/posts/{posts[1].id}/bookmark/")
        Post.objects.create(author=self.owner, repost_of=posts[0], content="")

        response = self.client.get("/api/social/feed/?page=1")
        bookmarks_response = self.client.get("/api/posts/?bookmarked=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        feed_posts = response.data["results"]
        feed_ids = [post["id"] for post in feed_posts]
        self.assertTrue(all(post.id in feed_ids for post in posts))
        self.assertLess(feed_ids.index(posts[2].id), feed_ids.index(posts[1].id))
        self.assertLess(feed_ids.index(posts[1].id), feed_ids.index(posts[0].id))
        by_id = {post["id"]: post for post in feed_posts}
        self.assertEqual(by_id[posts[0].id]["author_id"], self.other.id)
        self.assertEqual(by_id[posts[0].id]["author_full_name"], "Avery One")
        self.assertEqual(by_id[posts[0].id]["author_username"], "other")
        self.assertIsNone(by_id[posts[0].id]["author_profile_picture"])
        self.assertEqual(by_id[posts[0].id]["content"], "Update from other")
        self.assertTrue(by_id[posts[2].id]["is_liked"])
        self.assertEqual(by_id[posts[2].id]["like_count"], 1)
        self.assertTrue(by_id[posts[1].id]["is_bookmarked"])
        self.assertIn(
            posts[1].id,
            {post["id"] for post in bookmarks_response.data},
        )
        self.assertEqual(by_id[posts[0].id]["share_count"], 1)
        self.assertIn("created_at", by_id[posts[0].id])
        self.assertIn("image", by_id[posts[0].id])
        self.assertIn("video", by_id[posts[0].id])

    def test_feed_includes_public_posts_from_unfollowed_accounts(self):
        stranger = User.objects.create_user(
            username="stranger",
            email="stranger@example.com",
            password="StrongPass!2026",
        )
        public_post = Post.objects.create(author=stranger, content="Public update")

        response = self.client.get("/api/social/feed/?page=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            public_post.id,
            {post["id"] for post in response.data["results"]},
        )

    def test_feed_and_interactions_hide_private_draft_and_scheduled_posts(self):
        from django.utils import timezone
        from datetime import timedelta

        private_post = Post.objects.create(
            author=self.owner,
            content="Followers only",
            audience=Post.Audience.FOLLOWERS,
        )
        draft = Post.objects.create(
            author=self.owner,
            content="Draft",
            is_draft=True,
        )
        scheduled = Post.objects.create(
            author=self.owner,
            content="Not yet public",
            scheduled_for=timezone.now() + timedelta(days=1),
        )

        feed = self.client.get("/api/social/feed/?page=1")
        visible_ids = {post["id"] for post in feed.data["results"]}
        self.assertNotIn(private_post.id, visible_ids)
        self.assertNotIn(draft.id, visible_ids)
        self.assertNotIn(scheduled.id, visible_ids)

        for post in (private_post, draft, scheduled):
            self.assertEqual(
                self.client.post(f"/api/social/posts/{post.id}/like/").status_code,
                status.HTTP_404_NOT_FOUND,
            )
            self.assertEqual(
                self.client.post(
                    f"/api/social/posts/{post.id}/comments/",
                    {"content": "Should not be accepted"},
                ).status_code,
                status.HTTP_404_NOT_FOUND,
            )

        self.client.force_authenticate(user=self.owner)
        own_feed = self.client.get("/api/social/feed/?page=1")
        own_visible_ids = {post["id"] for post in own_feed.data["results"]}
        self.assertNotIn(draft.id, own_visible_ids)
        self.assertNotIn(scheduled.id, own_visible_ids)
        for post in (draft, scheduled):
            self.assertEqual(
                self.client.post(f"/api/social/posts/{post.id}/like/").status_code,
                status.HTTP_404_NOT_FOUND,
            )
            self.assertEqual(
                self.client.post(
                f"/api/social/posts/{post.id}/comments/",
                {"content": "Should not be accepted"},
                ).status_code,
                status.HTTP_404_NOT_FOUND,
            )

    def test_comment_replies_are_supported_and_must_stay_on_the_same_post(self):
        root = Comment.objects.create(
            post=self.post,
            user=self.owner,
            content="Root comment",
        )
        reply_response = self.client.post(
            f"/api/social/posts/{self.post.id}/comments/",
            {"content": "Reply", "parent": root.id},
        )

        self.assertEqual(reply_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("profile_picture", reply_response.data)
        reply = Comment.objects.get(id=reply_response.data["id"])
        self.assertEqual(reply.parent_id, root.id)

        other_post = Post.objects.create(author=self.owner, content="Other post")
        cross_post_response = self.client.post(
            f"/api/social/posts/{other_post.id}/comments/",
            {"content": "Invalid reply", "parent": root.id},
        )
        self.assertEqual(cross_post_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_comment_cannot_be_reparented_to_create_a_cycle(self):
        root = Comment.objects.create(
            post=self.post,
            user=self.owner,
            content="Root comment",
        )
        reply = Comment.objects.create(
            post=self.post,
            user=self.other,
            content="Reply",
            parent=root,
        )
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            f"/api/social/comments/{root.id}/",
            {"parent": reply.id},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        root.refresh_from_db()
        self.assertIsNone(root.parent_id)

    def test_friend_requests_reject_self_duplicate_and_reverse_pending(self):
        self_request = self.client.post(
            f"/api/social/users/{self.other.id}/friend-request/"
        )
        self.assertEqual(self_request.status_code, status.HTTP_400_BAD_REQUEST)

        sent = self.client.post(
            f"/api/social/users/{self.owner.id}/friend-request/"
        )
        self.assertEqual(sent.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sent.data["status"], FriendRequest.Status.PENDING)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.owner,
                notification_type="friend_request",
            ).count(),
            1,
        )

        duplicate = self.client.post(
            f"/api/social/users/{self.owner.id}/friend-request/"
        )
        self.assertEqual(duplicate.status_code, status.HTTP_200_OK)
        self.assertEqual(FriendRequest.objects.count(), 1)
        sender_profile = self.client.get(f"/api/users/{self.owner.id}/")
        self.assertEqual(sender_profile.data["friendship_status"], "outgoing_pending")
        self.assertEqual(sender_profile.data["friend_request_id"], sent.data["id"])
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.owner,
                notification_type="friend_request",
            ).count(),
            1,
        )

        self.client.force_authenticate(user=self.owner)
        reverse_pending = self.client.post(
            f"/api/social/users/{self.other.id}/friend-request/"
        )
        self.assertEqual(reverse_pending.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_friend_request_acceptance_list_unfriend_and_profile_status(self):
        sent = self.client.post(
            f"/api/social/users/{self.owner.id}/friend-request/"
        )
        friend_request_id = sent.data["id"]

        unauthorized_accept = self.client.post(
            f"/api/social/friend-requests/{friend_request_id}/accept/"
        )
        self.assertEqual(unauthorized_accept.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(user=self.owner)
        incoming = self.client.get("/api/social/friend-requests/?direction=incoming")
        self.assertEqual(incoming.status_code, status.HTTP_200_OK)
        self.assertEqual(incoming.data[0]["sender"]["id"], self.other.id)
        self.assertIn("profile_picture", incoming.data[0]["sender"])
        receiver_profile = self.client.get(f"/api/users/{self.other.id}/")
        self.assertEqual(receiver_profile.data["friendship_status"], "incoming_pending")
        self.assertEqual(receiver_profile.data["friend_request_id"], friend_request_id)

        accepted = self.client.post(
            f"/api/social/friend-requests/{friend_request_id}/accept/"
        )
        self.assertEqual(accepted.status_code, status.HTTP_200_OK)
        self.assertEqual(accepted.data["status"], FriendRequest.Status.ACCEPTED)

        friends = self.client.get("/api/social/friends/")
        self.assertEqual([friend["id"] for friend in friends.data], [self.other.id])
        already_friends = self.client.post(
            f"/api/social/users/{self.other.id}/friend-request/"
        )
        self.assertEqual(already_friends.status_code, status.HTTP_409_CONFLICT)

        profile = self.client.get(f"/api/users/{self.other.id}/")
        self.assertEqual(profile.data["friendship_status"], "friends")

        unfriended = self.client.delete(f"/api/social/friends/{self.other.id}/")
        self.assertEqual(unfriended.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get("/api/social/friends/").data, [])
        self.assertEqual(
            self.client.get(f"/api/users/{self.other.id}/").data["friendship_status"],
            "none",
        )

    def test_sender_can_cancel_and_receiver_can_reject_requests(self):
        sent = self.client.post(
            f"/api/social/users/{self.owner.id}/friend-request/"
        )
        request_id = sent.data["id"]
        outgoing = self.client.get("/api/social/friend-requests/?direction=outgoing")
        self.assertEqual(outgoing.data[0]["id"], request_id)

        cancelled = self.client.delete(
            f"/api/social/friend-requests/{request_id}/"
        )
        self.assertEqual(cancelled.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FriendRequest.objects.filter(id=request_id).exists())

        resent = self.client.post(
            f"/api/social/users/{self.owner.id}/friend-request/"
        )
        self.client.force_authenticate(user=self.owner)
        rejected = self.client.post(
            f"/api/social/friend-requests/{resent.data['id']}/reject/"
        )
        self.assertEqual(rejected.status_code, status.HTTP_200_OK)
        self.assertEqual(rejected.data["status"], FriendRequest.Status.REJECTED)

    def test_mutual_friends_endpoint_returns_shared_accepted_connections(self):
        mutual = User.objects.create_user(
            username="mutual",
            email="mutual@example.com",
            password="StrongPass!2026",
        )
        FriendRequest.objects.create(
            sender=self.other,
            receiver=mutual,
            status=FriendRequest.Status.ACCEPTED,
        )
        FriendRequest.objects.create(
            sender=self.owner,
            receiver=mutual,
            status=FriendRequest.Status.ACCEPTED,
        )

        response = self.client.get(
            f"/api/social/users/{self.owner.id}/mutual-friends/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([friend["id"] for friend in response.data], [mutual.id])

    def test_block_list_create_duplicate_self_and_unblock(self):
        Follow.objects.create(follower=self.other, following=self.owner)
        self.client.force_authenticate(user=self.other)

        blocked = self.client.post(f"/api/social/users/{self.owner.id}/block/")
        self.assertEqual(blocked.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Block.objects.filter(blocker=self.other, blocked=self.owner).exists()
        )
        self.assertTrue(
            Follow.objects.filter(follower=self.other, following=self.owner).exists()
        )

        duplicate = self.client.post(f"/api/social/users/{self.owner.id}/block/")
        self.assertEqual(duplicate.status_code, status.HTTP_200_OK)
        listed = self.client.get("/api/social/blocks/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in listed.data], [self.owner.id])

        self_block = self.client.post(f"/api/social/users/{self.other.id}/block/")
        self.assertEqual(self_block.status_code, status.HTTP_400_BAD_REQUEST)

        unblocked = self.client.delete(
            f"/api/social/users/{self.owner.id}/block/"
        )
        self.assertEqual(unblocked.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Block.objects.filter(blocker=self.other, blocked=self.owner).exists()
        )
        self.assertTrue(
            Follow.objects.filter(follower=self.other, following=self.owner).exists()
        )

    def test_block_hides_profiles_and_prevents_social_and_chat_access(self):
        from chat.models import Message

        Message.objects.create(
            sender=self.other,
            receiver=self.owner,
            content="Existing history is retained",
        )
        blocked = self.client.post(f"/api/social/users/{self.owner.id}/block/")
        self.assertEqual(blocked.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            self.client.get(f"/api/users/{self.owner.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get(f"/api/posts/{self.post.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertNotIn(
            self.owner.id,
            [person["id"] for person in self.client.get(
                f"/api/users/search/?search={self.owner.username}"
            ).data],
        )
        self.assertEqual(
            self.client.post(f"/api/social/users/{self.owner.id}/follow/").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(
                f"/api/social/users/{self.owner.id}/friend-request/"
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.get(
                f"/api/chat/conversations/{self.owner.id}/"
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertTrue(
            Message.objects.filter(
                sender=self.other,
                receiver=self.owner,
                content="Existing history is retained",
            ).exists()
        )

        self.client.delete(f"/api/social/users/{self.owner.id}/block/")
        self.assertEqual(
            self.client.get(f"/api/users/{self.owner.id}/").status_code,
            status.HTTP_200_OK,
        )

