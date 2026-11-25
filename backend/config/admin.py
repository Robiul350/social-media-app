from django.contrib.admin.apps import AdminConfig


class SocialConnectAdminConfig(AdminConfig):
    default_site = "config.admin_site.SocialConnectAdminSite"
