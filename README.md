# Prediction Tracker — Public Dashboard

Weekly Intelligence Brief dashboard, hosted on Cloudflare Pages with a dated archive.

- **Current edition**: `https://prediction-tracker.pages.dev/` (placeholder until first deploy)
- **Previous editions**: accessible via the `Editions ▾` widget top-right of the page
- **Search engines blocked** via `_headers` (`X-Robots-Tag: noindex`) and `robots.txt`

## How it works

```
index.html               ← current week's dashboard (mirror of newest archive)
archive/YYYY-MM-DD.html  ← one snapshot per week
editions.json            ← list of editions, newest first (fetched by the nav widget)
_archive-nav.html        ← injected floating "Editions ▾" widget (do not edit in-place)
_headers                 ← Cloudflare Pages response headers (noindex)
publish.py               ← one-command weekly publish
```

Each HTML file has the archive-nav widget injected between `<!-- ARCHIVE_NAV_START -->` and `<!-- ARCHIVE_NAV_END -->` markers. Re-running `publish.py` on the same file is idempotent — it replaces the block rather than duplicating it.

## One-time setup

1. **Install wrangler** (Cloudflare's CLI):
   ```sh
   brew install cloudflare-wrangler
   ```
   *(Alternative: `npm install -g wrangler`)*

2. **Authenticate** — opens your browser, one-time OAuth to your CF account:
   ```sh
   wrangler login
   ```

3. **First publish** from the current HTML in the vault:
   ```sh
   cd ~/code/prediction-tracker
   python3 publish.py "/Users/alexlintz/Documents/Obsidian Vault/00_Inbox/prediction-tracker-v2.html"
   ```
   Wrangler will ask to create the `prediction-tracker` Pages project on first run. Accept. Site goes live at `https://prediction-tracker.pages.dev/` within ~30 seconds.

## Weekly publish

After the Monday 3am trigger generates the new HTML to (e.g.) `00_Inbox/prediction-tracker-v2.html`:

```sh
python3 ~/code/prediction-tracker/publish.py "/Users/alexlintz/Documents/Obsidian Vault/00_Inbox/prediction-tracker-v2.html"
```

This will:
1. Inject the archive-nav widget into the HTML
2. Write `archive/YYYY-MM-DD.html` (today's date)
3. Overwrite `index.html` with the new edition
4. Regenerate `editions.json`
5. Git-commit locally
6. Deploy to Cloudflare Pages

Flags:
- `--date 2026-04-13` — override the edition date (default: today)
- `--no-deploy` — local-only dry run (useful for preview)
- `--no-commit` — skip git commit
- `--project <name>` — override CF Pages project name

## Wiring into the Monday 3am trigger

The existing remote trigger (`trig_015VW4j8oG44BzN9X7VsxJvw`) generates the weekly HTML. Add a final step to its prompt:

> After saving the new dashboard HTML to `00_Inbox/prediction-tracker-vN.html`, run:
> ```
> python3 ~/code/prediction-tracker/publish.py <path-to-new-html>
> ```
> to archive and deploy it.

Requires that the machine running the trigger has `wrangler` installed and authenticated with persistent credentials (`~/.wrangler/config/default.toml`).

## Custom domain (optional, later)

In the Cloudflare dashboard → Pages → `prediction-tracker` → Custom domains, add something like `tracker.lintz.io` (or a subdomain of any zone you own). CF handles TLS automatically.

## Removing an edition

```sh
rm archive/2026-04-15.html
python3 publish.py archive/$(ls archive/ | tail -1)   # re-publish current
```

The first step removes the file; the second regenerates `editions.json` and re-deploys so the widget no longer lists it.
