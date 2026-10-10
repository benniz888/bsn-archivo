# Paste this into Claude Code once (after copying this folder to `docs/specs/redesign_v3/`)

```
Set up model routing for this repo. Create ONLY these files; change no other file. Do not commit. Do not push.
Hard limits: no deletion outside /tmp without asking, never make parse-players, no writes to data/clean/, no force-push, no git reset/clean/rebase.

1. .claude/agents/planner.md
   frontmatter: name: planner, description: "Security-sensitive design review and architecture decisions only (accounts, auth, data model). Read specs in docs/specs/redesign_v3/. Never edits code.", model: opus, tools: Read, Grep, Glob
2. .claude/agents/builder.md
   frontmatter: name: builder, description: "Implements exactly one approved phase from docs/specs/redesign_v3/ and docs/session.md. Stops at phase end.", model: sonnet
3. .claude/agents/chores.md
   frontmatter: name: chores, description: "Mechanical work: alt text, table reformatting, first drafts of legal pages into docs/legal_drafts/, string lists.", model: haiku
4. Append (do not replace) a section "## Redesign v3 working rules" to CLAUDE.md:
   - Specs live in docs/specs/redesign_v3/. Read 01_master_plan.md first; it lists the rules every phase obeys.
   - One phase per turn. Build phases: do NOT commit, do NOT push. Commits happen only in a separate approved COMMIT ONLY step, staged by explicit path.
   - Owner approves every new or changed public Spanish string: list them in docs/strings_pending_<phase>.md.
   - Never fabricate data. Contrast >= 4.5:1 text, >= 3:1 graphics, tap targets >= 44px, visible focus, reduced-motion respected, no emoji in the UI.
   - Verify layout in Chromium AND WebKit at 390px and 1000px; one phone and one desktop screenshot per page per phase.
   - Report <= 12 lines: PHASE / DONE / VERIFIED / NEXT, plus git diff --stat and git status --short.
   - Routing: planner = auth/security design review only; builder = phase implementation; chores = mechanical edits. Main session stays on Sonnet, low effort; run /clear between phases.

Then show me the four file paths and stop.
```

Then in Claude Code run `/model`, choose Sonnet 5.5, set effort low. (If your version lists an "Opus plan" option, you can try it for PHASE_70 only.)
