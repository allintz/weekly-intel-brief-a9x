4/15/26
Last updated: 2026-04-15 11:50 ET

# Agent Handoff — Weekly Intelligence Brief Site

This document is the complete operating spec for `allintz/weekly-intel-brief-a9x` (public Cloudflare-hosted dashboard). It is written so that **any capable agent can pick up this project and execute from here without needing the prior conversation**.

---

## 1. Goal state

A fully cloud-native weekly dashboard at **https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/** that:

- **Auto-regenerates every Monday 3am ET** (existing remote trigger, currently posts to Notion — must be extended to publish HTML)
- **Archives every edition** under `/archive/YYYY-MM-DD` with a nav-widget dropdown linking them (already implemented)
- **Becomes Alex's primary artifact** for the Weekly Intelligence Brief (replacing Notion as the main deliverable — Notion may remain as a data-staging layer or be phased out entirely, see §6)
- **Deploys on `git push`** when Alex edits content locally (working now; see §5)
- **Stays unlisted + non-indexable** (`X-Robots-Tag: noindex, nofollow` is already applied via `_headers`)

Runs without Alex's laptop. No human-in-the-loop on the weekly refresh.

---

## 2. Current state (as of 2026-04-15)

### What is live

| Thing | State | Where |
|---|---|---|
| Public site | Live | https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/ |
| GitHub repo | Live, public | https://github.com/allintz/weekly-intel-brief-a9x |
| Cloudflare Pages project | Connected to repo, auto-deploys on push to `main` | CF dashboard → Workers & Pages → `weekly-intel-brief-a9x` |
| Initial edition | `2026-04-15` (derived from `00_Inbox/prediction-tracker-v2.html`) | `/archive/2026-04-15` |
| `noindex` headers | Applied | See `_headers` |
| Editions dropdown widget | Working (top-right pill on every page) | `_archive-nav.html` |

### What is NOT yet live

1. **Weekly auto-publish** — the Monday 3am trigger (`trig_015VW4j8oG44BzN9X7VsxJvw`) currently only writes to Notion. It does not yet generate or publish HTML. **This is the primary work for the next agent.**
2. **Content regeneration** — current HTML is a static snapshot. When the trigger is extended, each Monday must produce fresh content reflecting new data.

### Local working copy

- Path: `~/code/prediction-tracker/` (on Alex's laptop, `allintz`)
- `origin` remote points to `https://github.com/allintz/weekly-intel-brief-a9x.git`
- Local git is configured with `user.name="Alex Lintz"`, `user.email="alex.lintz@civitech.io"`
- Fresh clone works: `gh repo clone allintz/weekly-intel-brief-a9x`

---

## 3. Credentials & IDs

All tokens referenced below are **secrets**. Treat them accordingly.

| Name | Value | Scope | Notes |
|---|---|---|---|
| GitHub PAT (fine-grained) | **[REDACTED — see `~/.config/weekly-intel-brief-a9x/pat` on Alex's machine, or the trigger prompt once wired via `RemoteTrigger action=get`]** | `allintz/weekly-intel-brief-a9x` only, Contents: read/write | Expires ~1 year from 2026-04-15. Used by the trigger to PUT files. If leaked, worst case = vandalize static site. Generate a new one at https://github.com/settings/personal-access-tokens if needed. |
| Cloudflare account | Alex's (`alex-l-lintz.workers.dev` subdomain) | — | CF Pages project name: `weekly-intel-brief-a9x`. Production branch: `main`. Build command: none. Output dir: `/`. |
| Remote trigger | `trig_015VW4j8oG44BzN9X7VsxJvw` | — | Mon 7am UTC / 3am ET. Model: sonnet 4.6. Tools: Bash, Read, Write, Edit, Glob, Grep. MCP: Notion. |
| Notion hub page ID | `342860ae-240a-81a4-9c62-d696ce7890b0` | — | The canonical "current state" Notion page. Trigger reads this to get last week's numbers for WoW deltas. |
| Metaculus API token | `f9f57e4a81ffd0507769fc9cdb859e93d5a921f0` | Read-only API | Already embedded in trigger prompt. |

**Access pattern for agents**: fetch the trigger prompt via `RemoteTrigger action=get trigger_id=trig_015VW4j8oG44BzN9X7VsxJvw` to see current state before modifying. Treat the prompt body as the source of truth for anything not listed here.

---

## 4. Architecture

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │  MONDAY 7AM UTC (3AM ET) — remote trigger trig_015VW4j8oG44BzN9X7VsxJvw  │
 │                                                                     │
 │  1. Read Notion hub (last-week baseline for WoW deltas)             │
 │  2. Gather data (Polymarket, Metaculus, EBO, Silver Bulletin, etc)  │
 │  3. Compute movers                                                  │
 │  4. Update Notion (hub + new subpage)                               │
 │  5. [NEW] Render HTML from same data, PUT to GitHub                 │ ← agent work
 └────────────────────────────────┬────────────────────────────────────┘
                                  │ GitHub Contents API PUT (3 files)
                                  ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │   GitHub: allintz/weekly-intel-brief-a9x  (main branch)             │
 │                                                                     │
 │   /index.html                    ← mirror of newest archive         │
 │   /archive/YYYY-MM-DD.html       ← one per week                     │
 │   /editions.json                 ← list newest-first, widget fetches│
 │   /_headers                      ← CF response headers (noindex)    │
 │   /_archive-nav.html             ← widget template (fetched by      │
 │                                      publish flow, injected into    │
 │                                      each new edition)              │
 │   /style.css                     ← (optional future refactor; see §8)│
 │   /template.html                 ← (optional future refactor; see §8)│
 │   /publish.py                    ← local-edit → deploy helper       │
 │   /README.md, /AGENT_HANDOFF.md, /robots.txt, /.gitignore           │
 └────────────────────────────────┬────────────────────────────────────┘
                                  │ CF Pages GitHub App webhook → auto-deploy
                                  ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │   Cloudflare Pages: weekly-intel-brief-a9x                          │
 │   Public URL: weekly-intel-brief-a9x.alex-l-lintz.workers.dev       │
 │   Deploy time: ~30s from git push                                   │
 └─────────────────────────────────────────────────────────────────────┘
```

Cloudflare is running on the newer Workers-Static-Assets runtime (URL is `*.workers.dev` not `*.pages.dev`). Key behaviors:
- Default HTML-handling strips `.html` extensions (serves `/archive/2026-04-15` from `2026-04-15.html`)
- `_headers` file is respected (same syntax as old Pages)
- CORS same-origin (no cross-origin issues for widget's fetch of `/editions.json`)

---

## 5. Local edit → deploy flow (already works)

Alex can edit the site from his laptop. Any agent assisting with local edits should use:

```sh
cd ~/code/prediction-tracker
# ... make edits ...
git add -A
git commit -m "tweak: <what changed>"
git push origin main
# ~30 seconds later, changes are live at weekly-intel-brief-a9x.alex-l-lintz.workers.dev
```

**Common local-edit scenarios**:

| Task | Command |
|---|---|
| Edit a past edition | edit `archive/YYYY-MM-DD.html` → commit → push |
| Edit current edition | edit `index.html` → commit → push (does NOT update the archive copy) |
| Republish a new snapshot | `python3 publish.py <path-to-html>` (handles archive + index + editions.json + commit + CF deploy via wrangler) |
| Change widget styling | edit `_archive-nav.html` → re-run `publish.py` to re-inject → commit → push |
| Change site headers | edit `_headers` → commit → push |

**Agents assisting with edits MUST**:
1. Pull before editing: `git pull --rebase origin main` (the trigger pushes via API; other agents may push too — avoid diverging)
2. Commit with clear messages (agents can identify themselves in commit subjects if helpful)
3. Never force-push to `main`
4. Never commit secrets — `publish.py` and `.gitignore` avoid this, but check any new scripts

If an agent modifies widget template or `_headers`, it may also need to touch each archive file individually to propagate. The widget is currently injected per-file; future refactor (§8) should move to a shared template/CSS.

---

## 6. Primary task: extend the trigger to publish HTML

This is the next agent's main job.

### 6.1 What STEP 5 of the trigger needs to do

Add a final section to the trigger prompt (after the existing STEP 4 "WRITE THE WEEKLY SUBPAGE + UPDATE HUB") that:

1. Uses the same data gathered in STEPS 1-3 (Polymarket, Metaculus, EBO, Silver Bulletin, etc.)
2. Renders a standalone HTML dashboard
3. Pushes 3 files to GitHub via Contents API:
   - `archive/YYYY-MM-DD.html` (new file, today's UTC date)
   - `index.html` (mirror — overwrite; requires SHA)
   - `editions.json` (prepend today's date; requires SHA)
4. Verifies each PUT returned HTTP 200/201
5. Records the published URL in the Notion hub page summary for traceability

### 6.2 HTML generation requirements

The HTML must match the structure and styling of the existing `index.html` in the repo (fetch it as a structural reference before generating). Key requirements:

- **Preserve verbatim**: `<head>` contents (Chart.js + Google Fonts CDNs, all CSS), archive-nav widget block (between `<!-- ARCHIVE_NAV_START -->` and `<!-- ARCHIVE_NAV_END -->`, but update `data-edition` to today), nav bar layout, all CSS classes
- **Regenerate with fresh data**: snapshot badge date, every content section (hero, alerts, key dates, Sections 1-4, Alex's Estimates), chart data `<script>` blocks
- **Sections to include** (mirror the Notion subpage structure — full spec is in STEP 4 of the current trigger prompt):
  - Hero + "static snapshot, Notion version auto-updates Mon 3am ET" badge
  - Alerts (red_bg for 2-week deadlines)
  - Key Dates & Deadlines (two-column)
  - KPI strip (5-6 cards with context)
  - Executive Summary callout
  - Movers & Approaching Resolution
  - Section 1: Democratic Resilience (incl. Bright Line Watch historical trend, approvals, backsliding markets, nonprofit targeting tracker, intel bullets with source links)
  - Section 2: 2026 Midterms & 2028 Race (chamber control, individual senate races with democracy risk notes, 2028 Dem primary top tier, economic indicators, intel)
  - Section 3: AGI/ASI Timelines (community forecasts table, expert comparison with forecast dates, AGI definitions callout, capability milestones, intel)
  - Section 4: AI Governance (policy tracker, markets, international, upcoming events, intel)
  - Alex's Estimates (clearly labeled, DPA probability tree, electoral×AGI matrix, AGI arrival buckets)
  - Data Sources & Methodology (stable)
  - Bright Line Watch Deep Dive Appendix

- **Quality rules** (same as STEP 4 of existing prompt):
  - Every intel bullet needs a source link
  - Every market shows: Market, Prob, Δ Week, Volume, Activity, Source
  - Low-liquidity markets flagged ⚠️ Thin
  - Metaculus questions include forecaster count + activity + resolution criteria
  - Expert AGI forecasts include the forecast date
  - Alex's estimates never mixed with market/expert data
  - Escape `$` as `\$`

### 6.3 Note on the "snapshot" badge

Current index.html has a badge `<span class="badge"><span class="dot dot-amber"></span>Snapshot Apr 14 2026</span>` in the nav. Since HTML is becoming the primary artifact (per Alex's 2026-04-15 message), change this to `Updated <Date>`. And change the hero meta-badge `Static snapshot · Notion version auto-updates Mon 3am ET` to `Auto-updates every Monday 3am ET`.

### 6.4 Publish flow — exact commands

The trigger sandbox has Bash + curl + python3. This is the full publish sequence. Copy into STEP 5 of the trigger prompt as-is (tokens and repo filled in).

```bash
# === CONFIG ===
export GH_PAT="$(cat ~/.config/weekly-intel-brief-a9x/pat 2>/dev/null)"  # or inline literal in trigger prompt — see §3
export REPO='allintz/weekly-intel-brief-a9x'
export EDITION_DATE=$(date -u +%Y-%m-%d)
export API="https://api.github.com/repos/$REPO/contents"

# === 1. Write the generated HTML to /tmp/new.html ===
# (Agent generates HTML content at this step — see §6.2)
# After this step, /tmp/new.html must contain the full regenerated page.

# Also ensure the archive-nav widget block is present with data-edition=$EDITION_DATE.
# Easiest way: fetch the live widget template and inject before publish:
#
#   WIDGET=$(curl -s https://raw.githubusercontent.com/$REPO/main/_archive-nav.html \
#            | sed "s/__EDITION_DATE__/$EDITION_DATE/")
#   python3 -c "
#   import re
#   html = open('/tmp/new.html').read()
#   widget = open('/dev/stdin').read()
#   html = re.sub(r'<!-- ARCHIVE_NAV_START -->.*?<!-- ARCHIVE_NAV_END -->', '', html, flags=re.DOTALL)
#   html = re.sub(r'(<body[^>]*>)', r'\1\n' + widget + '\n', html, count=1)
#   open('/tmp/new.html','w').write(html)
#   " <<< "$WIDGET"

# === 2. Fetch SHAs of files being updated ===
INDEX_SHA=$(curl -sf -H "Authorization: Bearer $GH_PAT" "$API/index.html" | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")
EDITIONS_SHA=$(curl -sf -H "Authorization: Bearer $GH_PAT" "$API/editions.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")

# === 3. Build new editions.json (prepend today's date if not present) ===
curl -sf -H "Authorization: Bearer $GH_PAT" "$API/editions.json" | python3 -c "
import sys, json, base64, datetime, os
r = json.load(sys.stdin)
current = json.loads(base64.b64decode(r['content']).decode())
today = os.environ['EDITION_DATE']
if not any(e['date'] == today for e in current['editions']):
    current['editions'].insert(0, {'date': today})
current['updated'] = datetime.datetime.now().isoformat(timespec='seconds')
with open('/tmp/editions-new.json','w') as f:
    json.dump(current, f, indent=2); f.write('\n')
"

# === 4. Base64-encode payloads ===
export HTML_B64=$(base64 -i /tmp/new.html | tr -d '\n')
export EDITIONS_B64=$(base64 -i /tmp/editions-new.json | tr -d '\n')

# === 5. PUT archive file (new, no SHA) ===
python3 -c "import json,os;print(json.dumps({'message':f\"Publish edition {os.environ['EDITION_DATE']}\",'content':os.environ['HTML_B64']}))" \
  | curl -sf -X PUT -H "Authorization: Bearer $GH_PAT" -H "Content-Type: application/json" \
    "$API/archive/$EDITION_DATE.html" -d @- \
  | python3 -c "import json,sys;d=json.load(sys.stdin);assert 'content' in d, d; print('archive: OK')"

# === 6. PUT index.html (update, with SHA) ===
python3 -c "import json,os;print(json.dumps({'message':f\"Publish edition {os.environ['EDITION_DATE']}\",'content':os.environ['HTML_B64'],'sha':os.environ['INDEX_SHA']}))" \
  | curl -sf -X PUT -H "Authorization: Bearer $GH_PAT" -H "Content-Type: application/json" \
    "$API/index.html" -d @- \
  | python3 -c "import json,sys;d=json.load(sys.stdin);assert 'content' in d, d; print('index: OK')"

# === 7. PUT editions.json (update, with SHA) ===
python3 -c "import json,os;print(json.dumps({'message':f\"Publish edition {os.environ['EDITION_DATE']}\",'content':os.environ['EDITIONS_B64'],'sha':os.environ['EDITIONS_SHA']}))" \
  | curl -sf -X PUT -H "Authorization: Bearer $GH_PAT" -H "Content-Type: application/json" \
    "$API/editions.json" -d @- \
  | python3 -c "import json,sys;d=json.load(sys.stdin);assert 'content' in d, d; print('editions: OK')"

# === 8. Confirm deploy ===
echo "Published edition $EDITION_DATE. CF Pages deploy starts now; live in ~30s at:"
echo "https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/"
echo "Archive: https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/archive/$EDITION_DATE"
```

### 6.5 Modifying the trigger prompts

There are **two** triggers:

| ID | Purpose | Cron |
|---|---|---|
| `trig_015VW4j8oG44BzN9X7VsxJvw` | Weekly full HTML regeneration | `0 7 * * 1` (Mon 3am ET) |
| `trig_013ZJFtCfECjyChX5h6YPJen` | Daily price refresh (writes `/markets.json` only) | `0 16 * * *` (Noon ET daily) |

Both are edited the same way:

**1. Read the current prompt:**
```
RemoteTrigger action=get trigger_id=<TRIGGER_ID>
```
Save the `content` string verbatim as a local backup (e.g., `/tmp/trigger-backup-<date>.txt`). Do not commit the backup — it contains the GitHub PAT and Metaculus token.

**2. Apply surgical patches** to the content string. Prefer targeted find-and-replace over wholesale rewrites — the prompt is ~41KB and small errors propagate. Python/sed/awk locally is fine.

**3. Push the update:**
```
RemoteTrigger action=update trigger_id=<TRIGGER_ID>
body={
  "job_config": {
    "ccr": {
      "environment_id": "env_01XyfHyiHHbWTU8fupppmi1T",   ← REQUIRED; API returns 400 if omitted
      "events": [{"data": {"message": {"content": "<full new content>", "role": "user"}}}]
    }
  }
}
```
There is no partial-content update — the `content` string is replaced wholesale. Include the full new prompt body each time.

**Common gotchas:**
- Omitting `environment_id` → HTTP 400 `translate job_config v1→v2: job_config missing ccr.environment_id`.
- Writing Python `\uXXXX` escapes directly into HTML/prompt strings → literal `\u2013` etc. renders in the output. Always decode escapes to real Unicode chars before emitting.
- The prompt has many layered sections (STEP 1–6, REQUIRED SECTIONS, QUALITY RULES, FINAL CHECKS). Keep anchors unique when patching; use surrounding context to disambiguate.

**Test run (weekly trigger):**
```
RemoteTrigger action=run trigger_id=trig_015VW4j8oG44BzN9X7VsxJvw
```
Monitor via CF Pages deploys tab or `gh api repos/allintz/weekly-intel-brief-a9x/commits -q '.[0].commit.message'`. A full run pushes 4 files. Iterate until a valid edition publishes.

**Test run (daily refresh):**
```
RemoteTrigger action=run trigger_id=trig_013ZJFtCfECjyChX5h6YPJen
```
Monitor the repo for a `Refresh markets.json <timestamp>` commit. If nothing commits within ~3 minutes, the prompt probably failed silently — read the full prompt, trace the shell pipeline, and simplify.

**Rollback**: revert with `RemoteTrigger action=update` using the pre-change backup.

### 6.6 Making HTML the primary artifact

Per Alex's 2026-04-15 message, HTML should become primary, with Notion demoted to either:

**Option C-1 (recommended, gentle)**: Keep Notion updates but reorient — the Notion hub page becomes a pointer to the live HTML site (one block with the link) plus a lightweight change log. STEP 4 simplifies; STEP 5 becomes the main deliverable.

**Option C-2 (clean break)**: Remove all Notion write logic from the trigger (STEP 4). Keep reads from Notion hub (for continuity / archive linkage) if needed, or drop entirely. HTML is the sole output.

Before choosing, confirm with Alex. Default to C-1 until he says otherwise — Notion still has value as a data-staging layer, and removing it reduces flexibility.

Also update the in-HTML "Notion version auto-updates Mon 3am ET" copy (several places) to reflect the new primary.

---

## 7. Testing / verification checklist

After any trigger update or significant change, verify:

```sh
# Basic liveness
curl -sIL https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/ | head -1
# Expect: HTTP/2 200

# Headers intact
curl -sI https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/ | grep -iE "x-robots|referrer"
# Expect: x-robots-tag: noindex, nofollow; referrer-policy: no-referrer

# Editions JSON served
curl -s https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/editions.json
# Expect: {"editions":[{"date":"2026-..."}, ...], "updated":"..."}

# Latest archive reachable
LATEST=$(curl -s https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/editions.json | python3 -c "import json,sys;print(json.load(sys.stdin)['editions'][0]['date'])")
curl -s -o /dev/null -w "%{http_code}\n" "https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/archive/$LATEST"
# Expect: 200

# Widget injected in HTML
curl -s https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/ | grep -c "ARCHIVE_NAV_START"
# Expect: 1

# Trigger still valid
# Use RemoteTrigger action=get to confirm prompt + cron unchanged except for intended edits
```

---

## 8. Known issues & future work

### Issues

- **HTML is a large monolith** (~72KB, 877 lines). Each weekly push re-sends the entire file. Fine for now but makes diffs noisy in git history.
- **Widget is injected per-file.** Changing widget code requires re-running `publish.py` against every archive file. A shared `/widget.js` or templating approach would be cleaner (see future work).
- **Trigger runs on `alex-l-lintz.workers.dev` — this is personal to Alex's CF account.** If he ever moves CF accounts or the subdomain changes, the shareable URL breaks. Mitigation: add a custom domain (e.g. `tracker.<some-domain-alex-owns>`) as a second name; easy to do in CF dashboard.
- **Trigger prompt holds the PAT in plaintext.** Accepted risk (fine-grained, narrow scope). Rotate annually or sooner if leaked.
- **HTML content regeneration is expensive in tokens.** Sonnet 4.6 can handle it, but the trigger run time grows. If this becomes a cost concern, split data-gathering and rendering into separate triggers.

### Future refactors (not blocking, but worth doing)

1. **Extract CSS to `/style.css`** and replace inline `<style>` with `<link>`. Makes HTML regeneration easier and keeps visual consistency across editions.
2. **Extract an HTML skeleton to `/template.html`** with content placeholders (e.g. `<!-- SECTION:MOVERS -->`). Trigger generates only content, substitutes into template.
3. **Add a changelog page** at `/changelog` summarizing major deltas week over week.
4. **Add RSS** at `/rss.xml` so friends can subscribe. Trivial once a templater is in place.
5. **Custom domain** — CF dashboard → Pages → `weekly-intel-brief-a9x` → Custom domains → `tracker.<alex-owned-domain>`. CF provisions TLS automatically.
6. **Password protect via Cloudflare Access** (free tier, up to 50 emails) if sensitivity increases.

---

## 9. What to do if something breaks

| Symptom | First check | Fix |
|---|---|---|
| Site returns 500 | CF dashboard → Deployments → most recent. Look at build log. | If bad HTML was pushed, `git revert HEAD && git push origin main`. |
| 404 on `/` | Did the push succeed? `gh api repos/allintz/weekly-intel-brief-a9x/commits -q '.[0].commit.message'` | If CF Pages project unlinked, reconnect via dashboard. |
| Widget shows "Archive unavailable" | `editions.json` malformed or missing | `curl -s <site>/editions.json` — if not valid JSON, regenerate via `publish.py` against any archived HTML. |
| Trigger failed | `RemoteTrigger action=get trigger_id=trig_015VW4j8oG44BzN9X7VsxJvw` → check recent runs if exposed by API; otherwise check via CF / GH commits whether STEP 5 ran | If 401 on GitHub PUT, PAT expired or revoked — create new PAT (§3 instructions), update trigger prompt. |
| Push rejected | Another agent or the trigger pushed in parallel | `git pull --rebase origin main && git push` |
| Old edition disappears | Only way is someone deleted `archive/YYYY-MM-DD.html` or mangled `editions.json` | `git log -- archive/` → revert the deleting commit. |

---

## 10. Quick reference

| Thing | Value |
|---|---|
| Public URL | https://weekly-intel-brief-a9x.alex-l-lintz.workers.dev/ |
| GitHub repo | https://github.com/allintz/weekly-intel-brief-a9x |
| CF Pages project name | `weekly-intel-brief-a9x` |
| Production branch | `main` |
| Cron (UTC) | `0 7 * * 1` (Mon 7am UTC = 3am ET) |
| Trigger ID | `trig_015VW4j8oG44BzN9X7VsxJvw` |
| Notion hub page ID | `342860ae-240a-81a4-9c62-d696ce7890b0` |
| Local clone | `~/code/prediction-tracker/` |
| Widget markers | `<!-- ARCHIVE_NAV_START -->` / `<!-- ARCHIVE_NAV_END -->` |
| Archive filename | `archive/YYYY-MM-DD.html` (UTC date) |
| Editions JSON | `/editions.json`, newest first, `{"editions":[{"date":"YYYY-MM-DD"},...],"updated":"ISO8601"}` |

---

*If you are the agent picking this up: read §6 first (the core work), then §5 (local flow) and §8 (known issues). Everything else is reference. Confirm scope with Alex before touching the trigger. Good luck.*
