# Redesign v3: master plan

**GOAL (owner, Oct 9): a final, polished build to present to the president of the BSN.** No giveaways for now. Accounts are DEFERRED (see 03): they add a backend and legal exposure and are not needed for the presentation. The "Iniciar sesion" slot stays hidden. Priority is polish, correctness, accuracy of data, speed, and a clean legal/rights posture, because the league will look at crests, names, photos and sources.

Status of the repo as of the Oct 7 summary: `main` @ 8dce212 contains the redesign-v2 merge. Static site (`web/index.html`, `web/css/main.css`, `web/js/*.js`, `web/data/*.json`), GitHub Pages, hash router, PWA with service worker, no backend. Owner works on a Mac, previews in Safari with `python3 -m http.server 8123` in `web/`.

This plan continues the PHASE numbering (last used: PHASE_52B). Redesign v3 = PHASE_60 onward.

## Rules carried into every phase (verbatim in every prompt)
- No deletion outside /tmp without asking. Never `make parse-players`. No writes to `data/clean/`. No force-push. No `git reset` / `clean` / `rebase`.
- Build phases: do NOT commit, do NOT push. Commits are a separate approved step, staged by explicit path only.
- Owner approves every new or changed public Spanish string. Claude Code collects them in `docs/strings_pending_<phase>.md` with proposed text; owner approves the batch at review.
- Never fabricate data. Computed counts are never hardcoded.
- Contrast: text >= 4.5:1, graphics >= 3:1. Tap targets >= 44px. Visible `:focus-visible`.
- Real browsers (Chromium AND WebKit) at 390px and 1000px for any layout work. Screenshots: one phone + one desktop per page per phase (saves quota).
- Report format, max 12 lines: PHASE / DONE / VERIFIED / NEXT, plus `git diff --stat` and `git status --short`.
- Tests baseline (Oct 7): 676 passed, 1 xfailed, 1 known failure (`tests/test_web_text.py` byte test). Inventory baseline 476: read `docs/session.md` for the rule on adding top-level functions before adding any.

## Phase order (one per sitting)
| Phase | Scope | Model / effort | Notes |
|---|---|---|---|
| PHASE_60_AUDIT | Read-only: sync, deploy check, baseline, image/asset/rights inventory, find every item below | Sonnet low | No code changes |
| PHASE_61_SHELL | New logo + icons + manifest, header with search + sign-in slot, mobile tab-indicator bug, highlight color (not orange outline), sticky-header offset | Sonnet low | Icons already generated |
| PHASE_62_CUADRICULA_FIX | Correctness bug: valid answers rejected. Exhaustive test | Sonnet **medium** | Do before any visuals |
| PHASE_63_TABLES | One shared data-table component; apply to Historia, Jugadores, Archivo | Sonnet low | Biggest reuse win |
| PHASE_64_INICIO | Declutter, search top, remove the Piculin item, favorite-team ordering | Sonnet low | |
| PHASE_65_HISTORIA_JUGADORES | KPI reduction, streak text (no emoji), player-page circle overlap, phone landings | Sonnet low | |
| PHASE_66_EQUIPOS | Inviting landing, per-club pages, interactive rosters, hanging retired jerseys (SVG), phone landing | Sonnet low | Club lore needs sources, see 05 |
| PHASE_67A..D_JUEGA | A Cuadricula visuals, B Temporada Perfecta, C Quien Soy, D Sube y Baja restyle | Sonnet low (B and C: medium) | B and C change game logic |
| PHASE_68_ARCHIVO | Visual pass + phone landing | Sonnet low | |
| PHASE_69_LEGAL | Privacy, terms, cookies, accessibility statement, credits, notices | Haiku drafts, Sonnet wires in | Needs owner business details. Lawyer review before launch |
| PHASE_70_ACCOUNTS | Optional sign-in | Opus medium for the security review, Sonnet to build | DEFERRED until after the league presentation, see 03 |
| PHASE_71_PERF_A11Y | Performance + accessibility final pass | Sonnet low | After all redesign work |
| PHASE_72_DATA_UPDATE | One-command data update flow | Sonnet low | See 06 |
| PHASE_73_ARCHIVE_LOOK | Revisit the "El Archivo" folder look (deferred), final phase | Opus 5.5 | Starts from the WIP patch, see Archive look note below |

Realistic pacing: PHASE_60 to 64 fit a week at Sonnet low. Do not try all of it in one week.

## Model plan (final)
- Skip a separate Opus "planning session": the plans are already written here. Use **Opus 5.5 medium once**, only to review `03_accounts_spec.md` (security-sensitive) right before PHASE_70.
- Everything else Sonnet 5.5 low. Raise to medium only for PHASE_62, 67B, 67C.
- Haiku 5.5 for alt text, legal page first drafts, table reformatting.
- Do not use Fable / Mythos-class models for this project.
- Chat window: Sonnet 5.5 low, quick questions only.

## Decisions that need the owner (do not let Claude Code decide these silently)
1. Accounts: deferred. If you ever build them, they contradict the earlier "no backend" decision. See 03.
   Presentation risk to decide before the meeting: the league's own logos, crests and player photos. Show the PHASE_60 image-rights list to the president as part of the pitch, or confirm in the meeting what the league permits.
2. Name change timing. The new logo says "EL ARCHIVO" (no BSN), so it survives a rename. Header wordmark stays "BSN ARCHIVO" until the new name is chosen. Domain is elarchivopr.com.
3. Business details (SETTLED Oct 9): the site is run by "bennizpr", contact `benniz.8008@gmail.com` (Instagram @bennizpr). No legal entity or address is claimed. Legal pages say "proyecto independiente de bennizpr", not "company". No marketing email, so no mailing address is needed.
4. Whether you plan to earn money from the site or bennizpr (ads, sponsors, store). That decides refund policy, FTC disclosure, and tax questions.
5. Your employer: check the bank's outside-business-activities / conflict-of-interest policy before launching accounts, giveaways or monetization.

## Already settled (do not reopen)
- Complement bsnpr.com, not compete: historical depth only, no live standings.
- Sources: keep RealGM and latinbasket data as is, add no new mentions, wait on the league (Sep 24 decision).
- Unofficial-status notice, privacy line and corrections contact are live. Phase 69 extends them, it does not replace them.

## Archive look
Archive look: deferred by owner (Oct 10). Ignore all archive-look and folder-component requirements in 05_page_specs.md and 08_phase_prompts.md until PHASE_73_ARCHIVE_LOOK, the final phase. Page phases still make each page distinct through layout, accent and content, but built on the current visual style. WIP patch: docs/audits/archive_look_work_in_progress.patch.
