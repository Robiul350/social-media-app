"""Generate premium UI mockups and grayscale wireframes as real PNG/SVG images."""

from __future__ import annotations

from pathlib import Path

from vizlib import (
    C,
    BASE_CSS,
    Canvas,
    app_shell,
    auth_frame,
    avatar,
    badge,
    button,
    card,
    input_field,
    wireframe_shell,
    wf_box,
    write_html_source,
    write_text,
)

ROOT = Path(__file__).resolve().parents[1]
MOCK_DESKTOP = ROOT / "02_UI_MOCKUPS" / "Desktop"
MOCK_MOBILE = ROOT / "02_UI_MOCKUPS" / "Mobile"
MOCK_SOURCE = ROOT / "02_UI_MOCKUPS" / "Source_HTML_CSS"
WF_DESKTOP = ROOT / "03_WIREFRAMES" / "Desktop"
WF_MOBILE = ROOT / "03_WIREFRAMES" / "Mobile"
WF_SOURCE = ROOT / "03_WIREFRAMES" / "Source_HTML_CSS"

DESKTOP = (1920, 1080)
MOBILE = (720, 1280)
UNVERIFIED = "[NOT VERIFIED - USER CONFIRMATION REQUIRED]"

SCREENS = [
    ("UI-SCR-001", "Login", "Implemented", "Username/password sign-in; JWT stored in localStorage."),
    ("UI-SCR-002", "Registration", "Implemented", "Account creation with local password validation."),
    ("UI-SCR-003", "Forgot Password", "Backend only / Proposed", "REST reset endpoint exists; no SPA route was found."),
    ("UI-SCR-004", "Home / News Feed", "Implemented", "Stories, composer, audience control, and opt-in paginated feed."),
    ("UI-SCR-005", "User Profile", "Implemented", "Cover, avatar, stats, relationship actions, and posts."),
    ("UI-SCR-006", "Edit Profile", "Implemented", "Identity, bio, privacy, permissions, and media upload."),
    ("UI-SCR-007", "Create Post", "Partial / Proposed dedicated screen", "Active composer is embedded on home; no dedicated route."),
    ("UI-SCR-008", "Post Details", "Implemented", "Single post with comments, replies, and standard actions."),
    ("UI-SCR-009", "Comments and Replies", "Implemented", "Lazy comment panel with threaded replies and owner controls."),
    ("UI-SCR-010", "Stories Section", "Implemented", "Grouped 24-hour story strip with creation dialog."),
    ("UI-SCR-011", "Story Viewer", "Implemented", "Auto-advance viewer with pause, keyboard navigation, and view tracking."),
    ("UI-SCR-012", "Story Reaction", "Backend only / Proposed", "Seven backend reaction types; no reaction control in SPA."),
    ("UI-SCR-013", "Explore Page", "Not Found / Proposed", "No /explore route; people discovery lives at /search."),
    ("UI-SCR-014", "Search Results", "Implemented", "Debounced people discovery with follow/friend shortcuts."),
    ("UI-SCR-015", "Followers Page", "Implemented", "Connections followers tab with pagination metadata ignored."),
    ("UI-SCR-016", "Following Page", "Implemented", "Connections following tab with block-aware list."),
    ("UI-SCR-017", "Notification Page", "Implemented", "Notification feed, unread styling, read actions, and live status."),
    ("UI-SCR-018", "Messenger Page", "Implemented", "Conversation list with search, unread badges, and presence."),
    ("UI-SCR-019", "Individual Chat Page", "Implemented", "Direct chat with WebSocket send, typing, receipts, and attachments."),
    ("UI-SCR-020", "Settings Page", "Partial / Proposed", "Privacy controls are in Edit profile; preferences are a dialog."),
    ("UI-SCR-021", "User Dashboard", "Not Found / Proposed", "No dedicated SPA dashboard route was found."),
    ("UI-SCR-022", "Admin Dashboard", "Implemented (Django admin)", "Custom /admin/ dashboard with 12 real-data KPI cards."),
    ("UI-SCR-023", "Report User", "Not Found / Proposed", "Post reports exist; user report workflow was not found."),
    ("UI-SCR-024", "Block User", "Partial / Implemented action", "Block/unblock action on public profile; no block-list screen."),
]

WIREFRAMES = [
    ("WF-001", "Login", "UI-SCR-001"),
    ("WF-002", "Registration", "UI-SCR-002"),
    ("WF-003", "Home Feed", "UI-SCR-004"),
    ("WF-004", "Profile", "UI-SCR-005"),
    ("WF-005", "Create Post", "UI-SCR-007"),
    ("WF-006", "Story", "UI-SCR-010"),
    ("WF-007", "Explore", "UI-SCR-013"),
    ("WF-008", "Chat", "UI-SCR-019"),
    ("WF-009", "Notification", "UI-SCR-017"),
    ("WF-010", "Settings", "UI-SCR-020"),
    ("WF-011", "Admin Dashboard", "UI-SCR-022"),
]


def status_tone(status: str) -> str:
    if status.startswith("Implemented"):
        return "success"
    if "Backend only" in status or "Proposed" in status or "Not Found" in status:
        return "warn"
    return "primary"


def screen_label(c: Canvas, x: int, y: int, screen: tuple[str, str, str, str], max_width: int) -> None:
    sid, name, status, desc = screen
    label = f"{sid}  |  {name}  |  {status}"
    font_w = 12 * (len(label) ** 0.62) + 20
    badge(c, x, y, label[: min(len(label), 58)], status_tone(status))


def feed_card(c: Canvas, x: int, y: int, w: int, h: int, author: str, text: str, likes: str, comments: str, badge_text: str = "Public") -> None:
    card(c, x, y, w, h)
    avatar(c, x + 36, y + 38, 20, author[0])
    c.text(x + 66, y + 20, author, size=15, bold=True, color=C["ink"])
    c.text(x + 66, y + 42, "2 hours ago  ·  " + badge_text, size=11, color=C["muted"])
    badge(c, x + w - 100, y + 20, badge_text)
    c.text(x + 24, y + 78, text, size=14, color=C["gray_700"], max_width=w - 48)
    media_y = y + 128
    c.rect(x + 24, media_y, w - 48, min(120, h - 190), fill=C["gray_100"], radius=12)
    c.circle(x + w // 2, media_y + min(120, h - 190) // 2, 22, fill=C["primary_soft"])
    c.text(x + w // 2, media_y + min(120, h - 190) // 2, "MEDIA", size=10, bold=True, color=C["primary"], anchor="mm")
    actions_y = y + h - 44
    for i, txt in enumerate([f"♥ {likes}", f"♬ {comments}", "↗ Share", "▢ Save"]):
        c.text(x + 28 + i * max(90, (w - 60) // 4), actions_y, txt, size=12, color=C["gray_600"])


def story_strip(c: Canvas, x: int, y: int, w: int, own: bool = True) -> None:
    names = ["You", "Maya", "Noah", "Priya", "Liam", "Sofia", "Ethan"]
    c.text(x, y, "Stories", size=17, bold=True, color=C["ink"])
    for i, name in enumerate(names):
        sx = x + i * min(108, w // 7)
        color = C["primary"] if own and i == 0 else C["accent"]
        c.circle(sx + 30, y + 58, 27, fill=color)
        c.text(sx + 30, y + 58, name[0], size=14, bold=True, color=C["white"], anchor="mm")
        c.text(sx + 30, y + 96, name, size=11, color=C["gray_600"], anchor="mm")


def render_auth(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    sid, name, status, desc = screen
    if name == "Login":
        heading, sub = "Welcome back", "Sign in to continue to your circle."
        fields = [("Username", "alexmorgan"), ("Password", "••••••••••")]
        action, foot = "Sign in", "New here?  Create an account"
    elif name == "Registration":
        heading, sub = "Create your account", "Join SocialConnect to share and stay connected."
        fields = [("Username", "alexmorgan"), ("Email", "alex@example.com"), ("Password", "••••••••••"), ("Confirm password", "••••••••••")]
        action, foot = "Create account", "Already registered?  Sign in"
    else:
        heading, sub = "Reset your password", "Enter your email and we will send a reset link."
        fields = [("Email", "alex@example.com")]
        action, foot = "Send reset link", "Remembered it?  Back to sign in"
    f = auth_frame(c, width, height, heading, sub, device)
    screen_label(c, f["x"], f["y"] - 2, screen, f["w"])
    fy = f["y"] + 34
    for label, value in fields:
        input_field(c, f["x"], fy, f["w"], label, value, h=48 if device == "mobile" else 52)
        fy += 78 if device == "mobile" else 86
    button(c, f["x"], fy + 4, f["w"], 52, action)
    c.text(f["x"] + f["w"] / 2, fy + 82, foot, size=13, color=C["primary"], anchor="mm")
    if name == "Forgot Password":
        c.rect(f["x"], fy + 110, f["w"], 62, fill=C["warn_soft"], outline=C["warn"], radius=10)
        c.text(f["x"] + 12, fy + 124, "PROPOSED: REST endpoint exists; no SPA route found.", size=11, bold=True, color=C["warn"], max_width=f["w"] - 24)
        c.text(f["x"] + 12, fy + 146, f"Email delivery is {UNVERIFIED}.", size=10, color=C["warn"], max_width=f["w"] - 24)
    if device == "desktop":
        c.text(f["x"], fy + 130, "JWT session  ·  rotating refresh tokens  ·  username login", size=12, color=C["muted"])


def render_home(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    sid, name, status, desc = screen
    content = app_shell(c, width, height, "Home", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    story_strip(c, content["x"], y, content["w"])
    y += 118
    card(c, content["x"], y, content["w"], 112)
    avatar(c, content["x"] + 34, y + 38, 20, "A")
    c.rect(content["x"] + 66, y + 18, content["w"] - 92, 44, fill=C["gray_50"], radius=22, outline=C["line"])
    c.text(content["x"] + 82, y + 34, "What's happening, Alex?", size=13, color=C["muted"])
    for i, label in enumerate(["Photo", "Video", "Audience: Public"]):
        bx = content["x"] + 66 + i * min(150, (content["w"] - 100) // 3)
        c.text(bx, y + 78, label, size=11, color=C["primary"] if i == 2 else C["gray_600"])
    button(c, content["x"] + content["w"] - 116, y + 70, 94, 34, "Post")
    y += 132
    feed_card(c, content["x"], y, content["w"], 260, "Maya Chen", "Weekend hike with the crew. The view was worth every step.", "248", "31", "Friends")
    y += 276
    if y + 220 < content["y"] + content["h"]:
        feed_card(c, content["x"], y, content["w"], 220, "Noah Reed", "Shipping a new side project tonight. Feedback welcome.", "96", "14", "Public")


def render_profile(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    sid, name, status, desc = screen
    title = "Profile" if name != "Block User" else "Block User"
    content = app_shell(c, width, height, title, device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    card(c, content["x"], y, content["w"], 190)
    c.rect(content["x"] + 12, y + 12, content["w"] - 24, 86, fill=C["navy"], radius=12)
    c.text(content["x"] + 28, y + 36, "Cover photo", size=13, color="#CBD5E1")
    avatar(c, content["x"] + 64, y + 104, 46, "A", C["accent"])
    c.text(content["x"] + 124, y + 116, "Alex Morgan", size=19, bold=True, color=C["ink"])
    c.text(content["x"] + 124, y + 142, "@alexmorgan  ·  Jakarta, Indonesia", size=12, color=C["muted"])
    if device == "desktop":
        button(c, content["x"] + content["w"] - 300, y + 124, 84, 34, "Follow", primary=True)
        button(c, content["x"] + content["w"] - 206, y + 124, 84, 34, "Message", primary=False)
        button(c, content["x"] + content["w"] - 112, y + 124, 92, 34, "More", primary=False)
    stats = [("128", "Posts"), ("2.4k", "Followers"), ("486", "Following"), ("73", "Friends")]
    sy = y + 204
    card(c, content["x"], sy, content["w"], 76)
    for i, (num, label) in enumerate(stats):
        sx = content["x"] + (i + 0.5) * content["w"] / 4
        c.text(sx, sy + 16, num, size=18, bold=True, color=C["primary"], anchor="mm")
        c.text(sx, sy + 46, label, size=11, color=C["muted"], anchor="mm")
    py = sy + 94
    c.text(content["x"], py, "Posts", size=16, bold=True, color=C["ink"])
    feed_card(c, content["x"], py + 34, content["w"], min(230, content["y"] + content["h"] - py - 44), "Alex Morgan", "Designing a calmer social experience, one component at a time.", "412", "58", "Public")
    if name == "Block User":
        c.rect(content["x"] + content["w"] / 2 - 170, content["y"] + 150, 340, 190, fill=C["white"], radius=16, outline=C["danger"], shadow=True)
        c.text(content["x"] + content["w"] / 2, content["y"] + 176, "Block this user?", size=17, bold=True, color=C["ink"], anchor="mm")
        c.text(content["x"] + content["w"] / 2, content["y"] + 214, "Feed, chat, and notifications change immediately.", size=12, color=C["muted"], anchor="mm", max_width=300)
        button(c, content["x"] + content["w"] / 2 - 146, content["y"] + 270, 136, 40, "Cancel", primary=False)
        button(c, content["x"] + content["w"] / 2 + 10, content["y"] + 270, 136, 40, "Block", danger=True)


def render_edit_profile(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Edit Profile", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    card(c, content["x"], y, content["w"], 112)
    avatar(c, content["x"] + 56, y + 56, 34, "A")
    button(c, content["x"] + 108, y + 38, 138, 34, "Change photo")
    button(c, content["x"] + 108, y + 78, 138, 30, "Remove", primary=False)
    c.text(content["x"] + content["w"] - 210, y + 48, "Cover photo", size=13, bold=True, color=C["gray_700"])
    button(c, content["x"] + content["w"] - 210, y + 72, 170, 32, "Upload cover", primary=False)
    fy = y + 132
    fields = [
        ("First name", "Alex"), ("Last name", "Morgan"), ("Bio", "Product designer and part-time trail runner."),
        ("Location", "Jakarta, Indonesia"), ("Website", "https://alexmorgan.dev"), ("Privacy", "Followers can see my posts"),
    ]
    cols = 2 if device == "desktop" else 1
    gap = 18
    fw = (content["w"] - gap) // cols
    for i, (label, value) in enumerate(fields):
        col, row = i % cols, i // cols
        input_field(c, content["x"] + col * (fw + gap), fy + row * 82, fw, label, value, h=46)
    py = fy + (3 if cols == 2 else 6) * 82 + 8
    c.text(content["x"], py, "Permissions", size=16, bold=True, color=C["ink"])
    for i, label in enumerate(["Who can comment", "Who can message"]):
        input_field(c, content["x"] + i * (fw + gap) if cols == 2 else content["x"], py + 30 + i * (82 if cols == 1 else 0), fw, label, "Followers", h=44)
    button(c, content["x"] + content["w"] - 140, content["y"] + content["h"] - 52, 128, 40, "Save changes")


def render_create_post(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Create Post", device=device, proposed=True)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 12
    card(c, content["x"], y, content["w"], min(430, content["h"] - 20))
    avatar(c, content["x"] + 36, y + 40, 20, "A")
    c.text(content["x"] + 66, y + 24, "Alex Morgan", size=15, bold=True, color=C["ink"])
    c.rect(content["x"] + 24, y + 78, content["w"] - 48, 132, fill=C["gray_50"], radius=12, outline=C["line"])
    c.text(content["x"] + 40, y + 98, "Share something with your circle…", size=14, color=C["muted"])
    c.rect(content["x"] + 24, y + 224, content["w"] - 48, 92, fill=C["primary_soft"], radius=12)
    c.text(content["x"] + 40, y + 244, "Selected media: sunset.jpg", size=13, bold=True, color=C["primary"])
    c.text(content["x"] + 40, y + 270, "Image preview  ·  2.1 MB  ·  max 10 MB", size=11, color=C["muted"])
    for i, label in enumerate(["Photo", "Video", "Audience", "Draft", "Schedule"]):
        bx = content["x"] + 24 + i * min(118, (content["w"] - 48) // 5)
        button(c, bx, y + 332, min(104, (content["w"] - 60) // 5), 34, label, primary=(i == 2))
    button(c, content["x"] + content["w"] - 132, y + 382, 108, 38, "Publish")
    c.text(content["x"] + 24, y + 390, "Active composer is embedded on Home; dedicated screen is proposed.", size=11, color=C["warn"], max_width=content["w"] - 180)


def render_post_detail(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Post Details", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    feed_card(c, content["x"], y, content["w"], 280, "Maya Chen", "A quiet morning at the trailhead before the climb. #weekend #hiking", "312", "42", "Friends")
    cy = y + 296
    card(c, content["x"], cy, content["w"], max(140, content["y"] + content["h"] - cy - 10))
    c.text(content["x"] + 20, cy + 16, "Comments", size=16, bold=True, color=C["ink"])
    comments = [("Noah Reed", "This looks incredible!"), ("Priya Shah", "Adding this to my list."), ("Alex Morgan", "Trail conditions were perfect.")]
    for i, (name, text) in enumerate(comments):
        yy = cy + 50 + i * 54
        avatar(c, content["x"] + 34, yy + 12, 14, name[0], C["accent"] if i % 2 else C["primary"])
        c.text(content["x"] + 58, yy, name, size=12, bold=True, color=C["ink"])
        c.text(content["x"] + 58, yy + 20, text, size=12, color=C["gray_600"], max_width=content["w"] - 90)


def render_comments(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Comments & Replies", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    card(c, content["x"], y, content["w"], max(120, content["h"] - 50))
    c.text(content["x"] + 20, y + 16, "Threaded conversation", size=16, bold=True, color=C["ink"])
    rows = [
        ("Maya Chen", "Here is the route I mentioned yesterday.", 0),
        ("Noah Reed", "Saving this for Saturday.", 1),
        ("Alex Morgan", "I can share the GPX file tonight.", 2),
        ("Priya Shah", "Perfect, thank you!", 2),
    ]
    for i, (name, text, depth) in enumerate(rows):
        yy = y + 54 + i * 76
        xx = content["x"] + 20 + depth * 24
        c.rect(xx, yy, content["w"] - 40 - depth * 24, 62, fill=C["gray_50"], radius=12, outline=C["line"])
        avatar(c, xx + 24, yy + 31, 14, name[0], C["accent"] if depth else C["primary"])
        c.text(xx + 48, yy + 12, name, size=12, bold=True, color=C["ink"])
        c.text(xx + 48, yy + 32, text, size=12, color=C["gray_600"], max_width=content["w"] - 110 - depth * 24)
        if depth:
            c.text(xx + 14, yy + 18, "↳", size=13, color=C["muted"])
    c.rect(content["x"] + 20, content["y"] + content["h"] - 62, content["w"] - 40, 44, fill=C["white"], radius=22, outline=C["line"])
    c.text(content["x"] + 36, content["y"] + content["h"] - 47, "Write a reply…", size=12, color=C["muted"])


def render_stories(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Stories", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 52
    c.text(content["x"], y, "Your story", size=17, bold=True, color=C["ink"])
    c.rect(content["x"], y + 34, content["w"], 148, fill=C["white"], radius=16, outline=C["line"], shadow=True)
    avatar(c, content["x"] + 70, y + 108, 34, "+", C["primary"])
    c.text(content["x"] + 120, y + 88, "Add to your story", size=16, bold=True, color=C["ink"])
    c.text(content["x"] + 120, y + 116, "Photo or video up to 25 MB  ·  expires in 24 hours", size=12, color=C["muted"])
    button(c, content["x"] + content["w"] - 130, y + 92, 108, 36, "Create")
    c.text(content["x"], y + 220, "Recent stories", size=17, bold=True, color=C["ink"])
    names = ["Maya", "Noah", "Priya", "Liam", "Sofia"]
    for i, name in enumerate(names):
        x = content["x"] + i * min(140, content["w"] // 5)
        c.rect(x, y + 258, min(122, content["w"] // 5 - 12), 170, fill=C["white"], radius=14, outline=C["line"], shadow=True)
        c.circle(x + min(61, (content["w"] // 5 - 12) // 2), y + 322, 36, fill=[C["accent"], C["cyan"], C["success"], C["warn"], C["primary"]][i])
        c.text(x + min(61, (content["w"] // 5 - 12) // 2), y + 322, name[0], size=18, bold=True, color=C["white"], anchor="mm")
        c.text(x + 10, y + 388, name, size=12, bold=True, color=C["ink"])


def render_story_viewer(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    c.rect(0, 0, width, height, fill=C["navy"])
    c.rect(0, 0, width, 8, fill=C["gray_700"])
    for i in range(5):
        c.rect(24 + i * (width - 48) // 5, 20, (width - 88) // 5, 4, fill=C["white"] if i < 2 else C["gray_600"], radius=2)
    avatar(c, 62, 68, 24, "M", C["accent"])
    c.text(98, 52, "Maya Chen", size=15, bold=True, color=C["white"])
    c.text(98, 74, "12 minutes ago  ·  Public", size=11, color="#CBD5E1")
    c.text(width - 60, 56, "✕", size=20, color=C["white"], anchor="mm")
    c.rect(width // 2 - 260, height // 2 - 220, 520, 380, fill=C["navy_2"], radius=24, outline=C["gray_600"])
    c.text(width // 2, height // 2 - 80, "STORY MEDIA", size=17, bold=True, color="#CBD5E1", anchor="mm")
    c.text(width // 2, height // 2 - 30, "Cliffside trail, 07:42", size=14, color=C["white"], anchor="mm")
    c.rect(width // 2 - 240, height - 150, 480, 52, fill=C["white"], radius=26)
    c.text(width // 2, height - 124, "Send message", size=13, bold=True, color=C["ink"], anchor="mm")
    c.text(width // 2, height - 58, "5-second auto-advance  ·  pause/resume  ·  keyboard navigation", size=12, color="#CBD5E1", anchor="mm")
    screen_label(c, 24, height - 38, screen, width - 48)


def render_story_reaction(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    c.rect(0, 0, width, height, fill=C["navy"])
    c.rect(0, 0, width, 6, fill=C["accent"])
    c.text(44, 34, f"{screen[0]}  |  {screen[1]}  |  {screen[2]}", size=14, bold=True, color="#CBD5E1")
    c.rect(width // 2 - 300, height // 2 - 260, 600, 480, fill=C["white"], radius=24, shadow=True)
    c.text(width // 2, height // 2 - 210, "React to Maya's story", size=22, bold=True, color=C["ink"], anchor="mm")
    c.text(width // 2, height // 2 - 170, "PROPOSED: backend supports seven reaction types; no SPA control found.", size=12, bold=True, color=C["warn"], anchor="mm", max_width=540)
    reactions = ["like", "love", "care", "haha", "wow", "sad", "angry"]
    glyphs = ["♥", "♥", "♡", "☺", "◉", "☹", "!"]
    for i, (name, glyph) in enumerate(zip(reactions, glyphs)):
        col, row = i % 4, i // 4
        x = width // 2 - 240 + col * 128
        y = height // 2 - 110 + row * 128
        c.circle(x, y, 42, fill=C["primary_soft"] if i == 1 else C["gray_100"])
        c.text(x, y, glyph, size=24, bold=True, color=C["primary"] if i == 1 else C["gray_600"], anchor="mm")
        c.text(x, y + 58, name, size=11, color=C["gray_600"], anchor="mm")
    button(c, width // 2 - 80, height // 2 + 176, 160, 42, "Send reaction")


def render_explore(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Explore (Proposed)", device=device, proposed=True)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 12
    c.rect(content["x"], y, content["w"], 48, fill=C["white"], radius=24, outline=C["line"])
    c.text(content["x"] + 18, y + 15, "Search topics, people, or hashtags", size=13, color=C["muted"])
    c.text(content["x"], y + 76, "Trending topics", size=16, bold=True, color=C["ink"])
    topics = ["#designsystems", "#weekendhike", "#django", "#react", "#photography"]
    for i, topic in enumerate(topics):
        x = content["x"] + (i % 3) * (content["w"] // 3)
        yy = y + 110 + (i // 3) * 62
        c.rect(x, yy, content["w"] // 3 - 14, 50, fill=C["white"], radius=12, outline=C["line"])
        c.text(x + 14, yy + 16, topic, size=13, bold=True, color=C["primary"])
    c.text(content["x"], y + 250, "People to discover", size=16, bold=True, color=C["ink"])
    for i, name in enumerate(["Maya Chen", "Noah Reed", "Priya Shah"]):
        yy = y + 286 + i * 72
        card(c, content["x"], yy, content["w"], 60)
        avatar(c, content["x"] + 34, yy + 30, 18, name[0], C["accent"])
        c.text(content["x"] + 62, yy + 20, name, size=13, bold=True, color=C["ink"])
        c.text(content["x"] + 62, yy + 38, f"@{name.split()[0].lower()}", size=11, color=C["muted"])
        button(c, content["x"] + content["w"] - 94, yy + 14, 76, 32, "Follow")


def render_search(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Search", active="Explore", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    c.rect(content["x"], y, content["w"], 50, fill=C["white"], radius=25, outline=C["line"])
    c.text(content["x"] + 20, y + 16, "Search people", size=14, color=C["ink"])
    c.text(content["x"] + content["w"] - 92, y + 16, "⌕  Search", size=12, bold=True, color=C["primary"])
    c.text(content["x"], y + 78, "Results for “maya”", size=16, bold=True, color=C["ink"])
    for i, (name, handle, mutual) in enumerate([("Maya Chen", "@mayac", "12 mutual friends"), ("Maya Patel", "@mayap", "4 mutual friends"), ("Noah Reed", "@noahr", "8 mutual friends")]):
        yy = y + 112 + i * 88
        card(c, content["x"], yy, content["w"], 74)
        avatar(c, content["x"] + 40, yy + 37, 22, name[0], C["accent"] if i % 2 == 0 else C["cyan"])
        c.text(content["x"] + 74, yy + 16, name, size=14, bold=True, color=C["ink"])
        c.text(content["x"] + 74, yy + 40, handle + "  ·  " + mutual, size=11, color=C["muted"])
        button(c, content["x"] + content["w"] - 186, yy + 20, 76, 34, "Follow")
        button(c, content["x"] + content["w"] - 100, yy + 20, 82, 34, "Add friend", primary=False)


def render_connections(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    section = "Followers" if screen[1] == "Followers Page" else "Following"
    content = app_shell(c, width, height, section, active="Friends", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    tabs = ["Friends", "Followers", "Following"]
    for i, tab in enumerate(tabs):
        x = content["x"] + i * (content["w"] // 3)
        c.rect(x, y, content["w"] // 3 - 8, 44, fill=C["primary_soft"] if tab == section else C["white"], radius=10, outline=C["line"])
        c.text(x + (content["w"] // 3 - 8) / 2, y + 22, tab, size=13, bold=True, color=C["primary"] if tab == section else C["gray_600"], anchor="mm")
    people = ["Maya Chen", "Noah Reed", "Priya Shah", "Liam Brown", "Sofia Garcia", "Ethan Park"] if section == "Followers" else ["Noah Reed", "Priya Shah", "Liam Brown", "Ethan Park"]
    for i, name in enumerate(people):
        yy = y + 64 + i * 76
        if yy + 60 > content["y"] + content["h"]:
            break
        card(c, content["x"], yy, content["w"], 62)
        avatar(c, content["x"] + 36, yy + 31, 20, name[0], [C["accent"], C["cyan"], C["success"]][i % 3])
        c.text(content["x"] + 68, yy + 18, name, size=13, bold=True, color=C["ink"])
        c.text(content["x"] + 68, yy + 38, f"@{name.split()[0].lower()}  ·  Mutual: {8 + i}", size=11, color=C["muted"])
        button(c, content["x"] + content["w"] - 104, yy + 15, 84, 32, "Follow" if section == "Followers" else "Following", primary=section == "Followers")


def render_notifications(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Notifications", active="Notifications", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    c.text(content["x"], y, "Notifications", size=18, bold=True, color=C["ink"])
    badge(c, content["x"] + 150, y + 2, "LIVE", "success")
    button(c, content["x"] + content["w"] - 210, y - 4, 98, 32, "Refresh", primary=False)
    button(c, content["x"] + content["w"] - 104, y - 4, 98, 32, "Mark all read")
    items = [
        ("Maya Chen", "liked your post.", "like", True),
        ("Noah Reed", "started following you.", "follow", True),
        ("Priya Shah", "replied to your comment.", "reply", False),
        ("Story reaction", "Sofia reacted to your story.", "story_reaction", False),
        ("Friend request", "Liam sent you a friend request.", "friend_request", True),
    ]
    for i, (who, text, kind, unread) in enumerate(items):
        yy = y + 48 + i * 78
        c.rect(content["x"], yy, content["w"], 66, fill=C["primary_soft"] if unread else C["white"], radius=16, outline=C["line"], shadow=True)
        avatar(c, content["x"] + 36, yy + 33, 19, who[0], C["primary"] if unread else C["gray_400"])
        c.text(content["x"] + 66, yy + 14, who, size=13, bold=True, color=C["ink"])
        c.text(content["x"] + 66, yy + 36, text, size=12, color=C["gray_600"])
        c.text(content["x"] + content["w"] - 120, yy + 14, kind, size=10, color=C["muted"])


def render_messenger(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Messenger", active="Messages", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    c.rect(content["x"], y, content["w"], 44, fill=C["white"], radius=22, outline=C["line"])
    c.text(content["x"] + 16, y + 14, "Search conversations", size=12, color=C["muted"])
    conversations = [("Maya Chen", "See you on the trail!", "2m", 2, True), ("Noah Reed", "Sent the latest mockup.", "18m", 0, True), ("Priya Shah", "Thanks for the review.", "1h", 1, False), ("Liam Brown", "Are we still on for Friday?", "3h", 0, True)]
    for i, (name, preview, time, unread, online) in enumerate(conversations):
        yy = y + 64 + i * 82
        card(c, content["x"], yy, content["w"], 70)
        avatar(c, content["x"] + 40, yy + 35, 22, name[0], [C["accent"], C["cyan"], C["success"]][i % 3])
        if online:
            c.circle(content["x"] + 60, yy + 52, 6, fill=C["success"], outline=C["white"], width=2)
        c.text(content["x"] + 74, yy + 14, name, size=14, bold=True, color=C["ink"])
        c.text(content["x"] + 74, yy + 38, preview, size=12, color=C["muted"], max_width=content["w"] - 160)
        c.text(content["x"] + content["w"] - 54, yy + 16, time, size=10, color=C["muted"])
        if unread:
            c.circle(content["x"] + content["w"] - 36, yy + 46, 12, fill=C["primary"])
            c.text(content["x"] + content["w"] - 36, yy + 46, str(unread), size=10, bold=True, color=C["white"], anchor="mm")


def render_chat(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Chat with Maya", active="Messages", device=device)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 38
    card(c, content["x"], y, content["w"], 62)
    avatar(c, content["x"] + 36, y + 31, 20, "M", C["accent"])
    c.text(content["x"] + 66, y + 16, "Maya Chen", size=14, bold=True, color=C["ink"])
    c.text(content["x"] + 66, y + 38, "Online  ·  typing…", size=11, color=C["success"])
    c.text(content["x"] + content["w"] - 100, y + 30, "↩ Back", size=11, color=C["primary"])
    my = y + 78
    msgs = [("Maya", "Are we still on for Saturday?", False), ("You", "Yes! I found a route with a great viewpoint.", True), ("Maya", "Send me the link when you can.", False), ("You", "Done — check your messages.", True)]
    for i, (who, text, mine) in enumerate(msgs):
        yy = my + i * 72
        bw = min(content["w"] - 120, 520)
        bx = content["x"] + content["w"] - bw - 24 if mine else content["x"] + 24
        c.rect(bx, yy, bw, 56, fill=C["primary"] if mine else C["white"], radius=16, outline=None if mine else C["line"])
        c.text(bx + 16, yy + 12, text, size=12, color=C["white"] if mine else C["ink"], max_width=bw - 32)
        c.text(bx + 16, yy + 38, "12:0" + str(i) + "  ✓✓" if mine else "12:0" + str(i), size=9, color="#DBEAFE" if mine else C["muted"])
    c.rect(content["x"] + 20, content["y"] + content["h"] - 72, content["w"] - 40, 52, fill=C["white"], radius=26, outline=C["line"])
    c.text(content["x"] + 38, content["y"] + content["h"] - 55, "Type a message…", size=12, color=C["muted"])
    c.circle(content["x"] + content["w"] - 56, content["y"] + content["h"] - 46, 18, fill=C["primary"])
    c.text(content["x"] + content["w"] - 56, content["y"] + content["h"] - 46, "↑", size=16, bold=True, color=C["white"], anchor="mm")


def render_settings(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Settings (Proposed)", device=device, proposed=True)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 12
    sections = [
        ("Account", "Username, email, password change, deactivate account"),
        ("Privacy", "Private profile, comment and message permissions — implemented in Edit profile"),
        ("Notifications", "Eight preference switches — implemented as a global dialog"),
        ("Appearance", "Light/dark theme persisted as socialconnect-theme"),
        ("PWA", "App-shell caching only; offline data and push are not implemented"),
    ]
    for i, (title, desc) in enumerate(sections):
        yy = y + i * 88
        card(c, content["x"], yy, content["w"], 74)
        c.text(content["x"] + 20, yy + 16, title, size=15, bold=True, color=C["ink"])
        c.text(content["x"] + 20, yy + 42, desc, size=11, color=C["muted"], max_width=content["w"] - 120)
        c.text(content["x"] + content["w"] - 40, yy + 34, "›", size=20, color=C["muted"])


def render_user_dashboard(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "User Dashboard", device=device, proposed=True)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 12
    kpis = [("Posts", "128"), ("Followers", "2.4k"), ("Likes received", "8.6k"), ("Unread", "3")]
    for i, (label, value) in enumerate(kpis):
        x = content["x"] + (i % 2) * (content["w"] // 2)
        yy = y + (i // 2) * 100
        card(c, x, yy, content["w"] // 2 - 12, 86)
        c.text(x + 18, yy + 14, label, size=12, color=C["muted"])
        c.text(x + 18, yy + 42, value, size=24, bold=True, color=C["primary"])
    cy = y + 214
    card(c, content["x"], cy, content["w"], max(140, content["h"] - 224))
    c.text(content["x"] + 20, cy + 18, "Your recent activity", size=16, bold=True, color=C["ink"])
    for i, text in enumerate(["Published “Designing calmer feeds”", "Received 12 new followers this week", "3 friend requests waiting", "Viewed 7 stories today"]):
        c.circle(content["x"] + 28, cy + 60 + i * 42, 6, fill=C["primary"] if i % 2 == 0 else C["accent"])
        c.text(content["x"] + 46, cy + 52 + i * 42, text, size=12, color=C["gray_600"])


def render_admin(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    c.rect(0, 0, width, height, fill=C["gray_100"])
    c.rect(0, 0, width, 70, fill=C["navy"])
    c.circle(38, 35, 18, fill=C["primary"])
    c.text(38, 35, "SC", size=12, bold=True, color=C["white"], anchor="mm")
    c.text(68, 20, "SocialConnect Administration", size=18, bold=True, color=C["white"])
    c.text(68, 44, "Dashboard", size=11, color="#CBD5E1")
    c.text(width - 40, 34, "Admin  ·  Sign out", size=12, color="#CBD5E1", anchor="rm")
    nav_w = 220 if device == "desktop" else 0
    if nav_w:
        c.rect(0, 70, nav_w, height - 70, fill=C["white"])
        groups = ["MAIN MENU", "SOCIAL MANAGEMENT", "MODERATION & GOVERNANCE", "SYSTEM"]
        y = 100
        for g in groups:
            c.text(18, y, g, size=10, bold=True, color=C["gray_400"])
            y += 24
            for item in ["Dashboard", "Analytics", "Users", "Posts"][: 2 if g != "MAIN MENU" else 3]:
                c.rect(12, y - 4, nav_w - 24, 32, fill=C["primary_soft"] if item == "Dashboard" else C["white"], radius=8)
                c.text(26, y + 5, item, size=12, color=C["primary"] if item == "Dashboard" else C["gray_600"])
                y += 38
            y += 16
    x0 = nav_w + 24
    w0 = width - x0 - 24
    screen_label(c, x0, 88, screen, w0)
    kpis = [
        ("Total Users", "1,284", "+12%"), ("Active Users", "346", "refresh proxy"), ("Total Posts", "8,942", "+8%"), ("Total Comments", "24,118", "+5%"),
        ("Pending Reports", "17", "all reports"), ("Total Likes", "62,431", "+14%"), ("New Registrations", "128", "30 days"), ("Pending Friend Requests", "43", "+3%"),
        ("Active Stories", "29", "live"), ("Expired Stories", "112", "24 h"), ("Total Stories", "141", "+6%"), ("Story Reactions", "583", "+9%"),
    ]
    cols = 4 if device == "desktop" else 2
    kw = (w0 - (cols - 1) * 12) // cols
    kh = 78 if device == "desktop" else 70
    for i, (label, value, trend) in enumerate(kpis):
        col, row = i % cols, i // cols
        x = x0 + col * (kw + 12)
        y = 136 + row * (kh + 12)
        card(c, x, y, kw, kh)
        c.text(x + 14, y + 12, label, size=11, color=C["muted"], max_width=kw - 28)
        c.text(x + 14, y + 36, value, size=20, bold=True, color=C["navy"])
        c.text(x + kw - 14, y + 50, trend, size=9, color=C["success"] if "+" in trend else C["muted"], anchor="rb")
    cy = 136 + 3 * (kh + 12) + 12
    card(c, x0, cy, w0, max(150, height - cy - 24))
    c.text(x0 + 18, cy + 16, "Recent activity  ·  Django LogEntry", size=15, bold=True, color=C["ink"])
    for i, text in enumerate(["admin changed user Alex Morgan", "admin added post “Community guidelines”", "admin changed group Moderators", "admin deleted notification #4821"]):
        c.text(x0 + 20, cy + 52 + i * 32, "• " + text, size=12, color=C["gray_600"])


def render_report_user(c: Canvas, width: int, height: int, screen: tuple[str, str, str, str], device: str) -> None:
    content = app_shell(c, width, height, "Report User", device=device, proposed=True)
    screen_label(c, content["x"], content["y"], screen, content["w"])
    y = content["y"] + 12
    card(c, content["x"], y, content["w"], min(430, content["h"] - 20))
    c.text(content["x"] + 20, y + 18, "Report this user", size=18, bold=True, color=C["ink"])
    c.text(content["x"] + 20, y + 48, "PROPOSED: source exposes PostReport (post reports only), not a user-report model.", size=12, bold=True, color=C["warn"], max_width=content["w"] - 40)
    reasons = ["Harassment or bullying", "Spam or misleading content", "Impersonation", "Inappropriate content", "Other"]
    for i, reason in enumerate(reasons):
        yy = y + 96 + i * 50
        c.circle(content["x"] + 30, yy + 12, 9, fill=C["white"], outline=C["primary"], width=2)
        c.text(content["x"] + 52, yy + 3, reason, size=13, color=C["gray_700"])
    c.rect(content["x"] + 20, y + 350, content["w"] - 40, 62, fill=C["gray_50"], radius=10, outline=C["line"])
    c.text(content["x"] + 34, y + 364, "Additional details (optional)", size=11, color=C["muted"])
    button(c, content["x"] + content["w"] - 130, y + 372, 108, 34, "Submit")


RENDERERS = {
    "Login": render_auth,
    "Registration": render_auth,
    "Forgot Password": render_auth,
    "Home / News Feed": render_home,
    "User Profile": render_profile,
    "Block User": render_profile,
    "Edit Profile": render_edit_profile,
    "Create Post": render_create_post,
    "Post Details": render_post_detail,
    "Comments and Replies": render_comments,
    "Stories Section": render_stories,
    "Story Viewer": render_story_viewer,
    "Story Reaction": render_story_reaction,
    "Explore Page": render_explore,
    "Search Results": render_search,
    "Followers Page": render_connections,
    "Following Page": render_connections,
    "Notification Page": render_notifications,
    "Messenger Page": render_messenger,
    "Individual Chat Page": render_chat,
    "Settings Page": render_settings,
    "User Dashboard": render_user_dashboard,
    "Admin Dashboard": render_admin,
    "Report User": render_report_user,
}


def filename(sid: str, name: str) -> str:
    safe = name.replace("/", " or ").replace(":", "-")
    return f"{sid}_{safe.replace(' ', '_')}"


def write_ui_source(screen: tuple[str, str, str, str], stem: str) -> None:
    sid, name, status, desc = screen
    body = f"""
      <p><span class="badge">{sid}</span> <span class="badge">{html_escape(status)}</span></p>
      <p>{html_escape(desc)}</p>
      <h2>Layout notes</h2>
      <ul>
        <li><strong>Desktop:</strong> 1920×1080 three-zone shell or focused auth/admin layout.</li>
        <li><strong>Mobile:</strong> 720×1280 single column with fixed bottom navigation where applicable.</li>
        <li><strong>Design system:</strong> Segoe UI, 16 px base, 12–20 px spacing scale, 10–20 px radii, soft shadows, primary #2563EB, accent #7C3AED.</li>
        <li><strong>Source rule:</strong> proposed screens are visual proposals only; they are not active SPA routes.</li>
      </ul>
      <h2>Rendered references</h2>
      <div class="grid">
        <figure><img src="../../Desktop/{stem}.png" alt="Desktop mockup for {html_escape(name)}"/><figcaption>Desktop PNG</figcaption></figure>
        <figure><img src="../../Mobile/{stem}.png" alt="Mobile mockup for {html_escape(name)}"/><figcaption>Mobile PNG</figcaption></figure>
      </div>
    """
    write_html_source(MOCK_SOURCE / stem, f"{sid} {name}", desc, body)


def html_escape(value: str) -> str:
    import html
    return html.escape(value, quote=True)


# Generate mockups ------------------------------------------------------------------

for screen in SCREENS:
    sid, name, status, desc = screen
    stem = filename(sid, name)
    renderer = RENDERERS[name]
    for device, folder, size in [("desktop", MOCK_DESKTOP, DESKTOP), ("mobile", MOCK_MOBILE, MOBILE)]:
        c = Canvas(size[0], size[1], C["bg"])
        renderer(c, size[0], size[1], screen, device)
        c.save_png(folder / (stem + ".png"))
        c.save_svg(folder / (stem + ".svg"))
    write_ui_source(screen, stem)

write_text(MOCK_SOURCE / "design_system.css", BASE_CSS)

_inventory = ["# UI Mockup Inventory", "", "| Screen ID | Screen | Status | Description | Desktop | Mobile | Source |", "| --- | --- | --- | --- | --- | --- | --- |"]
for _screen in SCREENS:
    _sid, _name, _status, _desc = _screen
    _stem = filename(_sid, _name)
    _inventory.append(f"| {_sid} | {_name} | {_status} | {_desc} | Desktop/{_stem}.png | Mobile/{_stem}.png | Source_HTML_CSS/{_stem}.html |")
_inventory.append("")
write_text(MOCK_DESKTOP.parent / "SCREEN_INVENTORY.md", "\n".join(_inventory))

# Generate wireframes ---------------------------------------------------------------


def render_wireframe(c: Canvas, width: int, height: int, wf: tuple[str, str, str], device: str) -> None:
    wid, name, screen_id = wf
    proposed = name in {"Create Post", "Explore", "Settings"}
    content = wireframe_shell(c, width, height, f"{wid} {name}", device, proposed)
    y = content["y"]
    if name == "Login":
        wf_box(c, content["x"], y, content["w"], 60, "LOGO + TAGLINE")
        wf_box(c, content["x"], y + 76, content["w"], 56, "USERNAME FIELD")
        wf_box(c, content["x"], y + 144, content["w"], 56, "PASSWORD FIELD")
        wf_box(c, content["x"], y + 212, content["w"], 52, "SIGN IN BUTTON")
    elif name == "Registration":
        for i, label in enumerate(["USERNAME", "EMAIL", "PASSWORD", "CONFIRM PASSWORD", "CREATE BUTTON"]):
            wf_box(c, content["x"], y + i * 64, content["w"], 50, label)
    elif name == "Home Feed":
        wf_box(c, content["x"], y, content["w"], 70, "STORIES STRIP")
        wf_box(c, content["x"], y + 84, content["w"], 66, "COMPOSER / MEDIA / AUDIENCE")
        for i in range(2):
            wf_box(c, content["x"], y + 164 + i * 150, content["w"], 130, f"POST CARD {i + 1}: AUTHOR / TEXT / MEDIA / ACTIONS")
    elif name == "Profile":
        wf_box(c, content["x"], y, content["w"], 100, "COVER + AVATAR + NAME")
        wf_box(c, content["x"], y + 116, content["w"], 54, "STATS: POSTS / FOLLOWERS / FOLLOWING")
        wf_box(c, content["x"], y + 186, content["w"], 120, "POST GRID OR FEED")
    elif name == "Create Post":
        wf_box(c, content["x"], y, content["w"], 60, "PROPOSED SCREEN LABEL")
        wf_box(c, content["x"], y + 76, content["w"], 120, "TEXT EDITOR")
        wf_box(c, content["x"], y + 210, content["w"], 80, "MEDIA PREVIEW / VALIDATION")
        wf_box(c, content["x"], y + 304, content["w"], 60, "TOOLS: PHOTO / VIDEO / AUDIENCE / DRAFT / SCHEDULE")
        wf_box(c, content["x"], y + 378, content["w"], 50, "PUBLISH BUTTON")
    elif name == "Story":
        wf_box(c, content["x"], y, content["w"], 64, "STORY STRIP")
        wf_box(c, content["x"], y + 82, content["w"], 220, "STORY VIEWER: PROGRESS / MEDIA / REPLY")
    elif name == "Explore":
        wf_box(c, content["x"], y, content["w"], 54, "SEARCH FIELD")
        wf_box(c, content["x"], y + 70, content["w"], 90, "TRENDING TOPICS")
        wf_box(c, content["x"], y + 176, content["w"], 180, "PEOPLE / SUGGESTIONS")
    elif name == "Chat":
        wf_box(c, content["x"], y, content["w"], 60, "HEADER: PEER / PRESENCE / TYPING")
        wf_box(c, content["x"], y + 76, content["w"], 280, "MESSAGE LIST: INCOMING / OUTGOING / DATE SEPARATOR")
        wf_box(c, content["x"], y + 372, content["w"], 56, "COMPOSER + ATTACH + SEND")
    elif name == "Notification":
        for i in range(4):
            wf_box(c, content["x"], y + i * 84, content["w"], 68, f"NOTIFICATION {i + 1}: ICON / COPY / READ STATE")
        wf_box(c, content["x"], y + 344, content["w"], 50, "MARK ALL READ / REFRESH")
    elif name == "Settings":
        for i, label in enumerate(["ACCOUNT", "PRIVACY", "NOTIFICATIONS", "APPEARANCE", "PWA"]):
            wf_box(c, content["x"], y + i * 72, content["w"], 56, label)
    elif name == "Admin Dashboard":
        for i in range(4):
            wf_box(c, content["x"] + (i % 2) * (content["w"] // 2), y + (i // 2) * 72, content["w"] // 2 - 10, 58, f"KPI {i + 1}: VALUE / TREND")
        wf_box(c, content["x"], y + 160, content["w"], 130, "CHART: SIX-MONTH SERIES")
        wf_box(c, content["x"], y + 304, content["w"], 100, "RECENT ACTIVITY TABLE")


for wf in WIREFRAMES:
    wid, name, screen_id = wf
    stem = f"{wid}_{name.replace(' ', '_')}"
    for device, folder, size in [("desktop", WF_DESKTOP, DESKTOP), ("mobile", WF_MOBILE, MOBILE)]:
        c = Canvas(size[0], size[1], C["white"])
        render_wireframe(c, size[0], size[1], wf, device)
        c.save_png(folder / (stem + ".png"))
        c.save_svg(folder / (stem + ".svg"))
    body = f"""
      <p><span class="badge">{wid}</span> <span class="badge">Linked to {screen_id}</span></p>
      <p>Low-fidelity grayscale wireframe. Header/navigation, main content, cards, forms, buttons, footer, and responsive structure are labelled explicitly.</p>
      <div class="grid">
        <figure><img src="../../Desktop/{stem}.png" alt="Desktop wireframe for {html_escape(name)}"/><figcaption>Desktop PNG</figcaption></figure>
        <figure><img src="../../Mobile/{stem}.png" alt="Mobile wireframe for {html_escape(name)}"/><figcaption>Mobile PNG</figcaption></figure>
      </div>
    """
    write_html_source(WF_SOURCE / stem, f"{wid} {name}", "Grayscale wireframe source", body)

write_text(WF_SOURCE / "design_system.css", BASE_CSS)

_wf_inventory = ["# Wireframe Inventory", "", "| Wireframe ID | Name | Linked screen | Desktop | Mobile | Source |", "| --- | --- | --- | --- | --- | --- |"]
for _wf in WIREFRAMES:
    _wid, _name, _screen_id = _wf
    _stem = f"{_wid}_{_name.replace(' ', '_')}"
    _wf_inventory.append(f"| {_wid} | {_name} | {_screen_id} | Desktop/{_stem}.png | Mobile/{_stem}.png | Source_HTML_CSS/{_stem}.html |")
_wf_inventory.append("")
write_text(WF_DESKTOP.parent / "WIREFRAME_INVENTORY.md", "\n".join(_wf_inventory))
print(f"generated {len(SCREENS)} mockups x 2 devices and {len(WIREFRAMES)} wireframes x 2 devices")
