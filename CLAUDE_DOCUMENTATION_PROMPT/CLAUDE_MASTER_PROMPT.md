# Claude Master Prompt — Social Media App Documentation Package

Copy everything between the two horizontal rules below and paste it as a single prompt to Claude. The eight files in this folder are the supporting evidence package; Claude should read all of them before producing any deliverable.

---

You are a senior software engineer, systems analyst, and technical documentation lead. Your task is to analyze an existing university software engineering project and produce a complete, internally consistent documentation set suitable for a final-year Computer Science and Engineering (CSE) project report, viva preparation, and handover.

The application under analysis is a Django REST Framework + Django Channels backend with a React/Vite single-page frontend and a custom Django admin site. The workspace root is `C:\Django project\social media app`. The API root calls the project "Social Media App", while the UI/admin branding says "SocialConnect"; treat the official product name as unresolved until the user confirms it.

## 1. Mission

Produce, in professional English, all of the following deliverables from the **actual source code** of the project:

1. **Software Requirements Specification (SRS)** with stable requirement IDs (`FR-001`, `FR-002`, …, `NFR-001`, `NFR-002`, …).
2. **UML / system diagrams** in Mermaid syntax, including use case, class, sequence, activity, state, component, and deployment views, with traceable IDs (`UC-001`, `DB-TBL-…`, `API-…`, `UI-SCR-…`).
3. **Database documentation** covering every real model/table, field, relationship, constraint, index, lifecycle rule, and migration-driven schema change.
4. **UI/UX documentation** covering every real SPA screen, the custom admin screens, navigation, component inventory, interaction flows, accessibility notes, and responsive behavior.
5. **Technical documentation** covering architecture, authentication, authorization, REST API, WebSocket API, privacy model, notification pipeline, media handling, configuration, and verification commands.
6. **University project report support**: chapter outlines, problem statement, objectives, scope, stakeholder list, methodology, system analysis, design rationale, implementation summary, testing strategy, results discussion, limitations, future work, conclusion, glossary, and appendix mapping.

Do not produce the final report as a single undifferentiated document unless the user explicitly asks for that. Prefer separate, clearly named Markdown deliverables with a short index document if the user requests a package.

## 2. Non-negotiable source-of-truth rules

1. **Source code wins.** Inspect and cite actual files under `backend/` and `frontend/`. Do not treat existing reports as current truth.
2. **Historical reports are claims only.** Files such as `runtime-validation-report.md`, `PROJECT_COMPLETION_REPORT.md`, `BUG_FIX_REPORT.md`, `IMPLEMENTATION_REPORT.md`, `CODE_AUDIT_REPORT.md`, and the existing `PROJECT_ANALYSIS/` directory may be read for context, but every factual claim must be confirmed against source, migrations, tests, templates, or configuration before being presented as verified.
3. **No invention.** Do not invent screens, routes, API endpoints, database tables, fields, workflows, notifications, roles, deployment infrastructure, test results, or business rules. If something is not found in source, say so explicitly.
4. **Strict unknown marker.** For anything that cannot be verified from the available source, use the exact string:

   `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`

   Do not shorten, rephrase, italicize, or replace this marker. Use it verbatim in tables, prose, and diagrams. If a whole section depends on an unknown, put the marker in that section and continue with what is verifiable.
5. **Separate actual from proposed.** Keep implemented behavior, partial behavior, backend-only behavior, planned/documented behavior, missing behavior, and recommended future work in separate sections or clearly labelled table columns. Never describe a recommendation as if it exists.
6. **Read-only analysis.** Do not modify, delete, rename, or overwrite any original source file. If you create documentation files, create only the deliverables requested by the user.
7. **No secrets.** Never reproduce passwords, secret keys, tokens, API keys, connection strings with credentials, or values from `.env`. Discuss only environment variable **names** and their verified purpose.
8. **No unverified pass claims.** Do not claim tests, lint, build, migrations, or browser smoke tests passed unless you actually run the relevant command in this session and record the command and output. Otherwise state that the command is the documented verification command and that its current result is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

## 3. Evidence package supplied with this prompt

Read all eight files in `CLAUDE_DOCUMENTATION_PROMPT/` before writing anything:

- `CLAUDE_MASTER_PROMPT.md` — these instructions.
- `PROJECT_FACTS.md` — verified workspace, stack, configuration, naming, entrypoints, and constraints.
- `FEATURE_IMPLEMENTATION_MATRIX.md` — feature-by-feature implementation status with evidence and gaps.
- `SCREEN_ANALYSIS.md` — SPA pages, routes, components, admin screens, and UX findings.
- `DATABASE_ANALYSIS.md` — model/table inventory, fields, relationships, constraints, and migration history.
- `API_ANALYSIS.md` — REST and WebSocket endpoint catalogue with auth, payloads, responses, and caveats.
- `DIAGRAM_SOURCE_DATA.md` — curated actors, use cases, entities, sequences, states, components, and deployment facts for diagrams.
- `USER_CONFIRMATION_REQUIRED.md` — contradictions, unknowns, and questions requiring the exact placeholder.

Treat these files as **curated evidence summaries**, not as a replacement for reading source. If a companion file conflicts with current source, cite the source and flag the conflict in `USER_CONFIRMATION_REQUIRED.md`.

## 4. Inspection workflow

Follow this order and keep notes with file paths and line numbers:

1. **Workspace and configuration**: root `README.md`, `AGENTS.md`, `backend/AGENTS.md`, `backend/config/settings.py`, `backend/config/urls.py`, `backend/config/asgi.py`, `backend/requirements.txt`, `frontend/package.json`, `frontend/vite.config.js`, `frontend/index.html`, PWA files.
2. **Backend runtime source**: `backend/users/`, `backend/posts/`, `backend/social/`, `backend/chat/`, `backend/notifications/` — models, serializers, views, URLs, permissions, access helpers, utilities, signals, admin registrations, consumers, middleware, and routing.
3. **Database evidence**: all files under each app's `migrations/` directory; compare final source models with migrations.
4. **Test evidence**: `backend/users/tests.py`, `backend/posts/tests.py`, `backend/social/tests.py`, `backend/chat/tests.py`, `backend/notifications/tests.py`. Identify what is actually covered; do not assume coverage from filenames.
5. **Frontend source**: `frontend/src/main.jsx`, `frontend/src/App.jsx`, `frontend/src/api/`, all `pages/`, all `components/`, hooks, utilities, styles, and `frontend/public/`.
6. **Admin source**: `backend/config/admin.py`, `admin_site.py`, `admin_metrics.py`, `backend/templates/admin/`, and `backend/static/admin/`.
7. **Cross-check**: compare backend capabilities with SPA and admin surfaces; mark backend-only, UI-only, partial, or missing functionality explicitly.

## 5. Status vocabulary

Use this vocabulary consistently in every table and diagram legend:

| Status | Meaning |
| --- | --- |
| **Implemented** | Backend logic and a reachable UI/API path are present with no known blocking gap in the primary flow. |
| **Partial** | Code exists, but one part of the end-to-end flow, UI, notification, ordering, validation, or lifecycle is incomplete or inconsistent. |
| **Backend only** | A REST/WebSocket/model capability exists in Django but no corresponding SPA screen or action was found. |
| **Planned / documented** | Mentioned in historical documentation, design notes, or field intent, but not proven in active source. |
| **Not Found** | No supporting route, model, endpoint, component, test, or job was found in the inspected source. |
| **Needs Verification** | Runtime, environment, deployment, or user confirmation is required. Use the exact placeholder above. |

## 6. Deliverable A — Software Requirements Specification

Create an SRS with the following structure. Every functional requirement must have an ID, a source-evidence note, a priority, and a status.

1. **Document control** — version, date, status, audience, and unresolved-name note.
2. **Introduction** — purpose, scope, product perspective, stakeholder list, assumptions, dependencies.
3. **Overall description** — user classes, system context, operating environment, constraints.
4. **Functional requirements**
   - `FR-001` … identity and access: registration, login, JWT refresh, logout, password change/reset, deactivation.
   - `FR-…` profiles and discovery: own profile, public profile, search, suggestions, privacy settings.
   - `FR-…` content: post create/read/update/delete, audience, drafts, scheduling, pinning, reposts, reports, polls, hashtags, media.
   - `FR-…` social graph: likes, comments, replies, mentions, comment reactions, follows, friends, blocks, mutual friends.
   - `FR-…` stories: create, list, view, reactions, expiry, privacy.
   - `FR-…` notifications: types, preferences, REST actions, WebSocket delivery, unread counts.
   - `FR-…` messaging: direct conversations, messages, attachments, read receipts, typing, presence, edit/delete, groups.
   - `FR-…` admin: dashboard, analytics, model management, permission checks, roles, system status, activity log.
   - `FR-…` frontend shell: routing, navigation, theme, dialogs, media viewer, loading/empty/error states, PWA shell.
5. **Non-functional requirements**
   - `NFR-001` … security, authorization, token handling, input validation, media limits, privacy enforcement, availability, performance, maintainability, accessibility, responsiveness, observability, deployment/configuration.
6. **External interfaces** — REST, WebSocket, media URLs, email, PostgreSQL, Redis optional, Django admin.
7. **Traceability matrix** — map each FR/NFR to source files, tests, screens, API IDs, and diagram IDs.
8. **Open issues** — every item using `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.

For each requirement use this compact template:

```markdown
### FR-xxx — Short title
- **Description:** ...
- **Priority:** Must / Should / Could
- **Status:** Implemented / Partial / Backend only / Planned / Not Found / Needs Verification
- **Evidence:** `path/to/file:line`, endpoint/route, component, or test
- **Rationale:** ...
- **Dependencies:** ...
- **Verification:** test, manual flow, or `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`
```

## 7. Deliverable B — UML and system diagrams

Produce all diagrams as **Mermaid** fenced code blocks so they can be pasted into Markdown. Keep IDs and names consistent with the SRS, API, database, and screen documents. Add a short note under each diagram naming the source evidence and any unresolved item.

Required diagrams:

1. **Use case diagram** — actors: Guest, Registered User, Content Author, Friend/Follower, Story Viewer, Message Participant, Group Member, Moderator/Admin, External System. Include `UC-001` onwards for verified use cases; mark backend-only use cases distinctly.
2. **Class diagram** — every real Django model with fields, relationships, and multiplicities. Do not include imagined classes. Use `DB-TBL-…` IDs.
3. **Entity-relationship diagram** — tables, primary keys, foreign keys, unique constraints, and cardinalities. Distinguish application-enforced invariants from DB constraints.
4. **Sequence diagrams** for at least:
   - registration → login → JWT refresh;
   - create post with audience and media;
   - like and comment with notifications;
   - follow or friend request with privacy checks;
   - story list → view → reaction;
   - direct message via REST and WebSocket, including read receipt;
   - notification creation and WebSocket delivery;
   - admin analytics request and rendering.
5. **Activity diagrams** for:
   - authenticated route guard and token refresh;
   - feed visibility/audience/block filtering;
   - comment creation with parent validation, mentions, and notifications;
   - report submission and the **actual absence** of a moderation lifecycle;
   - story visibility/expiry.
6. **State diagrams** for:
   - `FriendRequest.status`;
   - `Notification.is_read`;
   - `Message` lifecycle including soft delete;
   - post lifecycle including draft/scheduled/published as represented in source.
7. **Component diagram** — React SPA, Axios client, Django REST API, Channels consumers, PostgreSQL, optional Redis, media storage, custom Django admin, browser service worker.
8. **Deployment diagram** — show only what source/README verifies. Label every production-only service, proxy, TLS endpoint, worker topology, static/media host, and monitoring component as `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless source proves it.

Use this legend in diagram notes:

```markdown
Solid label = verified in source. `Partial` = source exists but flow is incomplete. `Backend only` = no SPA/admin surface found. `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` = needs user/runtime confirmation.
```

## 8. Deliverable C — Database documentation

For every real model/table, provide:

- table/model name and app;
- field name, type, null/blank/default/choices, upload path where relevant;
- primary key and foreign keys with `on_delete` and `related_name`;
- many-to-many through models;
- unique constraints, check constraints, and indexes;
- ordering and lifecycle rules;
- which APIs/screens create, read, update, or delete records;
- whether the rule is enforced by the database, serializer/view, or only by convention;
- migration history that introduced or changed it;
- gaps such as missing status fields, incomplete invariants, or unused fields.

Include a final section titled **Application-level invariants not enforced by the database**, and a separate section titled **Proposed database improvements**. Never mix the two.

## 9. Deliverable D — UI/UX documentation

For every real screen and major component, provide:

- screen ID (`UI-SCR-…`) and exact route/template;
- purpose and target user;
- layout regions and primary components;
- API calls and WebSocket connections;
- states: loading, empty, error, success, busy/disabled;
- actions and navigation targets;
- accessibility details actually present in source;
- responsive behavior actually present in CSS source;
- known limitations or contradictions;
- implemented/partial/backend-only status.

Cover the SPA shell, authentication pages, feed, stories, post composer/actions, post detail, profile pages, edit profile, search, friend requests, connections, bookmarks, messages, notifications, notification settings, media viewer, confirm dialogs, theme toggle, PWA files, and the custom admin dashboard/analytics/roles/system screens. Explicitly state when a capability is API-only.

## 10. Deliverable E — Technical documentation

Include:

- architecture overview and request lifecycle;
- technology stack with exact package names from `backend/requirements.txt` and `frontend/package.json`;
- configuration and environment variable **names only**;
- authentication and authorization model, including JWT rotation/blacklist and WebSocket token passing;
- privacy/access-control matrix built from `backend/social/access.py` and view enforcement;
- REST API catalogue using `API-…` IDs, with method, path, auth, payload, response, errors, evidence, and status;
- WebSocket event catalogue with close codes, event names, payload shapes, and authorization rules;
- notification creation pipeline;
- media upload limits and storage paths;
- error handling and shared frontend interceptor behavior;
- verification commands from `AGENTS.md` using `..\venv\Scripts\python.exe` and `npm.cmd`;
- security review and risk register with `RISK-…` IDs.

## 11. Deliverable F — University project report support

Provide chapter-ready content, not generic filler:

1. Title page metadata with unresolved official-name note.
2. Abstract and keywords.
3. Problem statement.
4. Objectives.
5. Scope and limitations.
6. Literature/technology justification tied to the actual stack.
7. Requirements analysis using the SRS IDs.
8. System design using the diagrams.
9. Database design using real model evidence.
10. Implementation highlights by module.
11. Testing strategy and test inventory.
12. Results and discussion with honest implementation status.
13. Security and privacy analysis.
14. Future work separated into completion work and hardening work.
15. Conclusion.
16. Glossary.
17. Appendices: API summary, screen inventory, schema summary, verification commands, unresolved questions.

## 12. Writing style and quality gates

- Use concise, formal, third-person technical English. Avoid marketing language and unsupported superlatives such as "complete", "production-ready", "fully secure", or "bug-free" unless source and verification prove the claim.
- Every major factual assertion needs an evidence note with a file path and, where practical, line numbers.
- Use tables for inventories and matrices; use numbered lists for procedures; use Mermaid for diagrams.
- Keep requirement IDs stable. Do not renumber an existing ID when adding a new requirement; append new IDs instead.
- If two source files disagree, report both with paths and use `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`.
- Do not convert a backend capability into a user-facing feature unless a reachable route/component/template proves it.
- Do not convert a documented future improvement into a requirement unless the user explicitly asks for target-state requirements; label such items as proposed.
- Before finalizing, run a consistency check: every FR/NFR has evidence, every UC has an actor, every API-aligned screen has an endpoint, every model appears in the ER/class/database sections, every unknown uses the exact placeholder, and no secret values appear.

## 13. Final instruction

Begin by replying with a short confirmation that you have read all eight companion files and will treat source code as authoritative. Then produce the requested deliverables in the order above. If any information is missing, do not guess: insert `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` and continue.

---
