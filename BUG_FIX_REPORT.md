# SocialConnect Bug Fix Report

The project did not contain a `BUG_FIX_REPORT.md` when this audit phase resumed.
This report records fixes already implemented in the existing project and the
latest verified regression work. It does not claim that the broader product
roadmap is complete.

## Fixes

- **Global feed scope and ordering:** The feed includes visible public posts from
  users the viewer does not follow, with newest posts first and pagination. Feed
  access continues to apply audience, private-profile, and block rules.
- **Feed interaction and presentation:** Connected existing APIs for likes,
  nested comments, bookmarks, reporting, media display, and suggestions in the
  active feed. Added a bookmarks page and sidebar navigation. These do not imply
  that every advanced post feature has a complete UI.
- **Comment access and post validation:** Enforced the existing visibility rules
  when creating comments and reject posts that contain neither non-whitespace
  text nor media.
- **Story privacy exposure:** Story list and view endpoints previously accepted
  any unexpired story without applying its audience or private-profile rules.
  They now enforce public/follower/friend audience, private-profile visibility,
  expiration, and block exclusions. An inaccessible story view returns 404.
- **Notifications and WebSockets:** Added reply notification handling and
  authenticated notification delivery; inactive users are rejected by chat
  WebSocket authentication. Chat reconnection uses the API client so an expired
  access token can be refreshed.
- **Admin data access:** Dashboard counts/charts and post engagement figures
  respect the applicable model view permissions.
- **Login presentation:** Added shared design tokens and refreshed the Login
  layout without replacing its existing authentication behavior.
- **Documentation accuracy:** Updated README and project reports to distinguish
  integrated features from backend-only and partially wired features.

## Validation

- Full Django suite, run from `backend` with `manage.py test --keepdb --verbosity 1`:
  **40 passed, 0 failed, 0 skipped**. The existing test database was preserved.
- Focused story privacy regression test: **1 passed**.
- Django `check`: passed.
- Django `makemigrations --check --dry-run`: passed; no pending model changes.
- Frontend ESLint: passed.
- Frontend production build: passed.
- Browser testing was **not** performed for the latest Login redesign or story
  privacy fix. Earlier browser smoke evidence is recorded separately in
  [runtime-validation-report.md](./runtime-validation-report.md).

## Remaining Limitations

The complete Stories frontend, advanced post workflows, group real-time
messaging, creator analytics, and other partial features remain outstanding.
Redis-backed multi-worker WebSocket behavior and authenticated multi-account
browser flows remain unverified in this environment.
