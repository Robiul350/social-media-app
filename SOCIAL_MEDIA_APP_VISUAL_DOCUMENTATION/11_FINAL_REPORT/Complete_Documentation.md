# Complete Software Documentation — Social Media App (working UI/admin name: SocialConnect)

Generated visual documentation package. Product-brand finalization is [NOT VERIFIED - USER CONFIRMATION REQUIRED].

## 1. Purpose and evidence rule

This package converts the source-verified evidence in `CLAUDE_DOCUMENTATION_PROMPT/` into university-level project documentation and visual assets. Runtime source is the highest evidence source. Historical reports were used only to locate claims requiring confirmation. No application source file was modified.

Status vocabulary: Implemented, Partial, Backend only, Planned / documented, Not Found, Needs Verification.

## 2. Executive summary

| Area | Verified summary |
| --- | --- |
| Product | React 19.3.1 SPA + Django 6.1/DRF 3.18.0 backend over PostgreSQL; custom admin at `/admin/`. |
| Core implemented flows | Registration/login/JWT refresh/logout; profiles; feed; post CRUD; likes/comments/replies; follows/friends/blocks; stories create/list/view; notifications/preferences; direct chat; custom admin dashboard/analytics/roles/system. |
| Partial or backend-only | Password reset UI, polls, story/comment reactions, group chat, multi-image upload, drafts/scheduling controls, report moderation, hashtag browsing, block-list screen, message edit/delete controls, PWA offline/push/install/update. |
| Verification | `makemigrations --check --dry-run` returned `No changes detected` during the audit. Backend tests, lint, build, and browser smoke results are [NOT VERIFIED - USER CONFIRMATION REQUIRED]. |

## 3. Architecture overview

The browser reaches the React SPA through Vite in development and the Django REST API at `/api/`. WebSockets use ASGI with `config.asgi:application`; `ws/chat/<user_id>/?token=<access>` and `ws/notifications/?token=<access>` are the verified routes. PostgreSQL is mandatory. Redis is optional locally when `REDIS_URL` is unset and required for multi-process fan-out. Production topology, proxy, TLS, static/media hosting, monitoring, backups, and CI/CD are [NOT VERIFIED - USER CONFIRMATION REQUIRED].

See `06_SYSTEM_ARCHITECTURE/` for ten focused architecture images.

## 4. Database design

Twenty-six source-verified Django tables are documented in `04_ER_DIAGRAM/Data_Dictionary.md`. Relationships are implemented as foreign keys, one-to-one fields, and many-to-many through models. Privacy is enforced through `backend/social/access.py` application queries, not database row-level security. Chat deletion is soft through `Message.deleted_at`. Known schema-level gaps are documented in `DATABASE_ANALYSIS.md`.

### ER and database visualizations (5 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `04_ER_DIAGRAM/Database_Relationship_Diagram.png` | yes | `04_ER_DIAGRAM/Database_Relationship_Diagram.mmd` |
| `04_ER_DIAGRAM/Database_Schema_Visualization.png` | yes | `04_ER_DIAGRAM/Database_Schema_Visualization.mmd` |
| `04_ER_DIAGRAM/ER_Diagram.png` | yes | `04_ER_DIAGRAM/ER_Diagram.mmd` |
| `04_ER_DIAGRAM/Logical_Database_Diagram.png` | yes | `04_ER_DIAGRAM/Logical_Database_Diagram.mmd` |
| `04_ER_DIAGRAM/Physical_Database_Diagram.png` | yes | `04_ER_DIAGRAM/Physical_Database_Diagram.mmd` |


## 5. UML model

UML deliverables include one use-case diagram, one class diagram, twelve sequence diagrams, ten activity diagrams, and five additional diagrams (state, component, deployment, package, object). All participants, states, events, and components are source-verified; illustrative object values are explicitly labelled sample instances.

### UML diagrams (29 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `05_UML_DIAGRAMS/Activity/Activity_001_Registration.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_001_Registration.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_002_Login.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_002_Login.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_003_Post_Creation.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_003_Post_Creation.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_004_Like_and_Comment.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_004_Like_and_Comment.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_005_Follow.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_005_Follow.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_006_Story_Creation.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_006_Story_Creation.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_007_Story_Reaction.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_007_Story_Reaction.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_008_Chat.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_008_Chat.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_009_Notification.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_009_Notification.mmd` |
| `05_UML_DIAGRAMS/Activity/Activity_010_Admin_Management.png` | yes | `05_UML_DIAGRAMS/Activity/Activity_010_Admin_Management.mmd` |
| `05_UML_DIAGRAMS/Class/Class_Diagram.png` | yes | `05_UML_DIAGRAMS/Class/Class_Diagram.mmd` |
| `05_UML_DIAGRAMS/Component/Component_Diagram.png` | yes | `05_UML_DIAGRAMS/Component/Component_Diagram.mmd` |
| `05_UML_DIAGRAMS/Deployment/Deployment_Diagram.png` | yes | `05_UML_DIAGRAMS/Deployment/Deployment_Diagram.mmd` |
| `05_UML_DIAGRAMS/Object/Object_Diagram.png` | yes | `05_UML_DIAGRAMS/Object/Object_Diagram.mmd` |
| `05_UML_DIAGRAMS/Package/Package_Diagram.png` | yes | `05_UML_DIAGRAMS/Package/Package_Diagram.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_001_Registration.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_001_Registration.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_002_Login.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_002_Login.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_003_Create_Post.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_003_Create_Post.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_004_View_Feed.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_004_View_Feed.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_005_Like_Post.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_005_Like_Post.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_006_Comment_Post.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_006_Comment_Post.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_007_Follow_User.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_007_Follow_User.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_008_Create_Story.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_008_Create_Story.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_009_React_Story.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_009_React_Story.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_010_Send_Chat.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_010_Send_Chat.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_011_Receive_Notification.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_011_Receive_Notification.mmd` |
| `05_UML_DIAGRAMS/Sequence/Sequence_012_Update_Profile.png` | yes | `05_UML_DIAGRAMS/Sequence/Sequence_012_Update_Profile.mmd` |
| `05_UML_DIAGRAMS/State_Machine/State_Machine_Diagram.png` | yes | `05_UML_DIAGRAMS/State_Machine/State_Machine_Diagram.mmd` |
| `05_UML_DIAGRAMS/Use_Case/Use_Case_Diagram.png` | yes | `05_UML_DIAGRAMS/Use_Case/Use_Case_Diagram.mmd` |


## 6. UI/UX design system

Design tokens use Segoe UI typography, a blue/indigo primary palette, 12–20 px spacing increments, 10–20 px radii, white cards, soft shadows, and responsive three-zone desktop / single-column mobile layouts. Screens not present in the active router are labelled proposed. Mockups are visual proposals only and do not add routes or features to the implementation.

### UI mockups (desktop PNG; mobile PNG and SVG saved alongside) (24 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `02_UI_MOCKUPS/Desktop/UI-SCR-001_Login.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-002_Registration.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-003_Forgot_Password.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-004_Home__or__News_Feed.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-005_User_Profile.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-006_Edit_Profile.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-007_Create_Post.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-008_Post_Details.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-009_Comments_and_Replies.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-010_Stories_Section.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-011_Story_Viewer.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-012_Story_Reaction.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-013_Explore_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-014_Search_Results.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-015_Followers_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-016_Following_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-017_Notification_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-018_Messenger_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-019_Individual_Chat_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-020_Settings_Page.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-021_User_Dashboard.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-022_Admin_Dashboard.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-023_Report_User.png` | yes | — |
| `02_UI_MOCKUPS/Desktop/UI-SCR-024_Block_User.png` | yes | — |


### Wireframes (desktop PNG; mobile PNG and SVG saved alongside) (11 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `03_WIREFRAMES/Desktop/WF-001_Login.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-002_Registration.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-003_Home_Feed.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-004_Profile.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-005_Create_Post.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-006_Story.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-007_Explore.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-008_Chat.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-009_Notification.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-010_Settings.png` | yes | — |
| `03_WIREFRAMES/Desktop/WF-011_Admin_Dashboard.png` | yes | — |


## 7. Data flow diagrams

DFDs cover context, level 1, and five level 2 processes: authentication, post management, social interaction, chat, and notification. External entities, processes, stores, and flows are restricted to source-verified components.

### DFD diagrams (7 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `07_DFD/Level_0/DFD_Level_0.png` | yes | `07_DFD/Level_0/DFD_Level_0.mmd` |
| `07_DFD/Level_1/DFD_Level_1.png` | yes | `07_DFD/Level_1/DFD_Level_1.mmd` |
| `07_DFD/Level_2/Level_2_Authentication.png` | yes | `07_DFD/Level_2/Level_2_Authentication.mmd` |
| `07_DFD/Level_2/Level_2_Chat.png` | yes | `07_DFD/Level_2/Level_2_Chat.mmd` |
| `07_DFD/Level_2/Level_2_Notification.png` | yes | `07_DFD/Level_2/Level_2_Notification.mmd` |
| `07_DFD/Level_2/Level_2_Post_Management.png` | yes | `07_DFD/Level_2/Level_2_Post_Management.mmd` |
| `07_DFD/Level_2/Level_2_Social_Interaction.png` | yes | `07_DFD/Level_2/Level_2_Social_Interaction.mmd` |


## 8. Requirements and flows

Thirty-five user requirements (`UR-001`–`UR-035`) and twelve non-functional requirements (`NFR-001`–`NFR-012`) are defined in `08_USER_REQUIREMENTS/User_Requirements.md`. IDs are stable through the diagrams, `09_TRACEABILITY/Requirements_Traceability.xlsx`, and proposed test cases.

### Requirement/flow diagrams (7 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `08_USER_REQUIREMENTS/Feature_Hierarchy_Diagram.png` | yes | `08_USER_REQUIREMENTS/Feature_Hierarchy_Diagram.mmd` |
| `08_USER_REQUIREMENTS/Navigation_Flow_Diagram.png` | yes | `08_USER_REQUIREMENTS/Navigation_Flow_Diagram.mmd` |
| `08_USER_REQUIREMENTS/Sitemap/Sitemap.png` | yes | `08_USER_REQUIREMENTS/Sitemap/Sitemap.mmd` |
| `08_USER_REQUIREMENTS/Stakeholder_Diagram.png` | yes | `08_USER_REQUIREMENTS/Stakeholder_Diagram.mmd` |
| `08_USER_REQUIREMENTS/User_Flow/User_Flow_Diagram.png` | yes | `08_USER_REQUIREMENTS/User_Flow/User_Flow_Diagram.mmd` |
| `08_USER_REQUIREMENTS/User_Journey/User_Journey_Map.png` | yes | `08_USER_REQUIREMENTS/User_Journey/User_Journey_Map.mmd` |
| `08_USER_REQUIREMENTS/User_Requirement_Diagram.png` | yes | `08_USER_REQUIREMENTS/User_Requirement_Diagram.mmd` |


## 9. Testing and traceability

The traceability workbook maps Requirement → UI Screen → React Component → Django Module → API → Database Model → Proposed Test Case. Current test, lint, build, and browser results remain [NOT VERIFIED - USER CONFIRMATION REQUIRED] unless the documented commands are run and their output is recorded.

### Testing diagrams (4 PNG images)

| Image | SVG | Editable source |
| --- | --- | --- |
| `10_TESTING/Testing_Flow/API_Testing_Flow.png` | yes | `10_TESTING/Testing_Flow/API_Testing_Flow.mmd` |
| `10_TESTING/Testing_Flow/Authentication_Testing_Flow.png` | yes | `10_TESTING/Testing_Flow/Authentication_Testing_Flow.mmd` |
| `10_TESTING/Testing_Flow/Functional_Test_Case_Diagram.png` | yes | `10_TESTING/Testing_Flow/Functional_Test_Case_Diagram.mmd` |
| `10_TESTING/Testing_Flow/Testing_Workflow.png` | yes | `10_TESTING/Testing_Flow/Testing_Workflow.mmd` |


## 10. Limitations and unverified items

- Final product name and version: [NOT VERIFIED - USER CONFIRMATION REQUIRED].
- Production deployment topology and environment values: [NOT VERIFIED - USER CONFIRMATION REQUIRED].
- Email delivery and Redis runtime: [NOT VERIFIED - USER CONFIRMATION REQUIRED].
- Current backend test, frontend lint, and frontend build results: [NOT VERIFIED - USER CONFIRMATION REQUIRED].
- Browser accessibility and responsive smoke testing: [NOT VERIFIED - USER CONFIRMATION REQUIRED].
- Proposed screens for missing routes are not implemented features.

## 11. Deliverable counts

- UI mockups: 24 screens × 2 layouts = 48 PNG + 48 SVG; 24 HTML sources + 1 CSS source.
- Wireframes: 11 screens × 2 layouts = 22 PNG + 22 SVG; 11 HTML sources + 1 CSS source.
- ER/database diagrams: 5 PNG + 5 SVG + 5 Mermaid + 5 PlantUML sources.
- UML diagrams: 29 PNG + 29 SVG + 29 Mermaid + 29 PlantUML sources.
- Architecture diagrams: 10 PNG + 10 SVG + 10 Mermaid sources.
- DFD diagrams: 7 PNG + 7 SVG + 7 Mermaid sources.
- Requirement/flow diagrams: 7 PNG + 7 SVG + 7 Mermaid sources.
- Testing diagrams: 4 PNG + 4 SVG + 4 Mermaid sources.

## 12. Rendering note

Mermaid CLI, PlantUML, Graphviz, and browser screenshot tooling were not available in the checked-out environment. Therefore, every image was rendered deterministically with Python/Pillow from the same operation list that produces its SVG. `.mmd` and `.puml` files are provided as editable sources; HTML/CSS sources are provided for mockups and wireframes. No image is a placeholder.
