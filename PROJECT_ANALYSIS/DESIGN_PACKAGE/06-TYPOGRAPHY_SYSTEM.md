# 06 — Typography System

## Existing implemented UI

Current typography is defined in `frontend/src/index.css` and loaded from Google Fonts:

| Role | Family | Fallbacks |
| --- | --- | --- |
| Display | `Plus Jakarta Sans` | `Inter`, system UI. |
| Body | `Inter` | `Segoe UI`, system UI. |
| Weights loaded | 400, 500, 600, 700, 800 | — |

The active UI uses strong hierarchy: uppercase section eyebrows, bold headings, medium-weight body copy, and small muted metadata.

## Proposed type principles

1. Use display type for headings and product surfaces; body type for reading.
2. Keep line lengths comfortable: 60–75 characters for long text.
3. Maintain a 4 px vertical rhythm where possible.
4. Use weight and spacing before shrinking font size on mobile.
5. Never communicate state by type weight alone.

---

## Type scale

| Token | Size / line height | Weight | Tracking | Use |
| --- | --- | --- | --- | --- |
| `--sc-font-display` | 40 / 48 px | 800 | -0.03em | Auth hero, marketing panel, large admin title. |
| `--sc-font-h1` | 32 / 40 px | 700 | -0.025em | Page titles, dashboard heading. |
| `--sc-font-h2` | 24 / 32 px | 700 | -0.02em | Section headings, dialog titles. |
| `--sc-font-h3` | 20 / 28 px | 600 | -0.015em | Card titles, profile name. |
| `--sc-font-h4` | 18 / 26 px | 600 | -0.01em | Subsection headings. |
| `--sc-font-body-lg` | 16 / 24 px | 400 | 0 | Long-form post text, intro copy. |
| `--sc-font-body` | 15 / 22 px | 400 | 0 | Default body, comments, list descriptions. |
| `--sc-font-small` | 14 / 20 px | 500 | 0 | Buttons, labels, secondary actions. |
| `--sc-font-caption` | 12 / 16 px | 400 | 0.01em | Timestamps, metadata, helper text. |
| `--sc-font-overline` | 11 / 16 px | 700 | 0.08em | Uppercase section labels. |
| `--sc-font-button` | 14 / 20 px | 600 | 0.005em | All buttons and segmented controls. |
| `--sc-font-numeric` | 28 / 32 px | 700 | -0.02em | Admin KPI values. |

---

## Responsive type

| Token | Desktop | Tablet | Mobile |
| --- | --- | --- | --- |
| Display | 40 / 48 | 34 / 42 | 28 / 36 |
| H1 | 32 / 40 | 28 / 36 | 24 / 32 |
| H2 | 24 / 32 | 22 / 30 | 20 / 28 |
| H3 | 20 / 28 | 19 / 27 | 18 / 26 |
| Body large | 16 / 24 | 16 / 24 | 15 / 22 |
| Body | 15 / 22 | 15 / 22 | 14 / 21 |
| Caption | 12 / 16 | 12 / 16 | 11 / 16 |

Recommended CSS approach:

```css
:root {
  --sc-font-display: 800 40px/48px "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
  --sc-font-h1: 700 32px/40px "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
  --sc-font-body: 400 15px/22px "Inter", "Segoe UI", system-ui, sans-serif;
  --sc-font-small: 500 14px/20px "Inter", "Segoe UI", system-ui, sans-serif;
  --sc-font-caption: 400 12px/16px "Inter", "Segoe UI", system-ui, sans-serif;
  --sc-font-overline: 700 11px/16px "Inter", "Segoe UI", system-ui, sans-serif;
  --sc-font-button: 600 14px/20px "Inter", "Segoe UI", system-ui, sans-serif;
}

@media (max-width: 760px) {
  :root {
    --sc-font-display: 800 28px/36px "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
    --sc-font-h1: 700 24px/32px "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
    --sc-font-body: 400 14px/21px "Inter", "Segoe UI", system-ui, sans-serif;
  }
}
```

This is a design specification only; no source file is changed.

---

## Usage by surface

| Surface | Typography pattern |
| --- | --- |
| Auth split panel | Display heading on brand side; H1 on form side; body 15 px. |
| Home dashboard | H1 page title; overline `HOME`; body post text 16 px. |
| Post card | H3 author name; caption time/audience; body-lg content; small action labels. |
| Comments | Small 14 px body; caption metadata; reply indentation 24 px. |
| Profile | H2/H3 identity; caption metadata; numeric stats 20 px semibold. |
| Stories | Caption 15 px on media; overline time; accessible label on controls. |
| Messages | Small 14 px bubbles; caption timestamps; overline date separators. |
| Notifications | Small 14 px title; caption timestamp; body preview 14 px. |
| Admin | H1 page title; H2 section titles; numeric KPI value; caption labels/trends. |
| Dialogs | H2 title; body 15 px; button label 14 px semibold. |

---

## Hierarchy rules

1. One H1 per page; do not use H1 for card titles.
2. Section eyebrows sit 8 px above their heading.
3. Card title and body are separated by 8 px.
4. Metadata lines use caption size and muted colour.
5. Primary buttons use button token; never body size with bold weight.
6. Avoid more than three font weights in a single viewport.
7. Truncate long names with ellipsis rather than shrinking type below caption size.

---

## Alignment and reading comfort

| Context | Rule |
| --- | --- |
| Post content | Left aligned, 16 px font, 24 px line height. |
| Comments | Left aligned; max 65% width on desktop where practical. |
| Chat bubbles | Left/right by sender; max width 65% of chat pane. |
| Admin tables | Numeric values right aligned or tabular numerals. |
| KPI values | Tabular numerals to prevent width jitter during refresh. |
| Form help | Caption size, directly below field with 4–6 px gap. |
| Errors | Small size, danger colour, `role="alert"`. |

---

## Accessibility

- Do not set body text below 14 px on mobile or 15 px on desktop.
- Do not use font-weight 300 for essential text; thin type fails at low contrast and small sizes.
- Preserve user browser zoom to at least 200% without horizontal overflow.
- Use semantic heading levels; visual H3 should not jump from H1 without H2 except in isolated cards.
- Supporting text for icons must be real text, not CSS `::after` content.
- Underline links in body copy when colour alone may not communicate them.
- Ensure button labels are not all-caps paragraphs; overline is for labels, not instructions.

---

## Existing inconsistencies to resolve

| Item | Current observation | Proposed correction |
| --- | --- | --- |
| Legacy CSS | `App.css` contains Vite starter typography. | Remove or mark legacy; use token-based typography. |
| Manifest/meta | Manifest theme colour differs from active theme. | Align with colour/typography tokens and app theme. |
| Duplicate CSS | Repeated responsive/type blocks in `index.css`. | Single source of truth for type scale. |
| Register form | Labels not associated with inputs. | Add explicit label/input IDs and error role. |
| Form errors | Mixed plain paragraphs and role-based alerts. | Standardise on error text component. |

---

## Acceptance criteria

- All screens use tokens rather than one-off font sizes.
- Headings follow a logical semantic order.
- Text remains readable at 200% browser zoom and on 360 px width.
- Dark-theme text contrast meets WCAG AA for body copy.
- No essential instruction is rendered only as placeholder or icon tooltip.
- Type scale is documented in one place and referenced by component specs.
