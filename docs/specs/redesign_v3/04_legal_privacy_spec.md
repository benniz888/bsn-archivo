# Legal, privacy, accessibility: spec

I can draft pages and run technical checks. I cannot guarantee legal compliance or "no mistakes". A lawyer should read Terms, Privacy and any giveaway rules before accounts launch.

## What already exists (do not duplicate; extend)
Live since Sep 24 (owner-approved wording): unofficial-status line, correction/removal contact (`benniz.8008@gmail.com`, Instagram `@bennizpr`), privacy line (no cookies, no analytics; Google Fonts sends visitor IPs to Google; browser stores only preferences, game progress and an offline data copy), meta description and share tags, no og:image, no league logos in previews.

## Pages to add (PHASE_69; first drafts by Haiku into `docs/legal_drafts/`, owner approves Spanish text, English optional)
1. **Politica de privacidad** (`#privacidad`): what is stored (local only today; account data after PHASE_70), why, retention, who processes it (hosting, auth provider), user rights (access, delete, export), contact, children (13+), changes log with date.
2. **Terminos de uso** (`#terminos`): independent fan project, no affiliation, data accuracy disclaimer (the archive shows gaps on purpose), acceptable use, IP and takedown contact, no warranty, limitation of liability, governing law (confirm with lawyer: Puerto Rico). Statement that the site sells nothing (while true).
3. **Politica de cookies / almacenamiento** (`#cookies`): list every key in localStorage, the service-worker cache, and (later) auth tokens, each with purpose and "estrictamente necesario". Generated from a real inventory, not invented.
4. **Declaracion de accesibilidad** (`#accesibilidad`): target WCAG 2.2 AA, known gaps, how to report.
5. **Creditos y fuentes** (`#creditos`): Wikipedia-derived data carries CC BY-SA attribution obligations; list sources and licenses. Keep RealGM and latinbasket exactly as decided (no new mentions; data stays as is; see the Sep 24 decision).
6. **Aviso legal / contacto**: "Proyecto independiente de bennizpr". Contact: `benniz.8008@gmail.com`, Instagram `@bennizpr`. No legal entity, address or phone is claimed. Do not write "empresa", "S.A.", "LLC" or similar.
7. **Reembolsos**: only if the site ever sells something. Right now: a one-line "no vendemos productos ni servicios" in Terms, no separate page. Create the page the day monetization starts.

Footer links to all of the above, on every page, keyboard reachable, 44px targets (the footer email/Instagram links are 15px today: fix).

## Cookie consent: what is actually required
- Today: no cookies, no analytics. Nothing to consent to. A banner would be noise.
- If you add analytics: use a cookieless, privacy-first one (Plausible, GoatCounter, Cloudflare Web Analytics) and update Privacy. No Google Analytics without a real opt-in banner.
- Google Fonts: loading from Google sends visitors' IP addresses to Google (already disclosed). Cleaner: **self-host Inter and Oswald** (also faster). Do this in PHASE_71 or earlier; then update the privacy line.
- Accounts: auth tokens in storage are strictly necessary; disclose in the cookie/storage page. A banner is needed only if non-essential storage or trackers appear.
- EU/UK visitors: stricter rules apply if you target them. The site is Spanish-language, Puerto Rico focused; keep non-essential tracking off and the question disappears.

## Forms and consent
- Every sign-up/contact form: visible labels, keyboard operable, clear error text, button labels that say what they do ("Crear cuenta", not "Enviar").
- Terms/Privacy acknowledgement is plain text with links near the submit button.
- Marketing consent: separate, unchecked checkbox, stored with timestamp and text version.

## Audits for PHASE_60 (read-only; report, do not fix)
- Third-party requests: every external host contacted at load (fonts, embeds, scripts). Expect only Google Fonts; flag anything else.
- Third-party embeds: Instagram/YouTube/TikTok iframes or scripts. If any, they set cookies and need disclosure or click-to-load.
- Images (public repo, so rights matter): list every file under `web/img/` with what it is, where it came from, and its license. Crests that are original drawings vs. copied BSN logos; player photos. Output `docs/image_rights.csv` with columns file, subject, source, license, status. Anything without a documented right is flagged "remove or replace"; do not delete (P1) without approval.
- Claims and "reviews": grep for testimonials, ratings, "oficial", "el unico", "100%", "verificado", superlatives. List each with a proposed neutral rewording. Fake-looking reviews are removed.
- Alt text: every `<img>` and icon-only control. Crests: alt = club name. Decorative: `alt=""` / `aria-hidden`.
- Contrast: automated pass for every text/background pair in both themes, plus the known backlog (crest plates, "sin confirmar" label, gradient icon tile).
- Keyboard: tab through every page; no traps; visible focus; dialogs close with Escape.
- Reduced motion: every new animation respects `prefers-reduced-motion`.

## Risks flagged for the owner
- **Trademarks and logos:** "BSN" and team marks belong to others. Dropping "BSN" from the name (planned) lowers risk. Until then keep the "no afiliado" notice visible.
- **League contact:** emailed Sep 22, no reply as of Sep 24. If they reply, their position overrides this document.
- **Data sources:** Wikipedia = CC BY-SA attribution; RealGM / latinbasket handling is already decided.
- **Employer:** read the bank's outside-activities / conflict-of-interest policy before accounts, giveaways or revenue.
- **Sponsored content on bennizpr:** disclose paid or gifted promotion clearly (FTC endorsement rules).
- **Breach notification:** once you hold emails, a Puerto Rico breach-notification law applies; confirm specifics with a lawyer.
- **ADA/accessibility claims:** do not claim full compliance; claim the target and list known gaps.
