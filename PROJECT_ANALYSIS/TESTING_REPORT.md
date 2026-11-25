# Testing Report

## Audit boundary

This report documents the **test suite structure and coverage evidence found in source**. It is not a record of a successful test run performed during this audit. No Django test command, Django check, migration check, lint, or build was executed as part of the read-only analysis. Historical root reports contain several conflicting pass counts (22, 30, 40, 52, and 60) and build sizes; those numbers are treated as dated snapshots, not current results.

The current source contains **65 test methods** across five app test files. That number is a count of `def test_*` definitions, not a claim that 65 tests pass.

## Verification commands

From `backend/`, using the root virtual environment:

```powershell
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb
..\venv\Scripts\python.exe manage.py test social --keepdb
..\venv\Scripts\python.exe manage.py test social.tests.SocialFeatureTests.test_feed_pagination_is_opt_in_and_returns_next_page --keepdb
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

Notes:

- Backend tests use real PostgreSQL; the configured database user must be able to reuse/create the test database.
- `--keepdb` avoids the interactive database-creation prompt that breaks non-interactive shells.
- Historical full-suite timings range from roughly 5 to 13 minutes; do not treat any timing as current.
- `npm.cmd` is required on this machine because plain `npm` resolves to a PowerShell script blocked by execution policy.
- There is no `npm test` script and no frontend test files. Vitest/jsdom/testing-library are installed as dev dependencies but unused.

## Test inventory

### Summary by app

| App / file | Test classes | Test methods | Test style |
| --- | ---: | ---: | --- |
| `users/tests.py` | 3 | 26 | `APITestCase` + `TestCase` |
| `posts/tests.py` | 1 | 7 | `APITestCase` |
| `social/tests.py` | 1 | 14 | `APITestCase` |
| `notifications/tests.py` | 2 | 5 | `APITestCase` + `TransactionTestCase` |
| `chat/tests.py` | 2 | 13 | `APITestCase` + `TransactionTestCase` |
| **Total** | **9** | **65** | Django runner |

### `users/tests.py`

#### `AuthenticationAndProfileTests` — 13 tests

| Test | What it verifies |
| --- | --- |
| `test_story_privacy_expiration_and_blocks_are_enforced_for_lists_and_views` | Public/followers/friends/expired story visibility, private-profile gating, and either-direction blocks. |
| `test_story_upload_accepts_media_without_client_supplied_expiry` | Multipart upload, server-assigned author, `stories/` path, and ~24-hour server-set expiry. |
| `test_suggested_users_exclude_followed_and_blocked_accounts` | `?suggested=true` returns at most five users and excludes self, followed, and blocked accounts. |
| `test_registration_login_and_profile_update` | Register → login → Bearer access → PATCH profile chain. |
| `test_owner_can_upload_and_remove_avatar_and_cover` | Image upload and `on_commit` deletion of replaced/removed files. |
| `test_refresh_rotates_and_blacklists_the_previous_token` | Reuse of an old refresh token returns 401. |
| `test_password_change_revokes_outstanding_refresh_tokens` | Password change invalidates all refresh tokens. |
| `test_deactivation_revokes_outstanding_refresh_tokens` | Deactivation sets `is_active=False` and revokes tokens. |
| `test_password_reset_does_not_expose_token_in_response` | Generic reset response, one email, no uid/token in JSON, confirm works, tokens revoked. |
| `test_public_profile_does_not_expose_private_profile_fields` | Only allowed profile keys are exposed; email/date-of-birth are hidden. |
| `test_private_profile_hides_details_and_posts_until_friendship` | Profile/posts/detail hidden until friendship is accepted. |
| `test_profile_privacy_and_interaction_permissions_are_owner_controlled` | `friends` comment/message policies produce 403 for non-allowed users. |
| `test_profile_update_cannot_grant_verified_status` | `is_verified` is read-only and cannot be self-granted. |

#### `SocialConnectAdminTests` — 11 tests

| Test | What it verifies |
| --- | --- |
| `test_staff_dashboard_uses_admin_site_and_renders_metrics` | Custom admin site renders dashboard with 12 KPI cards, trends, and six chart labels. |
| `test_analytics_view_handles_partial_model_permissions` | Partial model-view permissions do not break analytics aggregation. |
| `test_application_models_are_registered_and_changelists_are_reachable` | 17 models registered and changelists reachable. |
| `test_non_staff_user_cannot_access_admin_dashboard` | Non-staff denial. |
| `test_staff_without_model_permissions_does_not_see_dashboard_counts` | Restricted counts/charts show `—` and zeroed data instead of real values. |
| `test_navigation_exposes_all_requested_admin_areas_for_superuser` | Superuser navigation areas are present. |
| `test_analytics_view_uses_real_aggregates_and_honors_range` | Real aggregates, `?range=7` yields eight daily labels, chart keys present. |
| `test_dashboard_and_analytics_survive_missing_optional_table` | `_relation_available` guard handles a missing optional table. |
| `test_custom_admin_views_are_permission_gated` | Analytics/roles/system views reject unauthorized staff. |
| `test_roles_and_system_views_render_for_superuser` | Roles/system pages render. |
| `test_notification_badge_is_scoped_to_signed_in_admin` | Unread notification badge is scoped to the signed-in admin. |

#### `StoryReactionTests` — 2 tests

| Test | What it verifies |
| --- | --- |
| `test_create_update_list_and_remove_reaction` | Create/update/list/count/remove reactions, emoji, and notification behaviour. |
| `test_invalid_and_own_story_reactions_are_rejected` | Invalid type and self-reaction rejection. |

### `posts/tests.py`

#### `PostPermissionTests` — 7 tests

| Test | What it verifies |
| --- | --- |
| `test_only_author_can_edit_or_delete_post` | Non-author PATCH/DELETE returns 403. |
| `test_author_can_create_post` | Author can create a valid post. |
| `test_empty_post_is_rejected` | Blank content without media returns 400. |
| `test_author_can_retrieve_and_edit_own_draft` | Author can retrieve/edit own draft; other user gets 404. |
| `test_hashtags_are_synced_when_a_post_is_edited` | `#tag` parsing and M2M sync on edit. |
| `test_repost_rejects_own_post_and_is_idempotent` | Own repost 400; repeated repost returns 200 after first 201. |
| `test_poll_vote_keeps_exactly_one_vote_per_user_per_poll` | Sequential vote changes leave one vote per poll. |

### `social/tests.py`

#### `SocialFeatureTests` — 14 tests

| Test | What it verifies |
| --- | --- |
| `test_like_and_follow_create_notifications` | Like/follow notification creation. |
| `test_followers_and_following_lists_return_the_authenticated_users_connections` | Follower/following list contents. |
| `test_feed_pagination_is_opt_in_and_returns_next_page` | Bare array without `page`; paginated dict with `page`. |
| `test_feed_shows_three_unfollowed_authors_in_newest_order_with_interaction_metadata` | Feed ordering, author fields, like/bookmark/share metadata. |
| `test_feed_includes_public_posts_from_unfollowed_accounts` | Public posts from non-followed users appear. |
| `test_feed_and_interactions_hide_private_draft_and_scheduled_posts` | Hidden content for viewer and owner; interactions blocked. |
| `test_comment_replies_are_supported_and_must_stay_on_the_same_post` | Parent validation for replies. |
| `test_existing_comment_cannot_be_reparented_to_create_a_cycle` | Reparenting cycle prevention. |
| `test_friend_requests_reject_self_duplicate_and_reverse_pending` | Self/duplicate/reverse-pending handling. |
| `test_friend_request_acceptance_list_unfriend_and_profile_status` | Accept, list, unfriend, profile status. |
| `test_sender_can_cancel_and_receiver_can_reject_requests` | Cancel and reject paths. |
| `test_mutual_friends_endpoint_returns_shared_accepted_connections` | Mutual-friends intersection. |
| `test_block_list_create_duplicate_self_and_unblock` | Block create/duplicate/self/unblock. |
| `test_block_hides_profiles_and_prevents_social_and_chat_access` | Block effects across profile, post, search, follow, friend request, and chat; history retention. |

### `notifications/tests.py`

#### `NotificationApiTests` — 3 tests

| Test | What it verifies |
| --- | --- |
| `test_notification_list_and_mark_read_are_scoped_to_recipient` | Recipient-only list/read. |
| `test_notification_hides_post_reference_after_block` | Post ID masked to `null` after block. |
| `test_reply_notifies_parent_comment_author` | Reply notification targets parent comment author, not post owner. |

#### `NotificationWebsocketTests` — 2 tests

| Test | What it verifies |
| --- | --- |
| `test_jwt_user_receives_new_notification` | JWT socket receives `{"type":"notification",...}` after `create_notification`. |
| `test_websocket_rejects_missing_jwt` | Missing token closes with 4401. |

### `chat/tests.py`

#### `ConversationTests` — 7 tests

| Test | What it verifies |
| --- | --- |
| `test_rest_message_creates_notification_for_recipient` | REST message notification side effect. |
| `test_chat_attachment_rejects_unsupported_file_types` | Attachment MIME rejection. |
| `test_blocked_user_cannot_read_or_list_the_blocked_conversation` | Block enforcement on REST chat reads. |
| `test_soft_deleted_messages_are_excluded_from_history_and_unread_counts` | `deleted_at` filtering. |
| `test_group_creation_rejects_unknown_and_blocked_members` | Group member validation. |
| `test_group_messages_do_not_break_direct_conversation_list` | Group/direct list separation. |
| `test_group_messages_from_blocked_members_are_hidden` | Blocked sender filtering in group messages. |

#### `ChatWebsocketTests` — 6 tests

| Test | What it verifies |
| --- | --- |
| `test_jwt_authenticated_users_exchange_messages_typing_and_presence` | Pair exchange, echo, typing, and presence frames. |
| `test_websocket_rejects_missing_or_invalid_jwt` | 4401 for missing/invalid token. |
| `test_websocket_rejects_inactive_user` | 4401 for inactive user. |
| `test_websocket_rejects_blocked_conversation` | 4403 for blocked pair. |
| `test_marking_messages_read_broadcasts_a_receipt` | REST read receipt broadcast. |
| `test_rest_message_is_delivered_to_an_active_websocket` | REST-originated `chat_message` delivery. |

---

## Coverage by architectural area

| Area | Coverage level | Evidence |
| --- | --- | --- |
| Registration/login/profile | Strong | 13 profile/auth tests including privacy, upload, token lifecycle. |
| Admin | Strong | 11 tests covering KPIs, permissions, charts, registration, nav, roles/system. |
| Stories | Moderate | Privacy, expiry, upload, reactions; no reaction-update notification regression. |
| Posts | Moderate | Author permissions, drafts, hashtags, repost, sequential poll vote; little media validation. |
| Social graph | Strong | Feed, likes/follows/comments, requests, mutual friends, blocks. |
| Notifications | Moderate | List/read/block masking/reply routing/WS delivery; preferences and read-all untested. |
| Direct chat | Moderate/strong | REST notification, attachments, blocks, soft delete, WS auth/presence/typing/read/REST delivery. |
| Group chat | Weak | Creation validation and message filtering only; no WS or membership management tests. |
| Frontend | **None** | No test files or test script. |
| Deployment/production | **None** | No infrastructure/runtime verification suite. |

---

## Notable test-quality strengths

- Uses Django's built-in runner and appropriate test base classes.
- API tests use `APITestCase` with authenticated clients, enabling direct contract-level assertions.
- WebSocket tests use Channels' `TransactionTestCase` pattern with real ASGI application/communicator behaviour, not the ordinary Django test client.
- Several privacy-sensitive behaviours are explicitly tested: story audience, private profile, block propagation, notification masking.
- Token rotation/blacklisting and password lifecycle revocation are covered.
- The feed pagination contract has a dedicated test, including the opt-in `page` behaviour.
- Admin permission gating has substantial coverage, including partial permissions.

---

## Coverage gaps

### Users / authentication

- `GET /api/users/profile/` success response is not asserted directly as a standalone test.
- Logout endpoint is not covered.
- Wrong-current-password branch of password change is not covered.
- General `?search=` / `?q=` path is not directly covered except indirectly through block tests.
- Positive `GET /api/users/<id>/posts/` response is not covered.
- `email_verified` has no writer or test.
- Password-reset email backend failure path is not covered.
- WebSocket reconnection after expired token is not covered.

### Posts

- `PinToggleView` untested.
- `PostReportView` untested.
- Bookmark toggle itself untested; only bookmarked filtering is covered.
- Author `PATCH`/`DELETE` success and `PUT` untested; only forbidden case is covered.
- Image/video size and MIME validation untested.
- Poll expiry branch untested.
- Scheduled publication/due visibility is covered indirectly by hiding, but no publisher exists.
- `PostImage` and images-only validation untested.

### Social

- `CommentDetailView` GET/PATCH success untested.
- `CommentReactionView` untested.
- Blocked branch of friend-request response untested.
- Mention notification behaviour untested, especially trailing punctuation.
- `page_size` interaction with feed pagination untested.
- Followers-only/friends-only post visibility untested.
- `can_message` serializer flag untested.
- Accept/reject notification absence is not asserted because no notification is implemented.

### Notifications

- `read-all/`, `unread-count/`, and `preferences/` GET/PATCH untested.
- Per-type preference opt-out in `create_notification` untested.
- `NotificationSerializer.comment` masking untested.
- Read-state WebSocket update absence is not asserted.
- WebSocket client-message ignore path untested.

### Chat

- `MessageDetailView` PATCH/DELETE success and corresponding `message_updated` / `message_deleted` broadcasts untested.
- `GroupConversationView` GET untested.
- Non-member group message access untested.
- Multi-conversation unread counts untested.
- Self-message 400 branch untested.
- WebSocket error branches (non-string, blank, >5000 chars) untested.
- WS 4400 self-chat and 4404 missing-user closes untested.
- Mid-session permission recheck untested.
- Successful attachment upload (as opposed to unsupported type rejection) untested.
- No group WebSocket because none exists.

### Admin

- Roles view with only `auth.view_group` untested.
- Invalid `?range=` fallback untested.
- `admin_metrics.py` lacks focused unit tests.
- `AdminAction` model is never written and untested.

### Frontend

- No component tests.
- No router/guard tests.
- No Axios refresh interceptor tests.
- No WebSocket reconnect/backoff tests.
- No form validation or accessibility tests.
- No lint/build result is claimed in this audit.

---

## Known historical verification claims

Existing root reports claim, at different dates:

- `manage.py check`: PASS.
- `makemigrations --check --dry-run`: no changes in some snapshots.
- Full suite: 22, 30, 40, 52, or 60 passed at different times; one report records 60 tests with one failure and an unfinished placeholder for a final run.
- `npm.cmd run lint`: PASS in later snapshots.
- `npm.cmd run build`: PASS, with differing artifact sizes.
- Daphne smoke: `/` 200, `/admin/login/` 200, protected routes 401 without token.
- Browser smoke: partial/unauthenticated only; no successful authenticated login in the latest changes.

These claims are useful as history but are **not current evidence**. The authoritative action is to re-run the commands above in the configured environment.

---

## Risk register for testing

| Risk | Severity | Impact |
| --- | --- | --- |
| No frontend tests despite complex WebSocket/reconnect logic | High | Regressions in search, messaging, notifications, and auth refresh can ship undetected. |
| Historical pass counts conflict | Medium | Reports can overstate current correctness. |
| Full suite depends on real PostgreSQL and is slow | Medium | Developers may skip it; `--keepdb` mitigates interactivity but not duration. |
| Migration drift not verified in this audit | Medium | Potential Block index-name mismatch should be checked with `makemigrations --check --dry-run`. |
| WebSocket tests cover auth and basic exchange, not all error frames | Medium | Edge-case protocol regressions possible. |
| No authenticated browser smoke evidence for latest UI/admin changes | Medium | Visual and client-server integration regressions possible. |
| No production/runtime tests for Redis multi-worker fan-out | High | Real-time delivery may fail in deployment. |
| Email delivery untested | Medium | Password reset may silently fail. |

---

## Recommended next tests

### Priority 1 — High value, low effort

1. Add tests for `MessageDetailView` PATCH/DELETE and their WebSocket broadcasts.
2. Test notification preferences and `read-all/` / `unread-count/`.
3. Test bookmark toggle, pin toggle, report creation, and expired poll vote.
4. Add a regression test proving story reaction updates do **not** emit duplicate notifications.
5. Add a test for rejection of client-supplied `deleted_at` / `edited_at` in message creation.
6. Add a test asserting one poll vote per poll under concurrent-style sequential updates.

### Priority 2 — Medium effort

1. Frontend Vitest tests for Axios refresh, route guard, `UserSearch` debounce/cache path, and notification `openNotification` busy-state behaviour.
2. WebSocket tests for self-chat, missing user, invalid message frames, and token expiry.
3. Admin tests for invalid analytics range and restricted roles access.
4. Search/profile interaction policy tests for followers/friends visibility.

### Priority 3 — Infrastructure/runtime

1. Run `manage.py check` and `makemigrations --check --dry-run` in the configured environment.
2. Run full backend suite with `--keepdb` and record the actual current result.
3. Run `npm.cmd run lint` and `npm.cmd run build` and record actual current output.
4. Perform an authenticated browser smoke test across login, feed post, comment, story creation, direct message, notification read, and admin dashboard.
5. Verify WebSocket fan-out with at least two ASGI workers and Redis configured.

---

## Testing verdict

The backend has a respectable, privacy-aware test suite for an advanced coursework project, especially around authentication, feed visibility, blocks, admin, and WebSocket basics. It is not comprehensive: many toggle endpoints, preference flows, message edit/delete paths, media validation branches, and all frontend behaviour remain untested. Current pass/fail status is **Needs Verification** and must be established by running the documented commands rather than citing historical reports.
