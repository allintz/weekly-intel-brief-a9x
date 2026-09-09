# Legacy dark style (retired 2026-09-09)

Kept so the brief can switch back. `index-2026-09-09.html` is the last edition produced in this style (identical to `archive/2026-09-09.html`); `_archive-nav.html` is the matching dark Editions widget. Below is the verbatim HTML spec from `prompts/weekly-brief.md` as it stood before the Letter redesign: STEP 4 (generation), QUALITY RULES, and FINAL CHECKS. To revert: restore this widget, point STEP 4 at this template, and paste these sections back over the current ones.

---

## STEP 4: GENERATE THE HTML

The HTML must match the existing structure and styling. **Fetch the current index.html from the repo as your template reference** to preserve the `<head>` block, CSS, Chart.js/fonts CDNs, archive-nav widget, and overall layout.

```bash
curl -s https://raw.githubusercontent.com/allintz/weekly-intel-brief-a9x/main/index.html > /tmp/template.html
curl -s https://raw.githubusercontent.com/allintz/weekly-intel-brief-a9x/main/_archive-nav.html > /tmp/widget.html
```

**Before writing any section**, cross-reference `/tmp/last_week_prose.txt` (extracted in STEP 1). If a section's content would be substantially the same as last week's, compress to a one-line "unchanged from [date]" link-back rather than rewriting the same prose. Specific compression rules:
- **Bright Line Watch card**: if no new wave data this week (BLW publishes semi-annually), show just the current score + appendix link. Don't rewrite static context.

### REQUIRED SECTIONS (in order)

1. **Nav bar** (preserve layout). Update badge to: `Updated <Month Day YYYY>` (not 'Snapshot')

2. **Hero**: "Weekly Democracy Intelligence Brief". h1 markup: `Weekly Democracy <span class="gradient">Intelligence Brief</span>`. Below h1, a prominent edition date:
   `<div style="font-size:26px;color:var(--accent-light);margin:12px 0 14px;letter-spacing:-0.01em;font-weight:600">Month D, YYYY</div>`
   Spelled-out format ("April 15, 2026" — not "2026-04-15" or abbreviations). Below the subtitle paragraph, a Claude-generated disclaimer:
   `<p style="font-size:13px;color:var(--text-secondary);margin:6px 0 0;line-height:1.5;max-width:720px">Fully Claude-generated each Sunday. Alex estimates about 97% accuracy. Expect 1–3 errors and maybe one big error each issue. Message him with corrections or feedback.</p>`
   Set the `.sub` paragraph to "Prediction markets, forecaster consensus, and curated intelligence on US democratic health, the 2026 midterms, and the 2028 race." Also set `<title>` to "Weekly Democracy Intelligence Brief — Prediction Market & Intel Tracker" and archive-nav `.hint` to "Weekly Democracy Intelligence Brief". Meta-badge: `Auto-updates every Sunday 7pm ET`. Repo + CF project name stay `weekly-intel-brief-a9x` (display-only rename).

3. **Watching this week** (clean list, not red/amber error callouts): Items with meaningful near-term action. Use `.update-item` cards with a left-accent border (`imminent` red for <2wk deadlines, `near` amber for 2–4wk, `watch` accent for longer-horizon items). Each item: date/window label on top (uppercase, muted), headline h4, 1–2 sentence summary. Use tooltips (`<span class="has-tip" data-tip="...">`) to hide secondary detail so the visible copy stays tight. No warning icons — border and label carry the urgency cue. CSS classes already in `<head>`: `.updates-list`, `.update-item`, `.update-item.imminent|near|watch`, `.update-date`.

   **Tight CSS for Watching This Week cards** (apply inline or via class overrides):
   - Card padding: `padding: 8px 14px`
   - h4: `font-size: 13px; margin: 2px 0`
   - Date row: `font-size: 10px`
   - Summary `p`: `font-size: 12px; color: var(--text-secondary); line-height: 1.4; margin-top: 4px`
   - MAX 2 lines of summary visible. Put extra detail in a tooltip (`<span class="has-tip" data-tip="...">`).
   - Gap between cards: `margin-bottom: 6px`

   **Always include Indiana state senate/house primaries** (first Tuesday of May = May 5, 2026) when within the 4-week horizon.

4. **Key Dates & Deadlines** (near top, abbreviated): Two-column (This Month / Coming Up). High-signal items only. Include top primary dates, SCOTUS windows, FISA/legislation votes, Election Day. No AI conferences or AI policy milestones. **Always include Indiana state senate/house primary (May 5, 2026)** when within the 4-week horizon.

5. **KPI strip** (4 cards, clickable links to source): House D% (EBO), Senate D% (EBO), Trump net approval (Silver Bulletin), P(recession) (Polymarket). Each rendered as `<a class="kpi ..." href="..." target="_blank">` with `display:block; color:inherit; text-decoration:none`. Include a detail line and a week-over-week delta labeled explicitly (e.g., '↓ from -13.4 last week'). **No AI cards.** **Do NOT include an Impeach card** — the thin 'impeached before term ends' market is banned. Grid: `repeat(4, 1fr)`.

6. **Section 1: 2026 Midterms & 2028 Race** — 'Implications' callout at BOTTOM.
   - Chamber control (EBO aggregated)
   - Individual Senate races with democracy risk notes (NC/ME/GA/MI/OH/TX/IA/NE/MT). Include independent-vs-R races in NE (Osborn) and MT; note their strategic value for chamber math.
   - Full Electoral Calendar (grouped by month): state primaries, specials, gubernatorial, down-ballot statewide, ballot initiatives, recalls, deadlines. **Indiana state senate/house primaries (May 5, 2026)** must appear when within the 4-week horizon.
   - Forecaster Commentary: past-week rating changes from Silver Bulletin/Cook/Sabato/Split Ticket. Delete this subsection entirely if no rating changes this week.
   - **2028 Presidential — TWO side-by-side tables**:
     - **Democratic Nominee 2028**: top 5 candidates by Polymarket probability, sorted descending. Source: `democratic-presidential-nominee-2028` event. Columns: Name | Prob | WoW Δ. WoW Δ is absolute pp change from last week's edition value; if the candidate isn't in last week's list, show `new` instead.
     - **Republican Nominee 2028**: top 5 candidates by Polymarket + Metaculus Q37321, sorted descending. Source: `republican-presidential-nominee-2028` event. Same columns. Never mix candidates across parties (no putting Vance in the Dem list).
   - Economic indicators (3 cards with context). Show BOTH absolute current value AND WoW percent change for each indicator. Format: `S&P 500: ~7,080 (WoW: +X.X%)` with green/red coloring for direction.
   - Generic ballot
   - Intel (sourced; every bullet starts with bolded 4–10 word lead headline)
   - THEN 'Implications' callout

7. **Section 2: Democratic Resilience** — 'Implications for our work' callout at BOTTOM.
   - Metaculus Democracy Threat Index
   - Sentinel takes on democratic backsliding (if any new this week)
   - Relevant LW/EAF posts on democracy/authoritarian trajectory from past 7 days, rendered in bullet format (see STEP 2 LW/EAF format instructions)
   - **Bright Line Watch card**: show ONLY the current score (e.g., `~57/100`, May 2026 report; survey Feb–Mar 2026) + a link to the BLW appendix at the bottom. VERIFY the current figure at brightlinewatch.org before publishing — do NOT carry forward a stale number or invent a declining trajectory; recent waves have stabilized (Dec 2024 = 67 → Apr 2025 = 53 → early 2026 = 57). Do NOT reproduce the full historical trajectory table here — it lives only in the appendix (item 12). BLW card must have `id="blw-short"` and its card-sub must include `<a href="#blw-appendix" style="color:var(--accent-light)">Methodology &amp; trajectory deep dive ↓</a>`. Appendix required (item 10).
   - **V-Dem cross-country comparison table — CONDITIONAL, default OMIT**: include the V-Dem Liberal Democracy Index cross-country table ONLY when V-Dem has published a new annual dataset or update this period. V-Dem releases roughly annually, so in most weeks there is NO new release — in that case OMIT the table entirely. Do NOT carry forward a prior annual snapshot as if it were current weekly content. When you DO include it (new release only): rescale native 0–1 scores to 0–100, bold the United States row, and title it `V-Dem Liberal Democracy Index (YYYY) — Cross-Country Context` with the actual release year.
   - **Always include this short interpretive note** immediately below the BLW card (whether or not the V-Dem table is shown):

     > **On the numbers**: BLW tracks expert-assessed democratic *practice* (how officials behave, norm-following, specific incidents), which tends to move faster than structural measures (institutions, rights, formal constraints). For how BLW compares to V-Dem, Freedom House, and EIU, point readers to the BLW deep-dive appendix. Only frame a BLW-vs-V-Dem divergence if the current numbers actually diverge — in 2026 they land close together (both near 57/100).

   - Approval/favorability + Silver Bulletin chart link
   - Trump tenure markets (3): Out before 2027, Impeached by EOY 2026, 25th Amendment. (Do NOT include 'Impeached before term ends'.)
   - Democracy/backsliding markets: Insurrection Act Dec+Jun, SCOTUS birthright citizenship/FTC/mail ballots, SAVE Act HR22 + HR7296, SCOTUS vacancy, Alito retirement, Court rules 2020 fraudulent. (VA redistricting referendum resolved No on 2026-04-21 — moved to Resolved sub-section.) Columns: Market | Prob | Δ Week | Volume | Activity | Created | Source. Apply row highlighting: any row where |Δ Week| ≥ 5pp gets `style="background: var(--amber-dim)"` on the `<tr>`.
   - Nonprofit targeting tracker — delete this subsection if no new enforcement actions or investigations this week (see QUALITY RULES: Empty-sections-get-deleted)
   - Press Freedom: recent incidents from U.S. Press Freedom Tracker (past 7 days) — arrests, seizures, credential revocations, assaults. Include RSF ranking (57th, annual) and V-Dem LDI (0.57, annual) as reference anchors. 2-4 sourced bullets. Delete this subsection entirely if no incidents in past 7 days.
   - Intel bullets (EVERY BULLET SOURCED; every bullet starts with a bolded 4–10 word lead headline — see QUALITY RULES)
   - THEN 'Implications for our work' callout

8. **Week in Authoritarian Drift** (callout between S2 and S3)
   - 3-5 bullets from Olga Lautman + corroborating sources (past 7 days)
   - Each: specific development + mechanism + how it differs from mainstream coverage
   - Every bullet sourced with publication date
   - If nothing substantial, say so
   - Styling: distinct callout (amber/warm-grey background or border-left accent)

9. **Data Sources & Methodology** (stable — Sentinel, LW, EAF as core; Olga Lautman; Cook/Sabato/Split Ticket/Silver Bulletin; Ballotpedia/NCSL/Bolts; U.S. Press Freedom Tracker; Bright Line Watch). Append one-line Claim Audit summary: 'Claim audit: N claims checked, X supported, Y softened, Z unable to verify, 0 hard-fail unresolved. <a href="archive/YYYY-MM-DD-audit.json">Full audit log</a>'

10. **Bright Line Watch Deep Dive Appendix** (at bottom, `id="blw-appendix"`, `style="padding-top:48px;border-top:1px solid var(--border)"`, section-num marker "A1"). Required cards in order: What BLW is, 0–100 scale, **Historical trajectory table** (full multi-wave data lives here — NOT in the main BLW card in Section 1), What the [month year] wave found, What it measures well (3 bullets), What it doesn't capture well (4 bullets), Comparison to other indices (V-Dem, Freedom House, EIU). Back-link to `#blw-short` at end. Same short→appendix pattern for any future deep-dive topic.

**DO NOT INCLUDE** an 'Alex's Estimates' section. Do NOT embed Alex-derived probability estimates in narrative paragraphs. Any probability in the HTML must come from a market, Metaculus/Manifold, a named expert forecaster with forecast date, Sentinel, or a LW/EAF post.

### ARCHIVE NAV WIDGET

Inject the widget from `_archive-nav.html`, replacing `__EDITION_DATE__` with today's UTC date. Widget goes right after `<body>`. Use the markers `<!-- ARCHIVE_NAV_START -->` / `<!-- ARCHIVE_NAV_END -->` to locate/replace.


---

## QUALITY RULES

- Every intel bullet MUST have a source link
- **Bold intel bullet leads**: every intel bullet across all sections (S1, S2, Authoritarian Drift) must start with a bolded lead headline of 4–10 words capturing WHAT the bullet is about, followed by the detail. Example: `<strong>Federal appeals court denies Anthropic's DoD designation block.</strong> Anthropic remains barred from... <a href="...">CNBC, Apr 8</a>`. This is the skimmable handle.
- Every market table has columns in this order: Market | Prob | Δ Week | Volume | Activity | Created | Source
- **Created column** for every prediction market table:
  - Fetch from each provider's API:
    - Polymarket: `createdAt` from `/markets?slug=` or `/events?slug=`
    - Metaculus: `created_time` or `publish_time` from `/api2/questions/ID/`
    - Manifold: `createdTime` (ms since epoch) from `/v0/slug/`
    - Kalshi: `create_time` if available
  - Format: `Mon YYYY` (e.g., `Feb 2026`, `Mar 2025`); `YYYY` alone if older than 1 year
  - If unavailable, leave cell blank (don't write "unknown" or "N/A")
  - If `createdAt` is within 30 days of today, add `<span class="tag tag-thin">new</span>` after the date — flags the Δ Week comparison as potentially unreliable (artifact of limited trading history)
- **Row highlighting for movers**: any row where |Δ Week| ≥ 5pp gets `style="background: var(--amber-dim)"` inline on the `<tr>`. This replaces the deleted Movers section.
- Consequentiality filter: skip markets where volume <$50K AND resolution is narrow/procedural. Note in methodology.
- Metaculus: forecaster count + activity + resolution criteria inline
- Low-liquidity (<$5K): ⚠️ Thin; >90% or <10%: Near resolution
- Escape `$` as `\$`
- Economic indicators: show absolute value + WoW % change with directional color; expand abbreviations; compare to Fed target; note direction
- Technical terms (FISA, Humphrey's, Insurrection Act, SAVE Act, 25th Amendment, VRA §2): tooltips/explanations
- BLW: historical trajectory table lives ONLY in the appendix; main card shows only current score + appendix link
- No unverified causal claims
- **Implications at section bottom, never top**. Sections 1–2: 'Implications for our work' callout AFTER all objective data.
- **No vault-derived private scoring in prose**. Never include scenario-matrix values or internal scoring frameworks. Qualitative points from the matrix are fine; numeric scoring is not.
- **No assistant-voice asides in HTML**. Forbidden: "Happy to build X", "Would you like me to add Y", "Let me know if useful", "Here's what I noticed", "I can add…", trailing italic sign-offs. Put alt-viz ideas in /tmp/audit.json, not the HTML.
- **Policy tracker rows require a 'why it matters' stakes line** below Next Event (muted secondary-text style).
- **Short → appendix cross-linking** (currently BLW). Short mention links via anchor; appendix has back-link.
- **Date format**: spell months out in body copy ("April 15, 2026", "March 2026"). Don't use "Apr 15, 2026" or "2026-04-15" in copy. Filenames/paths still use YYYY-MM-DD.
- If data source unavailable: silently omit and log to /tmp/issues.md. Never surface fetch errors in the HTML.
- Audience: EA/democracy insiders. Concise, factual, no fluff, no 'not X but Y' antithesis.
- **Scope discipline**: no AI timelines, capabilities, or AI-governance content. An AI item qualifies only if it is directly about civil liberties, elections, or executive power. Never mention the sibling AI brief.
- **Mechanism over headline** (Authoritarian Drift, Forecaster Commentary): explain WHY / WHAT CHANGED.
- **Probability provenance**: every probability figure traceable to a tradable market, Metaculus/Manifold, named expert with forecast date, Sentinel, or dated LW/EAF post. Never embed Alex-derived probabilities.
- **Prefer newer LW/EAF posts over older X/Twitter snippets** from same author.
- **Claim audit is a hard gate**.
- **Independent verification (Step 4.8) is a mandatory gate.** Cannot be skipped. Excises content that fails the cheating taxonomy — does not block the publish. Items removed are logged to audit.json pending_review array.
- **Never add QC banners, internal notes, or messages-to-Alex in the published HTML.** The site is public-facing. All internal QC communication goes through audit.json and issues.md.
- **Past-7-days filter**: only include dated news items from the past 7 days, unless there's new reporting this week on an older event (in which case note "new development" explicitly). Any bullet/card dated before today-minus-7 gets cut.
- **Prior-week dedupe**: before writing any section, cross-reference `/tmp/last_week_prose.txt`. If a section's content would be substantially the same as last week's, compress to a one-line "unchanged from [date]" link-back. See STEP 4 preamble for specific compression rules per section.
- **Empty-sections-get-deleted**: if applying the past-7-days filter + dedupe leaves a section with no content, DELETE the section header too. Never write "no new X this week" placeholder paragraphs. Specifically:
  - Nonprofit Targeting Tracker — delete if no new enforcement actions / investigations this week
  - Press Freedom — delete if no incidents in past 7 days (keep RSF/V-Dem reference anchors in BLW context, not as a standalone section)
  - Forecaster Commentary — delete if no rating changes this week
  - Sentinel card / LW/EAF cards — delete if no new posts (don't show "no new posts" placeholders)
- **No fetch-error text in HTML**: never surface fetch errors to readers. Don't write "Cook Political Report returned 403", "Metaculus API returned null aggregations", "X was not accessible", etc. If a source is unreachable, silently omit and log the error to /tmp/issues.md only.

## FINAL CHECKS BEFORE PUBLISHING

1. Every intel bullet has a source link
2. Every market has probability, volume, activity status
3. Every Metaculus entry has forecaster count
4. No unverified causal claims
5. Technical terms have tooltips or explanations
6. Economic indicators have context, absolute value, and WoW % change with directional color
7. Row highlighting applied: every market table has Δ Week column; rows where |Δ Week| ≥ 5pp have `style="background: var(--amber-dim)"` on `<tr>`
8. No 'Alex's Estimates' section AND no Alex-derived probabilities in prose
9. Archive nav widget injected with correct data-edition date
10. Badge reads 'Updated <Date>' not 'Snapshot'
11. Hero meta reads 'Auto-updates every Sunday 7pm ET'
12. All 4 GitHub PUTs returned 200/201
13. No `will-trump-be-impeached-before-his-term-ends` market anywhere
14. Week in Authoritarian Drift callout between S1 and S2
15. Full Electoral Calendar in S2 includes down-ballot + smaller races, grouped by month; Indiana state primary (May 5, 2026) present when within 4-week horizon
16. Forecaster Commentary subsection in S2 — or deleted entirely if no rating changes this week
17. NE and MT independent-vs-R Senate races present (or 'no tradable market yet')
18. Sentinel checked this run
19. LW + EA Forum checked this run
20. Claim audit completed, hard_fail_unresolved=0, summary + numbers match, audit JSON pushed
21. Display name 'Weekly Democracy Intelligence Brief' in title, h1, archive-nav `.hint`
22. Prominent edition date below h1 (26px, weight 600, accent color, "Month D, YYYY" spelled out)
23. Claude-generated disclaimer below subtitle: ~97% accuracy, 1–3 errors + maybe one big error per issue, message Alex
24. Implications at section bottom for S1–S2
25. No vault-derived scoring
26. No assistant-voice asides
27. Policy tracker rows have stakes lines
28. BLW short ↔ appendix cross-links intact; historical trajectory table in appendix only, NOT in Section 1 main card
29. Footer: no 'Notion auto-updates' or 'Notion version' text
30. Favicon present
31. KPI strip has exactly 4 cards (House D, Senate D, Trump net approval, P(recession)). NO AI cards. NO Impeach card.
32. KPI cards are clickable links (<a>, not <div>)
33. 'Watching this week' cards use compact CSS (padding 8px 14px; h4 13px; date row 10px; summary p 12px; margin-bottom 6px); max 2 visible summary lines with tooltips for overflow
34. WoW deltas labeled explicitly (e.g., 'last week', 'last Monday')
35. **Calendar scan** — before generating the Watching list, actively search for ballot measures, SCOTUS dates, legislative sunsets, special elections, primary deadlines in the next 1–4 weeks. Presence of a Polymarket/Kalshi market with resolution date in that window is a strong signal the item warrants coverage. Don't only process items already on the existing index.html.
36. Independent verification (Step 4.8) completed — all 7 cheating-taxonomy items explicitly checked and findings reported
37. If any items removed, pending_review array populated in audit.json (NO visible banners or notes in the HTML)
38. 2028 nominee tables: Dem and GOP rendered as two separate side-by-side tables, top 5 each, with WoW Δ column; no cross-party mixing
39. Press freedom bullets present in Section 2 (Democratic Resilience) (from pressfreedomtracker.us) — or subsection deleted entirely if no incidents in past 7 days
40. Created column present on every prediction market table (blank if unavailable; `new` tag if market is <30 days old)
41. Past-7-days filter applied to all intel bullets and news items; items older than 7 days cut or explicitly labeled "new development"
42. Step 5.5 completed — issues.md written to /tmp/, committed to run-status branch as `issues-YYYY-MM-DD.md`, written to Obsidian inbox at `00_Inbox/YYYY-MM-DD Weekly Democracy Brief Issues.md`
43. iMessage sent to Alex via send-imessage.sh (or failure logged to /tmp/texting-failed.txt)
44. No Executive Summary / 'This Week's Bottom Line' section in the HTML
45. No standalone 'Movers & Approaching Resolution' section in the HTML
