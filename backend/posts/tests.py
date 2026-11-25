from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Post

User = get_user_model()


class PostPermissionTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", email="owner@example.com", password="StrongPass!2026")
        self.other = User.objects.create_user(username="other", email="other@example.com", password="StrongPass!2026")
        self.post = Post.objects.create(author=self.owner, content="Test post")

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_only_author_can_edit_or_delete_post(self):
        self.authenticate(self.other)
        edit = self.client.patch(f"/api/posts/{self.post.id}/", {"content": "Changed"})
        delete = self.client.delete(f"/api/posts/{self.post.id}/")
        self.assertEqual(edit.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_create_post(self):
        self.authenticate(self.owner)
        response = self.client.post("/api/posts/", {"content": "A new post"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_post_is_rejected(self):
        self.authenticate(self.owner)
        response = self.client.post("/api/posts/", {"content": "   "})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_author_can_retrieve_and_edit_own_draft(self):
        self.authenticate(self.owner)
        created = self.client.post(
            "/api/posts/",
            {"content": "Unfinished thought", "is_draft": True},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        draft_id = created.data["id"]

        detail = self.client.get(f"/api/posts/{draft_id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)

        edit = self.client.patch(
            f"/api/posts/{draft_id}/",
            {"content": "Finished thought"},
            format="json",
        )
        self.assertEqual(edit.status_code, status.HTTP_200_OK)

        drafts = self.client.get("/api/posts/?drafts=true")
        self.assertEqual(drafts.status_code, status.HTTP_200_OK)
        self.assertIn(draft_id, [post["id"] for post in drafts.data])

        self.authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/posts/{draft_id}/").status_code, 404)

    def test_hashtags_are_synced_when_a_post_is_edited(self):
        self.authenticate(self.owner)
        created = self.client.post(
            "/api/posts/",
            {"content": "Shipping #Django today"},
            format="json",
        )
        post = Post.objects.get(pk=created.data["id"])
        self.assertEqual(list(post.hashtags.values_list("name", flat=True)), ["django"])

        self.client.patch(
            f"/api/posts/{post.id}/",
            {"content": "Now using #React"},
            format="json",
        )
        self.assertEqual(list(post.hashtags.values_list("name", flat=True)), ["react"])

    def test_repost_rejects_own_post_and_is_idempotent(self):
        self.authenticate(self.owner)
        own = self.client.post(f"/api/posts/{self.post.id}/repost/")
        self.assertEqual(own.status_code, status.HTTP_400_BAD_REQUEST)

        self.authenticate(self.other)
        first = self.client.post(f"/api/posts/{self.post.id}/repost/")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(f"/api/posts/{self.post.id}/repost/")
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data["id"], second.data["id"])

    def test_poll_vote_keeps_exactly_one_vote_per_user_per_poll(self):
        from .models import Poll, PollOption, PollVote

        poll = Poll.objects.create(post=self.post, question="Pick one")
        option_a = PollOption.objects.create(poll=poll, text="A")
        option_b = PollOption.objects.create(poll=poll, text="B")
        self.authenticate(self.other)

        self.client.post(f"/api/posts/{self.post.id}/poll/{option_a.id}/vote/")
        self.client.post(f"/api/posts/{self.post.id}/poll/{option_b.id}/vote/")

        self.assertEqual(
            PollVote.objects.filter(option__poll=poll, user=self.other).count(),
            1,
        )
        self.assertTrue(
            PollVote.objects.filter(option=option_b, user=self.other).exists()
        )
