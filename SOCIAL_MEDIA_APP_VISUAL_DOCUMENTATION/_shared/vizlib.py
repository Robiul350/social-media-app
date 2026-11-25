"""Shared vector/raster rendering helpers for the visual documentation package.

Everything produced here is generated from source-verified documentation data in
CLAUDE_DOCUMENTATION_PROMPT/. The same operation list is rendered to PNG with
Pillow and to SVG as editable vector markup. No application source is modified.
"""

from __future__ import annotations

import html
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\seguisb.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

C = {
    "bg": "#F5F7FB",
    "white": "#FFFFFF",
    "ink": "#172033",
    "muted": "#64748B",
    "line": "#DCE3EE",
    "primary": "#2563EB",
    "primary_dark": "#1D4ED8",
    "primary_soft": "#E8F0FE",
    "accent": "#7C3AED",
    "accent_soft": "#F1E9FE",
    "success": "#16A34A",
    "success_soft": "#E8F7EE",
    "warn": "#D97706",
    "warn_soft": "#FFF3DF",
    "danger": "#DC2626",
    "danger_soft": "#FEECEC",
    "navy": "#0F172A",
    "navy_2": "#1E293B",
    "cyan": "#0891B2",
    "gray_50": "#F8FAFC",
    "gray_100": "#F1F5F9",
    "gray_200": "#E2E8F0",
    "gray_300": "#CBD5E1",
    "gray_400": "#94A3B8",
    "gray_500": "#64748B",
    "gray_600": "#475569",
    "gray_700": "#334155",
}


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    ar, ag, ab = rgb(a)
    br, bg, bb = rgb(b)
    return "#%02X%02X%02X" % (
        round(ar + (br - ar) * t),
        round(ag + (bg - ag) * t),
        round(ab + (bb - ab) * t),
    )


def _font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REG)
    return ImageFont.truetype(path, size)


def _svg_anchor(anchor: str) -> tuple[str, str]:
    h = anchor[0] if len(anchor) > 0 else "l"
    v = anchor[1] if len(anchor) > 1 else "t"
    text_anchor = {"l": "start", "m": "middle", "r": "end"}.get(h, "start")
    baseline = {
        "t": "text-before-edge",
        "m": "central",
        "b": "text-after-edge",
        "a": "alphabetic",
    }.get(v, "text-before-edge")
    return text_anchor, baseline


class Canvas:
    """Records drawing operations and renders them to PNG and SVG."""

    def __init__(self, width: int, height: int, background: str = C["bg"]):
        self.width = width
        self.height = height
        self.background = background
        self.image = Image.new("RGB", (width, height), rgb(background))
        self.draw = ImageDraw.Draw(self.image)
        self.ops: list[dict] = []

    # ---------- primitives ----------

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str = C["white"],
        outline: str | None = None,
        radius: int = 0,
        width: int = 1,
        shadow: bool = False,
    ) -> None:
        x, y, w, h = map(int, (x, y, w, h))
        if shadow:
            sx, sy = x + 5, y + 6
            if radius:
                self.draw.rounded_rectangle(
                    (sx, sy, sx + w, sy + h), radius=radius, fill=mix(fill, "#000000", 0.16)
                )
            else:
                self.draw.rectangle((sx, sy, sx + w, sy + h), fill=mix(fill, "#000000", 0.16))
            self.ops.append(
                dict(kind="rect", x=sx, y=sy, w=w, h=h, fill=mix(fill, "#000000", 0.16), radius=radius)
            )
        if radius:
            self.draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=outline, width=width)
        else:
            self.draw.rectangle((x, y, x + w, y + h), fill=fill, outline=outline, width=width)
        self.ops.append(
            dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill, outline=outline, radius=radius, width=width)
        )

    def circle(self, cx: float, cy: float, r: float, fill: str, outline: str | None = None, width: int = 1) -> None:
        cx, cy, r = int(cx), int(cy), int(r)
        self.draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=width)
        self.ops.append(dict(kind="circle", cx=cx, cy=cy, r=r, fill=fill, outline=outline, width=width))

    def line(
        self,
        points: list[tuple[float, float]],
        fill: str = C["line"],
        width: int = 2,
        dash: tuple[int, int] | None = None,
    ) -> None:
        pts = [(int(x), int(y)) for x, y in points]
        if dash:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                length = math.hypot(x2 - x1, y2 - y1)
                if length == 0:
                    continue
                on, off = dash
                pos = 0.0
                while pos < length:
                    end = min(pos + on, length)
                    t1, t2 = pos / length, end / length
                    self.draw.line(
                        (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1, x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2),
                        fill=fill,
                        width=width,
                    )
                    pos += on + off
        else:
            self.draw.line(pts, fill=fill, width=width, joint="curve")
        self.ops.append(dict(kind="line", points=pts, fill=fill, width=width, dash=dash))

    def polygon(self, points: list[tuple[float, float]], fill: str, outline: str | None = None) -> None:
        pts = [(int(x), int(y)) for x, y in points]
        self.draw.polygon(pts, fill=fill, outline=outline)
        self.ops.append(dict(kind="polygon", points=pts, fill=fill, outline=outline))

    def text(
        self,
        x: float,
        y: float,
        value: str,
        size: int = 16,
        bold: bool = False,
        color: str = C["ink"],
        anchor: str = "lt",
        max_width: int | None = None,
        line_gap: float = 1.22,
        mono: bool = False,
        italic: bool = False,
    ) -> None:
        font = _font(size, bold, mono)
        value = str(value)
        if max_width:
            lines: list[str] = []
            for paragraph in value.split("\n"):
                current = ""
                for word in paragraph.split():
                    candidate = f"{current} {word}".strip()
                    if current and font.getlength(candidate) > max_width:
                        lines.append(current)
                        current = word
                    else:
                        current = candidate
                lines.append(current)
        else:
            lines = value.split("\n")
        line_h = int(size * line_gap)
        total_h = line_h * len(lines)
        v = anchor[1] if len(anchor) > 1 else "t"
        if v == "m":
            y -= total_h / 2
        elif v in ("b", "d"):
            y -= total_h
        for i, line in enumerate(lines):
            lx, ly = int(x), int(y + i * line_h)
            self.draw.text((lx, ly), line, font=font, fill=color, anchor=anchor)
            self.ops.append(
                dict(
                    kind="text",
                    x=lx,
                    y=ly,
                    value=line,
                    size=size,
                    bold=bold,
                    color=color,
                    anchor=anchor,
                    mono=mono,
                    italic=italic,
                )
            )

    def arrow(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        label: str = "",
        color: str = C["muted"],
        width: int = 2,
        dashed: bool = False,
        both: bool = False,
        label_size: int = 13,
    ) -> None:
        x1, y1 = start
        x2, y2 = end
        self.line([start, end], fill=color, width=width, dash=(7, 5) if dashed else None)
        angle = math.atan2(y2 - y1, x2 - x1)
        head = 11
        for direction in ([1] if not both else [1, -1]):
            a = angle if direction == 1 else angle + math.pi
            bx, by = (x2, y2) if direction == 1 else (x1, y1)
            p1 = (bx - head * math.cos(a - 0.45), by - head * math.sin(a - 0.45))
            p2 = (bx - head * math.cos(a + 0.45), by - head * math.sin(a + 0.45))
            self.polygon([(bx, by), p1, p2], fill=color)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            f = _font(label_size)
            tw = f.getlength(label)
            self.rect(mx - tw / 2 - 6, my - label_size / 2 - 5, tw + 12, label_size + 10, fill=C["white"], radius=6)
            self.text(mx, my, label, size=label_size, color=color, anchor="mm", max_width=None)

    # ---------- save ----------

    def save_png(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path, "PNG", optimize=True)
        return path

    def save_svg(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img">',
            f'<rect width="100%" height="100%" fill="{self.background}"/>',
        ]
        for op in self.ops:
            k = op["kind"]
            if k == "rect":
                out.append(
                    f'<rect x="{op["x"]}" y="{op["y"]}" width="{op["w"]}" height="{op["h"]}" rx="{op.get("radius",0)}" '
                    f'fill="{op["fill"]}" stroke="{op.get("outline") or "none"}" stroke-width="{op.get("width",1)}"/>'
                )
            elif k == "circle":
                out.append(
                    f'<circle cx="{op["cx"]}" cy="{op["cy"]}" r="{op["r"]}" fill="{op["fill"]}" '
                    f'stroke="{op.get("outline") or "none"}" stroke-width="{op.get("width",1)}"/>'
                )
            elif k == "line":
                dash = ' stroke-dasharray="7 5"' if op.get("dash") else ""
                pts = " ".join(f"{x},{y}" for x, y in op["points"])
                out.append(f'<polyline points="{pts}" fill="none" stroke="{op["fill"]}" stroke-width="{op["width"]}"{dash}/>')
            elif k == "polygon":
                pts = " ".join(f"{x},{y}" for x, y in op["points"])
                out.append(f'<polygon points="{pts}" fill="{op["fill"]}" stroke="{op.get("outline") or "none"}"/>')
            elif k == "text":
                ta, bl = _svg_anchor(op["anchor"])
                weight = 700 if op["bold"] else 400
                family = "Consolas, monospace" if op["mono"] else "Segoe UI, Arial, sans-serif"
                style = " italic" if op.get("italic") else ""
                out.append(
                    f'<text x="{op["x"]}" y="{op["y"]}" font-family="{family}" font-size="{op["size"]}" '
                    f'font-weight="{weight}" font-style="{style.strip()}" fill="{op["color"]}" text-anchor="{ta}" '
                    f'dominant-baseline="{bl}">{html.escape(op["value"])}</text>'
                )
        out.append("</svg>")
        path.write_text("\n".join(out), encoding="utf-8")
        return path


def save_pair(
    canvas: Canvas,
    stem: Path | str,
    source_ext: str | None = None,
    source_text: str | None = None,
) -> dict[str, Path]:
    stem = Path(stem)
    result = {
        "png": canvas.save_png(stem.with_suffix(".png")),
        "svg": canvas.save_svg(stem.with_suffix(".svg")),
    }
    if source_ext and source_text is not None:
        src = stem.with_suffix("." + source_ext.lstrip("."))
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text(source_text, encoding="utf-8")
        result["source"] = src
    return result


def write_text(path: Path | str, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------- diagram helpers ----------

KIND_STYLE = {
    "entity": (C["primary_soft"], C["primary"]),
    "actor": (C["accent_soft"], C["accent"]),
    "process": (C["success_soft"], C["success"]),
    "store": (C["warn_soft"], C["warn"]),
    "external": (C["gray_100"], C["gray_600"]),
    "api": (C["primary_soft"], C["primary_dark"]),
    "websocket": (C["accent_soft"], C["accent"]),
    "database": (C["warn_soft"], C["warn"]),
    "note": (C["gray_50"], C["gray_400"]),
    "decision": (C["warn_soft"], C["warn"]),
}


class DiagramRenderer:
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        width: int = 1920,
        height: int = 1080,
        dark_header: bool = True,
    ):
        self.width = width
        self.height = height
        self.c = Canvas(width, height, C["bg"])
        if dark_header:
            self.c.rect(0, 0, width, 118, fill=C["navy"])
            self.c.rect(0, 114, width, 4, fill=C["primary"])
            title_color, sub_color = C["white"], "#CBD5E1"
        else:
            title_color, sub_color = C["ink"], C["muted"]
        self.c.text(44, 28, title, size=32, bold=True, color=title_color)
        if subtitle:
            self.c.text(44, 74, subtitle, size=17, color=sub_color, max_width=width - 88)
        self.c.text(width - 44, height - 28, "Source-verified | Social Media App (UI name: SocialConnect)", size=13, color=C["muted"], anchor="rb")
        self.nodes: dict[str, dict] = {}

    def lane(self, x: int, y: int, w: int, h: int, label: str, fill: str = C["gray_50"], outline: str = C["gray_200"]) -> None:
        self.c.rect(x, y, w, h, fill=fill, outline=outline, radius=16)
        self.c.text(x + 16, y + 10, label, size=16, bold=True, color=C["gray_600"])

    def node(
        self,
        nid: str,
        label: str,
        x: int,
        y: int,
        w: int = 220,
        h: int = 92,
        kind: str = "entity",
        fields: list[str] | None = None,
        sublabel: str = "",
    ) -> dict:
        fill, outline = KIND_STYLE.get(kind, KIND_STYLE["entity"])
        self.c.rect(x, y, w, h, fill=fill, outline=outline, radius=12, width=2, shadow=True)
        if kind == "actor":
            self.c.circle(x + 30, y + 34, 14, fill=outline)
            self.c.text(x + 52, y + 18, label, size=16, bold=True, color=C["ink"], max_width=w - 66)
        else:
            self.c.text(x + 16, y + 14, label, size=17, bold=True, color=C["ink"], max_width=w - 32)
        if sublabel:
            self.c.text(x + 16, y + 42, sublabel, size=13, color=C["muted"], max_width=w - 32)
        if fields:
            fy = y + 42 if not sublabel else y + 62
            for field in fields[: max(0, (h - (fy - y) - 10) // 18)]:
                self.c.text(x + 16, fy, "• " + field, size=13, color=C["gray_600"], max_width=w - 30)
                fy += 18
        info = dict(id=nid, x=x, y=y, w=w, h=h, kind=kind)
        self.nodes[nid] = info
        return info

    def note(self, x: int, y: int, w: int, h: int, text: str, kind: str = "note") -> None:
        self.node("__note_" + str(len(self.nodes)), text, x, y, w, h, kind=kind)

    def edge(
        self,
        src: str,
        dst: str,
        label: str = "",
        color: str | None = None,
        dashed: bool = False,
        both: bool = False,
        offset: int = 0,
        width: int = 2,
    ) -> None:
        a, b = self.nodes[src], self.nodes[dst]
        ax, ay = a["x"] + a["w"] / 2 + offset, a["y"] + a["h"] / 2 + offset
        bx, by = b["x"] + b["w"] / 2 + offset, b["y"] + b["h"] / 2 + offset
        dx, dy = bx - ax, by - ay
        if abs(dx) > abs(dy):
            sx = ax + (a["w"] / 2 if dx > 0 else -a["w"] / 2)
            sy = ay
            ex = bx - (b["w"] / 2 if dx > 0 else -b["w"] / 2)
            ey = by
        else:
            sx = ax
            sy = ay + (a["h"] / 2 if dy > 0 else -a["h"] / 2)
            ex = bx
            ey = by - (b["h"] / 2 if dy > 0 else -b["h"] / 2)
        self.c.arrow((sx, sy), (ex, ey), label=label, color=color or C["gray_500"], dashed=dashed, both=both, width=width)

    def free_arrow(self, start, end, label="", color=None, dashed=False, both=False) -> None:
        self.c.arrow(start, end, label=label, color=color or C["gray_500"], dashed=dashed, both=both)

    def render(self, stem: Path | str, source_ext: str = "mmd", source_text: str = "") -> dict[str, Path]:
        return save_pair(self.c, stem, source_ext, source_text)


# ---------- UI mockup helpers ----------

NAV_ITEMS = [
    ("Home", "home"),
    ("Explore", "search"),
    ("Friends", "friends"),
    ("Messages", "messages"),
    ("Notifications", "bell"),
]


def _icon(c: Canvas, x: int, y: int, kind: str, color: str, size: int = 20) -> None:
    c.circle(x, y, size // 2 + 2, fill=mix(color, C["white"], 0.86))
    glyph = {
        "home": "⌂", "search": "⌕", "friends": "◎", "messages": "✉", "bell": "♢",
        "settings": "⚙", "bookmark": "▢", "profile": "☺", "more": "⋯", "sun": "☀", "moon": "☾",
    }.get(kind, "•")
    c.text(x, y - 1, glyph, size=size, bold=True, color=color, anchor="mm")


def app_shell(
    c: Canvas,
    width: int,
    height: int,
    title: str,
    active: str = "Home",
    device: str = "desktop",
    proposed: bool = False,
    user: str = "Alex Morgan",
) -> dict:
    c.rect(0, 0, width, height, fill=C["bg"])
    if device == "mobile":
        c.rect(0, 0, width, 66, fill=C["white"])
        c.rect(0, 64, width, 2, fill=C["line"])
        c.circle(32, 33, 16, fill=C["primary"])
        c.text(32, 33, "SC", size=13, bold=True, color=C["white"], anchor="mm")
        c.text(60, 16, "SocialConnect", size=17, bold=True, color=C["navy"])
        c.text(60, 38, title, size=12, color=C["muted"])
        bottom_y = height - 76
        c.rect(0, bottom_y, width, 76, fill=C["white"])
        c.rect(0, bottom_y, width, 2, fill=C["line"])
        for i, (label, kind) in enumerate(NAV_ITEMS):
            x = int((i + 0.5) * width / len(NAV_ITEMS))
            col = C["primary"] if label == active else C["muted"]
            _icon(c, x, bottom_y + 26, kind, col, 18)
            c.text(x, bottom_y + 52, label[:6], size=10, color=col, anchor="mm")
        content = dict(x=20, y=84, w=width - 40, h=height - 176)
    else:
        c.rect(0, 0, width, 76, fill=C["white"])
        c.rect(0, 74, width, 2, fill=C["line"])
        c.circle(40, 38, 19, fill=C["primary"])
        c.text(40, 38, "SC", size=15, bold=True, color=C["white"], anchor="mm")
        c.text(70, 23, "SocialConnect", size=21, bold=True, color=C["navy"])
        c.text(70, 49, title, size=13, color=C["muted"])
        c.rect(width - 430, 20, 270, 38, fill=C["gray_100"], radius=19)
        c.text(width - 412, 33, "Search people, posts…", size=14, color=C["gray_400"])
        _icon(c, width - 390, 39, "search", C["gray_400"], 17)
        c.circle(width - 118, 38, 19, fill=C["accent_soft"])
        c.text(width - 118, 38, "AM", size=12, bold=True, color=C["accent"], anchor="mm")
        c.text(width - 74, 33, user, size=13, bold=True, color=C["ink"])
        c.text(width - 74, 51, "View profile", size=11, color=C["muted"])
        nav_x, nav_y, nav_w = 22, 100, 228
        c.rect(nav_x, nav_y, nav_w, height - 130, fill=C["white"], radius=18, outline=C["line"], shadow=True)
        for i, (label, kind) in enumerate(NAV_ITEMS):
            y = nav_y + 24 + i * 54
            if label == active:
                c.rect(nav_x + 12, y - 10, nav_w - 24, 44, fill=C["primary_soft"], radius=12)
            col = C["primary"] if label == active else C["gray_600"]
            _icon(c, nav_x + 36, y + 12, kind, col, 18)
            c.text(nav_x + 66, y + 1, label, size=15, bold=label == active, color=col)
        c.rect(nav_x + 12, nav_y + 310, nav_w - 24, 2, fill=C["line"])
        for i, (label, kind) in enumerate([("Bookmarks", "bookmark"), ("Settings", "settings")]):
            y = nav_y + 330 + i * 46
            _icon(c, nav_x + 36, y + 11, kind, C["gray_600"], 17)
            c.text(nav_x + 66, y, label, size=14, color=C["gray_600"])
        right_x = width - 330
        c.rect(right_x, nav_y, 308, height - 130, fill=C["white"], radius=18, outline=C["line"], shadow=True)
        c.text(right_x + 20, nav_y + 20, "Suggested for you", size=16, bold=True, color=C["ink"])
        for i, (name, handle) in enumerate([("Maya Chen", "@mayac"), ("Noah Reed", "@noahr"), ("Priya Shah", "@priyas")]):
            y = nav_y + 58 + i * 70
            c.circle(right_x + 38, y + 20, 18, fill=[C["accent"], C["cyan"], C["success"]][i])
            c.text(right_x + 38, y + 20, name.split()[0][0], size=13, bold=True, color=C["white"], anchor="mm")
            c.text(right_x + 66, y + 5, name, size=13, bold=True, color=C["ink"])
            c.text(right_x + 66, y + 26, handle, size=11, color=C["muted"])
            c.rect(right_x + 210, y + 8, 72, 28, fill=C["primary_soft"], radius=14)
            c.text(right_x + 246, y + 22, "Follow", size=11, bold=True, color=C["primary"], anchor="mm")
        content = dict(x=nav_x + nav_w + 22, y=nav_y, w=right_x - (nav_x + nav_w + 44), h=height - 130)
    if proposed:
        c.rect(content["x"], content["y"], content["w"], 48, fill=C["warn_soft"], outline=C["warn"], radius=10)
        c.text(content["x"] + 16, content["y"] + 14, "PROPOSED DESIGN — not implemented as a dedicated screen", size=15, bold=True, color=C["warn"])
        content["y"] += 60
        content["h"] -= 60
    return content


def card(c: Canvas, x: int, y: int, w: int, h: int, title: str | None = None, subtitle: str | None = None) -> None:
    c.rect(x, y, w, h, fill=C["white"], radius=16, outline=C["line"], shadow=True)
    if title:
        c.text(x + 20, y + 18, title, size=17, bold=True, color=C["ink"])
    if subtitle:
        c.text(x + 20, y + 44, subtitle, size=13, color=C["muted"], max_width=w - 40)


def avatar(c: Canvas, x: int, y: int, r: int, initials: str, fill: str | None = None) -> None:
    c.circle(x, y, r, fill=fill or C["primary"])
    c.text(x, y, initials, size=max(11, int(r * 0.72)), bold=True, color=C["white"], anchor="mm")


def button(c: Canvas, x: int, y: int, w: int, h: int, label: str, primary: bool = True, danger: bool = False) -> None:
    fill = C["danger"] if danger else (C["primary"] if primary else C["gray_100"])
    color = C["white"] if primary or danger else C["gray_700"]
    c.rect(x, y, w, h, fill=fill, radius=h // 2)
    c.text(x + w / 2, y + h / 2, label, size=max(11, int(h * 0.38)), bold=True, color=color, anchor="mm")


def input_field(c: Canvas, x: int, y: int, w: int, label: str, value: str, h: int = 52) -> None:
    c.text(x, y, label, size=13, bold=True, color=C["gray_700"])
    c.rect(x, y + 22, w, h, fill=C["white"], radius=10, outline=C["line"], width=2)
    c.text(x + 14, y + 22 + h / 2, value or "—", size=14, color=C["ink"] if value else C["gray_400"], anchor="lm")


def badge(c: Canvas, x: int, y: int, label: str, tone: str = "primary") -> None:
    fills = {"primary": C["primary_soft"], "success": C["success_soft"], "warn": C["warn_soft"], "danger": C["danger_soft"]}
    colors = {"primary": C["primary"], "success": C["success"], "warn": C["warn"], "danger": C["danger"]}
    f = _font(11, True)
    w = int(f.getlength(label)) + 16
    c.rect(x, y, w, 22, fill=fills.get(tone, C["primary_soft"]), radius=11)
    c.text(x + w / 2, y + 11, label, size=11, bold=True, color=colors.get(tone, C["primary"]), anchor="mm")


def auth_frame(c: Canvas, width: int, height: int, heading: str, subheading: str, device: str = "desktop") -> dict:
    c.rect(0, 0, width, height, fill=C["bg"])
    if device == "mobile":
        c.rect(0, 0, width, height // 3, fill=C["navy"])
        c.circle(width / 2, 64, 30, fill=C["primary"])
        c.text(width / 2, 64, "SC", size=20, bold=True, color=C["white"], anchor="mm")
        c.text(width / 2, 116, "SocialConnect", size=25, bold=True, color=C["white"], anchor="mm")
        c.text(width / 2, 148, "Connect with people who matter.", size=13, color="#CBD5E1", anchor="mm")
        form_y = height // 3 + 28
        fx, fw = 24, width - 48
    else:
        c.rect(0, 0, width // 2 - 40, height, fill=C["navy"])
        c.circle(96, 96, 34, fill=C["primary"])
        c.text(96, 96, "SC", size=22, bold=True, color=C["white"], anchor="mm")
        c.text(96, 178, "SocialConnect", size=42, bold=True, color=C["white"])
        c.text(96, 238, "A calm, modern space to share, chat,\nand stay close to your circle.", size=20, color="#CBD5E1")
        for i, t in enumerate(["Share what matters", "Real-time conversations", "Stories that fade"]):
            c.circle(104, 344 + i * 54, 10, fill=C["primary"])
            c.text(130, 330 + i * 54, t, size=17, color=C["white"])
        fx, fw = int(width * 0.58), int(width * 0.36)
        form_y = int(height * 0.22)
    c.rect(fx, form_y - 40, fw, height - form_y - 40, fill=C["white"], radius=20, outline=C["line"], shadow=True)
    c.text(fx + 28, form_y - 4, heading, size=28, bold=True, color=C["navy"])
    c.text(fx + 28, form_y + 38, subheading, size=14, color=C["muted"], max_width=fw - 56)
    return dict(x=fx + 28, y=form_y + 78, w=fw - 56)


# ---------- wireframe helpers ----------

def wf_box(c: Canvas, x: int, y: int, w: int, h: int, label: str, dashed: bool = False) -> None:
    c.rect(x, y, w, h, fill=C["gray_50"], outline=C["gray_400"], radius=4, width=2)
    if label:
        c.text(x + 8, y + 8, label, size=13, bold=True, color=C["gray_600"], max_width=w - 16)
    if dashed:
        c.line([(x + 8, y + h - 12), (x + w - 8, y + h - 12)], fill=C["gray_300"], width=2, dash=(8, 6))


def wireframe_shell(c: Canvas, width: int, height: int, title: str, device: str = "desktop", proposed: bool = False) -> dict:
    c.rect(0, 0, width, height, fill=C["white"])
    if device == "mobile":
        wf_box(c, 0, 0, width, 64, "HEADER / LOGO / SEARCH")
        content = dict(x=16, y=82, w=width - 32, h=height - 164)
        wf_box(c, 0, height - 74, width, 74, "BOTTOM NAV")
    else:
        wf_box(c, 0, 0, width, 72, "HEADER + SEARCH + PROFILE")
        wf_box(c, 20, 92, 220, height - 112, "LEFT NAV")
        wf_box(c, width - 300, 92, 280, height - 112, "RIGHT RAIL")
        content = dict(x=260, y=92, w=width - 600, h=height - 112)
    if proposed:
        wf_box(c, content["x"], content["y"], content["w"], 42, "PROPOSED SCREEN LABEL")
        content["y"] += 54
        content["h"] -= 54
    c.text(width - 20, height - 18, title, size=12, color=C["gray_500"], anchor="rb")
    return content


# ---------- editable HTML/CSS source ----------

BASE_CSS = """
:root{--bg:#F5F7FB;--card:#fff;--ink:#172033;--muted:#64748B;--line:#DCE3EE;--primary:#2563EB;--primary-soft:#E8F0FE;--accent:#7C3AED;--success:#16A34A;--warn:#D97706;--danger:#DC2626;--navy:#0F172A}
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--ink)}
.shell{min-height:100vh}.topbar{height:76px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 32px;gap:20px}
.brand{width:38px;height:38px;border-radius:50%;background:var(--primary);color:#fff;display:grid;place-items:center;font-weight:700}
.grid{display:grid;grid-template-columns:228px minmax(0,1fr) 308px;gap:22px;padding:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 8px 24px rgba(15,23,42,.06)}
.btn{background:var(--primary);color:#fff;border:0;border-radius:999px;padding:10px 20px;font-weight:600}
.input{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:#fff}
.badge{display:inline-block;background:var(--primary-soft);color:var(--primary);border-radius:999px;padding:4px 10px;font-size:12px;font-weight:600}
.proposed{background:#FFF3DF;border:1px solid var(--warn);color:#92400E;border-radius:10px;padding:10px 14px;font-weight:700;margin-bottom:16px}
@media(max-width:760px){.grid{grid-template-columns:1fr;padding:14px}.topbar{padding:0 16px}.card{padding:16px}}
"""


def write_html_source(stem: Path | str, title: str, description: str, body: str, image_file: str | None = None) -> Path:
    stem = Path(stem)
    img = ""
    if image_file:
        img = f'<figure><img src="../{Path(image_file).parent.name}/{Path(image_file).name}" alt="{html.escape(title)}"/><figcaption>Rendered reference image</figcaption></figure>'
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)} — SocialConnect visual source</title>
<style>{BASE_CSS}
figure{{margin:24px 0}}figure img{{max-width:100%;border:1px solid var(--line);border-radius:12px}}figcaption{{color:var(--muted);font-size:12px;margin-top:6px}}
</style>
</head>
<body>
<div class="shell">
  <header class="topbar"><div class="brand">SC</div><strong>SocialConnect</strong><span class="badge">{html.escape(title)}</span></header>
  <main class="grid">
    <section class="card" style="grid-column:1/-1">
      <h1>{html.escape(title)}</h1>
      <p style="color:var(--muted)">{html.escape(description)}</p>
      {body}
    </section>
  </main>
  {img}
</div>
</body>
</html>
"""
    return write_text(stem.with_suffix(".html"), doc)
