# Implementation Status

## Purpose

This document converts the source audit into a readiness matrix and release checklist. It separates what is **working**, what is **working with caveats**, what is **partial/backend-only**, and what is **missing**. It does not claim that a current full test/lint/build run has passed; see `TESTING_REPORT.md` for verification commands and historical caveats.

## Readiness scale

| Level | Meaning |
| --- | --- |
| **Ready** | Implemented backend + reachable SPA flow + meaningful test coverage; no known blocking defect. |
| **Ready with caveats** | Implemented end to end, but with a known non-blocking bug, UX gap, or environment dependency. |
| **Needs work** | Core code exists but an important part of the flow, UI, notification, ordering, or validation is incomplete. |
| **Backend only** | REST/WebSocket/model capability exists but no SPA surface was found. |
| **Missing** | No implementation found in inspected source. |
| **Needs Verification** | Requires runtime/environment evidence before sign-off. |

---

## Module readiness matrix

| Module / capability | Backend | Frontend | Tests | Readiness | Blocking items |
| --- | --- | --- | --- | --- | --- |
| Registration + login | Complete | Complete | 3 auth/profile tests | **Ready with caveats** | Username-only login; localStorage tokens; guard checks token presence only. |
| JWT refresh + logout | Complete with rotation/blacklist | Complete in Axios interceptor | Rotation + deactivation/password revocation covered | **Ready with caveats** | Logout endpoint itself untested; WS token refresh not transparent. |
| Password change/reset/deactivate | Complete API | No dedicated screens | Reset/confirm + revocation covered; logout/change branch gaps | **Backend only** | No SPA routes for reset confirm/deactivate; email backend not configured. |
| Profile CRUD + privacy | Complete | Complete via `EditProfile.jsx`/`UserProfile.jsx` | Strong | **Ready with caveats** | No load retry; invalid file selection still allows submit. |
| User search + suggestions | Complete | Complete via `UserSearch.jsx` | Suggestions covered | **Ready with caveats** | Render-phase state update and abort/ref loading bug. |
| Stories list/create/view | Complete | Complete via `Stories.jsx` | Privacy/expiry/upload covered | **Ready with caveats** | No reaction UI; viewed IDs local; duplicate reaction notifications on update. |
| Story reactions | Complete endpoint | No UI | Basic create/update/list covered | **Backend only / Needs work** | Duplicate notifications; no preference producer surfaced in UI. |
| Posts CRUD + audience + drafts | Complete | Complete via `home.jsx` | Permission/draft/blank/hashtag covered | **Ready with caveats** | `?drafts=true` returns all authored posts; edit rejects images-only media. |
| Pins | Toggle endpoint | Menu action | Untested | **Needs work** | `is_pinned` has no ordering effect. |
| Reposts | Endpoint | Menu action | Idempotency covered | **Ready with caveats** | No notification; unconditional success notice. |
| Polls | Vote endpoint + models | No UI | Sequential single-vote covered | **Backend only / Needs work** | No poll CRUD/UI; DB uniqueness not per poll; expiry untested. |
| Reports | Create endpoint | Report form | Untested | **Needs work** | No status/moderation workflow/resolve endpoint. |
| Hashtags | Derived M2M | No UI | Sync-on-edit covered | **Backend only** | No browse/search endpoint or page. |
| Scheduling | Field + visibility filter | No UI | Hiding covered; no publisher | **Backend only / Needs work** | No publisher job or scheduler UI. |
| Multi-image posts | Model + read-only serializer | Gallery reads `post.images` | Untested | **Missing / Not reachable** | No upload endpoint; images-only posts rejected. |
| Likes + bookmarks | Complete | Complete via `PostActions.jsx` | Like covered; toggle untested | **Ready** | Minor UX/error-state issues only. |
| Comments + replies + mentions | Complete | Complete via `PostActions.jsx` | Parent/cycle/reply routing covered | **Ready with caveats** | Mention regex trailing-punctuation bug; no mention picker. |
| Comment reactions | Toggle endpoint | No UI | Untested | **Backend only / Needs work** | No notification; not registered in admin. |
| Follow / friends / blocks | Complete | Complete across profile/search/requests/connections | Strong social test coverage | **Ready** | Block list screen absent; history retention by design. |
| Friend request accept/reject | Complete | Complete | Covered | **Ready with caveats** | No notification to sender; rejected requests resurrect on resend. |
| Notifications REST + WS | Complete | Complete via `Notifications.jsx` + settings dialog | REST and WS basics covered | **Ready with caveats** | Read actions emit no WS update; no pagination; busy-navigation bug. |
| Direct chat REST + WS | Complete | Complete via `Messages.jsx` | Strong auth/flow coverage | **Ready with caveats** | Attachment-only send impossible; no edit/delete UI; no history pagination. |
| Group chat | REST models/endpoints | No UI | Creation/filtering only | **Backend only / Needs work** | No group WS; membership flags unused; no membership management. |
| Custom admin | Dashboard/analytics/roles/system | Separate Django site | Strong admin tests | **Ready with caveats** | Likes KPI link wrong; pending reports count all rows; browser smoke unverified. |
| SPA shell/nav/dialogs/dark mode | Not applicable | Complete and polished | No frontend tests | **Ready with caveats** | Duplicated CSS; dead `Profile.jsx`; icon semantics minor. |
| PWA/offline shell | Not applicable | SW + manifest | Untested | **Partial** | No offline data, push, install flow, or proper icon set. |
| Frontend automated tests | Not applicable | None | None | **Missing** | Dev dependencies installed but unused. |
| Production deployment config | Partial settings support | Static build expected | No tests | **Needs Verification / Missing** | No reverse proxy, ASGI process config, static/media host, CI/CD. |

---

## Feature completion scorecard

| Category | Implemented | Ready with caveats / Partial | Backend only | Missing / Not Found |
| --- | ---: | ---: | ---: | ---: |
| Identity/profile | 3 | 2 | 3 | 1 |
| Content/posts | 2 | 5 | 4 | 1 |
| Social graph | 4 | 3 | 2 | 0 |
| Stories | 1 | 2 | 1 | 0 |
| Notifications | 1 | 1 | 0 | 0 |
| Messaging | 1 | 1 | 1 | 0 |
| Admin | 1 | 1 | 0 | 0 |
| Frontend/PWA | 1 | 3 | 0 | 2 |
| Deployment/tooling | 0 | 1 | 0 | 3 |

Counts are feature groups from the readiness matrix, not line counts or test counts. They are intended for report discussion, not automated scoring.

---

## End-to-end flow sign-off

| Flow | Sign-off | Reason |
| --- | --- | --- |
| Guest registration → login → feed | **Conditional pass** | Source-complete; current test/lint/build not run in this audit. |
| Create post with text/image/video → like/comment → bookmark | **Conditional pass** | Core endpoints and UI present; edit-with-images caveat. |
| Follow/friend request → accept → message → notification | **Conditional pass** | Accept/reject notifications absent but flow works. |
| Story create → view → react | **Conditional hold** | Reaction UI missing. |
| Poll create → vote | **Blocked** | No poll creation UI or API; vote endpoint alone. |
| Report → admin review | **Blocked** | No status/moderation action. |
| Group creation → group messaging | **Blocked** | No UI and no group WebSocket. |
| Password reset via email link | **Blocked** | Email config and SPA confirm route not found. |
| Admin dashboard/analytics | **Conditional pass** | Tests present; browser verification historical only. |
| Production deployment | **Blocked** | No deployment configuration in source. |

---

## Release recommendation

**Do not release as a hardened production system yet.** The project is suitable for demonstration, coursework evaluation, and controlled local deployment. Release blocking work falls into three groups:

1. **Security and correctness (P0):** token transport, DEBUG/media, rate limiting, email config, serializer/invariant fixes, admin KPI link, WS presence, attachment-only messages, search loading bug.
2. **Feature completion (P1):** story reactions, polls, group chat real-time/UI, report moderation, message edit/delete UI, pagination, read-state real-time updates.
3. **Operational readiness (P2):** deployment topology, Redis verification, frontend tests, browser smoke, CSS/dead-code cleanup, accurate documentation.

---

## Release checklist

### P0 — Before any internet-facing deployment

| # | Item | Evidence / owner area | Acceptance criterion |
| --- | --- | --- | --- |
| P0-1 | Replace or harden browser JWT storage | `api/axios.js`, pages, WS connectors | Tokens not readable by arbitrary page JS, or CSP/XSS controls demonstrably enforced; WS handshake uses ticket/cookie rather than long-lived query token. |
| P0-2 | Enforce `DJANGO_DEBUG=False` and production security settings | `config/settings.py`, deployment | Explicit allowed hosts, CORS origins, HSTS, secure cookies, proxy headers verified. |
| P0-3 | Provide production static + media serving strategy | Vite build, `MEDIA_URL` | SPA history fallback works; media access controlled; no reliance on Django DEBUG static route. |
| P0-4 | Configure and verify Redis channel layer | `config/settings.py` | `REDIS_URL` set in production; multi-worker WS fan-out verified. |
| P0-5 | Configure email backend and monitor reset failures | `users/views.py` | Reset email actually delivered in staging; no `fail_silently` masking without alerting. |
| P0-6 | Add rate limiting/throttling | DRF settings, chat consumer | Auth, password reset, chat send, and notification endpoints have documented limits. |
| P0-7 | Fix `MessageSerializer` writable `deleted_at`/`edited_at` | `chat/serializers.py` | Fields read-only; regression test rejects client-supplied values. |
| P0-8 | Fix poll uniqueness invariant | `posts/models.py`, `PollVoteView` | DB constraint prevents more than one active vote per user per poll. |
| P0-9 | Fix false offline presence on rejected WS | `chat/consumers.py` | No `presence_update:false` emitted unless connection successfully joined group. |
| P0-10 | Fix admin likes KPI link | `config/admin_site.py` | KPI links to Likes changelist. |
| P0-11 | Fix attachment-only message send | `Messages.jsx` | Send button enabled when attachment selected; REST FormData path works with empty text. |
| P0-12 | Fix `UserSearch` loading/cache-ref bug | `UserSearch.jsx` | Aborted query can be retried; results never remain skeleton-only indefinitely. |
| P0-13 | Re-run authoritative verification | `AGENTS.md` commands | `check`, `makemigrations --check`, full tests, lint, build all recorded with actual output. |
| P0-14 | Verify no migration drift | `social/migrations/0004_block.py`, `social/models.py` | `makemigrations --check --dry-run` reports no changes. |

### P1 — Before calling the product feature-complete

| # | Item | Area | Acceptance criterion |
| --- | --- | --- | --- |
| P1-1 | Expose story reactions in UI | `Stories.jsx`, preference dialog | Seven reactions selectable; counts update; no duplicate notifications. |
| P1-2 | Add poll creation/list/vote UI | `posts`, SPA | User can create poll, see options/results, vote once, change vote before expiry. |
| P1-3 | Complete group chat real-time path | `chat` | Group WS consumer + SPA group screen; membership role/mute/archive decisions implemented or removed. |
| P1-4 | Add report status + moderation actions | `posts`, admin | Status field, resolve/reject action, pending count reflects open reports. |
| P1-5 | Expose message edit/delete controls | `Messages.jsx` | UI triggers existing PATCH/DELETE endpoints; WS update/delete frames render. |
| P1-6 | Add pagination to remaining list pages | SPA pages | `next`/`count` consumed consistently for bookmarks, connections, notifications, requests, profiles, chat. |
| P1-7 | Push notification read-state updates | `notifications` | Other clients receive read/unread-count event. |
| P1-8 | Fix `?drafts=true` contract | `posts/views.py` | Returns only drafts and scheduled posts; published posts excluded. |
| P1-9 | Make pinning affect ordering | `posts`, `social`, profiles | Pinned posts appear first where the badge is shown. |
| P1-10 | Add scheduled publisher job or remove scheduling UI intent | Backend | Due posts become visible automatically via task/management command. |
| P1-11 | Add story edit/delete if product requires it | `users` | Endpoints and UI match stated feature list. |
| P1-12 | Send notifications for accept/reject, comment reactions, reposts | `social`, `posts` | Preference-aware notifications produced consistently. |
| P1-13 | Fix mention regex | `social/views.py` | Trailing punctuation not included in mention lookup; mention picker optional. |
| P1-14 | Add retry/abort handling to load failures | Frontend pages | Feed/profile/search load failures offer retry and avoid stale updates. |

### P2 — Maintainability and documentation

| # | Item | Acceptance criterion |
| --- | --- | --- |
| P2-1 | Remove or archive dead `Profile.jsx` and `config/views.py` | No duplicate routes/views; docs reference live code only. |
| P2-2 | Deduplicate `index.css` | Single source for theme/responsive blocks; reduced stylesheet size. |
| P2-3 | Register `Mention` and `CommentReaction` in admin or document exclusion | Admin coverage matches model inventory. |
| P2-4 | Align PWA manifest colours/icons with SPA theme | 192/512 icons and consistent theme colour. |
| P2-5 | Populate Postman collection or remove empty scaffolding | Collection includes auth and representative endpoints. |
| P2-6 | Add frontend tests | At least router guard, Axios refresh, search debounce, notification busy navigation. |
| P2-7 | Replace stale root reports or label them clearly as historical | Current status points to `PROJECT_ANALYSIS/`. |
| P2-8 | Create initial commits/tags in root and backend repos | Change history and diff baseline exist. |
| P2-9 | Add deployment assets | ASGI service definition, reverse proxy config, static/media strategy. |
| P2-10 | Add API schema export | OpenAPI/Swagger route or committed schema artifact. |

---

## Definition of done for major features

| Feature | Done means |
| --- | --- |
| Story reactions | Backend endpoint, preference opt-out, SPA selector, counts, no duplicate notifications, tests. |
| Group chat | Group REST + WS, membership management, SPA screens, permission/block tests, multi-worker WS verification. |
| Polls | Poll CRUD, vote endpoint with DB invariant, SPA create/vote/results, expiry handling, tests. |
| Reports | Status model, submit/list/resolve, admin moderation UI, counts reflect open reports, tests. |
| Pagination | Consistent `{count,next,previous,results}` consumption or documented cursor strategy across all list screens. |
| Production readiness | Security settings, TLS/proxy, Redis, static/media, secrets, monitoring, authenticated smoke, current verification outputs. |

---

## Final status statement

The codebase already satisfies the objectives of a broad, integrated social networking prototype. Most core features are implemented and connected through the SPA. However, several advertised or partially coded capabilities are not end-to-end, and operational hardening is absent from source. The appropriate academic framing is **advanced functional prototype with strong architecture and documented gaps**, not a production-ready platform.
