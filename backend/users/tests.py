from datetime import date, timedelta
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib import admin
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image

from posts.models import Post
from social.models import Block, Follow, FriendRequest
from .models import Story, StoryReaction

User = get_user_model()


class AuthenticationAndProfileTests(APITestCase):
    def test_story_privacy_expiration_and_blocks_are_enforced_for_lists_and_views(self):
        author = User.objects.create_user(
            username="story-author",
            email="story-author@example.com",
            password="StrongPass!2026",
        )
        follower = User.objects.create_user(
            username="story-follower",
            email="story-follower@example.com",
            password="StrongPass!2026",
        )
        friend = User.objects.create_user(
            username="story-friend",
            email="story-friend@example.com",
            password="StrongPass!2026",
        )
        stranger = User.objects.create_user(
            username="story-stranger",
            email="story-stranger@example.com",
            password="StrongPass!2026",
        )
        Follow.objects.create(follower=follower, following=author)
        FriendRequest.objects.create(
            sender=author,
            receiver=friend,
            status=FriendRequest.Status.ACCEPTED,
        )
        expires_at = timezone.now() + timedelta(days=1)
        public_story = Story.objects.create(
            author=author,
            text="Public story",
            expires_at=expires_at,
        )
        followers_story = Story.objects.create(
            author=author,
            text="Followers story",
            privacy=Story.Privacy.FOLLOWERS,
            expires_at=expires_at,
        )
        friends_story = Story.objects.create(
            author=author,
            text="Friends story",
            privacy=Story.Privacy.FRIENDS,
            expires_at=expires_at,
        )
        expired_story = Story.objects.create(
            author=author,
            text="Expired story",
            expires_at=timezone.now() - timedelta(seconds=1),
        )

        self.client.force_authenticate(user=stranger)
        stranger_stories = self.client.get("/api/users/stories/")
        self.assertEqual(
            {story["id"] for story in stranger_stories.data},
            {public_story.id},
        )
        self.assertEqual(
            self.client.post(f"/api/users/stories/{followers_story.id}/view/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertNotIn(
            expired_story.id,
            {story["id"] for story in stranger_stories.data},
        )

        self.client.force_authenticate(user=follower)
        follower_stories = self.client.get("/api/users/stories/")
        self.assertEqual(
            {story["id"] for story in follower_stories.data},
            {public_story.id, followers_story.id},
        )

        self.client.force_authenticate(user=friend)
        friend_stories = self.client.get("/api/users/stories/")
        self.assertEqual(
            {story["id"] for story in friend_stories.data},
            {public_story.id, friends_story.id},
        )

        author.profile.is_private = True
        author.profile.save(update_fields=["is_private"])
        self.client.force_authenticate(user=stranger)
        self.assertEqual(self.client.get("/api/users/stories/").data, [])
        self.client.force_authenticate(user=friend)
        self.assertEqual(
            len(self.client.get("/api/users/stories/").data),
            2,
        )

        Block.objects.create(blocker=author, blocked=friend)
        self.assertEqual(self.client.get("/api/users/stories/").data, [])

    def test_story_upload_accepts_media_without_client_supplied_expiry(self):
        user = User.objects.create_user(
            username="story-uploader",
            email="story-uploader@example.com",
            password="StrongPass!2026",
        )
        self.client.force_authenticate(user=user)

        with TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                image = Image.new("RGB", (2, 2), color="blue")
                content = BytesIO()
                image.save(content, format="PNG")
                upload = SimpleUploadedFile(
                    "story.png",
                    content.getvalue(),
                    content_type="image/png",
                )
                response = self.client.post(
                    "/api/users/stories/",
                    {
                        "media": upload,
                        "text": "A story from today",
                        "privacy": Story.Privacy.PUBLIC,
                    },
                    format="multipart",
                )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story = Story.objects.get(pk=response.data["id"])
        self.assertEqual(story.author_id, user.id)
        self.assertTrue(story.media.name.startswith("stories/"))
        self.assertGreater(story.expires_at, timezone.now())
        self.assertLess(story.expires_at, timezone.now() + timedelta(hours=25))

    def test_suggested_users_exclude_followed_and_blocked_accounts(self):
        viewer = User.objects.create_user(
            username="suggestion-viewer",
            email="suggestion-viewer@example.com",
            password="StrongPass!2026",
        )
        followed = User.objects.create_user(
            username="suggestion-followed",
            email="suggestion-followed@example.com",
            password="StrongPass!2026",
        )
        blocked = User.objects.create_user(
            username="suggestion-blocked",
            email="suggestion-blocked@example.com",
            password="StrongPass!2026",
        )
        candidates = [
            User.objects.create_user(
                username=f"suggestion-{index}",
                email=f"suggestion-{index}@example.com",
                password="StrongPass!2026",
            )
            for index in range(6)
        ]
        Follow.objects.create(follower=viewer, following=followed)
        Block.objects.create(blocker=viewer, blocked=blocked)
        self.client.force_authenticate(user=viewer)

        response = self.client.get("/api/users/search/?suggested=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suggested_ids = {user["id"] for user in response.data}
        self.assertLessEqual(len(response.data), 5)
        self.assertNotIn(viewer.id, suggested_ids)
        self.assertNotIn(followed.id, suggested_ids)
        self.assertNotIn(blocked.id, suggested_ids)
        self.assertTrue(suggested_ids.issubset({user.id for user in candidates}))

    def test_registration_login_and_profile_update(self):
        registration = self.client.post("/api/users/register/", {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass!2026",
            "password2": "StrongPass!2026",
        })
        self.assertEqual(registration.status_code, status.HTTP_201_CREATED)

        login = self.client.post("/api/users/login/", {
            "username": "testuser",
            "password": "StrongPass!2026",
        })
        self.assertEqual(login.status_code, status.HTTP_200_OK)

        access = login.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        profile = self.client.patch("/api/users/profile/", {
            "first_name": "Test",
            "last_name": "User",
            "bio": "Hello",
        })
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data["first_name"], "Test")

    def test_owner_can_upload_and_remove_avatar_and_cover(self):
        user = User.objects.create_user(
            username="imageowner",
            email="imageowner@example.com",
            password="StrongPass!2026",
        )
        self.client.force_authenticate(user=user)

        with TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                def image_upload(name):
                    image = Image.new("RGB", (1, 1), color="blue")
                    content = BytesIO()
                    image.save(content, format="PNG")
                    return SimpleUploadedFile(
                        name,
                        content.getvalue(),
                        content_type="image/png",
                    )

                uploaded = self.client.patch(
                    "/api/users/profile/",
                    {
                        "profile_picture": image_upload("avatar.png"),
                        "cover_photo": image_upload("cover.png"),
                    },
                    format="multipart",
                )
                self.assertEqual(uploaded.status_code, status.HTTP_200_OK)
                self.assertTrue(
                    uploaded.data["profile"]["profile_picture"].startswith("http://testserver/")
                )
                self.assertTrue(
                    uploaded.data["profile"]["cover_photo"].startswith("http://testserver/")
                )
                profile = user.profile
                stored_names = (
                    profile.profile_picture.name,
                    profile.cover_photo.name,
                )
                self.assertTrue(profile.profile_picture.storage.exists(stored_names[0]))
                self.assertTrue(profile.cover_photo.storage.exists(stored_names[1]))

                with self.captureOnCommitCallbacks(execute=True):
                    removed = self.client.patch(
                        "/api/users/profile/",
                        {
                            "remove_profile_picture": "true",
                            "remove_cover_photo": "true",
                        },
                        format="multipart",
                    )

                self.assertEqual(removed.status_code, status.HTTP_200_OK)
                profile.refresh_from_db()
                self.assertEqual(profile.profile_picture.name, "")
                self.assertEqual(profile.cover_photo.name, "")
                self.assertFalse(profile.profile_picture.storage.exists(stored_names[0]))
                self.assertFalse(profile.cover_photo.storage.exists(stored_names[1]))

    def test_refresh_rotates_and_blacklists_the_previous_token(self):
        user = User.objects.create_user(
            username="refreshuser",
            email="refresh@example.com",
            password="StrongPass!2026",
        )
        old_refresh = str(RefreshToken.for_user(user))

        response = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotEqual(response.data["refresh"], old_refresh)

        reused_response = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(reused_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_revokes_outstanding_refresh_tokens(self):
        user = User.objects.create_user(
            username="passwordchanger",
            email="passwordchanger@example.com",
            password="StrongPass!2026",
        )
        old_refresh = str(RefreshToken.for_user(user))
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/users/password/change/",
            {
                "current_password": "StrongPass!2026",
                "new_password": "AnotherPass!2026",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivation_revokes_outstanding_refresh_tokens(self):
        user = User.objects.create_user(
            username="deactivateuser",
            email="deactivateuser@example.com",
            password="StrongPass!2026",
        )
        old_refresh = str(RefreshToken.for_user(user))
        self.client.force_authenticate(user=user)

        response = self.client.post("/api/users/account/deactivate/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_does_not_expose_token_in_response(self):
        user = User.objects.create_user(
            username="resetuser",
            email="resetuser@example.com",
            password="StrongPass!2026",
        )

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            response = self.client.post(
                "/api/users/password/reset/",
                {"email": user.email},
                format="json",
            )
            self.assertEqual(len(mail.outbox), 1)
            reset_email = mail.outbox[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data), ["detail"])
        self.assertNotIn("reset", response.data)
        self.assertIn("token=", reset_email.body)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        old_refresh = str(RefreshToken.for_user(user))
        confirm = self.client.post(
            "/api/users/password/reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "password": "ResetPass!2026",
            },
            format="json",
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        refresh_response = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_public_profile_does_not_expose_private_profile_fields(self):
        user = User.objects.create_user(
            username="publicuser",
            email="private@example.com",
            password="StrongPass!2026",
        )
        user.profile.date_of_birth = date(1990, 1, 1)
        user.profile.save(update_fields=["date_of_birth"])
        viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="StrongPass!2026",
        )
        self.client.force_authenticate(user=viewer)

        response = self.client.get(f"/api/users/{user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data["profile"]),
            {"profile_picture", "cover_photo", "bio", "location", "website"},
        )
        self.assertNotIn("email", response.data)
        self.assertNotIn("date_of_birth", response.data["profile"])

    def test_private_profile_hides_details_and_posts_until_friendship(self):
        private_user = User.objects.create_user(
            username="private-user",
            email="private-user@example.com",
            password="StrongPass!2026",
        )
        viewer = User.objects.create_user(
            username="private-viewer",
            email="private-viewer@example.com",
            password="StrongPass!2026",
        )
        post = Post.objects.create(author=private_user, content="Private post")
        private_user.profile.is_private = True
        private_user.profile.save(update_fields=["is_private"])
        self.client.force_authenticate(user=viewer)

        private_profile = self.client.get(f"/api/users/{private_user.id}/")
        self.assertEqual(private_profile.status_code, status.HTTP_200_OK)
        self.assertTrue(private_profile.data["is_private"])
        self.assertFalse(private_profile.data["can_view_profile"])
        self.assertIsNone(private_profile.data["profile"])
        self.assertEqual(
            self.client.get(f"/api/users/{private_user.id}/posts/").data,
            [],
        )
        self.assertEqual(
            self.client.get(f"/api/posts/{post.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

        FriendRequest.objects.create(
            sender=viewer,
            receiver=private_user,
            status=FriendRequest.Status.ACCEPTED,
        )
        friend_profile = self.client.get(f"/api/users/{private_user.id}/")
        self.assertTrue(friend_profile.data["can_view_profile"])
        self.assertEqual(friend_profile.data["profile"]["bio"], private_user.profile.bio)
        self.assertEqual(
            len(self.client.get(f"/api/users/{private_user.id}/posts/").data),
            1,
        )

    def test_profile_privacy_and_interaction_permissions_are_owner_controlled(self):
        from chat.models import Message
        from social.models import Comment

        owner = User.objects.create_user(
            username="policy-owner",
            email="policy-owner@example.com",
            password="StrongPass!2026",
        )
        visitor = User.objects.create_user(
            username="policy-visitor",
            email="policy-visitor@example.com",
            password="StrongPass!2026",
        )
        post = Post.objects.create(author=owner, content="Policy post")
        self.client.force_authenticate(user=owner)
        update = self.client.patch(
            "/api/users/profile/",
            {
                "is_private": True,
                "allow_comments": "friends",
                "allow_messages": "friends",
            },
            format="json",
        )
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertTrue(update.data["profile"]["is_private"])

        self.client.force_authenticate(user=visitor)
        denied_comment = self.client.post(
            f"/api/social/posts/{post.id}/comments/",
            {"content": "Not allowed"},
        )
        denied_message = self.client.post(
            f"/api/chat/conversations/{owner.id}/",
            {"content": "Not allowed"},
        )
        self.assertEqual(denied_comment.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(denied_message.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Comment.objects.filter(post=post).exists())
        self.assertFalse(Message.objects.filter(sender=visitor, receiver=owner).exists())

    def test_profile_update_cannot_grant_verified_status(self):
        user = User.objects.create_user(
            username="not-verified",
            email="not-verified@example.com",
            password="StrongPass!2026",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            "/api/users/profile/",
            {"is_verified": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.profile.refresh_from_db()
        self.assertFalse(user.profile.is_verified)
        self.assertFalse(response.data["profile"]["is_verified"])


class SocialConnectAdminTests(TestCase):
    def test_staff_dashboard_uses_admin_site_and_renders_metrics(self):
        admin_user = User.objects.create_superuser(
            username="dashboardadmin",
            email="admin@example.com",
            password="StrongPass!2026",
        )
        Post.objects.create(author=admin_user, content="Dashboard metric fixture")
        self.assertTrue(self.client.login(
            username=admin_user.username,
            password="StrongPass!2026",
        ))

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back")
        self.assertContains(response, "Total Users")
        self.assertContains(response, "Pending Reports")
        self.assertContains(response, "MAIN MENU")
        self.assertContains(response, "SOCIAL MANAGEMENT")
        self.assertContains(response, "Search users")
        self.assertNotContains(response, "recent-actions-module")
        self.assertContains(response, 'id="sc-dashboard-data"')
        self.assertContains(response, 'id="sc-topbar-nav-toggle"')
        self.assertContains(response, 'id="sc-confirm-modal"')
        self.assertContains(response, "vs previous 30d")
        self.assertEqual(response.content.count(b'class="sc-kpi-card'), 12)
        stats = response.context["dashboard_stats"]
        metric_values = {card["label"]: card["value"] for card in stats}
        self.assertEqual(metric_values["Total Users"], User.objects.count())
        self.assertEqual(metric_values["Total Posts"], Post.objects.count())
        self.assertEqual(len(stats), 12)
        # Story cards intentionally have no 30-day trend comparison.
        story_labels = {
            "Total Stories",
            "Active Stories",
            "Expired Stories",
            "Total Story Reactions",
        }
        self.assertTrue(all(card["trend"] for card in stats if card["label"] not in story_labels))
        self.assertTrue(all(card["trend"] is None for card in stats if card["label"] in story_labels))
        chart = response.context["dashboard_chart_data"]
        self.assertEqual(len(chart["labels"]), 6)
        self.assertEqual(sum(chart["posts"]), Post.objects.count())

    def test_analytics_view_handles_partial_model_permissions(self):
        from django.contrib.auth.models import Permission

        staff_user = User.objects.create_user(
            username="partialstaff",
            email="partialstaff@example.com",
            password="StrongPass!2026",
            is_staff=True,
        )
        # Posts + likes + users are visible, but comments are not. Analytics
        # must not order by annotation fields it did not add to the queryset.
        for codename, app_label in (
            ("view_post", "posts"),
            ("view_like", "social"),
            ("view_user", "users"),
        ):
            staff_user.user_permissions.add(
                Permission.objects.get(
                    codename=codename, content_type__app_label=app_label
                )
            )
        staff_user = User.objects.get(pk=staff_user.pk)
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:sc_analytics"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["analytics"]["range_days"], 30)

    def test_application_models_are_registered_and_changelists_are_reachable(self):
        from django.contrib.admin.models import LogEntry

        from chat.models import GroupConversation, GroupMembership, Message
        from notifications.models import Notification, NotificationPreference
        from posts.models import Post, PostReport
        from social.models import Comment, Follow, FriendRequest, Like
        from users.models import Profile, Story, StoryReaction, StoryView

        admin_user = User.objects.create_superuser(
            username="modeladmin",
            email="models@example.com",
            password="StrongPass!2026",
        )
        self.client.force_login(admin_user)
        models = (
            User,
            Profile,
            Post,
            PostReport,
            Comment,
            Like,
            Follow,
            FriendRequest,
            Story,
            StoryView,
            StoryReaction,
            GroupConversation,
            GroupMembership,
            Message,
            Notification,
            NotificationPreference,
            LogEntry,
        )

        for model in models:
            self.assertIn(model, admin.site._registry)
            response = self.client.get(
                reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")
            )
            self.assertEqual(response.status_code, 200, model.__name__)

    def test_non_staff_user_cannot_access_admin_dashboard(self):
        user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="StrongPass!2026",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 302)

    def test_staff_without_model_permissions_does_not_see_dashboard_counts(self):
        staff_user = User.objects.create_user(
            username="restrictedstaff",
            email="restrictedstaff@example.com",
            password="StrongPass!2026",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all(card["value"] == "—" for card in response.context["dashboard_stats"])
        )
        self.assertEqual(response.context["dashboard_chart_data"]["users"], [0] * 6)
        self.assertEqual(response.context["dashboard_chart_data"]["posts"], [0] * 6)
        self.assertFalse(response.context["recent_users"])
        self.assertFalse(response.context["recent_posts"])

    def test_navigation_exposes_all_requested_admin_areas_for_superuser(self):
        admin_user = User.objects.create_superuser(
            username="navigationadmin",
            email="navigation@example.com",
            password="StrongPass!2026",
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        for label in (
            "Analytics",
            "Friend Requests",
            "Reports &amp; Moderation",
            "Stories",
            "Messages",
            "Notifications",
            "Admin Management",
            "Roles &amp; Permissions",
            "Activity Logs",
            "Settings",
        ):
            self.assertContains(response, label)

    def test_analytics_view_uses_real_aggregates_and_honors_range(self):
        admin_user = User.objects.create_superuser(
            username="analyticsadmin",
            email="analytics@example.com",
            password="StrongPass!2026",
        )
        Post.objects.create(author=admin_user, content="Analytics fixture")
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:sc_analytics"), {"range": "7"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["analytics"]["range_days"], 7)
        self.assertEqual(len(response.context["analytics"]["labels"]), 8)
        self.assertEqual(
            response.context["analytics"]["totals"]["posts"],
            Post.objects.count(),
        )
        self.assertEqual(
            response.context["analytics"]["totals"]["registrations"],
            User.objects.count(),
        )
        self.assertContains(response, 'id="sc-analytics-data"')
        chart_data = response.context["analytics_chart_data"]
        for key in (
            "registrations_cumulative",
            "monthly_active_labels",
            "monthly_active_users",
            "engagement_values",
            "friend_requests_accepted",
        ):
            self.assertIn(key, chart_data)
        self.assertEqual(len(chart_data["monthly_active_labels"]), 6)
        self.assertEqual(len(chart_data["engagement_values"]), 2)

    @patch("config.admin_metrics._relation_available", return_value=False)
    def test_dashboard_and_analytics_survive_missing_optional_table(self, _available):
        admin_user = User.objects.create_superuser(
            username="optionalmetricadmin",
            email="optionalmetric@example.com",
            password="StrongPass!2026",
        )
        self.client.force_login(admin_user)

        index_response = self.client.get(reverse("admin:index"))
        analytics_response = self.client.get(reverse("admin:sc_analytics"))

        self.assertEqual(index_response.status_code, 200)
        self.assertEqual(analytics_response.status_code, 200)
        cards = {
            card["label"]: card
            for card in index_response.context["dashboard_stats"]
        }
        self.assertEqual(cards["Total Story Reactions"]["value"], "—")
        self.assertFalse(cards["Total Story Reactions"]["url"])
        analytics = analytics_response.context["analytics"]
        self.assertEqual(analytics["totals"]["story_reactions"], "—")
        self.assertTrue(
            all(value == "—" for value in analytics["reactions_by_type"].values())
        )

    def test_custom_admin_views_are_permission_gated(self):
        staff_user = User.objects.create_user(
            username="gatedstaff",
            email="gated@example.com",
            password="StrongPass!2026",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        for url_name in ("sc_analytics", "sc_roles", "sc_system"):
            response = self.client.get(reverse(f"admin:{url_name}"))
            self.assertEqual(response.status_code, 403, url_name)

    def test_roles_and_system_views_render_for_superuser(self):
        admin_user = User.objects.create_superuser(
            username="governanceadmin",
            email="governance@example.com",
            password="StrongPass!2026",
        )
        self.client.force_login(admin_user)

        roles_response = self.client.get(reverse("admin:sc_roles"))
        system_response = self.client.get(reverse("admin:sc_system"))

        self.assertEqual(roles_response.status_code, 200)
        self.assertEqual(system_response.status_code, 200)
        self.assertTrue(system_response.context["database_ok"])
        self.assertIn("channel_backend", system_response.context)
        self.assertNotContains(system_response, "REDIS_URL")

    def test_notification_badge_is_scoped_to_signed_in_admin(self):
        from notifications.models import Notification

        admin_user = User.objects.create_superuser(
            username="badgeadmin",
            email="badge@example.com",
            password="StrongPass!2026",
        )
        other_user = User.objects.create_user(
            username="badgeother",
            email="badgeother@example.com",
            password="StrongPass!2026",
        )
        Notification.objects.create(
            recipient=admin_user, sender=other_user, notification_type="like"
        )
        Notification.objects.create(
            recipient=admin_user, sender=other_user, notification_type="like"
        )
        Notification.objects.create(
            recipient=other_user, sender=admin_user, notification_type="like"
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["sc_notification_count"], 2)


class StoryReactionTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="reaction-author",
            email="reaction-author@example.com",
            password="StrongPass!2026",
        )
        self.reactor = User.objects.create_user(
            username="reaction-user",
            email="reaction-user@example.com",
            password="StrongPass!2026",
        )
        self.story = Story.objects.create(
            author=self.author,
            text="Reaction target",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        self.react_url = f"/api/users/stories/{self.story.pk}/react/"
        self.reactions_url = f"/api/users/stories/{self.story.pk}/reactions/"

    def test_create_update_list_and_remove_reaction(self):
        from notifications.models import Notification

        self.client.force_authenticate(user=self.reactor)

        created = self.client.post(self.react_url, {"reaction_type": "LIKE"}, format="json")

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["reaction_type"], "like")
        self.assertEqual(created.data["reaction_emoji"], "👍")
        self.assertEqual(created.data["user_id"], self.reactor.pk)
        reaction = StoryReaction.objects.get(user=self.reactor, story=self.story)
        self.assertIn(reaction, self.reactor.story_reactions.all())
        self.assertIn(reaction, self.story.reactions.all())
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.author,
                sender=self.reactor,
                notification_type="story_reaction",
            ).count(),
            1,
        )

        updated = self.client.post(self.react_url, {"reaction_type": "love"}, format="json")

        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        reaction.refresh_from_db()
        self.assertEqual(reaction.reaction_type, "love")
        self.assertEqual(StoryReaction.objects.count(), 1)

        listed = self.client.get(self.reactions_url)

        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data["story_id"], self.story.pk)
        self.assertEqual(listed.data["total_reactions"], 1)
        self.assertEqual(listed.data["user_reaction"], "love")
        self.assertEqual(listed.data["counts_by_type"]["love"], 1)
        self.assertEqual(len(listed.data["reactions"]), 1)

        stories = self.client.get("/api/users/stories/")

        self.assertEqual(stories.status_code, status.HTTP_200_OK)
        story_data = next(row for row in stories.data if row["id"] == self.story.pk)
        self.assertEqual(story_data["total_reactions"], 1)
        self.assertEqual(story_data["reaction_counts"]["love"], 1)
        self.assertEqual(story_data["user_reaction"], "love")

        removed = self.client.delete(self.react_url)

        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StoryReaction.objects.exists())
        self.assertEqual(
            self.client.delete(self.react_url).status_code, status.HTTP_404_NOT_FOUND
        )

    def test_invalid_and_own_story_reactions_are_rejected(self):
        self.client.force_authenticate(user=self.reactor)

        invalid = self.client.post(self.react_url, {"reaction_type": "invalid"}, format="json")

        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(StoryReaction.objects.exists())

        self.client.force_authenticate(user=self.author)
        own_story = self.client.post(self.react_url, {"reaction_type": "like"}, format="json")

        self.assertEqual(own_story.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(StoryReaction.objects.exists())
