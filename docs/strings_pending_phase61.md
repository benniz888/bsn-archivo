# Strings pending owner approval: PHASE_61_SHELL

New or changed public Spanish strings. Proposed text only; not final until approved.

| Where | Proposed text | Kind | Notes |
|---|---|---|---|
| Header search icon (phone, collapsed) | `Buscar en el archivo` | aria-label | Reuses the existing field's own wording. |
| Header search icon (phone, expanded) | `Cerrar búsqueda` | aria-label | New. |
| Header sign-in slot (hidden) | `Iniciar sesión` | link text | Not shown anywhere. Reserved for PHASE_70; accounts are deferred. |

Unchanged, moved only (listed so nothing is missed):
- Search placeholder `Prueba: cuándo murió Piculín · 1971 · títulos de Bayamón` (and the shorter phone form) and its aria-label. The field moved from Inicio into the header. The Piculín example is PHASE_64's removal item and was left as is.
- Header wordmark `BSN ARCHIVO` and `1930 — 2026`. The wordmark is hidden visually on phones (kept for screen readers).
- Mark button aria-label `Ir a Inicio`.

## Design notes (owner decision)
- Focus ring and selected/active outline now use site blue (`--azul-hi`). Previously orange (`--fuego`). Orange stays for live/data accents only. Contrast checked against the tightest ground (court cell): 3.8:1 dark, 7:1 light.
- Link colour decision from 02_brand_and_logo_spec.md: no change made in this phase. Links keep their current colour; decide in PHASE_64+.
- Sub-navigation pills raised to a 44px minimum height (was ~34px) while the edge fade was added. This makes pill rows slightly taller on every section page.
- On widths >= 860px the header now shows (brand + search); its theme, settings and club buttons are hidden there because the left rail already has theme and club controls. The rail no longer has its own logo. On widths < 360px the settings button is hidden to keep the row from overflowing.
