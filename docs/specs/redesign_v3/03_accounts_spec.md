# Accounts (optional sign-in): spec

**STATUS: IN SCOPE (owner, Oct 9). Giveaways are OUT of scope for now: do not build giveaway_entries, marketing consent, or any email-marketing feature. Build PHASE_70 only after the provider is approved and the PHASE_69 pages exist.**

## [PURPOSE]
Let visitors optionally sign in so the site remembers their club, favorites, game progress and (if they choose) searches, and so the owner can run giveaways to a consenting list. Browsing, games and every archive page keep working without an account.

## [DECISION NEEDED] (P2: architectural change, owner approval required)
`web_structure_ios_path_spec_v2.md` decided: static JSON, no backend, no database; revisit "only if accounts, live scores or push notifications require it". Accounts require it. Recommendation below; nothing is built until the owner approves.

Recommended: **managed auth + small database (Supabase: Auth + Postgres + row-level security)**, called from the existing static site with the client SDK. No server of your own.
- Sign-in methods: email magic link (no passwords stored), Google, Apple. If the iOS app is ever submitted and Google sign-in is offered, Apple requires Sign in with Apple as an option too, and in-app account deletion. Plan for both now.
- Alternatives considered: Firebase Auth (fine, more Google lock-in, weaker SQL for giveaway queries); Clerk or Auth0 (polished, but paid quickly and heavier); building your own login (rejected: you would be storing credentials).
- Verify current free-tier limits before committing (free projects can be paused after inactivity; check current terms).

## [DATA TO STORE] (minimum only)
| Table | Columns | Why |
|---|---|---|
| profiles | id (= auth user id), favorite_club, interests[] (optional), created_at, age_confirmed (bool) | personalize Inicio |
| favorites | user_id, kind (player/club), ref_id | saved items |
| game_progress | user_id, game, date, state (json) | resume games |
| search_history | user_id, query, at | only if user turns on "guardar mis busquedas"; default OFF; capped at last 50; one-click clear |
(Deferred with giveaways: marketing_consent and giveaway_entries tables. Not created now; the sign-up form has NO marketing checkbox. Add them later with the rules in [GIVEAWAYS].)

Not collected: birthdate, phone, address, real name (display name optional), device fingerprints, third-party trackers.

## [SECURITY] (security rules cannot be overridden)
- Row-level security ON for every table. Policy: a user can read/write only rows where `user_id = auth.uid()`. Test with two test users: user A must get zero rows of user B.
- The public (anon) key may live in the client; it is designed to be public ONLY because RLS is on. The service-role key never appears in the repo, in the client, or in chat. The repo is public.
- Add to `.gitignore`: `.env*`. Ship `.env.example` with placeholder names only.
- Email magic-link redirect URLs allowlisted to elarchivopr.com (and localhost for dev). Rate limits on auth enabled. Email confirmation required.
- Content-Security-Policy meta/headers limited to self + the auth provider + fonts host (or self-hosted fonts). GitHub Pages cannot set headers: use a `<meta http-equiv>` CSP and say what that cannot cover.
- Never log tokens or emails to the console. Escape every user-supplied string when rendering (display names, search history) to avoid XSS.
- Account deletion: one button, deletes the auth user and all rows (cascade). Data export: one button, downloads JSON of the user's rows.
- Breach plan: write down who is notified and how (a short `docs/incident_plan.md`). Puerto Rico has its own breach-notification law; confirm requirements with a lawyer.

## [UX]
- Header: "Iniciar sesión" button top-right (Statmuse pattern) opening a small dialog, not a page. Phone: icon only, labeled.
- Guest mode is the default. On first sign-in, offer to merge existing local progress and favorite club into the account (one explicit button).
- Sign-up dialog copy (Spanish, owner approves): what is stored, link to Privacy, link to Terms, an unchecked marketing box, an age line (13+; neutral age question, no "enter a fake date" hints).
- Keyboard + screen-reader friendly dialog: focus trap, Escape closes, labelled fields, visible errors, 44px targets.
- Copy must be honest: "Solo guardamos X, Y, Z." Do not claim "100% seguro". Do not promise things the stack cannot prove.

## [GIVEAWAYS] (separate from accounts; lawyer review required)
- Puerto Rico regulates promotional contests, raffles and giveaways, and may require permits or filings. I have not verified specifics. Ask a Puerto Rico attorney before the first giveaway: official rules, eligibility (age, residency), "no purchase necessary", how winners are chosen and verified, prize delivery, taxes on prizes, record keeping.
- If run on Instagram or TikTok, their promotion rules apply (platform release in the rules; do not use platform features in ways they forbid).
- Do not buy or rent emails. Do not use signup emails for anything outside the consent given.
- Marketing email (if any) must include an unsubscribe link and a postal address (CAN-SPAM).
- If a sponsor provides the prize, that is an endorsement/sponsorship: disclosure rules apply.

## [OPEN_QUESTIONS]
1. Provider choice and monthly budget ceiling.
2. Do you want Apple sign-in now (requires a paid Apple Developer membership) or later with the iOS wrapper?
3. Do you want the personalization ("algorithm") to be rules on favorite club + recent views (simple, private, local) or server-side? Recommendation: rules, computed in the browser. No profiling beyond what the user can see.
4. What happens if the provider shuts down or raises prices: export path is the user data JSON + the email list.
5. Who is "the business" on the Terms page (see 04).

## [BUILD ORDER] (after owner approves and 04 pages exist)
1. Provider project + schema + RLS + two-user policy test (no UI).
2. Auth dialog, guest mode, merge, delete, export.
3. Personalization rules on Inicio.
4. Security review by Opus (medium) using this file as the checklist.
5. Lawyer reads Privacy, Terms, and giveaway rules BEFORE the sign-in button goes live.
