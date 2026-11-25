# Feature Status

Source-oriented implementation status. Screens marked proposed in the visual package are not claimed to exist in the current router.

## Executive summary

| Domain | Overall status | Main caveat |
| --- | --- | --- |
| Identity and access | Implemented with caveats | Username-only login; JWTs in `localStorage`; route guard checks token presence only. |
| Password lifecycle | Partial / Backend only | REST endpoints exist; no dedicated SPA reset/confirm/deactivate screens. |
| Profiles and discovery | Implemented with caveats | Active screen is `UserProfile.jsx`; legacy `Profile.jsx` is unrouted. |
| Posts and feed | Implemented core, several partial extensions | Draft filter contract, pin ordering, scheduling, multi-image upload, polls, reports remain partial/backend-only. |
| Social graph | Implemented core | Block-list management and mutual-friend UI are backend-only; accept/reject notifications absent. |
| Stories | Partial | List/create/view UI exists; reaction UI, edit/delete, and viewed-state persistence are missing. |
| Notifications | Implemented with caveats | REST + WebSocket + preferences UI; read actions do not emit live updates; no pagination. |
| Direct messaging | Implemented with caveats | REST + WebSocket UI; attachment-only sends and message edit/delete controls are missing. |
| Group messaging | Backend only / Partial | REST models/endpoints exist; no group UI or group WebSocket. |
| Custom admin | Implemented with caveats | Real-data dashboard/analytics/roles/system pages; moderation workflow absent. |
| PWA | Partial | App-shell caching only; no offline data, push, install prompt, update flow, or full icon set. |
| Frontend tests | Not Found | Vitest/jsdom installed but no test files or script. |
| Production deployment | Needs Verification / Not Found | Topology, proxy, static/media hosting, Redis runtime, and CI/CD are unverified. |

## Detailed status by area

| Area | Verified capability | Status | Gap / caveat |
| --- | --- | --- | --- |
| Registration and login | `POST /api/users/register/`, `POST /api/users/login/`, SPA forms | Implemented | Generic login catch can swallow explicit invalid-response text. |
| Token refresh and logout | Rotating refresh, blacklist, Axios single-flight refresh | Implemented | Presence-only route guard. |
| Password reset / deactivate | REST endpoints exist | Backend only / Partial | No `/forgot-password` or reset-confirm route. Email delivery `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Own and public profile | `GET/PATCH /api/users/profile/`, `GET /api/users/<pk>/`, `UserProfile.jsx` | Implemented | Legacy `Profile.jsx` is unrouted. |
| User search and suggestions | `GET /api/users/search/`, right rail | Implemented | No pagination; render-phase URL state sync. |
| Post CRUD and feed | Post endpoints, `GET /api/social/feed/`, home composer/cards | Implemented | Pagination is opt-in via `?page=` only. |
| Drafts and scheduling | `is_draft`, `scheduled_for`, visibility filters | Backend only / Partial | No draft/scheduling UI and no publisher job found. |
| Pinning / reposts / reports | Endpoints and home actions exist | Partial | Pin not consumed by ordering; repost has no notification; reports have no lifecycle. |
| Polls / hashtags / multi-image | Models and partial endpoints | Backend only | No poll composer, hashtag browse endpoint, or `PostImage` writer. |
| Likes / comments / replies | Endpoints and `PostActions.jsx` | Implemented | Comments are not paginated. |
| Follows / friends / blocks | Full REST flows and SPA actions | Implemented with caveats | No block-list screen; no accept/reject notifications. |
| Stories | Create/list/view/view-tracking UI | Partial | No reaction UI, edit/delete, or persisted viewed state. |
| Notifications | List, read, count, preferences, WebSocket | Implemented with caveats | No pagination; read state is not pushed to other clients. |
| Direct chat | Conversation list, history, REST send, WebSocket send/typing/presence/read | Implemented with caveats | No attachment-only send, no edit/delete UI controls, no history pagination. |
| Group chat | Group REST endpoints and models | Backend only / Partial | No group UI and no group WebSocket route. |
| Admin dashboard | 12 KPIs, charts, analytics, roles, system, changelists | Implemented with caveats | Browser smoke result `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`; report moderation absent. |
| PWA | Production service worker, manifest | Partial | App shell only; no offline data/push/install/update flow. |
| Frontend automated tests | None found | Not Found | Do not claim frontend tests exist. |
| Product naming | Two names in source | Needs Verification | Final brand `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
