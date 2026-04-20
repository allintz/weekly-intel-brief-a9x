You are updating the master weekly brief prompt to bake in Alex's editorial feedback from the 2026-04-20 edition iteration. This is a one-shot prompt-surgery task.

## File to edit
`/Users/alexlintz/code/prediction-tracker/prompts/weekly-brief.md`

Make the edits, commit, push. Do NOT fire any new weekly brief runs — this is just prompt maintenance.

## Context
Today's weekly brief pipeline ran successfully using this prompt, but Alex gave substantial editorial feedback afterward that we then applied in three follow-up edit passes to this week's HTML (`archive/2026-04-20.html`). Your job: rewrite the master prompt so next Sunday's run produces the corrected format natively — no post-hoc patching needed.

Read the master prompt end-to-end first. Then make the edits below precisely.

## Edits to apply

### A. Schedule and metadata

- Change every reference to "Monday 3am ET" or "Mon 3am ET" to "Sunday 7pm ET"
- Change "Auto-updates every Monday 3am ET" badge text to "Auto-updates every Sunday 7pm ET"
- Change "Next auto-update" references accordingly

### B. Sections to remove from the required output

1. **"Movers & Approaching Resolution"** — delete Section 7 entirely. Instead, add instructions that every market table should include a `Δ Week` column AND rows with |Δ| ≥ 5pp should be highlighted with `style="background: var(--amber-dim)"` or a CSS class `.row-mover`. No standalone movers section.

2. **"Executive Summary" / "🎯 This Week's Bottom Line"** — delete Section 6 entirely. Don't have an exec summary at the top of the edition.

3. **BLW Historical Trajectory table** — remove the table from the main Section 1 output. The BLW card in Section 1 should ONLY show the current score + a link to the BLW appendix at the bottom. The full historical trajectory table lives ONLY in the appendix (#14).

4. **"AI Pause & Moratorium markets" as a separate block** — instead, lump ALL AI-related prediction markets into a SINGLE consolidated table in Section 4 titled "AI-related prediction markets". Include: data center moratorium before 2027 (Polymarket), US AI safety bill before 2027 (Polymarket), AI moratorium (Metaculus Q38766), OpenAI announces AGI before 2027 (Polymarket), Anthropic CEO arrested (Polymarket), and any other AI markets currently scattered. Single table with standard market columns.

### C. Compaction rules for Watching This Week cards

Update Section 3 of "REQUIRED SECTIONS" (the Watching This Week block) to specify tight CSS:
- `padding: 8px 14px`
- h4: `font-size: 13px`, `margin: 2px 0`
- Date row: `font-size: 10px`
- Summary `p`: `font-size: 12px`, `color: var(--text-secondary)`, `line-height: 1.4`, `margin-top: 4px`
- MAX 2 lines of summary. Put extra detail in a tooltip (`<span class="has-tip" data-tip="...">`).
- Gap: `margin-bottom: 6px`

### D. Hard content rules (add/update the QUALITY RULES section)

Add these as new quality rules:

1. **Past-7-days filter**: only include dated news items from the past 7 days, unless there's new reporting *this week* on an older event (in which case note "new development" explicitly). Any bullet/card dated before today-minus-7 gets cut.

2. **Prior-week dedupe**: before writing any section, read last week's archive (fetched in STEP 1) and check for duplication. If a section's content would be substantially the same as last week's, compress to a one-line "unchanged from [date]" link-back. Specifically:
   - **AGI Expert Timelines chart**: if no named forecaster updated this week, drop the chart entirely and replace with 2–4 sentences noting what changed (if anything) + link to prior edition for the full chart.
   - **Community forecasts table**: only show rows whose probability moved >5% or whose forecaster count changed significantly from last week. Otherwise compress to a link.
   - **Bright Line Watch card**: if no new wave data this week (BLW publishes semi-annually), show just the current score + appendix link. Don't rewrite static context.

3. **Empty-sections-get-deleted**: if applying the past-7-days filter + dedupe leaves a section with no content, DELETE the section header too. Never write "no new X this week" placeholder paragraphs. Specifically:
   - Nonprofit Targeting Tracker — delete if no new enforcement actions / investigations this week
   - Press Freedom — delete if no incidents in past 7 days (keep only the annual RSF/V-Dem reference anchors in the BLW context, not a standalone section)
   - Forecaster Commentary — delete if no rating changes this week
   - Sentinel card / LW/EAF cards — delete if no new posts (don't show "no new posts" placeholders)

4. **No fetch-error text in HTML**: never surface fetch errors to readers. Don't write "Cook Political Report returned 403", "Metaculus API returned null aggregations", "X was not accessible", etc. If a source is unreachable, silently omit that source's contribution and log the error to the issues file (see section F below).

5. **Bold intel bullet leads**: every intel bullet across all sections (S1, S2, S3, S4, Authoritarian Drift) must start with a bolded lead headline of 4–10 words capturing WHAT the bullet is about, followed by the detail paragraph. Example: `<strong>Federal appeals court denies Anthropic's DoD designation block.</strong> Anthropic remains barred from... <a href="...">CNBC, Apr 8</a>`. This is the skimmable handle.

### E. Table format rules (update requirements in the table-generation sections)

Every prediction market table must include these columns in this order:
`Market | Prob | Δ Week | Volume | Activity | Created | Source`

**Created column**:
- Fetch from each provider's API:
  - Polymarket: `createdAt` from `/markets?slug=` (or `/events?slug=` for multi-market events)
  - Metaculus: `created_time` or `publish_time` from `/api2/questions/ID/`
  - Manifold: `createdTime` (ms since epoch) from `/v0/slug/`
  - Kalshi: `create_time` if available
- Format: `Mon YYYY` (e.g. `Feb 2026`, `Mar 2025`); `YYYY` alone if older than 1 year
- If unavailable, leave cell blank (don't write "unknown" or "N/A")
- If `createdAt` is within 30 days of today, add `<span class="tag tag-thin">new</span>` after the date — flags the Δ Week comparison as potentially unreliable (artifact of limited trading history)

**Row highlighting for movers**: any row where |Δ Week| ≥ 5pp gets `style="background: var(--amber-dim)"` inline on the `<tr>`. This replaces the deleted Movers section.

### F. Nominee tables — separate Dem and GOP

Section 2 "2028 Presidential" subsection: render TWO side-by-side cards/tables:
- **Democratic Nominee 2028**: top 5 candidates by Polymarket probability, sorted DESCENDING. Source: `democratic-presidential-nominee-2028` event.
- **Republican Nominee 2028**: top 5 candidates by Polymarket + Metaculus Q37321, sorted DESCENDING. Source: `republican-presidential-nominee-2028` event.

Each candidate row: `Name | Prob | WoW Δ`. WoW Δ is absolute pp change from last week's edition value; if the candidate isn't in last week's list, show `new` instead. Never mix candidates across parties (no putting Vance in the Dem list).

### G. Economic indicators — add WoW

Section 2 economic indicators (S&P 500, CPI/inflation, unemployment, Fed rate): show BOTH absolute current value AND WoW percent change. Example: `S&P 500: ~7,080 (WoW: +X.X%)` with green/red coloring for direction.

### H. BLW card — add cross-country V-Dem comparison

Section 1 BLW card should show:
- Current BLW score (e.g. `~44/100` for Spring 2026)
- Methodology/trajectory deep-dive link to appendix
- NEW: V-Dem LDI cross-country comparison table. Include these countries (pull current values from V-Dem if possible, else use the 2025 snapshot below as a fallback):
  - Denmark: 0.88
  - Sweden: 0.85
  - Germany: 0.82
  - United Kingdom: 0.78
  - Israel: 0.66
  - **United States: 0.57** (bold the US row)
  - Poland: 0.50
  - India: 0.45
  - Hungary: 0.42
  - Turkey: 0.30
- One-line note: "V-Dem LDI (0–1) measures liberal-democratic institutions cross-nationally; BLW measures US democratic practice specifically (expert survey)."

### I. LW/EAF post format — expand and bullet

For LessWrong and EA Forum posts in sections 1, 3, 4: instead of cramming 2–3 sentences into one paragraph, target ~4 short lines per post with bullets where multiple claims are present:

```
**[Author] — "[Post title]"** (Date, LW|EAF[, karma if notable])
- First key claim from the post.
- Second claim / mechanism / driver.
- Third: specific number / finding / implication.
- Alex-relevant takeaway (one line).
[Link]
```

Don't invent new claims — expand from what's in the post plus reasonable implication-for-Alex given his work focus (democracy field-building + AI governance).

### J. Indiana state primaries

Always include Indiana state senate/house primaries in Key Dates and Watching This Week when the May primary date is within the 4-week horizon. Indiana's state primary is first Tuesday of May (May 5, 2026). Alex has a personal stake.

### K. CAISI rename context

Section 4 AI Governance policy tracker should include a "CAISI rename" item (until it stops being topical). Text:

> **CAISI rename.** NIST's AI Safety Institute was renamed the **Center for AI Standards and Innovation (CAISI)**; now releasing sector-specific RMF profiles. The rename signals a deliberate shift from "safety" to "standards and innovation" framing. If CAISI focuses on adoption barriers rather than risk, the US government's primary AI evaluation body is no longer oriented toward catching risks before deployment.

Include the rename date when you can confirm it via source; otherwise "announced early 2026 — date not confirmed".

### L. Substack API access

Update the Olga Lautman + Sentinel fetching instructions: Substack has a JSON API at `https://<publication>.substack.com/api/v1/archive?sort=new&limit=12` that returns recent posts. Use that instead of struggling with HTML scraping. Same for Sentinel's blog (`https://blog.sentinel-team.org/api/v1/archive?...`).

### M. Step 5.5: error-surface mechanism (NEW step, insert between 5 and 6)

Add a new section after STEP 5 PUBLISH TO GITHUB and before STEP 6 VERIFY DEPLOY:

```
## STEP 5.5: SURFACE ISSUES TO ALEX (required — do not skip)

Throughout this run, track every fetch failure, null API response, stale data, and data gap. At this step, emit them to three channels so Alex sees them Monday morning without them appearing in the public edition.

### 5.5a: Write /tmp/issues.md

Structured markdown file listing each issue:
- Source / API / step where it happened
- Error type (timeout, 403, 404, null response, stale data older than N days, missing createdAt, etc.)
- What was omitted from the edition as a consequence
- Suggested fix if obvious (e.g., "Kalshi doesn't have a public API; consider scraping the UI page")

### 5.5b: Commit to run-status branch

PUT `/tmp/issues.md` to the `run-status` branch as `issues-YYYY-MM-DD.md`. Same mechanism as the status pings. Use the GitHub Contents API.

### 5.5c: Write to Obsidian inbox

Also write a copy to `/Users/alexlintz/Documents/Obsidian Vault/00_Inbox/YYYY-MM-DD Weekly Brief Issues.md` on the local filesystem. Format with a date header (per Alex's convention: `M/D/YY` on first line of markdown files).

### 5.5d: Text Alex via iMessage

Call the local helper:
```bash
/Users/alexlintz/.config/weekly-brief/send-imessage.sh "Weekly Brief published. $(wc -l < /tmp/issues.md) issues logged — see 00_Inbox/YYYY-MM-DD Weekly Brief Issues.md"
```

If the helper script doesn't exist or fails, log to `/tmp/texting-failed.txt` and continue. Never block the publish on texting.

If there are NO issues this run, still send a short "Weekly Brief published. No issues this run." text.

### 5.5e: NEVER put issue text in the public HTML

Internal QC communication goes through audit.json, issues.md, and iMessage. Never put "fetch error" or "could not reach" language in the edition itself. When a source is unreachable, silently omit and log to issues.md only.
```

### N. STEP 1 — fetch last week's edition prose for dedupe

Update STEP 1 FETCH BASELINE. Currently it fetches only for WoW deltas. Expand to also fetch last week's full HTML prose content (intel bullets, callout text) so STEP 4 can dedupe. Specifically: after fetching `archive/LAST_WEEK_DATE.html`, extract and save to `/tmp/last_week_prose.txt` the content of Section 1 intel bullets, Authoritarian Drift bullets, Section 2/3/4 intel bullets, Executive Summary prose, and Implications callouts. STEP 4 HTML generation should cross-reference this to avoid duplicating language/claims.

## Process

1. Read `prompts/weekly-brief.md` end-to-end first
2. Apply all edits above in one coherent rewrite
3. Preserve anything not mentioned in these edits
4. Preserve the overall structure (STEPs, REQUIRED SECTIONS, QUALITY RULES, FINAL CHECKS)
5. Save to same path
6. Update FINAL CHECKS list at the end to reflect new rules (e.g. add items: "Created column present on every market table", "No AI Pause & Moratorium as separate block", "Past-7-days filter applied", "Step 5.5 completed", "iMessage sent")
7. Verify: `grep -c "Monday 3am" prompts/weekly-brief.md` should return 0. `grep -c "Sunday 7pm" prompts/weekly-brief.md` should return ≥1.
8. Git commit:
   ```
   cd ~/code/prediction-tracker
   git add prompts/weekly-brief.md
   git commit -m "Master prompt: bake in 2026-04-20 editorial feedback"
   git push origin main
   ```

## Don't

- Don't run a weekly brief (don't touch archive/*.html or editions.json)
- Don't commit to run-status branch
- Don't fabricate API endpoints or data
- Don't remove STEP 0 CHECKPOINT PINGS (keep it intact)
- Don't change the GitHub PAT or other secrets embedded in the prompt
- Don't touch the /root/.claude or similar — scope is ONLY `prompts/weekly-brief.md`

## Report

Short summary: lines before/after, sections modified / added / removed, verification grep results, commit SHA.
