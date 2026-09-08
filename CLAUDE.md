# CLAUDE.md — Loader

This repo operates under a three-tier instruction architecture. **Read all three, in order, before any work.**

1. `docs/global.md` — universal operating protocol (Tier 1)
2. `docs/project.md` — BSN-specific constraints and domain rules (Tier 2)
3. `docs/session.md` — current state, task queue, blockers (Tier 3)

If any tier file is missing, state which one and halt.

Precedence: `docs/global.md` → `[CONFLICT_RESOLUTION]`.

## Quick orientation

Project: a historical archive of Puerto Rico's Baloncesto Superior Nacional (BSN), 1930–present.
The interface exists (`app/bsn_archivo.html`). The database behind it is thin.
Everything in this repo is about **filling the data**, not building UI.

Top priority: `docs/specs/wayback_ingest_spec.md`.

## Commands

```bash
make setup      # venv + deps
make enumerate  # Phase 1: CDX enumeration of archived bsnpr.com stats pages
make fetch      # Phase 2: pull snapshots into data/raw/
make parse      # Phase 3: parse raw HTML into data/interim/
make verify     # run integrity checks against data/clean/
```
