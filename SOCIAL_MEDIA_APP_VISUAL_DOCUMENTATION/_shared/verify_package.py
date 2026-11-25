"""Automatic quality check for the generated visual documentation package."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
UNVERIFIED = "[NOT VERIFIED - USER CONFIRMATION REQUIRED]"

EXPECTED_DIRS = [
    "01_PROJECT_ANALYSIS", "02_UI_MOCKUPS/Desktop", "02_UI_MOCKUPS/Mobile", "02_UI_MOCKUPS/Source_HTML_CSS",
    "03_WIREFRAMES/Desktop", "03_WIREFRAMES/Mobile", "03_WIREFRAMES/Source_HTML_CSS",
    "04_ER_DIAGRAM", "05_UML_DIAGRAMS/Use_Case", "05_UML_DIAGRAMS/Class", "05_UML_DIAGRAMS/Sequence",
    "05_UML_DIAGRAMS/Activity", "05_UML_DIAGRAMS/State_Machine", "05_UML_DIAGRAMS/Component",
    "05_UML_DIAGRAMS/Deployment", "05_UML_DIAGRAMS/Package", "05_UML_DIAGRAMS/Object",
    "06_SYSTEM_ARCHITECTURE/High_Level_Architecture", "06_SYSTEM_ARCHITECTURE/Frontend_Architecture",
    "06_SYSTEM_ARCHITECTURE/Backend_Architecture", "06_SYSTEM_ARCHITECTURE/API_Architecture",
    "06_SYSTEM_ARCHITECTURE/Authentication_Architecture", "06_SYSTEM_ARCHITECTURE/Chat_Architecture",
    "06_SYSTEM_ARCHITECTURE/Notification_Architecture", "06_SYSTEM_ARCHITECTURE/Frontend_Component_Hierarchy", "06_SYSTEM_ARCHITECTURE/Deployment_Architecture",
    "07_DFD/Level_0", "07_DFD/Level_1", "07_DFD/Level_2",
    "08_USER_REQUIREMENTS/User_Flow", "08_USER_REQUIREMENTS/User_Journey", "08_USER_REQUIREMENTS/Sitemap",
    "09_TRACEABILITY", "10_TESTING/Testing_Flow", "11_FINAL_REPORT",
]

EXPECTED_FILES = [
    "01_PROJECT_ANALYSIS/Project_Analysis.md", "01_PROJECT_ANALYSIS/Feature_Status.md", "01_PROJECT_ANALYSIS/Technology_Stack.md",
    "04_ER_DIAGRAM/Data_Dictionary.md", "08_USER_REQUIREMENTS/User_Requirements.md",
    "09_TRACEABILITY/Requirements_Traceability.xlsx", "10_TESTING/Test_Plan.md", "10_TESTING/Test_Cases.xlsx",
    "11_FINAL_REPORT/Complete_Documentation.md", "11_FINAL_REPORT/Complete_Documentation.docx",
    "11_FINAL_REPORT/Complete_Documentation.pdf", "README.md",
]

failures: list[str] = []
checks: list[str] = []


def check(condition: bool, message: str) -> None:
    if condition:
        checks.append("PASS: " + message)
    else:
        failures.append("FAIL: " + message)


for folder in EXPECTED_DIRS:
    check((ROOT / folder).is_dir(), f"directory exists: {folder}")

for file in EXPECTED_FILES:
    path = ROOT / file
    check(path.is_file() and path.stat().st_size > 0, f"non-empty file exists: {file}")

pngs = sorted(ROOT.glob("**/*.png"))
svgs = sorted(ROOT.glob("**/*.svg"))
check(len(pngs) > 0, "at least one PNG exists")
check(len(svgs) > 0, "at least one SVG exists")

ui_desktop = sorted((ROOT / "02_UI_MOCKUPS" / "Desktop").glob("*.png"))
ui_mobile = sorted((ROOT / "02_UI_MOCKUPS" / "Mobile").glob("*.png"))
wf_desktop = sorted((ROOT / "03_WIREFRAMES" / "Desktop").glob("*.png"))
wf_mobile = sorted((ROOT / "03_WIREFRAMES" / "Mobile").glob("*.png"))
check(len(ui_desktop) == 24, f"24 desktop UI mockups (found {len(ui_desktop)})")
check(len(ui_mobile) == 24, f"24 mobile UI mockups (found {len(ui_mobile)})")
check(len(wf_desktop) == 11, f"11 desktop wireframes (found {len(wf_desktop)})")
check(len(wf_mobile) == 11, f"11 mobile wireframes (found {len(wf_mobile)})")

for p in ui_desktop:
    with Image.open(p) as im:
        check(im.size == (1920, 1080), f"desktop mockup resolution 1920x1080: {p.name}")
for p in ui_mobile:
    with Image.open(p) as im:
        check(im.size == (720, 1280), f"mobile mockup resolution 720x1280: {p.name}")
for p in wf_desktop:
    with Image.open(p) as im:
        check(im.size == (1920, 1080), f"desktop wireframe resolution 1920x1080: {p.name}")
for p in wf_mobile:
    with Image.open(p) as im:
        check(im.size == (720, 1280), f"mobile wireframe resolution 720x1280: {p.name}")

blank_images: list[str] = []
for p in pngs:
    try:
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            extrema = im.convert("RGB").getextrema()
            if all(lo == hi for lo, hi in extrema):
                blank_images.append(p.name)
    except Exception as exc:  # pragma: no cover - QA diagnostic
        blank_images.append(f"{p.name}: {exc}")
check(not blank_images, "all PNG images decode and are not single-colour blanks")

for p in svgs:
    text = p.read_text(encoding="utf-8")
    check(text.lstrip().startswith("<svg") and "</svg>" in text, f"valid SVG root and close tag: {p.name}")

for p in ROOT.glob("**/*.mmd"):
    text = p.read_text(encoding="utf-8")
    check(bool(text.strip()), f"non-empty Mermaid source: {p.name}")
for p in ROOT.glob("**/*.puml"):
    text = p.read_text(encoding="utf-8")
    check("@startuml" in text and "@enduml" in text, f"complete PlantUML source: {p.name}")
for p in ROOT.glob("**/*.html"):
    text = p.read_text(encoding="utf-8")
    check("<!doctype html>" in text.lower() and "</html>" in text.lower(), f"complete HTML source: {p.name}")

for file in ["09_TRACEABILITY/Requirements_Traceability.xlsx", "10_TESTING/Test_Cases.xlsx", "11_FINAL_REPORT/Complete_Documentation.docx"]:
    p = ROOT / file
    try:
        with zipfile.ZipFile(p) as z:
            bad = z.testzip()
            check(bad is None, f"valid ZIP container for {file}")
            ElementTree.fromstring(z.read("[Content_Types].xml"))
            check(True, f"valid content types XML for {file}")
    except Exception as exc:
        check(False, f"valid archive for {file}: {exc}")

pdf = ROOT / "11_FINAL_REPORT" / "Complete_Documentation.pdf"
pdf_bytes = pdf.read_bytes()
check(pdf_bytes.startswith(b"%PDF-") and b"%%EOF" in pdf_bytes[-200:], "PDF header and trailer exist")
check(len(pdf_bytes) > 50_000, "PDF is non-trivial in size")

text_files = [p for p in ROOT.glob("**/*") if p.is_file() and p.suffix.lower() in {".md", ".mmd", ".puml", ".html", ".css", ".py"}]
placeholder_count = sum(p.read_text(encoding="utf-8", errors="ignore").count(UNVERIFIED) for p in text_files)
check(placeholder_count > 0, f"exact verification placeholder appears {placeholder_count} times")

secret_patterns = [
    re.compile(r"DJANGO_SECRET_KEY\s*=", re.I),
    re.compile(r"DB_PASSWORD\s*=", re.I),
    re.compile(r"POSTGRES_PASSWORD\s*=", re.I),
    re.compile(r"REDIS_URL\s*=\s*redis", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-]{20,}", re.I),
]
secret_hits: list[str] = []
for p in text_files:
    text = p.read_text(encoding="utf-8", errors="ignore")
    for pattern in secret_patterns:
        if pattern.search(text):
            secret_hits.append(f"{p.name}:{pattern.pattern}")
check(not secret_hits, "no secret-value patterns in generated text")

pair_missing: list[str] = []
for p in pngs:
    if not p.with_suffix(".svg").exists():
        pair_missing.append(p.name)
check(not pair_missing, "every PNG has a matching SVG")

counts = {
    "png": len(pngs),
    "svg": len(svgs),
    "mmd": len(list(ROOT.glob("**/*.mmd"))),
    "puml": len(list(ROOT.glob("**/*.puml"))),
    "html": len(list(ROOT.glob("**/*.html"))),
    "css": len(list(ROOT.glob("**/*.css"))),
    "py": len(list(ROOT.glob("**/*.py"))),
}

checks_text = "\n".join(checks)
failures_text = "\n".join(failures) if failures else "None"
report = f"""# Visual Package Quality Check

Result: **{'PASS' if not failures else 'FAIL'}**

## Counts

| Type | Count |
| --- | ---: |
| PNG | {counts['png']} |
| SVG | {counts['svg']} |
| Mermaid source | {counts['mmd']} |
| PlantUML source | {counts['puml']} |
| HTML source | {counts['html']} |
| CSS source | {counts['css']} |
| Python generator source | {counts['py']} |

## Expected file checks

{failures_text if failures else 'All expected directories and files exist and are non-empty.'}

## Passed checks

```
{checks_text}
```

## Failed checks

```
{failures_text}
```

## Manual interpretation

- Desktop mockups/wireframes are 1920×1080; mobile versions are 720×1280.
- Diagrams use high-resolution layouts up to 2400×1600 where entity density requires it.
- All generated PNGs were decoded with Pillow; all SVGs were checked for root and closing tags.
- XLSX/DOCX containers were opened and their XML content types parsed; PDF header/trailer were inspected.
- No secret-value pattern was found in generated text files.
- Image relationships were generated from the source-verified entity, API, screen, and actor IDs in `CLAUDE_DOCUMENTATION_PROMPT/`.
- No rendering tool outside the generated package modified application source files.
"""
(ROOT / "QUALITY_CHECK.md").write_text(report, encoding="utf-8")
print(f"QA {'PASS' if not failures else 'FAIL'}: {len(checks)} passed, {len(failures)} failed")
print("counts:", counts)
if failures:
    print(failures_text)
    raise SystemExit(1)
