"""Generate the consolidated report package and root README with real file counts."""

from __future__ import annotations

import html
import io
import zipfile
from pathlib import Path

from PIL import Image

from vizlib import write_text

ROOT = Path(__file__).resolve().parents[1]
UNVERIFIED = "[NOT VERIFIED - USER CONFIRMATION REQUIRED]"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def count(pattern: str) -> int:
    return len(list(ROOT.glob(pattern)))


def md_escape(value: str) -> str:
    return value.replace("|", "\\|")


def build_markdown() -> str:
    ui_screens = sorted((ROOT / "02_UI_MOCKUPS" / "Desktop").glob("*.png"))
    wf_screens = sorted((ROOT / "03_WIREFRAMES" / "Desktop").glob("*.png"))
    er = sorted((ROOT / "04_ER_DIAGRAM").glob("*.png"))
    uml = sorted((ROOT / "05_UML_DIAGRAMS").glob("**/*.png"))
    arch = sorted((ROOT / "06_SYSTEM_ARCHITECTURE").glob("**/*.png"))
    dfd = sorted((ROOT / "07_DFD").glob("**/*.png"))
    req = sorted((ROOT / "08_USER_REQUIREMENTS").glob("**/*.png"))
    testing = sorted((ROOT / "10_TESTING" / "Testing_Flow").glob("*.png"))

    def table(items: list[Path], heading: str) -> str:
        lines = [f"### {heading} ({len(items)} PNG images)", "", "| Image | SVG | Editable source |", "| --- | --- | --- |"]
        for p in items:
            svg = p.with_suffix(".svg")
            src_candidates = [p.with_suffix(".mmd"), p.with_suffix(".puml"), p.with_suffix(".html")]
            src = next((s for s in src_candidates if s.exists()), None)
            src_cell = f"`{rel(src)}`" if src else "—"
            lines.append(f"| `{rel(p)}` | {'yes' if svg.exists() else 'no'} | {src_cell} |")
        lines.append("")
        return "\n".join(lines)

    parts = [
        "# Complete Software Documentation — Social Media App (working UI/admin name: SocialConnect)",
        "",
        f"Generated visual documentation package. Product-brand finalization is {UNVERIFIED}.",
        "",
        "## 1. Purpose and evidence rule",
        "",
        "This package converts the source-verified evidence in `CLAUDE_DOCUMENTATION_PROMPT/` into university-level project documentation and visual assets. Runtime source is the highest evidence source. Historical reports were used only to locate claims requiring confirmation. No application source file was modified.",
        "",
        "Status vocabulary: Implemented, Partial, Backend only, Planned / documented, Not Found, Needs Verification.",
        "",
        "## 2. Executive summary",
        "",
        "| Area | Verified summary |",
        "| --- | --- |",
        "| Product | React 19.3.1 SPA + Django 6.1/DRF 3.18.0 backend over PostgreSQL; custom admin at `/admin/`. |",
        "| Core implemented flows | Registration/login/JWT refresh/logout; profiles; feed; post CRUD; likes/comments/replies; follows/friends/blocks; stories create/list/view; notifications/preferences; direct chat; custom admin dashboard/analytics/roles/system. |",
        "| Partial or backend-only | Password reset UI, polls, story/comment reactions, group chat, multi-image upload, drafts/scheduling controls, report moderation, hashtag browsing, block-list screen, message edit/delete controls, PWA offline/push/install/update. |",
        "| Verification | `makemigrations --check --dry-run` returned `No changes detected` during the audit. Backend tests, lint, build, and browser smoke results are " + UNVERIFIED + ". |",
        "",
        "## 3. Architecture overview",
        "",
        "The browser reaches the React SPA through Vite in development and the Django REST API at `/api/`. WebSockets use ASGI with `config.asgi:application`; `ws/chat/<user_id>/?token=<access>` and `ws/notifications/?token=<access>` are the verified routes. PostgreSQL is mandatory. Redis is optional locally when `REDIS_URL` is unset and required for multi-process fan-out. Production topology, proxy, TLS, static/media hosting, monitoring, backups, and CI/CD are " + UNVERIFIED + ".",
        "",
        "See `06_SYSTEM_ARCHITECTURE/` for ten focused architecture images.",
        "",
        "## 4. Database design",
        "",
        "Twenty-six source-verified Django tables are documented in `04_ER_DIAGRAM/Data_Dictionary.md`. Relationships are implemented as foreign keys, one-to-one fields, and many-to-many through models. Privacy is enforced through `backend/social/access.py` application queries, not database row-level security. Chat deletion is soft through `Message.deleted_at`. Known schema-level gaps are documented in `DATABASE_ANALYSIS.md`.",
        "",
        table(er, "ER and database visualizations"),
        "",
        "## 5. UML model",
        "",
        "UML deliverables include one use-case diagram, one class diagram, twelve sequence diagrams, ten activity diagrams, and five additional diagrams (state, component, deployment, package, object). All participants, states, events, and components are source-verified; illustrative object values are explicitly labelled sample instances.",
        "",
        table(uml, "UML diagrams"),
        "",
        "## 6. UI/UX design system",
        "",
        "Design tokens use Segoe UI typography, a blue/indigo primary palette, 12–20 px spacing increments, 10–20 px radii, white cards, soft shadows, and responsive three-zone desktop / single-column mobile layouts. Screens not present in the active router are labelled proposed. Mockups are visual proposals only and do not add routes or features to the implementation.",
        "",
        table(ui_screens, "UI mockups (desktop PNG; mobile PNG and SVG saved alongside)"),
        "",
        table(wf_screens, "Wireframes (desktop PNG; mobile PNG and SVG saved alongside)"),
        "",
        "## 7. Data flow diagrams",
        "",
        "DFDs cover context, level 1, and five level 2 processes: authentication, post management, social interaction, chat, and notification. External entities, processes, stores, and flows are restricted to source-verified components.",
        "",
        table(dfd, "DFD diagrams"),
        "",
        "## 8. Requirements and flows",
        "",
        "Thirty-five user requirements (`UR-001`–`UR-035`) and twelve non-functional requirements (`NFR-001`–`NFR-012`) are defined in `08_USER_REQUIREMENTS/User_Requirements.md`. IDs are stable through the diagrams, `09_TRACEABILITY/Requirements_Traceability.xlsx`, and proposed test cases.",
        "",
        table(req, "Requirement/flow diagrams"),
        "",
        "## 9. Testing and traceability",
        "",
        "The traceability workbook maps Requirement → UI Screen → React Component → Django Module → API → Database Model → Proposed Test Case. Current test, lint, build, and browser results remain " + UNVERIFIED + " unless the documented commands are run and their output is recorded.",
        "",
        table(testing, "Testing diagrams"),
        "",
        "## 10. Limitations and unverified items",
        "",
        "- Final product name and version: " + UNVERIFIED + ".",
        "- Production deployment topology and environment values: " + UNVERIFIED + ".",
        "- Email delivery and Redis runtime: " + UNVERIFIED + ".",
        "- Current backend test, frontend lint, and frontend build results: " + UNVERIFIED + ".",
        "- Browser accessibility and responsive smoke testing: " + UNVERIFIED + ".",
        "- Proposed screens for missing routes are not implemented features.",
        "",
        "## 11. Deliverable counts",
        "",
        f"- UI mockups: {len(ui_screens)} screens × 2 layouts = {len(ui_screens) * 2} PNG + {len(ui_screens) * 2} SVG; {count('02_UI_MOCKUPS/Source_HTML_CSS/*.html')} HTML sources + 1 CSS source.",
        f"- Wireframes: {len(wf_screens)} screens × 2 layouts = {len(wf_screens) * 2} PNG + {len(wf_screens) * 2} SVG; {count('03_WIREFRAMES/Source_HTML_CSS/*.html')} HTML sources + 1 CSS source.",
        f"- ER/database diagrams: {len(er)} PNG + {len(er)} SVG + {len(er)} Mermaid + {len(er)} PlantUML sources.",
        f"- UML diagrams: {len(uml)} PNG + {len(uml)} SVG + {count('05_UML_DIAGRAMS/**/*.mmd')} Mermaid + {count('05_UML_DIAGRAMS/**/*.puml')} PlantUML sources.",
        f"- Architecture diagrams: {len(arch)} PNG + {len(arch)} SVG + {count('06_SYSTEM_ARCHITECTURE/**/*.mmd')} Mermaid sources.",
        f"- DFD diagrams: {len(dfd)} PNG + {len(dfd)} SVG + {count('07_DFD/**/*.mmd')} Mermaid sources.",
        f"- Requirement/flow diagrams: {len(req)} PNG + {len(req)} SVG + {count('08_USER_REQUIREMENTS/**/*.mmd')} Mermaid sources.",
        f"- Testing diagrams: {len(testing)} PNG + {len(testing)} SVG + {count('10_TESTING/Testing_Flow/*.mmd')} Mermaid sources.",
        "",
        "## 12. Rendering note",
        "",
        "Mermaid CLI, PlantUML, Graphviz, and browser screenshot tooling were not available in the checked-out environment. Therefore, every image was rendered deterministically with Python/Pillow from the same operation list that produces its SVG. `.mmd` and `.puml` files are provided as editable sources; HTML/CSS sources are provided for mockups and wireframes. No image is a placeholder.",
        "",
    ]
    return "\n".join(parts)


MARKDOWN = build_markdown()
write_text(ROOT / "11_FINAL_REPORT" / "Complete_Documentation.md", MARKDOWN)

# DOCX writer -----------------------------------------------------------------------


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def docx_paragraph(text: str, style: str = "Normal") -> str:
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ""
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'


def markdown_lines(md: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("#### "):
            out.append((line[5:], "Heading4"))
        elif line.startswith("### "):
            out.append((line[4:], "Heading3"))
        elif line.startswith("## "):
            out.append((line[3:], "Heading2"))
        elif line.startswith("# "):
            out.append((line[2:], "Heading1"))
        elif line.startswith("| "):
            out.append((line.replace("\\|", "|"), "Normal")) if len(line) < 500 else None
        elif line.startswith("- "):
            out.append(("• " + line[2:], "Normal"))
        else:
            out.append((line, "Normal"))
    return out


def write_docx(path: Path, md: str) -> None:
    paras = "".join(docx_paragraph(text, style) for text, style in markdown_lines(md))
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
        + paras
        + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
        '</w:body></w:document>'
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="21"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="0F172A"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="1D4ED8"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="172033"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading4"><w:name w:val="heading 4"/><w:rPr><w:b/><w:sz w:val="22"/></w:rPr></w:style>'
        '</w:styles>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '</Types>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '</Relationships>'
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/_rels/document.xml.rels", doc_rels)


write_docx(ROOT / "11_FINAL_REPORT" / "Complete_Documentation.docx", MARKDOWN)

# PDF writer ------------------------------------------------------------------------


def pdf_escape(text: str) -> str:
    text = text.encode("ascii", "replace").decode("ascii")
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap(text: str, width: int) -> list[str]:
    words = text.encode("ascii", "replace").decode("ascii").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines or [""]


class PDF:
    def __init__(self) -> None:
        self.objects: list[bytes] = []
        self.pages: list[int] = []
        self.images: list[tuple[str, int]] = []
        self.font_regular = self._reserve()
        self.font_bold = self._reserve()

    def _reserve(self) -> int:
        self.objects.append(b"")
        return len(self.objects)

    def _jpeg(self, path: Path, max_w: int = 900) -> tuple[bytes, int, int]:
        im = Image.open(path).convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=82)
        return buf.getvalue(), im.width, im.height

    def add_image(self, path: Path) -> str:
        data, w, h = self._jpeg(path)
        num = self._reserve()
        self.objects[num - 1] = (
            f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(data)} >>\nstream\n".encode()
            + data
            + b"\nendstream"
        )
        name = f"/Im{len(self.images) + 1}"
        self.images.append((name, num))
        return name

    def add_page(self, lines: list[str], images: list[str] | None = None) -> None:
        images = images or []
        ops = ["0.06 0.12 0.23 rg", "0 0 612 792 re f"]
        ops.append("1 1 1 rg")
        ops.append("BT /F2 18 Tf 1 0 0 1 42 748 Tm (" + pdf_escape("Social Media App — Visual Documentation") + ") Tj ET")
        ops.append("0.75 0.82 0.92 RG 1 w 42 736 m 570 736 l S")
        y = 714
        for text in lines:
            style = "F2" if text.startswith("HEADING:") else "F1"
            value = text[8:] if text.startswith("HEADING:") else text
            color = "0.96 0.98 1 rg" if style == "F2" else "0.85 0.89 0.95 rg"
            ops.append(color)
            for line in wrap(value, 96 if style == "F1" else 80):
                if y < 70:
                    break
                ops.append(f"BT /{style} {11 if style == 'F1' else 15} Tf 1 0 0 1 42 {y} Tm ({pdf_escape(line)}) Tj ET")
                y -= 15 if style == "F1" else 21
            y -= 4
        if images:
            y -= 10
            max_h = min(300, max(80, y - 60))
            for name in images[:2]:
                iw, ih = 700, int(700 * 9 / 16)
                if ih > max_h:
                    ih = max_h
                    iw = int(ih * 16 / 9)
                ops.append(f"q {iw} 0 0 {ih} 42 {y - ih} cm {name} Do Q")
                y -= ih + 12
        ops.append("0.55 0.62 0.72 rg BT /F1 8 Tf 1 0 0 1 42 28 Tm (" + pdf_escape(RULE) + ") Tj ET")
        content = ("\n".join(ops) + "\n").encode("latin-1", "replace")
        content_num = self._reserve()
        self.objects[content_num - 1] = f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"endstream"
        page_num = self._reserve()
        resources = f"/Font << /F1 {self.font_regular} 0 R /F2 {self.font_bold} 0 R >>"
        if self.images:
            resources += " /XObject << " + " ".join(f"{name} {num} 0 R" for name, num in self.images) + " >>"
        self.objects[page_num - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << {resources} >> /Contents {content_num} 0 R >>"
        ).encode()
        self.pages.append(page_num)

    def save(self, path: Path) -> None:
        self.objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
        kids = " ".join(f"{p} 0 R" for p in self.pages)
        self.objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(self.pages)} >>".encode()
        self.objects[self.font_regular - 1] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
        self.objects[self.font_bold - 1] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for idx, obj in enumerate(self.objects, start=1):
            offsets.append(len(out))
            out += f"{idx} 0 obj\n".encode() + obj + b"\nendobj\n"
        xref = len(out)
        out += f"xref\n0 {len(self.objects) + 1}\n0000000000 65535 f \n".encode()
        for off in offsets[1:]:
            out += f"{off:010d} 00000 n \n".encode()
        out += f"trailer\n<< /Size {len(self.objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bytes(out))


RULE = "Source-verified | Social Media App (working UI/admin name: SocialConnect)"
pdf = PDF()

# Title page
pdf.add_page([
    "HEADING:Complete Software Documentation",
    "Social Media App",
    "Working UI/admin name: SocialConnect",
    "",
    "Visual documentation package generated from current source evidence.",
    "",
    "Includes:",
    "• UI mockups and grayscale wireframes in desktop and mobile layouts",
    "• ER diagrams, data dictionary, UML diagrams, architecture diagrams, DFDs",
    "• Requirements, traceability, test plan, and consolidated report",
    "",
    f"Final brand and version: {UNVERIFIED}",
    f"Current test/lint/build results: {UNVERIFIED}",
])

# Text pages from the markdown, skipping asset inventory tables to keep readable pages
text_lines: list[str] = []
for raw in MARKDOWN.splitlines():
    line = raw.rstrip()
    if not line:
        continue
    if line.startswith("|"):
        continue
    if line.startswith("#"):
        if text_lines:
            pdf.add_page(text_lines)
            text_lines = []
        text_lines.append("HEADING:" + line.lstrip("# "))
    elif line.startswith("```"):
        continue
    else:
        text_lines.append(line)
    if len(text_lines) > 42:
        pdf.add_page(text_lines)
        text_lines = []
if text_lines:
    pdf.add_page(text_lines)

# Selected visual plates
plates = [
    ("ER / Database plate", ROOT / "04_ER_DIAGRAM" / "ER_Diagram.png"),
    ("UML use-case plate", ROOT / "05_UML_DIAGRAMS" / "Use_Case" / "Use_Case_Diagram.png"),
    ("Architecture plate", ROOT / "06_SYSTEM_ARCHITECTURE" / "High_Level_Architecture" / "High_Level_Architecture.png"),
    ("DFD plate", ROOT / "07_DFD" / "Level_0" / "DFD_Level_0.png"),
]
ui_plate = next((ROOT / "02_UI_MOCKUPS" / "Desktop").glob("UI-SCR-004_*.png"), None)
if ui_plate:
    plates.append(("UI mockup plate", ui_plate))
for caption, path in plates:
    if not path.exists():
        continue
    name = pdf.add_image(path)
    pdf.add_page(["HEADING:" + caption, f"File: {rel(path)}", "Rendered from source-verified documentation evidence."], [name])

pdf.save(ROOT / "11_FINAL_REPORT" / "Complete_Documentation.pdf")

# README -----------------------------------------------------------------------------

readme = f"""# Social Media App Visual Documentation Package

Generated output: `SOCIAL_MEDIA_APP_VISUAL_DOCUMENTATION/`

This package contains actual rendered PNG and SVG files plus editable Mermaid, PlantUML, HTML, and CSS sources. It is based on source inspection; no original application file was modified. Unresolved items use `{UNVERIFIED}` verbatim.

## Deliverable counts

| Category | Count |
| --- | ---: |
| UI mockup screens | {len(list((ROOT / '02_UI_MOCKUPS' / 'Desktop').glob('*.png')))} screens × desktop + mobile |
| UI mockup PNG images | {count('02_UI_MOCKUPS/**/*.png')} |
| UI mockup SVG images | {count('02_UI_MOCKUPS/**/*.svg')} |
| UI mockup HTML/CSS sources | {count('02_UI_MOCKUPS/Source_HTML_CSS/*.html') + count('02_UI_MOCKUPS/Source_HTML_CSS/*.css')} |
| Wireframe screens | {len(list((ROOT / '03_WIREFRAMES' / 'Desktop').glob('*.png')))} screens × desktop + mobile |
| Wireframe PNG images | {count('03_WIREFRAMES/**/*.png')} |
| Wireframe SVG images | {count('03_WIREFRAMES/**/*.svg')} |
| Wireframe HTML/CSS sources | {count('03_WIREFRAMES/Source_HTML_CSS/*.html') + count('03_WIREFRAMES/Source_HTML_CSS/*.css')} |
| ER/database diagrams | {count('04_ER_DIAGRAM/*.png')} PNG, {count('04_ER_DIAGRAM/*.svg')} SVG, {count('04_ER_DIAGRAM/*.mmd')} Mermaid, {count('04_ER_DIAGRAM/*.puml')} PlantUML |
| UML diagrams | {count('05_UML_DIAGRAMS/**/*.png')} PNG, {count('05_UML_DIAGRAMS/**/*.svg')} SVG, {count('05_UML_DIAGRAMS/**/*.mmd')} Mermaid, {count('05_UML_DIAGRAMS/**/*.puml')} PlantUML |
| Architecture diagrams | {count('06_SYSTEM_ARCHITECTURE/**/*.png')} PNG, {count('06_SYSTEM_ARCHITECTURE/**/*.svg')} SVG, {count('06_SYSTEM_ARCHITECTURE/**/*.mmd')} Mermaid |
| DFD diagrams | {count('07_DFD/**/*.png')} PNG, {count('07_DFD/**/*.svg')} SVG, {count('07_DFD/**/*.mmd')} Mermaid |
| Requirement/flow diagrams | {count('08_USER_REQUIREMENTS/**/*.png')} PNG, {count('08_USER_REQUIREMENTS/**/*.svg')} SVG, {count('08_USER_REQUIREMENTS/**/*.mmd')} Mermaid |
| Testing diagrams | {count('10_TESTING/Testing_Flow/*.png')} PNG, {count('10_TESTING/Testing_Flow/*.svg')} SVG, {count('10_TESTING/Testing_Flow/*.mmd')} Mermaid |
| Final report formats | Markdown, DOCX, PDF |

## Folder map

- `01_PROJECT_ANALYSIS/` — source-derived project analysis, feature status, technology stack.
- `02_UI_MOCKUPS/` — 24 premium mockups with desktop/mobile PNG+SVG and HTML/CSS sources.
- `03_WIREFRAMES/` — 11 grayscale wireframes with desktop/mobile PNG+SVG and HTML/CSS sources.
- `04_ER_DIAGRAM/` — five database visualizations plus `Data_Dictionary.md`.
- `05_UML_DIAGRAMS/` — use case, class, 12 sequence, 10 activity, state, component, deployment, package, object.
- `06_SYSTEM_ARCHITECTURE/` — ten focused architecture diagrams.
- `07_DFD/` — context, level 1, and five level 2 DFDs.
- `08_USER_REQUIREMENTS/` — UR/NFR documentation and seven flow diagrams.
- `09_TRACEABILITY/` — requirements traceability workbook.
- `10_TESTING/` — test plan, proposed test cases workbook, and four testing diagrams.
- `11_FINAL_REPORT/` — consolidated Markdown, DOCX, and PDF.
- `_shared/` — deterministic generators and rendering library.

## Rendering method

Mermaid CLI, PlantUML, Graphviz, and browser screenshot tools were not installed in the checkout. All images were rendered deterministically with Python/Pillow from a shared operation list, with matching SVG vector output. Mermaid and PlantUML files are provided as editable sources; no image is a placeholder.

## Missing or unverified deliverables

- No browser-based HTML screenshot was produced because no browser/Playwright binary was available; equivalent editable HTML/CSS and rendered PNG/SVG mockups are provided.
- No current backend test, frontend lint, frontend build, or browser smoke-test result is asserted: `{UNVERIFIED}`.
- Production deployment, Redis runtime, email delivery, media authorization, and final branding remain `{UNVERIFIED}`.
- Proposed screens (forgot password, explore, story reaction, settings, user dashboard, report user, dedicated composer) are labelled and are not active routes.
"""
write_text(ROOT / "README.md", readme)

print("generated consolidated Markdown, DOCX, PDF, and README")
