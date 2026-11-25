# User Confirmation Required

This file records information that cannot be established from the inspected source, contradictions between source and historical documentation, and decisions that require the project owner's confirmation.

Every unresolved item below uses the exact required marker:

`[NOT VERIFIED - USER CONFIRMATION REQUIRED]`

Claude must reproduce the marker verbatim wherever the item appears in generated SRS, diagrams, database documentation, UI/UX documentation, technical documentation, or the university report.

---

## 1. Product identity and branding

| Topic | Observed evidence | What requires confirmation |
| --- | --- | --- |
| Official product name | API root in `backend/config/urls.py` returns `"project": "Social Media App"`. `frontend/index.html` title, SPA route titles, inline auth UI, custom admin site, and email/UI strings use `SocialConnect`. Root `README.md` headings also say `SocialConnect`. | Which name is the official university submission name. Until confirmed, write "Social Media App (working UI/admin name: SocialConnect)" and mark the final brand as `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Version number | API root reports `"version": "1.0"`; `frontend/package.json` version is `0.0.0`. | Whether the submitted release has an intended academic version label. `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |

## 2. Documentation conflicts

| Conflict | Source-based finding | Required handling |
| --- | --- | --- |
| Stories integration | Root `README.md` states that stories are not integrated into the active frontend, but `frontend/src/pages/home.jsx` imports `Stories` and `frontend/src/components/Stories.jsx` implements list/create/view UIs. | Treat the README statement as stale. Document the component as present in source. Any explanation of when the README was accurate is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Current test status | Root `README.md` claims "52 passing tests"; historical reports make other pass/fail claims. No fresh full-suite result was produced as part of this evidence package. | Do not claim a current pass count. Record the documented commands and mark the current result `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` unless actually executed. |
| Admin dashboard status | Historical reports describe different KPI counts and browser-verification outcomes. Current source contains custom admin templates, metrics, roles, system, and analytics code. | Use current source for implemented screens. Browser smoke-test success is `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Frontend completeness | Root README describes a polished set of features but also says several backend features have no UI. Source shows some features (for example stories) that the README says are absent. | Always verify against `frontend/src` and mark feature status with the standard vocabulary. |

## 3. Runtime and deployment

| Topic | Why it cannot be verified from source | Required marker |
| --- | --- | --- |
| Production hosting topology | No verified reverse proxy, ASGI service definition, worker count, static/media host, monitoring stack, or CI/CD configuration was found in the inspected source. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Redis deployment | `config/settings.py` uses an in-memory channel layer unless `REDIS_URL` is set, but the runtime value of `REDIS_URL` and whether Redis runs in production cannot be read from source. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Production `DEBUG`, allowed hosts, CORS origins, HSTS, and proxy-header settings | Settings code supports environment-driven production behavior, but actual deployed values are environment-dependent. Discuss variable names only. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Media serving in production | Source serves media through Django only when `DJANGO_DEBUG=True`; the production media strategy is not present in source. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Email delivery for password reset | Source calls Django email APIs; configured backend, credentials, from-address, and successful delivery are environment-dependent. Do not expose or infer secret values. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Browser accessibility and responsive smoke testing | Source contains accessibility and CSS patterns, but no verified browser test results for real devices or assistive technologies were found. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Actual PostgreSQL state and migration application | Migration files are present, but whether the deployed database has applied them and has no drift is runtime state. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |

## 4. Domain and product decisions

| Question | Source evidence | Required confirmation |
| --- | --- | --- |
| Should password reset confirm and account deactivation have SPA screens? | REST endpoints exist; no dedicated SPA routes are proven in `App.jsx`. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Should poll creation, poll results, story reactions, comment reactions, group chat, hashtag browsing, draft/scheduling controls, report moderation, and scheduled publishing be treated as required target features? | Some models/endpoints exist; UI or lifecycle parts are absent. No `draft` or `schedul` references were found in `frontend/src`. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Is the absence of a report status/moderation workflow intentional? | `PostReport` has no status/resolution field and no resolve endpoint; admin dashboard counts reports without a status filter. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Should `email_verified` be part of the requirements? | `User.email_verified` exists, but no writer or verification endpoint was found in the inspected source. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Is multi-image posting required? | `PostImage` model and read-only serializer field exist, but no API writer was found. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Should `AdminAction` be treated as an audit log? | Model exists, but no actor field or writer was found; admin source uses Django `LogEntry` for real activity history. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Are the unused frontend files intentional? | `Profile.jsx`, `CreatePost.jsx`, `AuthWelcomePanel.jsx`, `formErrors.js`, `App.css`, several assets, and `icons.svg` have no live import/reference. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Are the PWA limitations acceptable? | Service worker caches only `/` and `/index.html`; no offline API/media data, push notifications, install prompt, update flow, or 192/512 PNG icons are present. | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |

## 5. Test and verification evidence

| Item | State |
| --- | --- |
| Current result of `..\venv\Scripts\python.exe manage.py check` | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| `..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run` was executed during the source audit and returned `No changes detected`. | Verified. Whether the deployed database has applied all migrations remains `[NOT VERIFIED - USER CONFIRMATION REQUIRED]`. |
| Current result of `..\venv\Scripts\python.exe manage.py test --keepdb` | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Current result of `npm.cmd run lint` | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Current result of `npm.cmd run build` | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |
| Whether frontend tests should be added to the project scope | `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` |

## 6. How to use this file in generated documents

- Copy unresolved items into the relevant section rather than creating a single appendix-only list.
- In SRS requirement `Verification` fields, use `[NOT VERIFIED - USER CONFIRMATION REQUIRED]` when no source-level or executed verification exists.
- In diagrams, append the marker to any node or note that depends on an unresolved deployment/product decision.
- In the university report, place runtime and deployment unknowns in **Limitations** and **Future Work**, not in **Results**.
- Never resolve an unknown by guessing a value, a route, a table, a workflow, or a test result.
