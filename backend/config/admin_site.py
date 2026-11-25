from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, connections
from django.db.models import Count
from django.shortcuts import render
from django.urls import path, reverse

from chat.models import GroupConversation, Message
from notifications.models import Notification, NotificationPreference
from posts.models import Post, PostReport
from social.models import Block, Comment, Follow, FriendRequest, Like
from users.models import Story, StoryReaction

from . import admin_metrics


class SocialConnectAdminSite(AdminSite):
    site_header = "SocialConnect Administration"
    site_title = "SocialConnect Admin"
    index_title = "Dashboard"
    index_template = "admin/socialconnect_index.html"

    def get_urls(self):
        custom_urls = [
            path(
                "analytics/",
                self.admin_view(self.analytics_view),
                name="sc_analytics",
            ),
            path(
                "roles/",
                self.admin_view(self.roles_view),
                name="sc_roles",
            ),
            path(
                "system/",
                self.admin_view(self.system_view),
                name="sc_system",
            ),
        ]
        return custom_urls + super().get_urls()

    def each_context(self, request):
        context = super().each_context(request)
        permissions = self._dashboard_permissions(request)
        context["sc_navigation_groups"] = (
            self._navigation_groups(request, permissions)
            if self.has_permission(request)
            else []
        )
        context["sc_admin_avatar"] = self._profile_picture(request.user)
        context["sc_admin_role"] = self._role_label(request.user)
        context["sc_notification_count"] = (
            Notification.objects.filter(recipient=request.user, is_read=False).count()
            if request.user.is_authenticated and permissions["notifications"]
            else 0
        )
        context["sc_user_search_url"] = self._changelist_url("users", permissions)
        context["sc_post_search_url"] = self._changelist_url("posts", permissions)
        context["sc_comment_search_url"] = self._changelist_url("comments", permissions)
        context["sc_profile_url"] = (
            reverse("admin:users_user_change", args=[request.user.pk])
            if request.user.is_authenticated and permissions["users"]
            else ""
        )
        context["sc_notification_url"] = self._changelist_url(
            "notifications", permissions
        )
        context["sc_frontend_url"] = settings.FRONTEND_URL
        context["sc_system_url"] = (
            reverse("admin:sc_system") if request.user.is_superuser else ""
        )
        context["sc_analytics_url"] = (
            reverse("admin:sc_analytics")
            if self._can_view_analytics(permissions)
            else ""
        )
        return context

    def index(self, request, extra_context=None):
        context = self._dashboard_context(request)
        if extra_context:
            context.update(extra_context)
        return super().index(request, extra_context=context)

    def analytics_view(self, request):
        permissions = self._dashboard_permissions(request)
        allowed_keys = (
            "users",
            "posts",
            "comments",
            "likes",
            "friend_requests",
            "reports",
            "messages",
            "notifications",
        )
        if not self.has_permission(request) or not any(
            permissions[key] for key in allowed_keys
        ):
            raise PermissionDenied

        days = admin_metrics.normalize_range(request.GET.get("range"))
        analytics = admin_metrics.build_analytics(permissions, days)
        chart_keys = (
            "labels",
            "registrations",
            "registrations_cumulative",
            "active_users",
            "posts",
            "comments",
            "likes",
            "friend_requests_created",
            "friend_requests_accepted",
            "reports",
            "messages",
            "notifications",
            "monthly_active_labels",
            "monthly_active_users",
            "engagement_values",
        )
        context = self.each_context(request)
        context.update(
            {
                "title": "Analytics",
                "analytics": analytics,
                "analytics_chart_data": {
                    key: analytics[key] for key in chart_keys
                },
                "range_options": admin_metrics.RANGE_OPTIONS,
            }
        )
        return render(request, "admin/analytics.html", context)

    def roles_view(self, request):
        if not self.has_permission(request) or not (
            request.user.is_superuser or request.user.has_perm("auth.view_group")
        ):
            raise PermissionDenied

        groups = (
            Group.objects.annotate(
                user_count=Count("user", distinct=True),
                permission_count=Count("permissions", distinct=True),
            )
            .order_by("name")
        )
        context = self.each_context(request)
        context.update(
            {
                "title": "Roles & Permissions",
                "role_labels": self._role_labels(request.user),
                "permission_groups": groups,
                "group_admin_url": reverse("admin:auth_group_changelist"),
                "user_admin_url": reverse("admin:users_user_changelist"),
                "is_superuser": request.user.is_superuser,
                "is_staff": request.user.is_staff,
                "direct_permission_count": request.user.user_permissions.count(),
            }
        )
        return render(request, "admin/admin_roles.html", context)

    def system_view(self, request):
        if not self.has_permission(request) or not request.user.is_superuser:
            raise PermissionDenied

        try:
            connections["default"].ensure_connection()
            database_status = "Connected"
            database_ok = True
        except DatabaseError:
            database_status = "Unavailable"
            database_ok = False

        channel_backend = settings.CHANNEL_LAYERS.get("default", {}).get(
            "BACKEND", "Not configured"
        )
        context = self.each_context(request)
        context.update(
            {
                "title": "System Settings",
                "database_status": database_status,
                "database_ok": database_ok,
                "database_vendor": connections["default"].vendor,
                "redis_configured": bool(getattr(settings, "REDIS_URL", None)),
                "channel_backend": channel_backend.rsplit(".", 1)[-1],
                "asgi_application": settings.ASGI_APPLICATION or "Not configured",
                "websocket_status": (
                    "ASGI routing configured"
                    if settings.ASGI_APPLICATION
                    else "Not configured"
                ),
                "debug_enabled": bool(settings.DEBUG),
                "recent_admin_activity": list(
                    LogEntry.objects.select_related("user", "content_type")
                    .order_by("-action_time")[:8]
                ),
                "log_admin_url": reverse("admin:admin_logentry_changelist"),
            }
        )
        return render(request, "admin/admin_system.html", context)

    def _dashboard_permissions(self, request):
        models = {
            "users": get_user_model(),
            "posts": Post,
            "comments": Comment,
            "likes": Like,
            "friend_requests": FriendRequest,
            "follows": Follow,
            "blocks": Block,
            "reports": PostReport,
            "stories": Story,
            "story_reactions": StoryReaction,
            "messages": Message,
            "group_conversations": GroupConversation,
            "notifications": Notification,
            "notification_preferences": NotificationPreference,
            "groups": Group,
            "activity": LogEntry,
        }
        return {
            key: self._can_view_model(request, model)
            for key, model in models.items()
        }

    def _changelist_url(self, model_key, permissions):
        model_map = {
            "users": get_user_model(),
            "posts": Post,
            "comments": Comment,
            "friend_requests": FriendRequest,
            "likes": Like,
            "follows": Follow,
            "blocks": Block,
            "notifications": Notification,
            "notification_preferences": NotificationPreference,
            "group_conversations": GroupConversation,
            "reports": PostReport,
            "stories": Story,
            "story_reactions": StoryReaction,
            "messages": Message,
            "activity": LogEntry,
        }
        model = model_map.get(model_key)
        if not model or not permissions.get(model_key):
            return ""
        return reverse(
            f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
        )

    def _can_view_model(self, request, model):
        model_admin = self._registry.get(model)
        if not model_admin:
            return False
        permissions = model_admin.get_model_perms(request)
        return permissions.get("view", False) or permissions.get("change", False)

    @staticmethod
    def _can_view_analytics(permissions):
        return any(
            permissions[key]
            for key in (
                "users",
                "posts",
                "comments",
                "likes",
                "friend_requests",
                "reports",
                "messages",
                "notifications",
            )
        )

    def _profile_picture(self, user):
        try:
            picture = user.profile.profile_picture
            return picture.url if picture else ""
        except (AttributeError, ValueError):
            return ""

    def _role_label(self, user):
        return " · ".join(self._role_labels(user))

    def _role_labels(self, user):
        if not user or not user.is_authenticated:
            return []
        labels = []
        if user.is_superuser:
            labels.append("Super Admin")
        elif user.is_staff:
            labels.append("Admin")
        else:
            labels.append("Member")
        labels.extend(group.name for group in user.groups.all()[:3])
        return labels

    def _navigation_groups(self, request, permissions):
        user_model = get_user_model()

        def add(items, label, icon, url, allowed=True, route_prefix=""):
            if allowed and url:
                items.append(
                    self._nav_item(label, icon, url, request, route_prefix)
                )

        main = []
        add(main, "Overview", "dashboard", reverse("admin:index"), True, "index")
        add(
            main,
            "Analytics",
            "analytics",
            reverse("admin:sc_analytics"),
            self._can_view_analytics(permissions),
            "sc_analytics",
        )
        add(
            main,
            "Users",
            "users",
            self._changelist_url("users", permissions),
            permissions["users"],
            "users_user_",
        )
        add(
            main,
            "Posts",
            "posts",
            self._changelist_url("posts", permissions),
            permissions["posts"],
            "posts_post_",
        )
        add(
            main,
            "Comments",
            "comments",
            self._changelist_url("comments", permissions),
            permissions["comments"],
            "social_comment_",
        )

        social = []
        add(
            social,
            "Friend Requests",
            "friend_requests",
            self._changelist_url("friend_requests", permissions),
            permissions["friend_requests"],
            "social_friendrequest_",
        )
        add(
            social,
            "Stories",
            "stories",
            self._changelist_url("stories", permissions),
            permissions["stories"],
            "users_story_",
        )
        add(
            social,
            "Story Reactions",
            "reactions",
            self._changelist_url("story_reactions", permissions),
            permissions["story_reactions"],
            "users_storyreaction_",
        )
        add(
            social,
            "Messages",
            "messages",
            self._changelist_url("messages", permissions),
            permissions["messages"],
            "chat_message_",
        )
        add(
            social,
            "Group Conversations",
            "messages",
            self._changelist_url("group_conversations", permissions),
            permissions["group_conversations"],
            "chat_groupconversation_",
        )
        add(
            social,
            "Notifications",
            "notifications",
            self._changelist_url("notifications", permissions),
            permissions["notifications"],
            "notifications_notification_",
        )
        add(
            social,
            "Notification Preferences",
            "settings",
            self._changelist_url("notification_preferences", permissions),
            permissions["notification_preferences"],
            "notifications_notificationpreference_",
        )
        add(
            social,
            "Blocks",
            "users",
            self._changelist_url("blocks", permissions),
            permissions["blocks"],
            "social_block_",
        )
        add(
            social,
            "Likes",
            "likes",
            self._changelist_url("likes", permissions),
            permissions["likes"],
            "social_like_",
        )
        add(
            social,
            "Followers",
            "follows",
            self._changelist_url("follows", permissions),
            permissions["follows"],
            "social_follow_",
        )

        governance = []
        add(
            governance,
            "Reports & Moderation",
            "reports",
            self._changelist_url("reports", permissions),
            permissions["reports"],
            "posts_postreport_",
        )
        add(
            governance,
            "Admin Management",
            "admin",
            (
                reverse("admin:users_user_changelist") + "?is_staff__exact=1"
                if permissions["users"]
                else ""
            ),
            permissions["users"],
            "users_user_",
        )
        add(
            governance,
            "Roles & Permissions",
            "roles",
            reverse("admin:sc_roles"),
            request.user.is_superuser or request.user.has_perm("auth.view_group"),
            "sc_roles",
        )
        add(
            governance,
            "Activity Logs",
            "activity",
            self._changelist_url("activity", permissions),
            permissions["activity"],
            "admin_logentry_",
        )

        system = [
            self._nav_item(
                "Settings",
                "system",
                reverse("admin:sc_system"),
                request,
                "sc_system",
            )
            if request.user.is_superuser
            else None,
            self._nav_item(
                "Account Settings",
                "settings",
                reverse("admin:password_change"),
                request,
                "password_change",
            ),
            self._nav_item("Back to Website", "website", settings.FRONTEND_URL, request),
            {"label": "Logout", "icon": "logout", "logout": True, "active": False},
        ]
        system = [item for item in system if item]

        groups = [
            {"label": "MAIN MENU", "items": main},
            {"label": "SOCIAL MANAGEMENT", "items": social},
            {"label": "MODERATION & GOVERNANCE", "items": governance},
            {"label": "SYSTEM", "items": system},
        ]
        return [group for group in groups if group["items"]]

    def _nav_item(self, label, icon, url, request, route_prefix=""):
        match = getattr(request, "resolver_match", None)
        active = False
        if match:
            if icon == "dashboard":
                active = match.url_name == "index"
            elif route_prefix:
                active = match.url_name.startswith(route_prefix)
        return {"label": label, "icon": icon, "url": url, "active": active}

    def _dashboard_context(self, request):
        permissions = self._dashboard_permissions(request)
        chart = admin_metrics.dashboard_series()
        if not permissions["users"]:
            chart["users"] = [0] * len(chart["labels"])
        if not permissions["posts"]:
            chart["posts"] = [0] * len(chart["labels"])

        stat_cards = admin_metrics.dashboard_kpis(permissions)
        url_map = {
            "users": self._changelist_url("users", permissions),
            "posts": self._changelist_url("posts", permissions),
            "comments": self._changelist_url("comments", permissions),
            "likes": self._changelist_url("posts", permissions),
            "friend_requests": self._changelist_url("friend_requests", permissions),
            "reports": self._changelist_url("reports", permissions),
        }
        for card in stat_cards:
            card["url"] = (
                url_map.get(card["permission"], "")
                if card.get("available", True)
                else ""
            )

        recent_users = []
        if permissions["users"]:
            recent_users = list(
                get_user_model()
                .objects.select_related("profile")
                .order_by("-date_joined")[:6]
            )

        recent_posts = []
        if permissions["posts"]:
            annotations = {}
            if permissions["likes"]:
                annotations["dashboard_like_count"] = Count("likes", distinct=True)
            if permissions["comments"]:
                annotations["dashboard_comment_count"] = Count(
                    "comments", distinct=True
                )
            posts = Post.objects.select_related("author", "author__profile")
            if annotations:
                posts = posts.annotate(**annotations)
            recent_posts = list(posts.order_by("-created_at")[:5])

        recent_activity = []
        if permissions["activity"]:
            recent_activity = list(
                LogEntry.objects.select_related("user", "content_type")
                .order_by("-action_time")[:5]
            )

        return {
            "dashboard_stats": stat_cards,
            "dashboard_chart_data": chart,
            "recent_users": recent_users,
            "recent_posts": recent_posts,
            "recent_admin_activity": recent_activity,
            "analytics_url": reverse("admin:sc_analytics")
            if self._can_view_analytics(permissions)
            else "",
            "can_view_users": permissions["users"],
            "can_view_posts": permissions["posts"],
            "can_view_likes": permissions["likes"],
            "can_view_comments": permissions["comments"],
            "can_view_reports": permissions["reports"],
            "can_view_stories": permissions["stories"],
            "can_view_activity": permissions["activity"],
            "can_view_user_stats": permissions["users"],
            "can_view_post_stats": permissions["posts"],
            "can_change_users": bool(
                self._registry.get(get_user_model())
                and self._registry[get_user_model()]
                .get_model_perms(request)
                .get("change", False)
            ),
            "can_change_posts": bool(
                self._registry.get(Post)
                and self._registry[Post].get_model_perms(request).get("change", False)
            ),
        }
