from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_email_verified"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminAction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "action_type",
                    models.CharField(
                        choices=[
                            ("user_create", "User Created"),
                            ("user_update", "User Updated"),
                            ("user_deactivate", "User Deactivated"),
                            ("user_activate", "User Activated"),
                            ("user_delete", "User Deleted"),
                            ("post_create", "Post Created"),
                            ("post_update", "Post Updated"),
                            ("post_delete", "Post Deleted"),
                            ("post_pin", "Post Pinned/Unpinned"),
                            ("comment_delete", "Comment Deleted"),
                            ("report_review", "Report Reviewed"),
                            ("report_resolve", "Report Resolved"),
                            ("report_reject", "Report Rejected"),
                            ("role_change", "Role Changed"),
                            ("settings_update", "Settings Updated"),
                            ("other", "Other Action"),
                        ],
                        max_length=30,
                    ),
                ),
                ("target_type", models.CharField(blank=True, max_length=50)),
                ("target_id", models.BigIntegerField(blank=True, null=True)),
                ("target_label", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]