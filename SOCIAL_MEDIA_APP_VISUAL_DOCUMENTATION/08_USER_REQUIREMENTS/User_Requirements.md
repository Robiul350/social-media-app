# User Requirements

IDs are stable across the visual package. `UR` identifies a user-facing requirement, `FR` references the source-derived feature ID from `FEATURE_IMPLEMENTATION_MATRIX.md`, and `NFR` identifies a non-functional requirement.

## Functional requirements

| ID | Requirement | Primary actor | Source feature | Status |
| --- | --- | --- | --- | --- |
| UR-001 | Register account | Guest | F-001 | Implemented |
| UR-002 | Login and receive JWT | Guest | F-002 | Implemented |
| UR-003 | Refresh access token | Registered User | F-003 | Implemented |
| UR-004 | Logout / blacklist refresh | Registered User | F-004 | Implemented |
| UR-005 | Request password reset | Guest | F-006 | Backend only |
| UR-006 | Confirm password reset | Guest | F-007 | Backend only |
| UR-007 | Deactivate account | Registered User | F-008 | Backend only |
| UR-008 | Edit own profile and privacy | Registered User | F-011 | Implemented |
| UR-009 | Search and discover people | Registered User | F-015 | Implemented |
| UR-010 | View public profile | Registered User | F-012 | Implemented |
| UR-011 | Create/edit/delete post | Content Author | F-019 | Implemented |
| UR-012 | Browse filtered feed | Registered User | F-020 | Implemented |
| UR-013 | Like post | Registered User | F-034 | Implemented |
| UR-014 | Comment and reply | Registered User | F-035, F-036 | Implemented |
| UR-015 | Bookmark post | Registered User | F-028 | Implemented |
| UR-016 | Pin / repost / report post | Content Author / Registered User | F-026, F-027, F-031 | Partial |
| UR-017 | Create and view story | Registered User | F-045, F-046, F-047 | Implemented |
| UR-018 | React to story | Registered User | F-049 | Backend only |
| UR-019 | Follow / unfollow user | Registered User | F-040 | Implemented |
| UR-020 | Send/accept/reject friend request | Registered User | F-042 | Partial |
| UR-021 | Block / unblock user | Registered User | F-044 | Partial |
| UR-022 | Manage notification preferences | Registered User | F-054 | Implemented |
| UR-023 | Read notifications and counts | Registered User | F-051, F-053 | Implemented |
| UR-024 | Send direct message | Message Participant | F-059, F-060 | Implemented |
| UR-025 | Send typing/presence/read events | Message Participant | F-061, F-062 | Implemented |
| UR-026 | Create group conversation | Group Member | F-064 | Backend only |
| UR-027 | Send group message | Group Member | F-064 | Backend only |
| UR-028 | Vote in poll | Registered User | F-030 | Backend only |
| UR-029 | Submit post report | Registered User | F-031 | Partial |
| UR-030 | Review admin analytics | Admin | F-068 | Implemented |
| UR-031 | Manage users via admin actions | Admin | F-065 | Implemented |
| UR-032 | View system status | Admin | F-070, F-071 | Implemented |
| UR-033 | Persist JWT session in browser storage | Registered User | F-003 | Implemented |
| UR-034 | Use light/dark theme | Registered User | F-074 | Implemented |
| UR-035 | Cache only the app shell offline | Registered User | F-073 | Partial |

## Non-functional requirements

| ID | Category | Requirement |
| --- | --- | --- |
| NFR-001 | Authentication | HTTP requests use bearer access tokens; WebSocket connections use query-string access tokens. |
| NFR-002 | Token lifecycle | Refresh tokens rotate and blacklisting is enabled; the SPA refreshes once on 401. |
| NFR-003 | Privacy | Audience, block, private-profile, and story-expiry filters are applied in application query layers. |
| NFR-004 | Notification delivery | Notifications are persisted before `on_commit` channel publication; preferences and blocks are checked centrally. |
| NFR-005 | Real-time transport | ASGI/Daphne is required; Redis is needed for multi-process WebSocket fan-out. |
| NFR-006 | Performance | Home feed supports opt-in pagination; most other SPA lists render the first response only. |
| NFR-007 | Accessibility | Dialogs, tabs, switches, keyboard navigation, focus traps, and reduced-motion handling exist; several form-label gaps remain. |
| NFR-008 | Responsiveness | CSS breakpoints support desktop, tablet, mobile, and very small screens. |
| NFR-009 | Security | LocalStorage tokens and query-string WebSocket tokens are documented risks; media URLs are not authorization-aware. |
| NFR-010 | Observability | Admin system page reports DB connectivity and configuration facts; no Redis ping or socket handshake is performed. |
| NFR-011 | Verification | Backend tests exist; frontend tests are not found. Current command results are [NOT VERIFIED - USER CONFIRMATION REQUIRED]. |
| NFR-012 | Deployment | Production topology, proxy, TLS, static/media hosting, CI/CD, and monitoring are [NOT VERIFIED - USER CONFIRMATION REQUIRED]. |

## Requirement handling rules

- Proposed mockups for password reset, explore/settings-style screens, story reactions, user dashboard, and user reporting are visual proposals only; they do not convert backend-only features into implemented requirements.
- Requirements marked Backend only or Partial keep that status in every diagram and matrix.
- No new route, model, endpoint, workflow, or test result is invented.
- Unresolved runtime and product decisions retain the exact marker [NOT VERIFIED - USER CONFIRMATION REQUIRED].
