# Step 4.8: Independent Verification (behavioral integrity gate)

**Reference**: Greenblatt 2026, "Current AIs seem pretty misaligned to me" — AI agents systematically oversell their work, downplay problems, and silently drop hard sections. This step counteracts those tendencies when you are checking your own work.

## 4.8a: Re-read the actual HTML

Do NOT rely on your memory of what you generated. Actually read `/tmp/new.html` and count sections, tables, and source links:

```bash
echo "=== Section headings ===" && grep -c '<h2\|<section' /tmp/new.html
echo "=== Source links in intel bullets ===" && grep -co 'href="http' /tmp/new.html
echo "=== Table rows ===" && grep -c '<tr' /tmp/new.html
echo "=== Required sections present ===" && for s in "Democratic Resilience" "Midterms" "AGI" "Governance" "Movers" "Executive Summary" "Authoritarian Drift" "Bright Line Watch"; do echo -n "$s: "; grep -c "$s" /tmp/new.html; done
```

Compare these counts against the REQUIRED SECTIONS list in the main instructions. If any required section is missing, that's a failure.

## 4.8b: Cheating taxonomy — check EACH item explicitly and report findings for EACH

1. **Fabricated data**: Any market probability, volume, forecaster count, or economic indicator that does not trace to an API response or web fetch performed in THIS session. If you cannot point to the specific fetch that produced a number, the number is fabricated — remove it.

2. **Stale data as fresh**: Numbers copied from last week's template rather than freshly fetched. Spot-check 3 market values: look up what your Step 2 fetches returned and verify those values appear in the HTML (not last week's values from the template).

3. **Silently dropped sections**: Every REQUIRED SECTION from the main prompt must be present in the HTML. If a data source was unavailable, there must be an explicit "data unavailable" flag in that section — not a missing section. An empty section heading with no content also counts as a silent drop.

4. **Wrong baselines for movers**: WoW deltas must be computed from the actual previous edition values fetched in Step 1 (the baseline archive HTML). Spot-check 2 movers: verify the old value matches last week's archive, the new value matches this week's fetch, and the arithmetic is correct.

5. **Overclaimed completeness**: Search your output for phrases like "all markets updated," "comprehensive coverage," "all checks pass." For each such claim, verify the count or scope actually matches what's in the HTML. Vague completeness claims that can't be verified must be removed or made specific.

6. **Source link spot-check**: Pick 3 random intel bullets from different sections. For each, verify: (a) the URL follows a real URL pattern for that source (e.g., polymarket.com, metaculus.com, lesswrong.com — not a hallucinated URL), (b) the claim beside the link is something the source would plausibly contain. If you performed a WebFetch for this URL earlier, confirm the fetched content supports the claim.

7. **Overstated movers**: For any market or forecast flagged as a significant mover, independently recompute: old value (from Step 1 baseline), new value (from Step 2 fetch), absolute change, relative change. If the math doesn't check out, remove the mover or correct it.

## 4.8c: For each failure found

- **REMOVE** the specific affected content from the HTML: the individual bullet, table row, data point, or claim. Do not remove entire sections — only the specific items that failed.
- **ADD** the removed item to a `pending_review` array in `/tmp/audit.json`:
  ```json
  {
    "item": "brief description of what was removed",
    "failure_type": "fabricated_data | stale_data | silent_drop | wrong_baseline | overclaimed | broken_link | overstated_mover",
    "evidence": "why it failed verification",
    "original_content": "the HTML that was removed"
  }
  ```
- Do NOT add any visible banners, notes, or warnings to the published HTML. The site is public-facing — no internal QC messages belong on it.

## 4.8d: Notification

All removed items are logged in the `pending_review` array of `/tmp/audit.json`, which gets published to `archive/YYYY-MM-DD-audit.json`. Alex reviews the audit log to see what was excised and can restore items manually. No changes to the visible HTML beyond removing the failed content.

## Additional Final Checks

Add these to the final checklist:

40. Independent verification (Step 4.8) completed — all 7 cheating-taxonomy items explicitly checked and findings reported for each
41. If any items were removed, pending_review array is populated in audit.json (NO visible banners or notes added to the HTML — site is public-facing)
