# Project Report Outline

This outline is designed for a university-level software project report. Each section maps to evidence files in `PROJECT_ANALYSIS/` so claims can be traced back to inspected source rather than historical reports.

## 1. Title page

- Project title: **SocialConnect — Full-Stack Social Media Application**
- Candidate name / registration number / course / institution / date.
- Supervisor or evaluator fields if required by the department.

## 2. Abstract

Suggested content:

> SocialConnect is a full-stack social networking application built with Django REST Framework, Django Channels, PostgreSQL, and a React/Vite single-page application. The system supports JWT authentication, profiles, posts with media and audience controls, stories, likes, threaded comments, follows, friend requests, blocking, bookmarks, polls, reports, notifications, and real-time direct messaging. This report documents the architecture, implementation, testing, security considerations, and remaining development work based on a source-level audit of the existing codebase.

Keep the abstract to 150–250 words.

## 3. Acknowledgements

Optional: supervisor, peers, documentation sources, and tools used. Do not include credentials or private environment values.

## 4. Table of contents

Generate after the final page numbers are known.

## 5. List of figures and tables

Suggested figures:

- Figure 1: System architecture (`SYSTEM_ARCHITECTURE.md`).
- Figure 2: Entity-relationship diagram (`ER_DIAGRAM.md`).
- Figure 3: Authenticated desktop shell wireframe (`WIREFRAMES.md`).
- Figure 4: Mobile navigation wireframe (`WIREFRAMES.md`).
- Figure 5: Home feed wireframe (`WIREFRAMES.md`).
- Figure 6: Message/notification real-time sequence diagrams (`SYSTEM_ARCHITECTURE.md`).

Suggested tables:

- Technology stack (`TECHNOLOGY_STACK.md`).
- Feature status matrix (`COMPLETE_FEATURE_ANALYSIS.md`).
- API endpoint catalogue (`API_DOCUMENTATION.md`).
- Model summary (`DATABASE_DESIGN.md`).
- Test inventory (`TESTING_REPORT.md`).
- Risk register (`BUGS_AND_RECOMMENDATIONS.md`).

## 6. Introduction

### 6.1 Background

Social platforms combine identity, content publishing, social graph interactions, and real-time communication. This project implements those concerns in a modular Django backend and React SPA.

### 6.2 Problem statement

Existing coursework projects often present disconnected pages or mock data. SocialConnect aims to provide an integrated, API-driven experience with persistent data, authorization, privacy controls, and real-time updates.

### 6.3 Objectives

- Implement secure registration/login and profile management.
- Support rich post creation and interaction with visibility controls.
- Implement social graph features (follow, friend, block).
- Provide notifications and direct messaging over WebSockets.
- Deliver a responsive, accessible SPA.
- Maintain a custom admin dashboard for moderation and analytics.
- Document architecture, database, API, testing, and known limitations.

### 6.4 Scope

Describe what is implemented and explicitly state exclusions: no production deployment config, no frontend test suite, no group-chat UI, no full moderation workflow, no `/explore` or `/settings` route.

### 6.5 Report structure

Briefly summarize chapters 7–15.

## 7. Literature / technology review

- Django 6.1 and DRF for REST APIs.
- Django Channels/ASGI for WebSockets; Redis channel layer for multi-process deployments.
- SimpleJWT access/refresh tokens with rotation and blacklisting.
- PostgreSQL relational persistence.
- React 19 with Vite and react-router-dom for SPA navigation.
- Axios interceptors for bearer tokens and refresh.
- CSS custom properties, responsive layout, dark mode, and accessibility patterns.

Cite official documentation where appropriate. Source evidence: `TECHNOLOGY_STACK.md`.

## 8. System analysis

### 8.1 Functional requirements

Use the implemented/partial/missing feature matrix from `COMPLETE_FEATURE_ANALYSIS.md`.

### 8.2 Non-functional requirements

- Authentication and object-level authorization.
- Privacy through audience, follow, friend, and block rules.
- Responsive design and reduced-motion support.
- Real-time delivery with reconnect/backoff.
- Testability through Django test runner and Channels communicators.
- Maintainability through modular apps and centralized access helpers.

### 8.3 Use cases

Suggested actors and use cases:

- Guest: register, log in.
- Member: manage profile, create posts/stories, browse feed, like/comment/bookmark, follow/friend/block, message, receive notifications.
- Admin: view dashboard/analytics, manage users/content, review reports where permissions allow.

### 8.4 Constraints and assumptions

- PostgreSQL must be available and configured through environment variables.
- WebSockets require ASGI/Daphne.
- Redis is optional locally but required for cross-process WebSocket fan-out.
- The SPA stores JWTs in localStorage; this is a deliberate but security-sensitive choice.
- Historical reports are snapshots; current source is authoritative.

## 9. System design

### 9.1 High-level architecture

Use the Mermaid architecture diagram and narrative from `SYSTEM_ARCHITECTURE.md`.

### 9.2 Module/package design

Describe `config`, `users`, `posts`, `social`, `notifications`, `chat`, and frontend `api/components/pages/hooks/utils` from `PROJECT_STRUCTURE.md`.

### 9.3 Database design

Use `DATABASE_DESIGN.md` and `ER_DIAGRAM.md`. Discuss normalization, relationships, soft deletion, and indexes.

### 9.4 API design

Use the endpoint tables in `API_DOCUMENTATION.md`. Highlight REST conventions, JWT auth, query parameters, pagination, and WebSocket frames.

### 9.5 UI/UX design

Use `UI_UX_ANALYSIS.md`, `WIREFRAMES.md`, and `UI_MOCKUP_SPECIFICATIONS.md`. Discuss layout grid, responsive breakpoints, design tokens, focus management, skeletons, and modal patterns.

## 10. Implementation

### 10.1 Backend implementation

- Auth/profile/stories (`users`).
- Content/polls/reports (`posts`).
- Social graph/access control (`social`).
- Notifications and preferences (`notifications`).
- Chat/groups/consumers (`chat`).
- Custom admin (`config/admin_site.py`, templates/static).

### 10.2 Frontend implementation

- Router and protected layout.
- Axios/token refresh/profile store.
- Shell/navbar/right rail/mobile drawer.
- Page-by-page behaviour from the page-layer analysis.
- Shared dialogs, media viewer, focus trap, and form error helpers.

### 10.3 Real-time implementation

- Chat WebSocket authentication, message flow, typing/presence/read receipts.
- Notification WebSocket publishing and client reconnect logic.
- Channel layer topology caveat.

### 10.4 Implementation highlights

- Centralized `social/access.py` for privacy checks.
- `create_notification()` enforcing blocks/preferences.
- Optimistic UI updates with rollback.
- AbortController usage and StrictMode guards on several pages.
- Custom admin analytics based on real database timestamps.

## 11. Testing and validation

### 11.1 Test strategy

Describe Django `APITestCase`, `TestCase`, Channels `TransactionTestCase`, `WebsocketCommunicator`, and the absence of frontend tests.

### 11.2 Test coverage

Use `TESTING_REPORT.md`. Summarize coverage by app and explicitly state that historical pass counts are not current evidence.

### 11.3 Verification commands

Include the commands from `AGENTS.md`, using `npm.cmd` on Windows.

### 11.4 Results and limitations

Report only commands actually executed for this audit. If none were executed, say so. Discuss historical claims as context, not current status.

## 12. Security analysis

Use `SECURITY_ANALYSIS.md`:

- JWT configuration, refresh rotation, blacklisting.
- Object-level authorization and privacy filters.
- Block enforcement and notification opt-outs.
- CORS, allowed hosts, HSTS/proxy settings.
- Token-in-localStorage and WebSocket query-token risks.
- Media upload/serving risks.
- Admin permission gating.
- Concrete recommendations.

## 13. Results and discussion

- Map objectives to implemented outcomes.
- Show what works end-to-end.
- Discuss backend-only features and partial integrations.
- Compare desktop and mobile UX.
- Discuss maintainability findings such as duplicated CSS and dead files.

## 14. Limitations and future work

Prioritize from `BUGS_AND_RECOMMENDATIONS.md`:

1. Security hardening (HttpOnly cookies or memory tokens, short-lived WS tickets, rate limiting).
2. Complete group chat UI/WebSocket consumer.
3. Poll/hashtag/report-moderation UI.
4. Message edit/delete and attachment-only sending.
5. Pagination across list pages.
6. Frontend automated tests.
7. Production deployment configuration and Redis topology.
8. CSS deduplication and dead-file removal.

## 15. Conclusion

Summarize that the project is a broad, functional social platform with strong backend foundations and a polished responsive SPA, while remaining a prototype rather than a fully hardened production deployment.

## 16. References

- Official Django, DRF, SimpleJWT, Channels, React, Vite, and PostgreSQL documentation.
- Project source files listed in `PROJECT_STRUCTURE.md`.
- Historical project reports, clearly cited as snapshots.

## 17. Appendices

### Appendix A — API endpoint catalogue

From `API_DOCUMENTATION.md`.

### Appendix B — Model/ER reference

From `DATABASE_DESIGN.md` and `ER_DIAGRAM.md`.

### Appendix C — Wireframe set

From `WIREFRAMES.md` and `UI_MOCKUP_SPECIFICATIONS.md`.

### Appendix D — Audit index

From `README.md`.

## Presentation mapping

| Conference paper section | Audit source |
| --- | --- |
| System model | `PROJECT_OVERVIEW.md`, `SYSTEM_ARCHITECTURE.md` |
| Architecture | `SYSTEM_ARCHITECTURE.md`, `TECHNOLOGY_STACK.md` |
| Implementation | `COMPLETE_FEATURE_ANALYSIS.md`, `PROJECT_STRUCTURE.md` |
| Evaluation | `TESTING_REPORT.md`, `UI_UX_ANALYSIS.md` |
| Security | `SECURITY_ANALYSIS.md` |
| Limitations | `BUGS_AND_RECOMMENDATIONS.md`, `IMPLEMENTATION_STATUS.md` |
