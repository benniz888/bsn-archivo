# START HERE (Saturday, after the usage reset)

Goal: a final build to present to the league president. Accounts are IN. Giveaways are OUT for now. Run phases 60 to 72 in order.
You do not need to read the other files. Claude Code reads them. Copy the folder in (step 2) and paste the prompts.

You only ever do one thing at a time. Do these in order.

1. In Terminal: `cd ~/Projects/bsn-archivo && git checkout main && git pull`
2. Copy this whole folder into the repo as `docs/specs/redesign_v3/` (the repo's `docs/specs/` is where the framework wants specs).
3. Open Claude Code in the repo. Run `/model`, pick **Sonnet 5.5**, effort **low**.
4. Paste the contents of `07_claude_code_setup_prompt.md` (creates the planner / builder / chores agents + a CLAUDE.md section). Review, say "approved".
5. Paste PHASE_60 from `08_phase_prompts.md`. It is read-only. Come back to the chat only when it reports.
6. Then one phase per sitting, `/clear` between phases.

Files in this pack
- 01_master_plan.md       order of phases, model and effort per phase, decisions that need you
- 02_brand_and_logo_spec  logo choice, header/phone behavior, icon files (already generated in assets/logo/)
- 03_accounts_spec.md     sign-in, what is stored, security, giveaways. GATED: needs your decision first
- 04_legal_privacy_spec   pages, consent, audits, what a lawyer must review
- 05_page_specs.md        per-page work, from your screenshots
- 06_performance_and_data_updates.md
- 07_claude_code_setup_prompt.md
- 08_phase_prompts.md     copy-paste prompts, one per phase
- assets/logo/            icons already generated from logos-04
