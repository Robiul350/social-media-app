# Security Analysis

## Scope and evidence boundary

This analysis is based on source inspection only. The root `.env` was not opened and no secret, password, token, or private environment value is reproduced. Environment variable **names** are discussed where they affect security behaviour. Runtime penetration testing, dependency vulnerability scanning, and authenticated browser testing were not performed as part of this audit.

## Security-relevant configuration

| Area | Observed behaviour |
| --- | --- |
| Secret key | `DJANGO_SECRET_KEY` is required unless both debug and the explicit insecure-development override are enabled. The key is read from the root `.env` only. |
| Debug | Controlled by `DJANGO_DEBUG`; defaults to enabled in source when unset. Production must set it false. |
| Allowed hosts | Controlled by `DJANGO_ALLOWED_HOSTS`; defaults to localhost/127.0.0.1 in source. |
| CORS | `django-cors-headers` is installed and configured via `CORS_ALLOWED_ORIGINS` / `FRONTEND_URL`. Exact deployed values are environment-dependent. |
| HTTPS/HSTS | Settings reference proxy and HSTS environment flags (`DJANGO_USE_HTTPS_PROXY`, `DJANGO_SECURE_HSTS_*`). Effective values are environment-dependent. |
| Database | PostgreSQL credentials come from environment variables. No credentials are stored in the audited source. |
| Channel layer | Redis when `REDIS_URL` is set; otherwise in-memory. |
| Media | `MEDIA_URL` is served by Django only when `DEBUG` is true. Uploaded files live under `MEDIA_ROOT`. |
| Admin | Custom Django admin with permission-gated dashboard data and display-only roles/system pages. |

## Authentication

### Implemented flow

- Registration creates a user and profile (via signal), then the SPA navigates to login.
- Login posts credentials to `users/login/` and receives access/refresh tokens plus user identity.
- The SPA stores `access`, `refresh`, `user_id`, and `username` in `localStorage`.
- Axios adds `Authorization: Bearer <access>` to every API request when a token exists.
- On a 401 response, the interceptor calls `users/token/refresh/` once, updates tokens, and replays the request. Concurrent 401s share a single refresh promise.
- SimpleJWT is configured for rotating refresh tokens with blacklisting.
- Logout posts the refresh token to `users/logout/`, which blacklists it; local keys are cleared regardless of server response.
- Route guards check only for the presence of `localStorage.access`.

### Strengths

- Standard JWT library with rotation and blacklisting rather than custom token code.
- Refresh failure clears session state and redirects to `/login`.
- Logout attempts server-side revocation, not only client-side deletion.
- Inactive users are rejected by WebSocket authentication middleware.

### Risks

- **High:** Tokens in `localStorage` are readable by any JavaScript running on the origin, so an XSS flaw can steal both access and refresh tokens.
- **Medium:** Route guards validate token presence, not token validity or expiry. An expired token still renders protected screens until an API call fails.
- **Medium:** Access tokens are passed in WebSocket query strings, which are more likely to appear in logs, browser history, or proxy telemetry than headers.
- **Medium:** The refresh interceptor relies on localStorage staying in sync across tabs; logout in one tab triggers a `storage` event in others, but timing windows remain.
- **Low:** No “remember me” or session-duration UI; refresh lifetime is environment-configured.

## Authorization and object-level controls

### Observed mechanisms

- DRF default permission is authenticated-or-read-only, with per-view overrides such as `IsAuthenticated` for private actions.
- Post edit/delete is restricted to the author in `posts/permissions.py` and covered by tests.
- Comment edit/delete is owner-restricted in the social views and surfaced conditionally in `PostActions.jsx`.
- `social/access.py` centralizes audience, visibility, follow/friend, and block checks for profiles and feeds.
- Chat access uses `can_chat_between()` and block checks in REST views and the WebSocket consumer.
- Notification creation uses `create_notification()`, which enforces block checks and per-category preferences.
- Admin analytics/views check model permissions before exposing counts/charts; roles/system pages are display-only and do not grant access.
- Message records are soft-deleted; queries are expected to exclude non-null `deleted_at`.

### Risks

- **Medium:** Some SPA controls rely on client-side state (for example ownership checks based on `localStorage.user_id`). Server-side permission checks are still present, but UI can mislead.
- **Medium:** `?drafts=true` returns all posts authored by the caller, not only drafts/scheduled posts. This is an information-scope issue within the caller's own data, but it violates the documented contract.
- **Medium:** `PostReport` has no status field, so admin “Pending Reports” counts every report row. This can mislead moderation.
- **Medium:** `AdminAction` exists in a migration but has no actor field and no writer; it must not be treated as an audit trail.
- **Low:** Some lists are read-only in the SPA and do not expose backend actions; this is a functionality gap rather than a privilege escalation.

## Privacy controls

- Profiles support `is_private`, `allow_comments`, and `allow_messages`, plus `first_name`/`last_name` and social fields.
- Posts support `audience` (`public`, `followers`, `friends`), `is_draft`, `is_pinned`, and `scheduled_for`.
- Stories support per-story privacy (`public`, `followers`, `friends`) and expiry.
- Blocks are enforced in feed/profile visibility, chat, and notification delivery paths.
- Notification preferences allow opt-out by category.

### Privacy caveats

- Private-profile policy details are partly environment/product-decision dependent; historical reports list this as unresolved.
- Username, display name, and some profile fields appear in suggestions/search results; exact serializer exposure should be reviewed before public deployment.
- Media URLs are direct file paths under `MEDIA_URL`; authorization is not applied to the file itself. Anyone with a valid direct URL can retrieve media while DEBUG serving is enabled.

## Input validation and upload handling

- DRF serializers validate API payloads; the SPA also performs client-side checks.
- Frontend limits observed: images 10 MB for posts, videos 100 MB for posts, stories 25 MB, chat attachments 25 MB, comment/reply 5000 characters, story caption 500 characters, report reason 250 characters.
- Client-side checks improve UX but are not a security boundary; backend validation must be authoritative. Exact backend size/type validators are `Needs Verification` from this audit's summary level.
- Uploaded files use original/generated paths under `MEDIA_ROOT` and are referenced through `MEDIA_URL`.

### Risks

- **Medium:** Media serving outside production controls is not configured in source. A deployment that leaves `DEBUG=True` exposes uploads directly.
- **Medium:** No malware scanning, content-type sniffing hardening, or signed media URL mechanism was found.
- **Low:** URL-extension-based media type inference in the SPA can misclassify files with unusual names.

## WebSocket security

- ASGI routes: `ws/chat/<user_id>/` and `ws/notifications/`.
- `JWTAuthMiddleware` parses `?token=`, validates it with SimpleJWT, loads only active users, and falls back to `AnonymousUser`.
- `ChatConsumer` rejects unauthenticated users, self-chat, blocked pairs, and invalid target users.
- Direct-chat room names are deterministic from sorted pair IDs, reducing ambiguity but making them predictable.
- The SPA implements reconnect with exponential backoff capped at 30 seconds and re-reads the access token from localStorage on reconnect.

### Risks

- **High/Medium:** Query-string tokens can leak through logs. Prefer short-lived WebSocket tickets or a secure cookie-based handshake.
- **Medium:** With the in-memory channel layer, multi-worker deployments break cross-process real-time delivery. This is availability/correctness, not confidentiality.
- **Medium:** No rate limiting or message-size throttling was observed in the consumer; automated clients could flood rooms.
- **Low:** Group conversation REST endpoints exist, but there is no group WebSocket consumer; group real-time behaviour is `Not Found`.

## CORS, hosts, and transport

- CORS is configured through Django middleware and environment-driven origins; the SPA defaults to `http://127.0.0.1:8000/api/`.
- Allowed hosts and frontend URL are environment-driven.
- HSTS and secure-proxy flags exist in settings and are intended for production, but effective enforcement depends on deployment configuration.
- No TLS termination, reverse-proxy config, or CSP configuration was found in source.

### Recommendations

- Set `DJANGO_DEBUG=False`, strong secret key, explicit allowed hosts, strict CORS origins, secure proxy headers, HSTS, and a Content Security Policy in production.
- Serve the built SPA through a proper static host; do not rely on Django DEBUG media serving.
- Add `X-Content-Type-Options: nosniff`, `Referrer-Policy`, frame-ancestors CSP, and Permissions-Policy.

## Admin security

- Custom admin uses Django's authentication/permission system.
- Dashboard KPIs and charts are permission-gated; restricted users see “Restricted” rather than counts.
- Roles page explains that Django groups/permissions are authoritative and grants nothing.
- System page reports verifiable runtime facts and explicitly never displays credentials, keys, or token values.
- Logout is a CSRF-protected POST with confirmation.
- Admin templates include theme/nav state in localStorage only.

### Risks

- **Low:** Admin browser verification is historically partial/absent; visual/permission behaviour should be smoke-tested with superuser, staff, and restricted accounts.
- **Low:** Custom admin CSS/JS is large and layered; review for unintended client-side exposure is advisable.

## Session and cross-tab behaviour

- `socialconnect:auth-change`, `socialconnect:profile-change`, and `socialconnect:refresh-counts` custom events coordinate components.
- `storage` events synchronize auth state across tabs.
- Theme persists as `socialconnect-theme`; admin uses `sc-admin-theme` and `sc-admin-sidebar-collapsed`.

This is convenient UX but increases the amount of state in browser storage. Sensitive values should eventually move to more secure transport.

## Risk register

| ID | Risk | Severity | Likelihood | Recommendation |
| --- | --- | --- | --- | --- |
| S-01 | XSS can steal localStorage JWTs | High | Medium | Move access/refresh to HttpOnly Secure SameSite cookies or keep access in memory with cookie-backed refresh. |
| S-02 | WebSocket access token in query string | High | Medium | Use short-lived single-use WS tickets or cookie authentication with Origin checks. |
| S-03 | DEBUG media serving in production | High | Medium | Serve media via a controlled endpoint/CDN with auth/signed URLs; enforce `DEBUG=False`. |
| S-04 | No rate limiting on auth/chat/notification endpoints | Medium | High | Add DRF throttles and per-room WebSocket limits. |
| S-05 | Route guard checks token presence only | Medium | High | Decode/validate expiry or call a `/me` endpoint before rendering protected routes. |
| S-06 | Unvalidated redirect-like navigation from notification targets | Low | Low | Targets are locally constructed; continue avoiding arbitrary user-supplied URLs. |
| S-07 | Drafts filter contract mismatch | Medium | Medium | Filter `is_draft`/`scheduled_for` correctly and document semantics. |
| S-08 | Report status absent | Medium | High | Add status/workflow fields and moderation actions. |
| S-09 | AdminAction not a real audit trail | Low | High | Remove it or implement an actor-bearing audit model. |
| S-10 | In-memory channel layer in multi-worker deployment | Medium | Medium | Require Redis in production and verify with multiple ASGI workers. |
| S-11 | No CSP / security headers in source | Medium | Medium | Add Django security middleware configuration and deployment-level CSP. |
| S-12 | Historical reports contain stale security claims | Low | High | Keep source-based documentation authoritative, as this audit does. |

## Positive findings

- Secrets are not committed in source; local `.env` is ignored.
- JWT implementation uses established libraries with rotation/blacklisting.
- Centralized access helpers reduce duplicated authorization logic.
- Blocking is considered in feed/profile, chat, and notification paths.
- Admin analytics respects view permissions.
- WebSocket middleware rejects inactive users and unauthenticated connections.
- No hardcoded credential value was found in the inspected source.

## Conclusion

The application has a solid security baseline for an advanced academic project. The main production blockers are browser-stored tokens, query-string WebSocket authentication, DEBUG-dependent media serving, missing rate limiting, and incomplete deployment hardening. Addressing the high-severity items would materially improve readiness without changing the product's core architecture.
