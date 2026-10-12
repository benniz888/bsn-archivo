# CLAUDE.md — Loader

This repo operates under a three-tier instruction architecture. **Read all three, in order, before any work.**

1. `docs/global.md` — universal operating protocol (Tier 1)
2. `docs/project.md` — BSN-specific constraints and domain rules (Tier 2)
3. `docs/session.md` — current state, task queue, blockers (Tier 3)

If any tier file is missing, state which one and halt.

Precedence: `docs/global.md` → `[CONFLICT_RESOLUTION]`.

## Quick orientation

Project: a historical archive of Puerto Rico's Baloncesto Superior Nacional (BSN), 1930–present.
The interface exists (`web/` — a multi-file static site, `web/index.html` + `web/css/` + `web/js/`;
see `docs/specs/app_split_spec.md` for the file map. `app/bsn_archivo.html` is an archived pointer,
not the app). The database behind it is thin. Everything in this repo is about **filling the
data**, not building UI.

Top priority: `docs/specs/wayback_ingest_spec.md`.

## Commands

```bash
make setup      # venv + deps
make enumerate  # Phase 1: CDX enumeration of archived bsnpr.com stats pages
make fetch      # Phase 2: pull snapshots into data/raw/
make parse      # Phase 3: parse raw HTML into data/interim/
make verify     # run integrity checks against data/clean/
```

## Redesign v3 working rules

- Specs live in docs/specs/redesign_v3/. Read 01_master_plan.md first; it lists the rules every phase obeys.
- One phase per turn. Build phases: do NOT commit, do NOT push. Commits happen only in a separate approved COMMIT ONLY step, staged by explicit path.
- Owner approves every new or changed public Spanish string: list them in docs/strings_pending_<phase>.md.
- Never fabricate data. Contrast >= 4.5:1 text, >= 3:1 graphics, tap targets >= 44px, visible focus, reduced-motion respected, no emoji in the UI.
- Verify layout in Chromium AND WebKit at 390px and 1000px; one phone and one desktop screenshot per page per phase.
- Report <= 12 lines: PHASE / DONE / VERIFIED / NEXT, plus git diff --stat and git status --short.
- Routing: planner = auth/security design review only; builder = phase implementation; chores = mechanical edits. Main session stays on Sonnet, low effort; run /clear between phases.
