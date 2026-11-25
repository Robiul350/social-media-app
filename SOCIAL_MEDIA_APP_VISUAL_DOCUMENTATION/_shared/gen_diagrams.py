"""Generate ER, UML, architecture, DFD, requirement, and testing diagram images."""

from __future__ import annotations

from pathlib import Path

from vizlib import C, DiagramRenderer, save_pair, write_text

ROOT = Path(__file__).resolve().parents[1]
ER = ROOT / "04_ER_DIAGRAM"
UML = ROOT / "05_UML_DIAGRAMS"
ARCH = ROOT / "06_SYSTEM_ARCHITECTURE"
DFD = ROOT / "07_DFD"
REQ = ROOT / "08_USER_REQUIREMENTS"
TEST = ROOT / "10_TESTING" / "Testing_Flow"

UNVERIFIED = "[NOT VERIFIED - USER CONFIRMATION REQUIRED]"
RULE = "Source-verified | Social Media App (working UI/admin name: SocialConnect)"


def mmsafe(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(value))


def mmd_flow(nodes: list[dict], edges: list[dict], title: str) -> str:
    lines = [f"%% {title}", "%% " + RULE, "flowchart LR"]
    for n in nodes:
        label = n.get("label", n["id"]).replace('"', "'")
        if n.get("fields"):
            label += "<br/>" + "<br/>".join("• " + f for f in n["fields"][:4])
        lines.append(f'  {mmsafe(n["id"])}["{label}"]')
    for e in edges:
        arrow = "---" if e.get("both") else ("-.->" if e.get("dashed") else "-->")
        label = e.get("label", "")
        suffix = f'|"{label}"|' if label else ""
        lines.append(f"  {mmsafe(e['src'])} {arrow}{suffix} {mmsafe(e['dst'])}")
    return "\n".join(lines) + "\n"


def puml_flow(nodes: list[dict], edges: list[dict], title: str) -> str:
    lines = ["@startuml", f"title {title}", "left to right direction", "skinparam rectangleBackgroundColor #E8F0FE", "skinparam rectangleBorderColor #2563EB"]
    for n in nodes:
        label = n.get("label", n["id"])
        if n.get("fields"):
            label += "\\n" + "\\n".join(n["fields"][:4])
        lines.append(f'rectangle "{label}" as {mmsafe(n["id"])}')
    for e in edges:
        arrow = "---" if e.get("both") else ("..>" if e.get("dashed") else "-->")
        label = e.get("label", "")
        suffix = f" : {label}" if label else ""
        lines.append(f"{mmsafe(e['src'])} {arrow} {mmsafe(e['dst'])}{suffix}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def draw_graph(
    path: Path,
    title: str,
    subtitle: str,
    nodes: list[dict],
    edges: list[dict],
    note: str = "",
    width: int = 1920,
    height: int = 1080,
    puml: bool = True,
) -> None:
    r = DiagramRenderer(title, subtitle, width, height)
    for n in nodes:
        r.node(n["id"], n["label"], n["x"], n["y"], n.get("w", 220), n.get("h", 92), n.get("kind", "entity"), n.get("fields"), n.get("sublabel", ""))
    for e in edges:
        r.edge(e["src"], e["dst"], e.get("label", ""), e.get("color"), e.get("dashed", False), e.get("both", False), e.get("offset", 0), e.get("width", 2))
    if note:
        r.c.rect(40, height - 122, width - 80, 62, fill=C["white"], radius=12, outline=C["line"])
        r.c.text(60, height - 108, "EXPLANATION / SOURCE RULE", size=12, bold=True, color=C["primary"])
        r.c.text(60, height - 86, note, size=13, color=C["gray_600"], max_width=width - 120)
    result = r.render(path, "mmd", mmd_flow(nodes, edges, title))
    if puml:
        write_text(path.with_suffix(".puml"), puml_flow(nodes, edges, title))


def n(nid, label, x, y, w=220, h=92, kind="entity", fields=None, sublabel="") -> dict:
    return dict(id=nid, label=label, x=x, y=y, w=w, h=h, kind=kind, fields=fields, sublabel=sublabel)


def e(src, dst, label="", dashed=False, both=False, color=None, offset=0) -> dict:
    return dict(src=src, dst=dst, label=label, dashed=dashed, both=both, color=color, offset=offset)


# ---------------------------------------------------------------------------
# ER and database visualizations
# ---------------------------------------------------------------------------

ER_ENTITIES = [
    ("DB-TBL-001", "User", ["id", "username UQ", "email UQ", "email_verified"]),
    ("DB-TBL-002", "Profile", ["user 1-1", "is_private", "allow_comments", "allow_messages"]),
    ("DB-TBL-003", "Story", ["author FK", "privacy", "expires_at", "media"]),
    ("DB-TBL-004", "StoryView", ["story FK", "viewer FK", "UQ(story,viewer)"]),
    ("DB-TBL-005", "StoryReaction", ["story FK", "user FK", "7 types", "UQ(user,story)"]),
    ("DB-TBL-006", "AdminAction", ["inert model", "no actor", "no writer"]),
    ("DB-TBL-007", "Post", ["author FK", "audience", "is_draft", "scheduled_for"]),
    ("DB-TBL-008", "PostImage", ["post FK", "image", "position", "no writer"]),
    ("DB-TBL-009", "Bookmark", ["post FK", "user FK", "UQ(post,user)"]),
    ("DB-TBL-010", "Poll", ["post 1-1", "question", "expires_at"]),
    ("DB-TBL-011", "PollOption", ["poll FK", "text"]),
    ("DB-TBL-012", "PollVote", ["option FK", "user FK", "UQ(option,user)"]),
    ("DB-TBL-013", "Hashtag", ["name UQ", "M2M Post"]),
    ("DB-TBL-014", "PostReport", ["post FK", "reporter FK", "no status"]),
    ("DB-TBL-015", "Like", ["post FK", "user FK", "UQ(post,user)"]),
    ("DB-TBL-016", "Comment", ["post FK", "user FK", "parent self-FK"]),
    ("DB-TBL-017", "Mention", ["comment FK", "post FK", "mentioned FK"]),
    ("DB-TBL-018", "CommentReaction", ["comment FK", "user FK", "6 types"]),
    ("DB-TBL-019", "Follow", ["follower FK", "following FK", "UQ direction"]),
    ("DB-TBL-020", "Block", ["blocker FK", "blocked FK", "self-check"]),
    ("DB-TBL-021", "FriendRequest", ["sender FK", "receiver FK", "status"]),
    ("DB-TBL-022", "Notification", ["recipient FK", "sender FK", "type", "is_read"]),
    ("DB-TBL-023", "NotificationPreference", ["user 1-1", "8 booleans"]),
    ("DB-TBL-024", "GroupConversation", ["created_by FK", "name", "M2M members"]),
    ("DB-TBL-025", "GroupMembership", ["group FK", "user FK", "role", "muted/archived"]),
    ("DB-TBL-026", "Message", ["sender FK", "receiver FK", "group FK", "deleted_at"]),
]

ER_RELATIONS = [
    ("DB-TBL-001", "DB-TBL-002", "1—1"),
    ("DB-TBL-001", "DB-TBL-007", "1—N"),
    ("DB-TBL-001", "DB-TBL-003", "1—N"),
    ("DB-TBL-003", "DB-TBL-004", "1—N"),
    ("DB-TBL-003", "DB-TBL-005", "1—N"),
    ("DB-TBL-007", "DB-TBL-008", "1—N"),
    ("DB-TBL-007", "DB-TBL-010", "1—1"),
    ("DB-TBL-010", "DB-TBL-011", "1—N"),
    ("DB-TBL-011", "DB-TBL-012", "1—N"),
    ("DB-TBL-007", "DB-TBL-013", "M—N"),
    ("DB-TBL-007", "DB-TBL-016", "1—N"),
    ("DB-TBL-016", "DB-TBL-016", "self replies"),
    ("DB-TBL-007", "DB-TBL-015", "1—N"),
    ("DB-TBL-001", "DB-TBL-019", "1—N"),
    ("DB-TBL-001", "DB-TBL-020", "1—N"),
    ("DB-TBL-001", "DB-TBL-021", "1—N"),
    ("DB-TBL-001", "DB-TBL-022", "1—N"),
    ("DB-TBL-001", "DB-TBL-023", "1—1"),
    ("DB-TBL-024", "DB-TBL-025", "1—N"),
    ("DB-TBL-026", "DB-TBL-024", "N—1 group"),
    ("DB-TBL-001", "DB-TBL-026", "1—N sender"),
]

complete_nodes = []
for idx, (tid, label, fields) in enumerate(ER_ENTITIES):
    col, row = idx % 5, idx // 5
    complete_nodes.append(n(tid, label, 40 + col * 470, 150 + row * 220, 420, 170, "entity", fields, tid))
complete_edges = [e(a, b, label, both=True) for a, b, label in ER_RELATIONS if a != b]
draw_graph(
    ER / "ER_Diagram",
    "Complete Entity-Relationship Diagram",
    "All 26 source-verified Django tables; DB-TBL IDs match Database_Analysis.md.",
    complete_nodes,
    complete_edges,
    "Attributes are abbreviated. Cardinality is shown on the relationship diagram. Privacy is application-layer only; no row-level security is present.",
    width=2400,
    height=1600,
)

logical_nodes = []
groups = {
    "users": (40, 170, ["DB-TBL-001", "DB-TBL-002", "DB-TBL-003", "DB-TBL-004", "DB-TBL-005", "DB-TBL-006"]),
    "posts": (440, 170, ["DB-TBL-007", "DB-TBL-008", "DB-TBL-009", "DB-TBL-010", "DB-TBL-011", "DB-TBL-012", "DB-TBL-013", "DB-TBL-014"]),
    "social": (840, 170, ["DB-TBL-015", "DB-TBL-016", "DB-TBL-017", "DB-TBL-018", "DB-TBL-019", "DB-TBL-020", "DB-TBL-021"]),
    "notifications": (1240, 170, ["DB-TBL-022", "DB-TBL-023"]),
    "chat": (1560, 170, ["DB-TBL-024", "DB-TBL-025", "DB-TBL-026"]),
}
lookup = {tid: (label, fields) for tid, label, fields in ER_ENTITIES}
for app, (gx, gy, ids) in groups.items():
    r = DiagramRenderer  # noqa: F841 - keeps naming explicit
    logical_nodes.append(n(f"lane_{app}", f"{app} app", gx, gy, 340, 700, "note", None, "LOGICAL GROUP"))
    for j, tid in enumerate(ids):
        label, fields = lookup[tid]
        logical_nodes.append(n(tid, label.replace("DB-TBL-", ""), gx + 10, gy + 54 + j * 92, 320, 78, "entity", fields[:3], tid))
draw_graph(
    ER / "Logical_Database_Diagram",
    "Logical Database Diagram",
    "Entities grouped by Django application; physical table names are documented in the data dictionary.",
    logical_nodes,
    [e("lane_users", "lane_posts", "author/posts", dashed=True), e("lane_posts", "lane_social", "likes/comments", dashed=True), e("lane_social", "lane_notifications", "events", dashed=True), e("lane_users", "lane_chat", "members/messages", dashed=True)],
    "Logical grouping only. Cross-app foreign keys are implemented in Python model definitions and migrations.",
    width=1920,
    height=1080,
)

physical_nodes = []
for idx, (tid, label, fields) in enumerate(ER_ENTITIES):
    table = next(t for t, _, _, _ in [] ) if False else tid  # explicit placeholder
    col, row = idx % 4, idx // 4
    physical_nodes.append(n(tid, f"{label} → {tid}", 40 + col * 470, 150 + row * 145, 430, 120, "store", fields, "PostgreSQL table"))
draw_graph(
    ER / "Physical_Database_Diagram",
    "Physical Database Diagram",
    "PostgreSQL tables implied by current Django models and migrations.",
    physical_nodes,
    [],
    "Primary keys are implicit BigAutoField IDs. See Data_Dictionary.md for exact field names, constraints, and indexes.",
    width=1920,
    height=1320,
)

rel_nodes = []
for idx, (tid, label, fields) in enumerate(ER_ENTITIES):
    col, row = idx % 6, idx // 6
    rel_nodes.append(n(tid, label, 30 + col * 310, 150 + row * 240, 270, 130, "entity", fields[:2], tid))
rel_edges = [e(a, b, label, both=True) for a, b, label in ER_RELATIONS]
draw_graph(
    ER / "Database_Relationship_Diagram",
    "Database Relationship Diagram",
    "Relationship cardinality and direction from current model foreign keys and many-to-many fields.",
    rel_nodes,
    rel_edges,
    "Self-relations are labelled. PollVote DB uniqueness is per option only; Message has no receiver/group exclusive constraint.",
    width=1920,
    height=1080,
)

schema_nodes = [
    n("browser", "React SPA + Django admin", 60, 180, 300, 100, "actor"),
    n("api", "DRF APIView / generics", 430, 180, 300, 100, "api"),
    n("access", "social/access.py", 810, 180, 260, 100, "process"),
    n("notify", "notifications/utils.py", 1150, 180, 280, 100, "process"),
    n("pg", "PostgreSQL", 1500, 180, 300, 100, "database"),
    n("channel", "Channel layer", 1150, 380, 280, 100, "websocket"),
    n("ws", "Channels consumers", 810, 380, 260, 100, "websocket"),
    n("media", "Media storage", 1500, 380, 300, 100, "store"),
    n("blacklist", "JWT blacklist tables", 1500, 580, 300, 100, "database"),
    n("app_filter", "Application-layer visibility", 430, 580, 300, 100, "note"),
]
draw_graph(
    ER / "Database_Schema_Visualization",
    "Database Schema Visualization",
    "How application layers reach persistent state.",
    schema_nodes,
    [e("browser", "api", "REST/WS"), e("api", "access", "visibility"), e("api", "notify", "create_notification"), e("access", "pg", "filtered queries"), e("notify", "pg", "persist"), e("notify", "channel", "on_commit"), e("channel", "ws", "fan-out"), e("api", "media", "uploads"), e("api", "blacklist", "refresh rotation"), e("access", "app_filter", "not DB RLS")],
    "Media URLs are not authorization-aware; production media strategy is " + UNVERIFIED + ".",
)

# ---------------------------------------------------------------------------
# UML diagrams
# ---------------------------------------------------------------------------

USE_CASES = [
    ("UC-001", "Register account"), ("UC-002", "Login and receive JWT"), ("UC-003", "Refresh access token"),
    ("UC-004", "Logout / blacklist refresh"), ("UC-005", "Request password reset"), ("UC-006", "Confirm password reset"),
    ("UC-007", "Deactivate account"), ("UC-008", "Edit own profile and privacy"), ("UC-009", "Search and discover people"),
    ("UC-010", "View public profile"), ("UC-011", "Create/edit/delete post"), ("UC-012", "Browse filtered feed"),
    ("UC-013", "Like post"), ("UC-014", "Comment and reply"), ("UC-015", "Bookmark post"),
    ("UC-016", "Pin/repost/report post"), ("UC-017", "Create and view story"), ("UC-018", "React to story"),
    ("UC-019", "Follow / unfollow user"), ("UC-020", "Friend request lifecycle"), ("UC-021", "Block / unblock user"),
    ("UC-022", "Manage notification preferences"), ("UC-023", "Read notifications and counts"), ("UC-024", "Send direct message"),
    ("UC-025", "Typing/presence/read events"), ("UC-026", "Create group conversation"), ("UC-027", "Send group message"),
    ("UC-028", "Vote in poll"), ("UC-029", "Submit post report"), ("UC-030", "Review admin analytics"),
    ("UC-031", "Manage users via admin"), ("UC-032", "Mark notifications read in admin"), ("UC-033", "View system status"),
]
uc_nodes = [n("system", "Social Media App system boundary", 250, 140, 1360, 820, "note", None, "SYSTEM BOUNDARY")]
uc_nodes += [
    n("Guest", "Guest", 30, 190, 180, 90, "actor"),
    n("User", "Registered User", 30, 360, 180, 90, "actor"),
    n("Author", "Content Author", 30, 530, 180, 90, "actor"),
    n("Member", "Message Participant", 30, 700, 180, 90, "actor"),
    n("Admin", "Administrator", 1640, 190, 220, 90, "actor"),
    n("GroupMember", "Group Member", 1640, 360, 220, 90, "actor"),
    n("External", "External System", 1640, 530, 220, 90, "external"),
]
for idx, (uid, label) in enumerate(USE_CASES):
    col, row = idx % 5, idx // 5
    uc_nodes.append(n(uid, f"{uid} {label}", 270 + col * 268, 180 + row * 118, 250, 86, "entity", None, ""))
uc_edges = [
    e("Guest", "UC-001"), e("Guest", "UC-002"), e("Guest", "UC-005"), e("Guest", "UC-006"),
    e("User", "UC-008"), e("User", "UC-012"), e("User", "UC-013"), e("User", "UC-023"),
    e("Author", "UC-011"), e("Author", "UC-016"), e("Author", "UC-029"),
    e("Member", "UC-024"), e("Member", "UC-025"),
    e("Admin", "UC-030"), e("Admin", "UC-031"), e("Admin", "UC-032"), e("Admin", "UC-033"),
    e("GroupMember", "UC-026"), e("GroupMember", "UC-027"),
    e("External", "UC-012", "PostgreSQL / Redis / email", dashed=True),
    e("UC-002", "UC-003", "<<include>> on 401", dashed=True),
    e("UC-011", "UC-029", "<<extend>> report", dashed=True),
    e("UC-017", "UC-018", "<<extend>> backend only", dashed=True),
]
draw_graph(
    UML / "Use_Case" / "Use_Case_Diagram",
    "Use Case Diagram",
    "Actors and 33 source-derived use cases. Backend-only cases remain labelled as such in documentation.",
    uc_nodes,
    uc_edges,
    "Administrator is the Django admin actor; no SPA moderation workflow exists. Email delivery is " + UNVERIFIED + ".",
    width=1920,
    height=1080,
)

CLASS_ENTITIES = [
    ("User", "AbstractUser + email_verified", ["username", "email", "is_staff", "is_active"], "authenticate, profile signal"),
    ("Profile", "OneToOne User", ["is_private", "allow_comments", "allow_messages"], "privacy fields"),
    ("Post", "author FK", ["content", "image", "video", "audience"], "hashtag sync in view"),
    ("Story", "author FK", ["media", "text", "privacy", "expires_at"], "24-hour expiry"),
    ("StoryView", "through model", ["story", "viewer", "viewed_at"], "unique pair"),
    ("StoryReaction", "reaction model", ["user", "story", "reaction_type"], "7 choices"),
    ("Like", "toggle model", ["post", "user", "created_at"], "unique pair"),
    ("Comment", "threaded", ["post", "user", "parent", "content"], "owner-only writes"),
    ("Mention", "comment/post target", ["mentioned", "created_at"], "regex extraction"),
    ("CommentReaction", "toggle model", ["comment", "user", "reaction"], "no UI"),
    ("Follow", "directional", ["follower", "following"], "unique direction"),
    ("Block", "directional", ["blocker", "blocked"], "self-check"),
    ("FriendRequest", "stateful", ["sender", "receiver", "status"], "accept/reject"),
    ("Notification", "typed", ["recipient", "sender", "post", "comment"], "central utility"),
    ("NotificationPreference", "OneToOne User", ["8 booleans"], "opt-outs"),
    ("Poll", "OneToOne Post", ["question", "expires_at"], "no CRUD"),
    ("PollOption", "poll FK", ["text"], "vote target"),
    ("PollVote", "option FK", ["user", "option"], "view-level guard"),
    ("Bookmark", "toggle model", ["post", "user"], "unique pair"),
    ("Hashtag", "M2M Post", ["name"], "regex sync"),
    ("PostReport", "create-only", ["post", "reporter", "reason"], "no status"),
    ("PostImage", "ordered gallery", ["post", "image", "position"], "no writer"),
    ("GroupConversation", "M2M members", ["name", "created_by", "avatar"], "REST only"),
    ("GroupMembership", "through model", ["group", "user", "role"], "muted/archived unused"),
    ("Message", "soft-deleted", ["sender", "receiver", "group", "deleted_at"], "WS broadcast"),
    ("AdminAction", "inert", ["action_type", "target_type", "metadata"], "no writer"),
    ("APISerializer", "DRF serializers", ["validate", "create", "update"], "permission-aware output"),
    ("APIView", "DRF endpoints", ["get", "post", "patch", "delete"], "no ViewSets"),
    ("ChatConsumer", "Async consumer", ["connect", "receive", "disconnect"], "JWT query token"),
    ("NotificationConsumer", "Async consumer", ["group_add", "receive"], "client frame translation"),
]
class_nodes = []
for idx, (name, sub, fields, method) in enumerate(CLASS_ENTITIES):
    col, row = idx % 5, idx // 5
    class_nodes.append(n(f"class_{name}", name, 30 + col * 380, 150 + row * 155, 350, 132, "entity", fields + [method], f"DB model / class: {sub}"))
class_edges = [
    e("class_User", "class_Profile", "1—1"), e("class_User", "class_Post", "1—N"), e("class_User", "class_Story", "1—N"),
    e("class_Story", "class_StoryView", "1—N"), e("class_Story", "class_StoryReaction", "1—N"),
    e("class_Post", "class_Like", "1—N"), e("class_Post", "class_Comment", "1—N"), e("class_Post", "class_Poll", "1—1"),
    e("class_Poll", "class_PollOption", "1—N"), e("class_PollOption", "class_PollVote", "1—N"),
    e("class_Post", "class_Hashtag", "M—N"), e("class_Comment", "class_Mention", "1—N"),
    e("class_Comment", "class_CommentReaction", "1—N"), e("class_User", "class_Follow", "1—N"),
    e("class_User", "class_Block", "1—N"), e("class_User", "class_FriendRequest", "1—N"),
    e("class_User", "class_Notification", "1—N"), e("class_User", "class_NotificationPreference", "1—1"),
    e("class_GroupConversation", "class_GroupMembership", "1—N"), e("class_Message", "class_GroupConversation", "N—1"),
    e("class_APIView", "class_APISerializer", "uses"), e("class_APISerializer", "class_Post", "serializes"),
    e("class_ChatConsumer", "class_Message", "persists"), e("class_NotificationConsumer", "class_Notification", "broadcasts"),
]
draw_graph(
    UML / "Class" / "Class_Diagram",
    "Class Diagram",
    "Django models plus the two Channels consumers and representative DRF layers.",
    class_nodes,
    class_edges,
    "Methods shown are source-derived responsibilities, not an exhaustive Python API. AdminAction is inert; LogEntry is the real activity source.",
    width=1920,
    height=1300,
)

SEQUENCES = [
    ("Sequence_001_Registration", "User Registration", ["Guest", "React Login/Register", "DRF API", "User/Profile", "PostgreSQL"], [
        ("Guest", "React Login/Register", "Enter username, email, password"),
        ("React Login/Register", "DRF API", "POST /api/users/register/ [API-010]"),
        ("DRF API", "User/Profile", "Validate password; create User"),
        ("User/Profile", "PostgreSQL", "Signal creates Profile"),
        ("DRF API", "React Login/Register", "201 Registration successful"),
        ("React Login/Register", "Guest", "Redirect to /login"),
    ]),
    ("Sequence_002_Login", "User Login", ["Guest", "Login.jsx", "DRF API", "SimpleJWT", "localStorage"], [
        ("Guest", "Login.jsx", "Enter username/password"),
        ("Login.jsx", "DRF API", "POST /api/users/login/ [API-011]"),
        ("DRF API", "SimpleJWT", "Issue access + refresh"),
        ("DRF API", "Login.jsx", "200 user + tokens"),
        ("Login.jsx", "localStorage", "Store access/refresh/user_id/username"),
        ("Login.jsx", "Guest", "Dispatch auth-change; redirect"),
    ]),
    ("Sequence_003_Create_Post", "Creating a Post", ["Author", "home.jsx composer", "DRF API", "PostSerializer", "PostgreSQL"], [
        ("Author", "home.jsx composer", "Text/media/audience"),
        ("home.jsx composer", "DRF API", "POST /api/posts/ [API-031] multipart"),
        ("DRF API", "PostSerializer", "Validate content/media and sizes"),
        ("PostSerializer", "PostgreSQL", "Create Post; sync hashtags"),
        ("DRF API", "home.jsx composer", "201 PostSerializer"),
        ("home.jsx composer", "Author", "Refresh feed or prepend post"),
    ]),
    ("Sequence_004_View_Feed", "Viewing News Feed", ["User", "home.jsx", "DRF API", "social/access.py", "PostgreSQL"], [
        ("User", "home.jsx", "Open /"),
        ("home.jsx", "DRF API", "GET /api/social/feed/?page=1 [API-040]"),
        ("DRF API", "social/access.py", "Audience/block/private filters"),
        ("social/access.py", "PostgreSQL", "Query visible posts"),
        ("DRF API", "home.jsx", "Paginated object"),
        ("home.jsx", "User", "IntersectionObserver loads next page"),
    ]),
    ("Sequence_005_Like_Post", "Liking a Post", ["User", "PostActions.jsx", "DRF API", "Notification utility", "PostgreSQL"], [
        ("User", "PostActions.jsx", "Click like"),
        ("PostActions.jsx", "DRF API", "POST posts/<id>/like/ [API-041]"),
        ("DRF API", "PostgreSQL", "Toggle Like unique pair"),
        ("DRF API", "Notification utility", "create_notification(like)"),
        ("Notification utility", "PostgreSQL", "Persist if allowed"),
        ("DRF API", "PostActions.jsx", "{liked, like_count}"),
    ]),
    ("Sequence_006_Comment_Post", "Commenting on a Post", ["User", "PostActions.jsx", "DRF API", "social/access.py", "PostgreSQL"], [
        ("User", "PostActions.jsx", "Submit comment or reply"),
        ("PostActions.jsx", "DRF API", "POST posts/<id>/comments/ [API-043]"),
        ("DRF API", "social/access.py", "Visibility + parent same-post check"),
        ("DRF API", "PostgreSQL", "Create Comment; extract mentions"),
        ("DRF API", "PostgreSQL", "Create comment/reply/mention notifications"),
        ("DRF API", "PostActions.jsx", "201 CommentSerializer"),
    ]),
    ("Sequence_007_Follow_User", "Following a User", ["User", "UserProfile.jsx", "DRF API", "social/access.py", "PostgreSQL"], [
        ("User", "UserProfile.jsx", "Click Follow"),
        ("UserProfile.jsx", "DRF API", "POST users/<id>/follow/ [API-046]"),
        ("DRF API", "social/access.py", "Self/block guard"),
        ("DRF API", "PostgreSQL", "Toggle Follow unique pair"),
        ("DRF API", "PostgreSQL", "Create follow notification"),
        ("DRF API", "UserProfile.jsx", "200/201 message; refresh state"),
    ]),
    ("Sequence_008_Create_Story", "Creating a Story", ["Author", "Stories.jsx", "DRF API", "StorySerializer", "PostgreSQL"], [
        ("Author", "Stories.jsx", "Select media/text/privacy"),
        ("Stories.jsx", "DRF API", "POST /api/users/stories/ [API-022]"),
        ("DRF API", "StorySerializer", "Validate ≤25 MB media"),
        ("StorySerializer", "PostgreSQL", "Set author and +24 h expiry"),
        ("DRF API", "Stories.jsx", "201 StorySerializer"),
        ("Stories.jsx", "Author", "Story strip updates"),
    ]),
    ("Sequence_009_React_Story", "Reacting to a Story", ["Viewer", "No SPA control", "DRF API", "Notification utility", "PostgreSQL"], [
        ("Viewer", "No SPA control", "Backend endpoint available only"),
        ("DRF API", "DRF API", "POST stories/<id>/react/ [API-024]"),
        ("DRF API", "PostgreSQL", "Upsert StoryReaction"),
        ("DRF API", "Notification utility", "create_notification(story_reaction)"),
        ("Notification utility", "PostgreSQL", "Persist; on_commit publish"),
        ("DRF API", "No SPA control", "201/200 StoryReactionSerializer"),
    ]),
    ("Sequence_010_Send_Chat", "Sending a Chat Message", ["Sender", "Messages.jsx", "WebSocket / DRF", "ChatConsumer", "PostgreSQL"], [
        ("Sender", "Messages.jsx", "Open /messages/<user_id>/"),
        ("Messages.jsx", "WebSocket / DRF", "ws/chat/<id>/?token=... [API-090]"),
        ("WebSocket / DRF", "ChatConsumer", "can_chat_between recheck"),
        ("ChatConsumer", "PostgreSQL", "Persist Message; create notification"),
        ("ChatConsumer", "Messages.jsx", "chat_message / typing / presence frames"),
        ("Messages.jsx", "Sender", "Render message and receipt"),
    ]),
    ("Sequence_011_Receive_Notification", "Receiving Notifications", ["Domain view", "PostgreSQL", "Channel layer", "NotificationConsumer", "Notifications.jsx", "Recipient"], [
        ("Domain view", "PostgreSQL", "Persist Notification"),
        ("Domain view", "Channel layer", "on_commit notification.created"),
        ("Channel layer", "NotificationConsumer", "Group notifications_<id>"),
        ("NotificationConsumer", "Notifications.jsx", '{"type":"notification",...}'),
        ("Notifications.jsx", "Recipient", "Prepend item; refresh count locally"),
        ("Recipient", "Notifications.jsx", "Mark read: DB/local only"),
    ]),
    ("Sequence_012_Update_Profile", "Updating Profile", ["User", "EditProfile.jsx", "DRF API", "ProfileSerializer", "PostgreSQL"], [
        ("User", "EditProfile.jsx", "Edit fields/privacy/media"),
        ("EditProfile.jsx", "DRF API", "PATCH /api/users/profile/ [API-019]"),
        ("DRF API", "ProfileSerializer", "Validate image sizes/removal flags"),
        ("ProfileSerializer", "PostgreSQL", "Update Profile"),
        ("DRF API", "EditProfile.jsx", "200 Profile updated"),
        ("EditProfile.jsx", "User", "Dispatch profile-change; refresh UI"),
    ]),
]


def render_sequence(path: Path, title: str, participants: list[str], steps: list[tuple[str, str, str]], subtitle: str) -> None:
    r = DiagramRenderer(title, subtitle)
    c = r.c
    top = 160
    bottom = 930
    xs = [int(90 + i * (1740 / max(1, len(participants) - 1))) for i in range(len(participants))]
    for i, p in enumerate(participants):
        c.rect(xs[i] - 110, top, 220, 62, fill=C["primary_soft"], radius=12, outline=C["primary"])
        c.text(xs[i], top + 31, p, size=14, bold=True, color=C["ink"], anchor="mm", max_width=200)
        c.line([(xs[i], top + 62), (xs[i], bottom)], fill=C["gray_300"], width=2, dash=(6, 6))
    y = top + 100
    gap = min(72, (bottom - top - 120) // max(1, len(steps)))
    for idx, (src, dst, label) in enumerate(steps):
        si = participants.index(src) if src in participants else 0
        di = participants.index(dst) if dst in participants else len(participants) - 1
        color = C["primary"] if si != di else C["accent"]
        c.arrow((xs[si], y), (xs[di], y), label=label, color=color, width=2)
        c.text(xs[si], y - 28, f"{idx + 1}", size=10, color=C["muted"], anchor="mm")
        y += gap
    c.rect(40, 980, 1840, 58, fill=C["white"], radius=12, outline=C["line"])
    c.text(62, 996, "EXPLANATION / SOURCE RULE", size=12, bold=True, color=C["primary"])
    c.text(62, 1018, "Participants are limited to those that participate in the verified flow; backend-only branches are explicit.", size=13, color=C["gray_600"], max_width=1800)
    seq_lines = ["@startuml", f"title {title}", "participant " + " participant ".join(p.replace(" ", "_") for p in participants)]
    for src, dst, label in steps:
        seq_lines.append(f"{src.replace(' ', '_')} -> {dst.replace(' ', '_')} : {label}")
    seq_lines.append("@enduml")
    mmd = "sequenceDiagram\n" + "\n".join(f"    participant {p.replace(' ', '_')}" for p in participants) + "\n" + "\n".join(f"    {s.replace(' ', '_')}->>{d.replace(' ', '_')}: {l}" for s, d, l in steps) + "\n"
    result = r.render(path, "mmd", mmd)
    write_text(path.with_suffix(".puml"), "\n".join(seq_lines) + "\n")


for stem, title, participants, steps in SEQUENCES:
    render_sequence(UML / "Sequence" / stem, title, participants, steps, "Source-derived interaction flow; API IDs from API_ANALYSIS.md.")

ACTIVITIES = [
    ("Activity_001_Registration", "Registration Activity", [("start", "Start", "initial"), ("act", "Open /register", "action"), ("act", "Submit username/email/password", "action"), ("dec", "Valid?", "decision"), ("act", "Create User + Profile signal", "action"), ("act", "Redirect to /login", "action"), ("end", "End", "final")]),
    ("Activity_002_Login", "Login Activity", [("start", "Start", "initial"), ("act", "Open /login", "action"), ("act", "POST /api/users/login/", "action"), ("dec", "Credentials valid?", "decision"), ("act", "Store four localStorage keys", "action"), ("act", "Dispatch auth-change; redirect", "action"), ("end", "End", "final")]),
    ("Activity_003_Post_Creation", "Post Creation Activity", [("start", "Start", "initial"), ("act", "Compose text/media/audience", "action"), ("dec", "Content or media present?", "decision"), ("dec", "Within file-size limits?", "decision"), ("act", "POST /api/posts/", "action"), ("act", "Sync hashtags; persist", "action"), ("end", "End", "final")]),
    ("Activity_004_Like_and_Comment", "Like and Comment Activity", [("start", "Start", "initial"), ("act", "Open post", "action"), ("dec", "Like or comment?", "decision"), ("act", "Toggle Like", "action"), ("act", "Create Comment/reply + mentions", "action"), ("act", "create_notification()", "action"), ("end", "End", "final")]),
    ("Activity_005_Follow", "Follow Activity", [("start", "Start", "initial"), ("act", "Open profile/search result", "action"), ("dec", "Self or blocked?", "decision"), ("act", "Toggle Follow", "action"), ("act", "Create follow notification", "action"), ("end", "End", "final")]),
    ("Activity_006_Story_Creation", "Story Creation Activity", [("start", "Start", "initial"), ("act", "Choose media/text/privacy", "action"), ("dec", "Media ≤25 MB?", "decision"), ("act", "POST /api/users/stories/", "action"), ("act", "Set expires_at = now + 24 h", "action"), ("end", "End", "final")]),
    ("Activity_007_Story_Reaction", "Story Reaction Activity", [("start", "Start", "initial"), ("note", "SPA has no reaction control", "note"), ("act", "Backend POST /react/ available", "action"), ("dec", "Reaction exists?", "decision"), ("act", "Create or update StoryReaction", "action"), ("act", "Emit notification on every POST", "action"), ("end", "End", "final")]),
    ("Activity_008_Chat", "Chat Activity", [("start", "Start", "initial"), ("act", "Open /messages/<id>", "action"), ("act", "Connect WebSocket with token", "action"), ("dec", "can_chat_between?", "decision"), ("act", "Persist Message; broadcast", "action"), ("act", "Render chat_message/typing/presence", "action"), ("end", "End", "final")]),
    ("Activity_009_Notification", "Notification Activity", [("start", "Start", "initial"), ("act", "Domain view calls create_notification", "action"), ("dec", "Self/blocked/preference off?", "decision"), ("act", "Persist Notification", "action"), ("act", "on_commit publish notification.created", "action"), ("act", "Consumer sends client frame", "action"), ("end", "End", "final")]),
    ("Activity_010_Admin_Management", "Admin Management Activity", [("start", "Start", "initial"), ("act", "Open /admin/", "action"), ("dec", "Staff and model permission?", "decision"), ("act", "View KPI cards/charts", "action"), ("act", "Open changelist or analytics", "action"), ("act", "LogEntry records mutating action", "action"), ("end", "End", "final")]),
]


def render_activity(path: Path, title: str, steps: list[tuple[str, str, str]], subtitle: str) -> None:
    r = DiagramRenderer(title, subtitle)
    c = r.c
    x = 960
    y = 160
    ids = []
    act_lines = ["@startuml", f"title {title}", "start"]
    for idx, (kind, label, node_kind) in enumerate(steps):
        nid = f"a{idx}"
        ids.append(nid)
        if node_kind == "decision":
            c.polygon([(x, y - 34), (x + 110, y), (x, y + 34), (x - 110, y)], fill=C["warn_soft"], outline=C["warn"])
            c.text(x, y, label, size=13, bold=True, color=C["ink"], anchor="mm", max_width=200)
            act_lines.append(f"if ({label}) then (yes)")
        elif node_kind == "initial":
            c.circle(x, y + 10, 20, fill=C["success"])
            c.text(x, y + 10, "S", size=13, bold=True, color=C["white"], anchor="mm")
        elif node_kind == "final":
            c.circle(x, y + 10, 22, fill=C["navy"])
            c.circle(x, y + 10, 16, fill=C["white"], outline=C["navy"], width=3)
            act_lines.append("endif" if any(k == "decision" for _, _, k in steps) else "")
            act_lines.append("stop")
        else:
            fill = C["warn_soft"] if node_kind == "note" else C["primary_soft"]
            c.rect(x - 240, y - 24, 480, 54, fill=fill, radius=12, outline=C["primary"] if node_kind != "note" else C["warn"])
            c.text(x, y + 3, label, size=13, bold=True, color=C["ink"], anchor="mm", max_width=450)
            act_lines.append(f":{label};")
        if idx > 0:
            c.arrow((x, y - 76), (x, y - 34), color=C["gray_500"], width=2)
        y += 86
    c.rect(40, 980, 1840, 58, fill=C["white"], radius=12, outline=C["line"])
    c.text(62, 996, "EXPLANATION / SOURCE RULE", size=12, bold=True, color=C["primary"])
    c.text(62, 1018, "Decision branches follow source-verified validation; failed branches are documented in the accompanying text, not inferred as new workflows.", size=13, color=C["gray_600"], max_width=1800)
    act_lines.append("@enduml")
    mmd = "flowchart TD\n" + "\n".join(f"  n{i}[{label}]" for i, (_, label, _) in enumerate(steps)) + "\n" + "\n".join(f"  n{i} --> n{i+1}" for i in range(len(steps) - 1)) + "\n"
    r.render(path, "mmd", mmd)
    write_text(path.with_suffix(".puml"), "\n".join(act_lines) + "\n")


for stem, title, steps in ACTIVITIES:
    render_activity(UML / "Activity" / stem, title, steps, "Initial node, actions, decisions, branches, merge, and final node.")

state_nodes = [
    n("friend", "FriendRequest", 60, 170, 330, 180, "entity", ["send → pending", "accept → accepted", "reject → rejected", "delete cancels pending"], "STATE-001"),
    n("notif", "Notification", 430, 170, 330, 180, "entity", ["create → unread", "mark read → read", "no reverse flow", "no WS read update"], "STATE-002"),
    n("message", "Message", 800, 170, 330, 180, "entity", ["send → active", "PATCH → edited", "DELETE → soft-deleted"], "STATE-003"),
    n("post", "Post", 1170, 170, 330, 180, "entity", ["is_draft → draft", "future scheduled → hidden", "otherwise visible"], "STATE-004"),
    n("jwt", "JWT session", 1540, 170, 330, 180, "entity", ["anonymous", "authenticated", "refreshing", "expired/cleared"], "STATE-005"),
    n("s1", "pending", 60, 430, 150, 70, "process"), n("s2", "accepted", 250, 430, 150, 70, "process"), n("s3", "rejected", 440, 430, 150, 70, "process"),
    n("s4", "unread", 700, 430, 150, 70, "process"), n("s5", "read", 900, 430, 150, 70, "process"),
    n("s6", "active", 1160, 430, 150, 70, "process"), n("s7", "edited", 1360, 430, 150, 70, "process"), n("s8", "soft-deleted", 1560, 430, 170, 70, "process"),
    n("s9", "anonymous", 60, 580, 170, 70, "process"), n("s10", "authenticated", 270, 580, 190, 70, "process"), n("s11", "refreshing", 500, 580, 170, 70, "process"), n("s12", "expired/cleared", 710, 580, 190, 70, "process"),
]
state_edges = [e("s1", "s2", "accept"), e("s1", "s3", "reject"), e("s4", "s5", "mark read"), e("s6", "s7", "PATCH"), e("s7", "s8", "DELETE"), e("s9", "s10", "login"), e("s10", "s11", "401"), e("s11", "s10", "refresh ok"), e("s11", "s12", "refresh fail")]
draw_graph(UML / "State_Machine" / "State_Machine_Diagram", "State Machine Diagram", "Five source-verified stateful objects.", state_nodes, state_edges, "Post states are represented by flags/fields, not a dedicated status column. No publisher job was found.", width=1920, height=760)

component_nodes = [
    n("spa", "React SPA", 40, 170, 280, 120, "actor", ["pages/components", "router/theme", "dialogs"], "COMP-001"),
    n("axios", "Axios API client", 360, 170, 280, 120, "api", ["Bearer injection", "single-flight refresh"], "COMP-002"),
    n("store", "Profile store", 680, 170, 260, 120, "process", ["snapshot/subscribe", "in-flight de-dup"], "COMP-003"),
    n("wsclient", "WebSocket clients", 980, 170, 280, 120, "websocket", ["chat + notifications", "reconnect/backoff"], "COMP-004"),
    n("sw", "Service worker", 1280, 170, 260, 120, "process", ["app-shell precache", "network-first nav"], "COMP-005"),
    n("drf", "Django HTTP / DRF", 40, 400, 300, 130, "api", ["5 API prefixes", "serializers/permissions"], "COMP-006"),
    n("access", "social/access.py", 380, 400, 280, 130, "process", ["audience/block", "private/visibility"], "COMP-007"),
    n("notifyutil", "notifications/utils.py", 700, 400, 300, 130, "process", ["preference/block", "on_commit publish"], "COMP-008"),
    n("consumers", "Channels consumers", 1040, 400, 280, 130, "websocket", ["chat protocol", "notification protocol"], "COMP-009"),
    n("admin", "Custom Django admin", 1360, 400, 280, 130, "entity", ["dashboard/analytics", "roles/system"], "COMP-010"),
    n("pg", "PostgreSQL", 380, 620, 280, 110, "database", ["system of record", "JWT blacklist"], "COMP-011"),
    n("channel", "Channel layer", 700, 620, 280, 110, "websocket", ["Redis if REDIS_URL", "else in-memory"], "COMP-012"),
    n("media", "Media storage", 1040, 620, 280, 110, "store", ["MEDIA_ROOT", "prod host unverified"], "COMP-013"),
    n("email", "Email service", 1360, 620, 280, 110, "external", ["password reset", UNVERIFIED], "COMP-014"),
]
component_edges = [e("spa", "axios"), e("spa", "store"), e("spa", "wsclient"), e("spa", "sw"), e("axios", "drf", "REST"), e("wsclient", "consumers", "WS"), e("drf", "access"), e("drf", "notifyutil"), e("drf", "pg"), e("drf", "media"), e("notifyutil", "channel"), e("channel", "consumers"), e("consumers", "pg"), e("admin", "pg"), e("drf", "email")]
draw_graph(UML / "Component" / "Component_Diagram", "Component Diagram", "Source-verified runtime components and external dependencies.", component_nodes, component_edges, "No group WebSocket component exists. Email delivery and production media hosting are " + UNVERIFIED + ".")

deploy_nodes = [
    n("browser", "Browser", 60, 190, 260, 110, "actor", ["React SPA", "Django admin"], "Vite dev server default localhost:5173"),
    n("vite", "Vite dev server", 360, 190, 260, 110, "process", ["dev/build/preview"], "Development only"),
    n("django", "Django ASGI", 660, 190, 300, 110, "api", ["config.asgi:application", "Daphne for WS"], "HTTP + WebSocket"),
    n("drf", "DRF / Channels", 1000, 190, 280, 110, "api", ["5 prefixes", "2 consumers"], "Application layer"),
    n("pg", "PostgreSQL", 1340, 190, 280, 110, "database", ["mandatory", "blacklist tables"], "System of record"),
    n("redis", "Redis channel layer", 660, 420, 300, 110, "websocket", ["if REDIS_URL set", "multi-process fan-out"], "Optional locally"),
    n("memory", "In-memory layer", 1000, 420, 280, 110, "note", ["default fallback", "single-process"], "Source verified"),
    n("media", "Media storage", 1340, 420, 280, 110, "store", ["MEDIA_ROOT", "dev served if DEBUG"], "Production " + UNVERIFIED),
    n("email", "Email provider", 1000, 620, 280, 110, "external", ["reset links"], UNVERIFIED),
    n("proxy", "Reverse proxy / TLS", 360, 620, 280, 110, "external", ["not found in source"], UNVERIFIED),
]
deploy_edges = [e("browser", "vite", "dev SPA"), e("browser", "django", "API/WS"), e("vite", "django", "proxy in dev"), e("django", "drf"), e("drf", "pg"), e("drf", "redis", "if configured"), e("drf", "memory", "otherwise"), e("drf", "media"), e("drf", "email", "password reset"), e("proxy", "django", UNVERIFIED, dashed=True)]
draw_graph(UML / "Deployment" / "Deployment_Diagram", "Deployment Diagram", "Verified development topology plus explicitly unverified production placeholders.", deploy_nodes, deploy_edges, "Production domain, proxy, TLS, worker count, supervisor, static/media host, monitoring, backups, and CI/CD are " + UNVERIFIED + ".")

package_nodes = [
    n("frontend", "frontend/src", 60, 170, 250, 100, "note", None, "React SPA"),
    n("pages", "pages/", 350, 150, 220, 80, "entity"), n("components", "components/", 350, 250, 220, 80, "entity"), n("api", "api/", 350, 350, 220, 80, "entity"), n("hooks", "hooks/", 350, 450, 220, 80, "entity"),
    n("backend", "backend", 660, 170, 250, 100, "note", None, "Django project"),
    n("config", "config/", 960, 150, 220, 80, "entity"), n("users", "users/", 960, 240, 220, 80, "entity"), n("posts", "posts/", 960, 330, 220, 80, "entity"), n("social", "social/", 960, 420, 220, 80, "entity"), n("chat", "chat/", 1230, 240, 220, 80, "entity"), n("notifications", "notifications/", 1230, 330, 220, 80, "entity"),
    n("adminpkg", "templates/admin + static/admin", 660, 480, 280, 90, "entity"),
    n("migrations", "migrations in five apps", 1230, 480, 280, 90, "store"),
]
package_edges = [e("frontend", "pages"), e("frontend", "components"), e("frontend", "api"), e("frontend", "hooks"), e("backend", "config"), e("backend", "users"), e("backend", "posts"), e("backend", "social"), e("backend", "chat"), e("backend", "notifications"), e("backend", "adminpkg"), e("backend", "migrations")]
draw_graph(UML / "Package" / "Package_Diagram", "Package Diagram", "Logical source organization, not a build-system dependency graph.", package_nodes, package_edges, "Dead/unwired frontend files are excluded from active package behavior but documented in SCREEN_ANALYSIS.md.")

object_nodes = [
    n("user1", ":User id=12", 80, 180, 260, 150, "entity", ["username=alexmorgan", "email=alex@example.com"], "sample instance"),
    n("profile1", ":Profile", 400, 180, 260, 150, "entity", ["is_private=false", "allow_messages=followers"], "sample instance"),
    n("post1", ":Post id=88", 720, 180, 260, 150, "entity", ["audience=friends", "is_draft=false"], "sample instance"),
    n("comment1", ":Comment", 1040, 180, 260, 150, "entity", ["parent=null", "content=..."], "sample instance"),
    n("notif1", ":Notification", 1360, 180, 260, 150, "entity", ["type=like", "is_read=false"], "sample instance"),
    n("msg1", ":Message", 400, 460, 260, 150, "entity", ["receiver_id=19", "deleted_at=null"], "sample instance"),
    n("story1", ":Story", 720, 460, 260, 150, "entity", ["privacy=public", "expires_at=+24h"], "sample instance"),
    n("react1", ":StoryReaction", 1040, 460, 260, 150, "entity", ["reaction_type=love"], "backend only"),
    n("prefs", ":NotificationPreference", 1360, 460, 280, 150, "entity", ["likes=true", "mentions=true"], "sample instance"),
]
object_edges = [e("user1", "profile1", "profile"), e("user1", "post1", "author"), e("post1", "comment1", "comments"), e("post1", "notif1", "target"), e("user1", "msg1", "sender"), e("user1", "story1", "author"), e("story1", "react1", "reactions"), e("user1", "prefs", "preferences")]
draw_graph(UML / "Object" / "Object_Diagram", "Object Diagram", "Illustrative object instances using only source-verified attributes and values.", object_nodes, object_edges, "Values are realistic examples for documentation, not extracted database rows.", width=1920, height=720)

# ---------------------------------------------------------------------------
# Architecture diagrams
# ---------------------------------------------------------------------------

ARCHITECTURES = [
    ("High_Level_Architecture", "High-Level System Architecture", "Browser clients, Django HTTP/ASGI services, and persistent/external stores.", [
        n("browser", "Browser: React SPA", 60, 200, 300, 130, "actor", ["routes/components", "localStorage session"]),
        n("admin", "Browser: Django admin", 60, 420, 300, 130, "actor", ["dashboard/roles/system"]),
        n("api", "Django REST Framework", 450, 250, 320, 140, "api", ["users/posts/social", "notifications/chat"]),
        n("ws", "Django Channels", 450, 470, 320, 140, "websocket", ["chat consumer", "notification consumer"]),
        n("pg", "PostgreSQL", 900, 250, 280, 140, "database", ["26 app tables", "JWT blacklist"]),
        n("channel", "Redis / in-memory", 900, 470, 280, 140, "websocket", ["REDIS_URL optional"]),
        n("media", "Media storage", 1300, 250, 280, 140, "store", ["dev Django serving"]),
        n("email", "Email service", 1300, 470, 280, 140, "external", ["reset links " + UNVERIFIED]),
    ], [e("browser", "api", "REST"), e("browser", "ws", "WebSocket"), e("admin", "api", "Django views"), e("api", "pg"), e("api", "media"), e("ws", "channel"), e("ws", "pg"), e("api", "email")]),
    ("Frontend_Architecture", "Frontend Architecture", "React Router pages, shared components, API client, stores, and service worker.", [
        n("main", "main.jsx → App.jsx", 60, 200, 300, 120, "actor", ["router + guards"]),
        n("pages", "Pages (14 routes)", 420, 150, 300, 120, "entity", ["auth/feed/profile/chat"]),
        n("components", "Shared components", 420, 320, 300, 120, "entity", ["AppShell/navbar/actions"]),
        n("api", "Axios client", 800, 200, 280, 120, "api", ["Bearer + refresh"]),
        n("store", "Profile store", 800, 400, 280, 120, "process", ["subscribe/load/reset"]),
        n("ws", "WS clients", 1160, 200, 280, 120, "websocket", ["chat/notifications"]),
        n("sw", "Service worker", 1160, 400, 280, 120, "process", ["app shell only"]),
        n("css", "index.css tokens", 800, 580, 280, 110, "note", ["light/dark"]),
    ], [e("main", "pages"), e("main", "components"), e("pages", "api"), e("components", "api"), e("components", "store"), e("components", "ws"), e("main", "sw"), e("components", "css")]),
    ("Backend_Architecture", "Backend Architecture", "Django apps, shared helpers, API layers, admin, and persistence.", [
        n("urls", "config/urls.py", 60, 200, 260, 110, "api", ["5 API prefixes"]),
        n("users", "users app", 380, 150, 250, 100, "entity"), n("posts", "posts app", 380, 280, 250, 100, "entity"), n("social", "social app", 380, 410, 250, 100, "entity"), n("chat", "chat app", 680, 150, 250, 100, "entity"), n("notifications", "notifications app", 680, 280, 250, 100, "entity"),
        n("access", "social/access.py", 1000, 200, 280, 110, "process", ["visibility centrally"]),
        n("notifyutil", "notifications/utils.py", 1000, 380, 280, 110, "process", ["on_commit publish"]),
        n("admin", "Custom admin", 1340, 200, 260, 110, "entity", ["metrics/analytics"]),
        n("pg", "PostgreSQL", 1340, 420, 260, 110, "database"),
    ], [e("urls", "users"), e("urls", "posts"), e("urls", "social"), e("urls", "chat"), e("urls", "notifications"), e("social", "access"), e("notifications", "notifyutil"), e("access", "pg"), e("notifyutil", "pg"), e("admin", "pg")]),
    ("API_Architecture", "API Communication Architecture", "REST and WebSocket request paths with authentication and refresh behavior.", [
        n("client", "SPA / admin", 60, 240, 260, 120, "actor"),
        n("axios", "Axios interceptor", 360, 200, 280, 120, "api", ["Bearer token", "401 refresh"]),
        n("jwt", "SimpleJWT", 700, 200, 280, 120, "process", ["rotate/blacklist"]),
        n("rest", "DRF APIView/generics", 1040, 200, 320, 120, "api", ["no ViewSets"]),
        n("wsauth", "JWT middleware", 700, 440, 280, 120, "process", ["query-string token"]),
        n("ws", "Channels consumers", 1040, 440, 320, 120, "websocket", ["chat/notifications"]),
        n("db", "PostgreSQL", 1400, 320, 260, 120, "database"),
    ], [e("client", "axios"), e("axios", "jwt"), e("jwt", "rest"), e("rest", "db"), e("client", "wsauth", "WebSocket"), e("wsauth", "ws"), e("ws", "db")]),
    ("Authentication_Architecture", "Authentication Architecture", "JWT session lifecycle from browser storage to blacklist tables.", [
        n("login", "Login.jsx", 60, 200, 260, 110, "actor"),
        n("storage", "localStorage", 380, 200, 260, 110, "store", ["4 keys"]),
        n("guard", "Route guard", 60, 400, 260, 110, "process", ["presence only"]),
        n("api", "Auth endpoints", 700, 200, 280, 110, "api", ["API-010—017"]),
        n("jwt", "SimpleJWT", 1040, 200, 280, 110, "process", ["access + refresh"]),
        n("blacklist", "Blacklist tables", 1380, 200, 280, 110, "database"),
        n("refresh", "Axios 401 flow", 700, 440, 280, 110, "api", ["single-flight"]),
        n("clear", "Clear session", 1040, 440, 280, 110, "process", ["auth-change"]),
    ], [e("login", "api"), e("api", "jwt"), e("jwt", "storage"), e("guard", "storage"), e("api", "refresh", "401"), e("refresh", "jwt"), e("refresh", "clear", "failure"), e("jwt", "blacklist", "logout/rotation")]),
    ("Database_Architecture", "Database Architecture", "PostgreSQL as system of record with application-layer privacy filtering.", [
        n("api", "DRF views", 60, 220, 260, 120, "api"),
        n("access", "social/access.py", 380, 220, 300, 120, "process", ["application filtering"]),
        n("tables", "26 app tables", 760, 220, 300, 120, "database", ["BigAutoField IDs"]),
        n("constraints", "Unique + check constraints", 1140, 220, 320, 120, "store", ["no RLS"]),
        n("media", "Media files", 760, 440, 300, 120, "store", ["direct URLs"]),
        n("blacklist", "JWT blacklist", 1140, 440, 320, 120, "database", ["SimpleJWT"]),
    ], [e("api", "access"), e("access", "tables"), e("tables", "constraints"), e("api", "media"), e("api", "blacklist")]),
    ("Chat_Architecture", "Real-Time Chat Architecture", "Direct-message WebSocket and REST flows; group chat has no WebSocket.", [
        n("ui", "Messages.jsx", 60, 220, 280, 130, "actor", ["typing/presence UI"]),
        n("middleware", "JWTAuthMiddleware", 390, 220, 300, 130, "process", ["?token=<access>"]),
        n("consumer", "ChatConsumer", 740, 220, 300, 130, "websocket", ["direct group"]),
        n("rest", "Chat REST API", 390, 440, 300, 130, "api", ["history/send/read"]),
        n("channel", "Channel layer", 1080, 220, 280, 130, "websocket", ["Redis/in-memory"]),
        n("pg", "PostgreSQL", 1080, 440, 280, 130, "database", ["Message soft delete"]),
        n("notify", "Notification utility", 1420, 330, 260, 130, "process", ["message notification"]),
    ], [e("ui", "middleware", "WS"), e("middleware", "consumer"), e("consumer", "channel"), e("channel", "ui", "frames"), e("ui", "rest", "REST fallback"), e("rest", "pg"), e("consumer", "pg"), e("rest", "notify"), e("notify", "pg")]),
    ("Notification_Architecture", "Notification Architecture", "Central creation utility, preference checks, persistence, and WebSocket fan-out.", [
        n("domain", "Domain views", 60, 220, 260, 120, "api", ["like/comment/follow/..."]),
        n("util", "create_notification()", 380, 220, 320, 120, "process", ["self/block/preferences"]),
        n("pg", "PostgreSQL", 760, 220, 280, 120, "database", ["persist first"]),
        n("commit", "transaction.on_commit", 1100, 220, 300, 120, "process", ["publish event"]),
        n("channel", "Channel layer", 1440, 220, 280, 120, "websocket", ["notification.created"]),
        n("consumer", "NotificationConsumer", 1100, 440, 300, 120, "websocket", ["client frame"]),
        n("ui", "Notifications.jsx", 1440, 440, 280, 120, "actor", ["prepend + count"]),
    ], [e("domain", "util"), e("util", "pg"), e("util", "commit"), e("commit", "channel"), e("channel", "consumer"), e("consumer", "ui"), e("ui", "pg", "mark read")]),
    ("Frontend_Component_Hierarchy", "Frontend Component Hierarchy", "Verified React component tree from main.jsx through shared components.", [
        n("main", "main.jsx", 760, 140, 260, 90, "actor", ["React root"]),
        n("app", "App.jsx", 760, 270, 260, 90, "process", ["router + guards"]),
        n("shell", "AppShell", 420, 430, 260, 100, "entity", ["desktop/mobile shell"]),
        n("nav", "navbar", 140, 600, 240, 100, "entity", ["search/badges/theme"]),
        n("pages", "Pages", 760, 430, 260, 100, "entity", ["14 active routes"]),
        n("shared", "Shared components", 1100, 430, 300, 100, "entity", ["PostActions/Stories/dialogs"]),
        n("api", "Axios client", 760, 610, 260, 100, "api", ["Bearer + refresh"]),
        n("store", "Profile store", 1100, 610, 280, 100, "process", ["subscribe/load"]),
        n("hooks", "useFocusTrap", 420, 610, 260, 100, "process", ["modal keyboard focus"]),
        n("ws", "WS clients", 140, 790, 240, 100, "websocket", ["chat/notifications"]),
    ], [e("main", "app"), e("app", "shell"), e("app", "pages"), e("shell", "nav"), e("pages", "shared"), e("pages", "api"), e("shared", "hooks"), e("shared", "store"), e("pages", "ws")]),
    ("Deployment_Architecture", "Deployment Architecture", "Verified development topology with production items explicitly unverified.", [
        n("browser", "Browser", 60, 220, 240, 110, "actor"),
        n("vite", "Vite dev server", 340, 220, 260, 110, "process"),
        n("daphne", "Daphne ASGI", 660, 220, 280, 110, "api", ["config.asgi:application"]),
        n("pg", "PostgreSQL", 1000, 220, 260, 110, "database"),
        n("redis", "Redis optional", 1000, 420, 260, 110, "websocket", ["multi-process"]),
        n("media", "Media storage", 1320, 220, 260, 110, "store", ["prod " + UNVERIFIED]),
        n("proxy", "Proxy/TLS", 340, 440, 260, 110, "external", UNVERIFIED),
        n("monitor", "Monitoring/CI/CD", 660, 440, 280, 110, "external", UNVERIFIED),
    ], [e("browser", "vite", "dev"), e("browser", "daphne", "API/WS"), e("daphne", "pg"), e("daphne", "redis"), e("daphne", "media"), e("proxy", "daphne", UNVERIFIED, dashed=True), e("monitor", "daphne", UNVERIFIED, dashed=True)]),
]

for stem, title, subtitle, nodes, edges in ARCHITECTURES:
    folder = ARCH / stem
    draw_graph(folder / stem, title, subtitle, nodes, edges, "Actual technologies and modules only. Any deployment element not present in source retains the exact verification marker.", puml=False)

# ---------------------------------------------------------------------------
# DFD diagrams
# ---------------------------------------------------------------------------

DFD_LEVEL0 = [
    n("guest", "Guest", 60, 220, 220, 110, "external"),
    n("user", "Registered User", 60, 430, 220, 110, "external"),
    n("admin", "Admin", 60, 640, 220, 110, "external"),
    n("system", "Social Media App", 420, 300, 560, 520, "process", ["REST API", "WebSockets", "Django admin"]),
    n("pg", "D1 PostgreSQL", 1100, 280, 300, 110, "store"),
    n("media", "D2 Media storage", 1100, 460, 300, 110, "store"),
    n("channel", "D3 Channel layer", 1100, 640, 300, 110, "store"),
    n("email", "Email service", 1500, 460, 260, 110, "external", [UNVERIFIED]),
]
draw_graph(DFD / "Level_0" / "DFD_Level_0", "DFD Level 0 — Context Diagram", "External entities, the system boundary, and major data stores.", DFD_LEVEL0, [e("guest", "system", "register/login"), e("user", "system", "REST + WS"), e("admin", "system", "admin requests"), e("system", "pg", "queries"), e("system", "media", "uploads"), e("system", "channel", "events"), e("system", "email", "reset link")], "Email delivery and production media access are " + UNVERIFIED + ".", puml=False)

DFD_LEVEL1 = [
    n("user", "User", 40, 250, 180, 100, "external"), n("admin", "Admin", 40, 620, 180, 100, "external"),
    n("p1", "1.0 Identity & Profile", 300, 170, 320, 110, "process"), n("p2", "2.0 Content & Feed", 300, 330, 320, 110, "process"), n("p3", "3.0 Social Interaction", 300, 490, 320, 110, "process"), n("p4", "4.0 Messaging", 300, 650, 320, 110, "process"), n("p5", "5.0 Notifications", 300, 810, 320, 110, "process"), n("p6", "6.0 Administration", 300, 970, 320, 110, "process"),
    n("d1", "D1 User/Profile/Content", 760, 250, 320, 110, "store"), n("d2", "D2 Social tables", 760, 470, 320, 110, "store"), n("d3", "D3 Messages/Notifications", 760, 690, 320, 110, "store"), n("d4", "D4 Channel layer", 760, 910, 320, 110, "store"),
]
draw_graph(DFD / "Level_1" / "DFD_Level_1", "DFD Level 1", "Major processes and data stores derived from Django apps.", DFD_LEVEL1, [e("user", "p1"), e("user", "p2"), e("user", "p3"), e("user", "p4"), e("user", "p5"), e("admin", "p6"), e("p1", "d1"), e("p2", "d1"), e("p3", "d2"), e("p4", "d3"), e("p5", "d3"), e("p5", "d4"), e("p6", "d1"), e("p6", "d2")], "Process numbers are documentation IDs, not source code identifiers.", width=1920, height=1320, puml=False)

DFD_L2 = {
    "Level_2_Authentication": ("Authentication", [
        n("guest", "Guest", 50, 240, 180, 100, "external"), n("p", "2.1 Identity process", 340, 240, 300, 120, "process", ["validate/tokenize"]), n("d1", "D1 users_user", 760, 180, 280, 100, "store"), n("d2", "D2 users_profile", 760, 360, 280, 100, "store"), n("d3", "D3 JWT blacklist", 760, 540, 280, 100, "store"), n("email", "Email service", 1120, 360, 260, 100, "external", [UNVERIFIED]),
    ], [e("guest", "p", "credentials"), e("p", "d1"), e("p", "d2", "signal"), e("p", "d3", "rotate/logout"), e("p", "email", "reset")]),
    "Level_2_Post_Management": ("Post Management", [
        n("author", "Author", 50, 260, 180, 100, "external"), n("p", "2.2 Post process", 340, 260, 300, 120, "process", ["CRUD/visibility"]), n("d1", "D1 posts_post", 760, 160, 280, 100, "store"), n("d2", "D2 posts_* related", 760, 360, 280, 100, "store"), n("d3", "D3 Media storage", 760, 560, 280, 100, "store"),
    ], [e("author", "p", "post/write"), e("p", "d1"), e("p", "d2"), e("p", "d3", "upload")]),
    "Level_2_Social_Interaction": ("Social Interaction", [
        n("user", "User", 50, 260, 180, 100, "external"), n("p", "2.3 Social process", 340, 260, 300, 120, "process", ["like/comment/follow/block"]), n("d1", "D1 social tables", 760, 180, 280, 100, "store"), n("d2", "D2 posts_post", 760, 380, 280, 100, "store"), n("d3", "D3 Notifications", 1120, 280, 280, 100, "store"),
    ], [e("user", "p", "actions"), e("p", "d1"), e("p", "d2"), e("p", "d3", "notification")]),
    "Level_2_Chat": ("Chat", [
        n("sender", "Sender", 50, 250, 180, 100, "external"), n("receiver", "Receiver", 50, 470, 180, 100, "external"), n("p", "2.4 Chat process", 340, 340, 300, 130, "process", ["REST + WS"]), n("d1", "D1 chat_message", 760, 200, 280, 100, "store"), n("d2", "D2 Channel layer", 760, 420, 280, 100, "store"), n("d3", "D3 Notifications", 1120, 320, 280, 100, "store"),
    ], [e("sender", "p"), e("p", "receiver", "frames"), e("p", "d1"), e("p", "d2"), e("p", "d3")]),
    "Level_2_Notification": ("Notification", [
        n("domain", "Domain view", 50, 280, 190, 100, "external"), n("p", "2.5 Notification process", 340, 280, 320, 130, "process", ["preferences/block"]), n("d1", "D1 notifications_*", 760, 180, 280, 100, "store"), n("d2", "D2 Channel layer", 760, 400, 280, 100, "store"), n("user", "Recipient SPA", 1120, 280, 280, 100, "external"),
    ], [e("domain", "p"), e("p", "d1"), e("p", "d2", "on_commit"), e("d2", "user", "client frame")]),
}
for stem, (name, nodes, edges) in DFD_L2.items():
    draw_graph(DFD / "Level_2" / stem, f"DFD Level 2 — {name}", "External entities, process, data stores, and data flows.", nodes, edges, "Only source-verified stores and flows are shown.", puml=False)

# ---------------------------------------------------------------------------
# User requirements and flow diagrams
# ---------------------------------------------------------------------------

draw_graph(REQ / "User_Requirement_Diagram", "User Requirement Diagram", "UR IDs from User_Requirements.md grouped by source-verified domain.", [
    n("guest", "Guest", 40, 180, 180, 90, "actor"), n("user", "Registered User", 40, 420, 180, 90, "actor"), n("admin", "Admin", 40, 660, 180, 90, "actor"),
    n("identity", "UR-001—007 Identity", 300, 150, 320, 110, "entity", ["register/login/reset"]), n("profile", "UR-008—010 Profile", 300, 300, 320, 110, "entity"), n("content", "UR-011—016 Content", 300, 450, 320, 110, "entity"), n("social", "UR-019—021 Social", 300, 600, 320, 110, "entity"), n("rt", "UR-022—028 Real time", 700, 300, 320, 110, "entity", ["notifications/chat/polls"]), n("adminreq", "UR-030—032 Admin", 700, 600, 320, 110, "entity"),
], [e("guest", "identity"), e("user", "profile"), e("user", "content"), e("user", "social"), e("user", "rt"), e("admin", "adminreq")], "Proposed screens do not change requirement status; backend-only items remain backend only.", puml=False)

draw_graph(REQ / "Feature_Hierarchy_Diagram", "Feature Hierarchy Diagram", "High-level product capability groups from FEATURE_IMPLEMENTATION_MATRIX.md.", [
    n("root", "Social Media App", 760, 150, 340, 110, "entity"),
    n("auth", "Identity & access", 60, 360, 280, 100, "entity"), n("profile", "Profiles & discovery", 380, 360, 280, 100, "entity"), n("content", "Posts & feed", 700, 360, 280, 100, "entity"), n("social", "Social graph", 1020, 360, 280, 100, "entity"), n("stories", "Stories", 1340, 360, 280, 100, "entity"),
    n("notify", "Notifications", 220, 600, 280, 100, "entity"), n("chat", "Messaging", 580, 600, 280, 100, "entity"), n("admin", "Admin & platform", 940, 600, 280, 100, "entity"), n("pwa", "PWA / theme", 1300, 600, 280, 100, "entity"),
], [e("root", "auth"), e("root", "profile"), e("root", "content"), e("root", "social"), e("root", "stories"), e("root", "notify"), e("root", "chat"), e("root", "admin"), e("root", "pwa")], "Grouping is documentation structure, not a source package hierarchy.", puml=False)

draw_graph(REQ / "Stakeholder_Diagram", "Stakeholder Diagram", "Actors from DIAGRAM_SOURCE_DATA.md and their verified interests.", [
    n("guest", "Guest", 60, 190, 240, 100, "actor"), n("user", "Registered User", 60, 400, 240, 100, "actor"), n("admin", "Admin", 60, 610, 240, 100, "actor"), n("external", "External System", 60, 820, 240, 100, "external"),
    n("system", "System outcome", 500, 400, 300, 130, "process", ["source-verified value"]),
    n("access", "Account access", 920, 170, 280, 100, "entity"), n("engage", "Content engagement", 920, 360, 280, 100, "entity"), n("moderate", "Platform oversight", 920, 550, 280, 100, "entity"), n("infra", "Persistence/delivery", 920, 740, 280, 100, "entity"),
], [e("guest", "access"), e("user", "engage"), e("admin", "moderate"), e("external", "infra"), e("access", "system"), e("engage", "system"), e("moderate", "system"), e("infra", "system")], "External System includes PostgreSQL, optional Redis, media storage, and email; delivery success is " + UNVERIFIED + ".", puml=False)

draw_graph(REQ / "User_Flow" / "User_Flow_Diagram", "User Flow Diagram", "End-to-end journeys proven by source routes and components.", [
    n("start", "Start", 60, 400, 160, 80, "process"), n("login", "Login / Register", 280, 400, 240, 90, "entity"), n("home", "Home feed", 580, 400, 220, 90, "entity"), n("post", "Create/like/comment", 860, 250, 280, 90, "entity"), n("search", "Search/follow", 860, 430, 280, 90, "entity"), n("chat", "Direct chat", 860, 610, 280, 90, "entity"), n("notify", "Notifications", 1180, 430, 260, 90, "entity"), n("profile", "Profile/settings", 1480, 430, 260, 90, "entity"), n("logout", "Logout", 1480, 650, 260, 90, "process"),
], [e("start", "login"), e("login", "home"), e("home", "post"), e("home", "search"), e("home", "chat"), e("post", "notify"), e("search", "notify"), e("chat", "notify"), e("home", "profile"), e("profile", "logout")], "No /explore or /settings route exists; related mockups are proposals.", puml=False)

draw_graph(REQ / "User_Journey" / "User_Journey_Map", "User Journey Map", "Source-verified stages, actions, and system touchpoints.", [
    n("discover", "1. Discover", 60, 220, 240, 100, "actor", ["register or login"]), n("settle", "2. Settle", 360, 220, 240, 100, "entity", ["profile + privacy"]), n("consume", "3. Consume", 660, 220, 240, 100, "entity", ["feed + stories"]), n("contribute", "4. Contribute", 960, 220, 260, 100, "entity", ["posts + reactions"]), n("connect", "5. Connect", 1280, 220, 240, 100, "entity", ["follow/friend/chat"]), n("manage", "6. Manage", 60, 520, 240, 100, "entity", ["notifications/preferences"]), n("admin", "7. Oversee", 500, 520, 260, 100, "entity", ["Django admin"]), n("limits", "Known friction", 900, 520, 300, 100, "note", ["pagination/partial UI"]),
], [e("discover", "settle"), e("settle", "consume"), e("consume", "contribute"), e("contribute", "connect"), e("connect", "manage"), e("manage", "admin"), e("admin", "limits", dashed=True)], "Friction points are source-derived gaps, not usability test findings.", puml=False)

draw_graph(REQ / "Sitemap" / "Sitemap", "Sitemap", "Reachable SPA routes, custom admin, and explicitly proposed screens.", [
    n("root", "/ home", 720, 150, 220, 90, "entity"),
    n("login", "/login", 60, 300, 180, 80, "entity"), n("register", "/register", 280, 300, 180, 80, "entity"), n("search", "/search", 500, 300, 180, 80, "entity"), n("edit", "/edit-profile", 720, 300, 200, 80, "entity"), n("messages", "/messages/:userId", 960, 300, 220, 80, "entity"), n("notif", "/notifications", 1220, 300, 200, 80, "entity"),
    n("friends", "/friend-requests", 60, 460, 220, 80, "entity"), n("conn", "/connections/:section", 320, 460, 240, 80, "entity"), n("book", "/bookmarks", 600, 460, 200, 80, "entity"), n("post", "/posts/:postId", 840, 460, 200, 80, "entity"), n("profile", "/users/:userId", 1080, 460, 220, 80, "entity"), n("admin", "/admin/ (Django)", 1360, 460, 240, 80, "entity"),
    n("proposed", "Proposed only: /explore, /settings, /forgot-password, /groups, /polls, moderation", 500, 640, 820, 110, "note", ["not active routes"]),
], [e("root", "search"), e("root", "edit"), e("root", "messages"), e("root", "notif"), e("root", "book"), e("root", "post"), e("root", "profile"), e("login", "root"), e("register", "login"), e("root", "friends"), e("root", "conn"), e("root", "admin"), e("root", "proposed", "proposed", dashed=True)], "Solid nodes are source-verified routes; the dashed node is a proposal label, not a route.", puml=False)

draw_graph(REQ / "Navigation_Flow_Diagram", "Navigation Flow Diagram", "Shell navigation and cross-screen transitions.", [
    n("shell", "AppShell / navbar", 760, 160, 320, 100, "process", ["three-zone desktop", "drawer + bottom nav"]),
    n("home", "Home", 60, 340, 200, 90, "entity"), n("search", "Search", 300, 340, 200, 90, "entity"), n("friends", "Friends/Connections", 540, 340, 220, 90, "entity"), n("messages", "Messages", 800, 340, 200, 90, "entity"), n("notif", "Notifications", 1040, 340, 200, 90, "entity"), n("profile", "My profile", 1280, 340, 200, 90, "entity"), n("detail", "Post detail", 300, 560, 220, 90, "entity"), n("edit", "Edit profile", 1280, 560, 220, 90, "entity"), n("dialog", "Notification settings dialog", 760, 560, 300, 90, "entity"),
], [e("shell", "home"), e("shell", "search"), e("shell", "friends"), e("shell", "messages"), e("shell", "notif"), e("shell", "profile"), e("home", "detail"), e("profile", "edit"), e("notif", "dialog")], "Navigation labels match AppShell.jsx and navbar.jsx; Explore points to /search.", puml=False)

# ---------------------------------------------------------------------------
# Testing diagrams
# ---------------------------------------------------------------------------

draw_graph(TEST / "Testing_Workflow", "Testing Workflow", "Verification order derived from source guidance.", [
    n("analysis", "Source analysis", 60, 240, 240, 100, "process"), n("check", "manage.py check", 360, 180, 260, 90, "entity"), n("mig", "makemigrations --check", 360, 340, 300, 90, "entity"), n("tests", "manage.py test --keepdb", 720, 180, 300, 90, "entity"), n("lint", "npm.cmd run lint", 1080, 180, 280, 90, "entity"), n("build", "npm.cmd run build", 1080, 340, 280, 90, "entity"), n("qa", "Visual QA", 720, 520, 300, 100, "process", ["file/dimension checks"]), n("report", "Record results", 1080, 520, 280, 100, "store", [UNVERIFIED]),
], [e("analysis", "check"), e("analysis", "mig"), e("check", "tests"), e("lint", "build"), e("tests", "qa"), e("build", "qa"), e("qa", "report")], "Current command results are not asserted. Only makemigrations --check was executed during the audit and returned No changes detected.", puml=False)

draw_graph(TEST / "Functional_Test_Case_Diagram", "Functional Test Case Diagram", "UR-to-TC mapping summarized from Test_Plan.md.", [
    n("ur", "UR-001—035", 60, 280, 240, 110, "entity"), n("tc1", "TC-001—010 Auth/profile", 380, 170, 320, 100, "process"), n("tc2", "TC-011—019 Content/social", 380, 330, 320, 100, "process"), n("tc3", "TC-020—029 Realtime/backend-only", 380, 490, 320, 100, "process"), n("tc4", "TC-030—035 Admin/session/PWA", 380, 650, 320, 100, "process"), n("src", "Source evidence", 820, 330, 280, 110, "store", ["models/views/routes"]), n("status", "Status vocabulary", 1160, 330, 300, 110, "note", ["Implemented/Partial/etc."]),
], [e("ur", "tc1"), e("ur", "tc2"), e("ur", "tc3"), e("ur", "tc4"), e("tc1", "src"), e("tc2", "src"), e("tc3", "src"), e("tc4", "src"), e("src", "status")], "TC IDs are proposals for documentation, not claims that test methods exist.", puml=False)

draw_graph(TEST / "API_Testing_Flow", "API Testing Flow", "REST verification path with authentication and visibility checks.", [
    n("client", "API test client", 60, 260, 240, 100, "actor"), n("auth", "Obtain JWT", 340, 260, 240, 100, "process"), n("request", "Send REST request", 660, 260, 260, 100, "process"), n("perm", "Permission + access.py", 980, 180, 300, 100, "process"), n("serializer", "Serializer validation", 980, 360, 300, 100, "process"), n("db", "PostgreSQL", 1320, 270, 240, 100, "database"), n("assert", "Assert response/state", 1320, 500, 240, 100, "store"),
], [e("client", "auth"), e("auth", "request", "Bearer"), e("request", "perm"), e("request", "serializer"), e("perm", "db"), e("serializer", "db"), e("db", "assert")], "No ViewSets or @action decorators exist; test requests target APIView/generics endpoints.", puml=False)

draw_graph(TEST / "Authentication_Testing_Flow", "Authentication Testing Flow", "JWT lifecycle verification from login through refresh and blacklist.", [
    n("login", "POST /api/users/login/", 60, 220, 280, 100, "process"), n("tokens", "access + refresh", 380, 220, 260, 100, "store"), n("protected", "Protected request", 380, 420, 260, 100, "process"), n("expired", "401 response", 700, 420, 240, 100, "decision"), n("refresh", "POST token/refresh/", 1000, 300, 280, 100, "process"), n("replay", "Replay original request", 1320, 300, 280, 100, "process"), n("clear", "Clear session on failure", 1000, 560, 280, 100, "process"), n("blacklist", "Blacklist tables", 1320, 560, 280, 100, "database"),
], [e("login", "tokens"), e("tokens", "protected", "Bearer"), e("protected", "expired"), e("expired", "refresh", "yes"), e("refresh", "replay"), e("expired", "clear", "no"), e("refresh", "blacklist", "rotation"), e("clear", "blacklist", "logout")], "Route guard checks token presence only; validity is enforced by API authentication and Axios refresh.", puml=False)

print("generated ER, UML, architecture, DFD, requirement, and testing diagrams")
