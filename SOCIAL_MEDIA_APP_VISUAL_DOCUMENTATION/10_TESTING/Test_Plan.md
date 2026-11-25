# Test Plan

## Scope

This plan is source-derived. It describes what should be verified for the documented requirements; it does not claim that any command currently passes. Current results for backend tests, frontend lint, frontend build, and browser smoke checks are `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless executed and recorded.

## Verification commands

```powershell
# backend/
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb

# frontend/
npm.cmd run lint
npm.cmd run build
```

`makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`.

## Test levels

| Level | Source evidence | Coverage focus |
| --- | --- | --- |
| Model/schema | 26 Django tables; migrations for users/posts/social/notifications/chat | Constraints, soft delete, relationships, migration alignment |
| API | DRF APIView/generics endpoints under five prefixes | Auth, ownership, visibility, toggles, state transitions, error codes |
| WebSocket | Channels `WebsocketCommunicator` tests against `config.asgi.application` | JWT close codes, chat events, notification delivery |
| Frontend | No test files or `npm test` script found | Lint/build only; interaction tests are proposed, not existing |
| Admin | Custom admin views and metrics | Permission masking, range normalization, KPI aggregation, activity source |
| Browser/UX | No verified smoke results in source | Responsive layout, focus traps, dialogs; `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |

## Proposed test cases

Test IDs below are proposals for the documentation package, not claims of existing test methods.

| ID | Requirement | Objective | Expected source-aligned result |
| --- | --- | --- | --- |
| TC-001 | UR-001 | Verify register account for guest using UI-SCR-002. | Source-aligned behavior for Implemented; API API-010; models users_user, users_profile. |
| TC-002 | UR-002 | Verify login and receive jwt for guest using UI-SCR-001. | Source-aligned behavior for Implemented; API API-011; models users_user. |
| TC-003 | UR-003 | Verify refresh access token for registered user using Global API client. | Source-aligned behavior for Implemented; API API-012; models users_user. |
| TC-004 | UR-004 | Verify logout / blacklist refresh for registered user using Navbar account menu. | Source-aligned behavior for Implemented; API API-013; models users_user. |
| TC-005 | UR-005 | Verify request password reset for guest using No SPA route (proposed mockup). | Source-aligned behavior for Backend only; API API-015; models users_user. |
| TC-006 | UR-006 | Verify confirm password reset for guest using No SPA route. | Source-aligned behavior for Backend only; API API-016; models users_user. |
| TC-007 | UR-007 | Verify deactivate account for registered user using No SPA screen. | Source-aligned behavior for Backend only; API API-017; models users_user. |
| TC-008 | UR-008 | Verify edit own profile and privacy for registered user using UI-SCR-007. | Source-aligned behavior for Implemented; API API-018, API-019; models users_profile. |
| TC-009 | UR-009 | Verify search and discover people for registered user using UI-SCR-008. | Source-aligned behavior for Implemented; API API-020; models users_user, users_profile. |
| TC-010 | UR-010 | Verify view public profile for registered user using UI-SCR-006. | Source-aligned behavior for Implemented; API API-027, API-028; models users_user, users_profile. |
| TC-011 | UR-011 | Verify create/edit/delete post for content author using UI-SCR-003. | Source-aligned behavior for Implemented; API API-031, API-032; models posts_post. |
| TC-012 | UR-012 | Verify browse filtered feed for registered user using UI-SCR-003. | Source-aligned behavior for Implemented; API API-040; models posts_post, social_block. |
| TC-013 | UR-013 | Verify like post for registered user using UI-SCR-003, UI-SCR-005. | Source-aligned behavior for Implemented; API API-041; models social_like. |
| TC-014 | UR-014 | Verify comment and reply for registered user using UI-SCR-005. | Source-aligned behavior for Implemented; API API-042, API-043; models social_comment. |
| TC-015 | UR-015 | Verify bookmark post for registered user using UI-SCR-011. | Source-aligned behavior for Implemented; API API-033; models posts_bookmark. |
| TC-016 | UR-016 | Verify pin / repost / report post for content author / registered user using UI-SCR-003. | Source-aligned behavior for Partial; API API-034, API-035, API-037; models posts_post, posts_postreport. |
| TC-017 | UR-017 | Verify create and view story for registered user using UI-SCR-004. | Source-aligned behavior for Implemented; API API-021, API-022, API-023; models users_story, users_storyview. |
| TC-018 | UR-018 | Verify react to story for registered user using No reaction control. | Source-aligned behavior for Backend only; API API-024, API-026; models users_storyreaction. |
| TC-019 | UR-019 | Verify follow / unfollow user for registered user using UI-SCR-006, UI-SCR-008. | Source-aligned behavior for Implemented; API API-046, API-047; models social_follow. |
| TC-020 | UR-020 | Verify send/accept/reject friend request for registered user using UI-SCR-009. | Source-aligned behavior for Partial; API API-048—API-052; models social_friendrequest. |
| TC-021 | UR-021 | Verify block / unblock user for registered user using UI-SCR-006. | Source-aligned behavior for Partial; API API-059, API-060; models social_block. |
| TC-022 | UR-022 | Verify manage notification preferences for registered user using Notification settings dialog. | Source-aligned behavior for Implemented; API API-074, API-075; models notifications_notificationpreference. |
| TC-023 | UR-023 | Verify read notifications and counts for registered user using UI-SCR-013. | Source-aligned behavior for Implemented; API API-070—API-073; models notifications_notification. |
| TC-024 | UR-024 | Verify send direct message for message participant using UI-SCR-012. | Source-aligned behavior for Implemented; API API-081, API-082, API-090; models chat_message. |
| TC-025 | UR-025 | Verify send typing/presence/read events for message participant using UI-SCR-012. | Source-aligned behavior for Implemented; API API-083, API-090; models chat_message. |
| TC-026 | UR-026 | Verify create group conversation for group member using No SPA screen. | Source-aligned behavior for Backend only; API API-087, API-088; models chat_groupconversation, chat_groupmembership. |
| TC-027 | UR-027 | Verify send group message for group member using No SPA screen. | Source-aligned behavior for Backend only; API API-089; models chat_message. |
| TC-028 | UR-028 | Verify vote in poll for registered user using No SPA control. | Source-aligned behavior for Backend only; API API-036; models posts_pollvote. |
| TC-029 | UR-029 | Verify submit post report for registered user using UI-SCR-003. | Source-aligned behavior for Partial; API API-037; models posts_postreport. |
| TC-030 | UR-030 | Verify review admin analytics for admin using Admin analytics page. | Source-aligned behavior for Implemented; API API-002; models Django aggregates. |
| TC-031 | UR-031 | Verify manage users via admin actions for admin using Django admin changelist. | Source-aligned behavior for Implemented; API API-002; models users_user. |
| TC-032 | UR-032 | Verify view system status for admin using Admin system page. | Source-aligned behavior for Implemented; API API-002; models Django LogEntry. |
| TC-033 | UR-033 | Verify persist jwt session in browser storage for registered user using Global session state. | Source-aligned behavior for Implemented; API API-011, API-012; models None. |
| TC-034 | UR-034 | Verify use light/dark theme for registered user using Navbar / admin theme toggle. | Source-aligned behavior for Implemented; API None; models None. |
| TC-035 | UR-035 | Verify cache only the app shell offline for registered user using PWA shell. | Source-aligned behavior for Partial; API None; models None. |

## Risks and exclusions

- Do not assert a current pass count from historical reports.
- No frontend automated tests exist to run.
- No production deployment, email delivery, Redis runtime, or media authorization test was verified.
- Concurrency and raw-ORM constraint tests were not found; proposed cases should be added only if approved.
