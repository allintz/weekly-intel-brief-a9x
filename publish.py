#!/usr/bin/env python3
"""Publish a new edition of the Weekly Intelligence Brief to Cloudflare Pages.

Flow:
  1. Read the source HTML file (a newly generated dashboard).
  2. Inject the archive-nav widget (idempotent; replaces any existing block).
  3. Write the modified HTML to archive/YYYY-MM-DD.html AND index.html.
  4. Regenerate editions.json from archive/ contents.
  5. Commit locally for version history.
  6. Deploy to Cloudflare Pages via wrangler.

Usage:
  python publish.py <path-to-new-html> [--date YYYY-MM-DD] [--no-deploy] [--no-commit]

Requires:
  - wrangler installed + authenticated (`brew install cloudflare-wrangler`, then `wrangler login`)
  - git initialized in this directory

Environment (optional):
  CF_PAGES_PROJECT  Cloudflare Pages project name (default: prediction-tracker)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
ARCHIVE_DIR = ROOT / "archive"
INDEX = ROOT / "index.html"
EDITIONS_JSON = ROOT / "editions.json"
NAV_SNIPPET = ROOT / "_archive-nav.html"

NAV_START = "<!-- ARCHIVE_NAV_START -->"
NAV_END = "<!-- ARCHIVE_NAV_END -->"

DEFAULT_PROJECT = os.environ.get("CF_PAGES_PROJECT", "prediction-tracker")


def inject_nav(html: str, edition_date: str) -> str:
    """Inject or replace the archive-nav block in the HTML."""
    if not NAV_SNIPPET.exists():
        sys.exit(f"Missing nav template: {NAV_SNIPPET}")
    snippet = NAV_SNIPPET.read_text().replace("__EDITION_DATE__", edition_date).strip()

    # Remove any existing nav block (idempotent re-runs).
    html = re.sub(
        re.escape(NAV_START) + r".*?" + re.escape(NAV_END),
        "",
        html,
        flags=re.DOTALL,
    )

    # Insert right after <body ...> open tag.
    new_html, count = re.subn(
        r"(<body[^>]*>)",
        lambda m: m.group(1) + "\n" + snippet + "\n",
        html,
        count=1,
    )
    if count == 0:
        sys.exit("Could not find <body> tag in source HTML.")
    return new_html


def regenerate_editions_json() -> list[str]:
    """Scan archive/ and write editions.json (newest first). Returns dates."""
    dates = sorted(
        [p.stem for p in ARCHIVE_DIR.glob("*.html") if re.match(r"^\d{4}-\d{2}-\d{2}$", p.stem)],
        reverse=True,
    )
    payload = {
        "editions": [{"date": d} for d in dates],
        "updated": dt.datetime.now().isoformat(timespec="seconds"),
    }
    EDITIONS_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    return dates


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=check, cwd=ROOT)


def git_commit(date: str) -> None:
    # Ensure a git repo exists.
    if not (ROOT / ".git").exists():
        run("git", "init", "-b", "main")
    # Make sure a user is configured locally if none globally.
    name = subprocess.run(
        ["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    if not name:
        run("git", "config", "user.name", "Alex Lintz")
        run("git", "config", "user.email", "alex.lintz@civitech.io")

    run("git", "add", "-A")
    # Skip commit if nothing changed.
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    if not status:
        print("  (no changes to commit)")
        return
    run("git", "commit", "-m", f"Publish edition {date}")


def deploy_to_cloudflare(project: str) -> None:
    """Invoke wrangler to deploy. Assumes wrangler is installed + authenticated."""
    try:
        subprocess.run(
            [
                "wrangler",
                "pages",
                "deploy",
                str(ROOT),
                f"--project-name={project}",
                "--commit-dirty=true",
            ],
            check=True,
            cwd=ROOT,
        )
    except FileNotFoundError:
        sys.exit(
            "wrangler not found. Install with: brew install cloudflare-wrangler\n"
            "Then authenticate: wrangler login"
        )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="Path to the newly generated HTML file")
    p.add_argument("--date", help="Edition date (YYYY-MM-DD), default today")
    p.add_argument("--no-deploy", action="store_true", help="Skip Cloudflare deploy")
    p.add_argument("--no-commit", action="store_true", help="Skip git commit")
    p.add_argument("--project", default=DEFAULT_PROJECT, help="CF Pages project name")
    args = p.parse_args()

    date = args.date or dt.date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        sys.exit(f"Invalid date: {date}")

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        sys.exit(f"Source not found: {source}")

    print(f"Publishing edition {date} from {source.name}")

    html = source.read_text()
    injected = inject_nav(html, date)

    ARCHIVE_DIR.mkdir(exist_ok=True)
    archive_file = ARCHIVE_DIR / f"{date}.html"
    archive_file.write_text(injected)
    INDEX.write_text(injected)
    dates = regenerate_editions_json()

    print(f"  archive/{archive_file.name}")
    print(f"  index.html")
    print(f"  editions.json  ({len(dates)} edition{'s' if len(dates) != 1 else ''})")

    if not args.no_commit:
        print("\nCommitting locally...")
        git_commit(date)

    if not args.no_deploy:
        print(f"\nDeploying to Cloudflare Pages (project: {args.project})...")
        deploy_to_cloudflare(args.project)
        print("\nDone. Live at https://{}.pages.dev/".format(args.project))
    else:
        print("\nSkipped deploy (--no-deploy).")


if __name__ == "__main__":
    main()
