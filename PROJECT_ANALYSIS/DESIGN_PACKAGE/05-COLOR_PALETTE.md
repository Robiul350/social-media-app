# 05 — Color Palette

## Scope

This palette extends the colours already observed in `frontend/src/index.css`. It defines semantic roles for light and dark themes so the proposed redesign can stay premium, consistent, and accessible.

**Existing implemented UI** values are factual source observations. **Proposed** values are recommendations for normalisation and dark-mode expansion.

---

## Existing brand colours

| Role | Hex | Current usage |
| --- | --- | --- |
| Navy | `#172554` | Deep brand accent / dark identity tone. |
| Primary blue | `#2563EB` | Primary actions, focus, links. |
| Primary hover | `#1D4ED8` | Hover/dark primary variant. |
| Violet | `#8B5CF6` | Secondary accent and gradient partner. |
| Teal | `#0D9488` | Success/presence/positive accent. |
| Amber | `#F59E0B` | Warning, highlights, some notification types. |
| App background | `#F8FAFC` | Light canvas. |
| Surface | `#FFFFFF` | Cards, dialogs, navbar. |
| Border | `#E2E8F0` | Card/input dividers. |
| Text primary | `#0F172A` | Headings and high-emphasis text. |
| Text body | `#334155` | Body copy. |
| Text muted | `#64748B` | Metadata, captions, labels. |
| Primary soft | `#EFF6FF` | Blue tinted surfaces. |
| Dark meta colour | `#18191A` | Current theme-color meta dark value. |

### Existing gradients

```css
/* Observed identity gradient */
linear-gradient(135deg, #2563EB, #8B5CF6);

/* Proposed cool surface lift */
linear-gradient(135deg, rgba(37, 99, 235, .08), rgba(13, 148, 136, .06));

/* Proposed premium auth/admin panel */
linear-gradient(145deg, #172554 0%, #2563EB 48%, #8B5CF6 100%);
```

Use gradients for brand panels, KPI accents, and decorative media placeholders. Do not use gradients for body text, dense tables, or small controls.

---

## Proposed semantic palette — light theme

| Token | Hex | Purpose |
| --- | --- | --- |
| `--sc-color-app` | `#F8FAFC` | Page canvas. |
| `--sc-color-surface` | `#FFFFFF` | Cards, panels, inputs. |
| `--sc-color-surface-muted` | `#F1F5F9` | Subtle rows, disabled surfaces, code-like blocks. |
| `--sc-color-surface-raised` | `#FFFFFF` | Dropdowns, dialogs, popovers. |
| `--sc-color-border` | `#E2E8F0` | Default borders. |
| `--sc-color-border-strong` | `#CBD5E1` | Input hover and emphasis borders. |
| `--sc-color-text` | `#0F172A` | Headings. |
| `--sc-color-text-body` | `#334155` | Primary body copy. |
| `--sc-color-text-muted` | `#64748B` | Metadata and secondary copy. |
| `--sc-color-text-on-accent` | `#FFFFFF` | Text on blue/violet/teal filled surfaces. |
| `--sc-color-primary` | `#2563EB` | Primary actions, active nav, links. |
| `--sc-color-primary-hover` | `#1D4ED8` | Hover/pressed primary. |
| `--sc-color-primary-soft` | `#EFF6FF` | Selected rows, unread surfaces. |
| `--sc-color-primary-contrast` | `#1E3A8A` | Text on soft blue surfaces. |
| `--sc-color-violet` | `#8B5CF6` | Secondary accent. |
| `--sc-color-violet-soft` | `#F5F3FF` | Secondary accent tint. |
| `--sc-color-teal` | `#0D9488` | Success, online, positive trend. |
| `--sc-color-teal-soft` | `#F0FDFA` | Success tint. |
| `--sc-color-amber` | `#F59E0B` | Warning, pending, highlight. |
| `--sc-color-amber-soft` | `#FFFBEB` | Warning tint. |
| `--sc-color-danger` | `#DC2626` | Destructive actions, errors. |
| `--sc-color-danger-hover` | `#B91C1C` | Danger hover / error text. |
| `--sc-color-danger-soft` | `#FEF2F2` | Error surface. |
| `--sc-color-scrim` | `rgba(2, 6, 23, .72)` | Dialog backdrop. |

---

## Proposed semantic palette — dark theme

Dark mode overrides semantic roles only. Component classes remain unchanged.

| Token | Proposed value | Notes |
| --- | --- | --- |
| `--sc-color-app` | `#0B1120` | Deep slate canvas; replaces reliance on `#18191A` meta alone. |
| `--sc-color-surface` | `#111827` | Standard dark card. |
| `--sc-color-surface-muted` | `#1E293B` | Rows, chips, disabled surfaces. |
| `--sc-color-surface-raised` | `#172033` | Dialogs and popovers. |
| `--sc-color-border` | `#334155` | Default dark border. |
| `--sc-color-border-strong` | `#475569` | Hover/emphasis border. |
| `--sc-color-text` | `#F8FAFC` | High-emphasis text. |
| `--sc-color-text-body` | `#E2E8F0` | Body copy. |
| `--sc-color-text-muted` | `#94A3B8` | Metadata. |
| `--sc-color-primary` | `#60A5FA` | Lighter blue for contrast on dark. |
| `--sc-color-primary-hover` | `#93C5FD` | Hover/focus. |
| `--sc-color-primary-soft` | `rgba(37, 99, 235, .18)` | Selected/unread surface. |
| `--sc-color-primary-contrast` | `#DBEAFE` | Text on soft blue. |
| `--sc-color-violet` | `#A78BFA` | Secondary accent. |
| `--sc-color-violet-soft` | `rgba(139, 92, 246, .18)` | Accent tint. |
| `--sc-color-teal` | `#2DD4BF` | Success/online. |
| `--sc-color-teal-soft` | `rgba(13, 148, 136, .18)` | Success tint. |
| `--sc-color-amber` | `#FBBF24` | Warning. |
| `--sc-color-amber-soft` | `rgba(245, 158, 11, .16)` | Warning tint. |
| `--sc-color-danger` | `#F87171` | Error/destructive. |
| `--sc-color-danger-hover` | `#FCA5A5` | Hover. |
| `--sc-color-danger-soft` | `rgba(220, 38, 38, .18)` | Error surface. |
| `--sc-color-scrim` | `rgba(0, 0, 0, .78)` | Backdrop. |

---

## State colour mapping

| State | Light | Dark | Non-colour signal |
| --- | --- | --- | --- |
| Primary action | Blue | Light blue | Label + button shape. |
| Success / online | Teal | Bright teal | Check icon, dot + text `Online`. |
| Warning / pending | Amber | Amber | Clock/warning icon, `Pending` label. |
| Error / danger | Red | Light red | Alert icon, `role="alert"`, text prefix. |
| Unread | Soft blue + left accent | Soft blue + left accent | Bold text and `Unread` label where useful. |
| Selected nav | Soft blue + left bar | Soft blue + left bar | `aria-current="page"`. |
| Muted/disabled | Slate | Slate | Disabled attribute and cursor. |
| Verified | Blue | Light blue | Badge icon and tooltip. |

---

## Type colour usage

| Text token | Use | Avoid |
| --- | --- | --- |
| Text primary | Headings, post body, key values. | Long metadata blocks. |
| Text body | Paragraphs, comments, form help. | Placeholder text. |
| Text muted | Timestamps, captions, labels, navigation disabled states. | Essential instructions. |
| Text on accent | Button labels, selected chips, KPI accents. | Body paragraphs. |
| Danger text | Error messages only. | General secondary copy. |

Contrast rules:

- Body text target ≥4.5:1 against its background.
- Large text (≥24 px or ≥19 px bold) target ≥3:1.
- UI borders and focus indicators target ≥3:1 where they convey state.
- Do not put muted text on tinted surfaces without rechecking contrast.

---

## Surface and shadow usage

| Surface token | Use |
| --- | --- |
| App | Page background, canvas behind cards. |
| Surface | Cards, forms, feed items. |
| Surface muted | Hover rows, skeleton base, inactive chips. |
| Surface raised | Dialogs, dropdowns, popovers, toasts. |

Shadows use slate at low opacity. Avoid pure black shadows; they muddy the premium appearance. In dark mode, reduce shadow opacity and rely more on borders and elevation surfaces.

---

## Accessibility guidance

1. Never encode status only in colour; pair with icon, label, or shape.
2. Check contrast in both themes for every new token pairing.
3. Keep focus ring colour distinct from the adjacent surface.
4. Avoid saturated full-area backgrounds behind long text.
5. Use tinted soft surfaces for information, not large solid colour blocks.
6. Test with common colour-vision simulations, especially teal/green and red/amber distinctions.
7. Respect `prefers-contrast: more` by increasing border strength and removing decorative gradients where necessary.

---

## Implementation note

Current source already defines many light-theme values. The proposed work is to:

- promote raw values into semantic token roles,
- add a coherent dark semantic set,
- align manifest and meta theme colours with the token system,
- remove duplicated CSS theme blocks.

No secret, password, token, or private environment value is included in this palette.
