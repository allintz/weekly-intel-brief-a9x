# run-status branch

This branch holds run-status pings from the weekly-publisher trigger. Not deployed by Cloudflare (CF only builds `main`). Each run overwrites `status.json` at major checkpoints so Claude can poll progress without touching `main`.

Checkpoints:
1. `started` — trigger fired, baseline fetched
2. `markets_gathered` — Polymarket/Metaculus/Kalshi/Manifold done
3. `sources_gathered` — Sentinel/LW/EAF/Lautman/forecasters done
4. `html_generated` — fresh HTML written to /tmp/new.html
5. `audit_complete` — Step 4.5 claim audit done
6. `verification_complete` — Step 4.8 independent verification done
7. `published` — 4 GitHub PUTs returned 200/201

Poll: `curl -s https://raw.githubusercontent.com/allintz/weekly-intel-brief-a9x/run-status/status.json`
