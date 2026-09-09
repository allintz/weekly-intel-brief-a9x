#!/usr/bin/env python3
"""Market history for the Weekly Democracy Intelligence Brief.

history.json holds one series per tracked market, keyed by a stable id, with
(edition date, probability) points. Used to draw the trend lines in the brief
and to compute "change since last edition" without re-parsing old HTML.

Usage:
  history_tools.py update  EDITION_HTML [EDITION_HTML ...]   # parse editions, merge points
  history_tools.py spark   KEY [--w 64 --h 16 --mover]        # print inline SVG trend line
  history_tools.py delta   KEY                                # print "now prev delta" for KEY
  history_tools.py keys                                        # list series with last value
  history_tools.py set     KEY DATE VALUE [--label TEXT]       # add/overwrite one point by hand

Edition date is taken from the filename (YYYY-MM-DD.html) or --date.
Senate rows are stored Democrat-first: a Republican leader's probability is
converted to 100 - p. In three-way races (Nebraska, Montana) the series is the
Democratic-aligned independent's probability, read from the note text.
"""
import argparse, html as htmlmod, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, 'history.json')

# canonical key -> (label, list of regexes matched against the market/name cell, case-insensitive)
MARKETS = {
  'control_dem_sweep':        ('Democrats sweep both chambers', [r'^democrats sweep']),
  'control_r_senate_d_house': ('Republican Senate, Democratic House', [r'^republican senate,? democratic house']),
  'control_gop_sweep':        ('Republicans sweep both chambers', [r'^republicans sweep']),
  'control_d_senate_r_house': ('Democratic Senate, Republican House', [r'^democratic senate,? republican house']),
  'trump_out_before_2027':    ('Trump out as President before 2027', [r'^trump out (as president )?before']),
  'trump_impeached_2026':     ('Trump impeached by December 31, 2026', [r'impeached by dec']),
  'trump_25th_before_2027':   ('25th Amendment removal before 2027', [r'25th amendment']),
  'insurrection_dec_2026':    ('Insurrection Act invoked by December 31, 2026', [r'insurrection act.*dec(ember)? ?31,? 2026', r'insurrection act.*by dec']),
  'insurrection_sep_2026':    ('Insurrection Act invoked by September 30, 2026', [r'insurrection act.*sep']),
  'scotus_vacancy_2026':      ('Supreme Court vacancy in 2026', [r'supreme court vacancy']),
  'alito_sep_2026':           ('Alito announces retirement by September 30, 2026', [r'alito.*sep']),
  'alito_dec_2026':           ('Alito announces retirement by December 31, 2026', [r'alito.*dec']),
  'alito_jun_2027':           ('Alito announces retirement by June 30, 2027', [r'alito.*jun.*2027']),
  'save_act_signed_2026':     ('SAVE Act (H.R. 22) signed into law in 2026', [r'save act.*signed', r'h\.?r\.?\s?22.*signed']),
  'court_2020_fraud':         ('US court rules the 2020 election was fraudulent', [r'2020 election.*fraud']),
  'recession_2026':           ('US recession by end of 2026', [r'recession']),
  'gop_2028_vance':           ('J.D. Vance, GOP nominee 2028', [r'^j\.?\s?d\.? vance$', r'^vance$']),
  'gop_2028_rubio':           ('Marco Rubio, GOP nominee 2028', [r'^marco rubio$', r'^rubio$']),
  'gop_2028_carlson':         ('Tucker Carlson, GOP nominee 2028', [r'^tucker carlson$']),
  'gop_2028_desantis':        ('Ron DeSantis, GOP nominee 2028', [r'^ron desantis$']),
  'gop_2028_trump':           ('Donald Trump, GOP nominee 2028', [r'^donald trump( jr\.?)?$']),
  'dem_2028_aoc':             ('Alexandria Ocasio-Cortez, Dem nominee 2028', [r'ocasio-cortez', r'^aoc$']),
  'dem_2028_ossoff':          ('Jon Ossoff, Dem nominee 2028', [r'^jon ossoff$']),
  'dem_2028_newsom':          ('Gavin Newsom, Dem nominee 2028', [r'^gavin newsom$']),
  'dem_2028_harris':          ('Kamala Harris, Dem nominee 2028', [r'^kamala harris$']),
  'dem_2028_buttigieg':       ('Pete Buttigieg, Dem nominee 2028', [r'^pete buttigieg$']),
}
STATES = ['Alaska','Colorado','Delaware','Georgia','Iowa','Maine','Michigan','Montana','Nebraska','New Hampshire','North Carolina','Ohio','Texas']

def clean(cell):
    t = re.sub(r'<[^>]+>', ' ', cell)
    t = htmlmod.unescape(t).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def parse_edition(path):
    """Return {key: prob} for one edition HTML."""
    s = open(path, encoding='utf-8', errors='replace').read()
    out = {}
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', s, flags=re.S):
        cells = [clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.S)]
        if len(cells) < 2: continue
        name = cells[0]
        # plain market row: name | prob
        m = re.match(r'^([0-9.]+)%', cells[1])
        if m:
            low = name.lower()
            for key, (label, pats) in MARKETS.items():
                if any(re.search(p, low) for p in pats):
                    out.setdefault(key, float(m.group(1))); break
            continue
        # senate row: state | candidate | prob
        if len(cells) >= 3 and name in STATES:
            m = re.match(r'^([0-9.]+)%', cells[2])
            if not m: continue
            p = float(m.group(1)); cand = cells[1].lower()
            rowtext = ' '.join(cells).lower()
            if '(r)' in cand or cand.startswith('republican') or cand.startswith('rep') or cand.startswith('gop'):
                # Three-way race (Nebraska, Montana): the tracked candidate is the
                # Democratic-aligned independent; take their figure from the note.
                m2 = re.search(r'independent[^%]{0,40}?([0-9.]+)%', rowtext) or re.search(r'\(i\)[^%]{0,20}?([0-9.]+)%', rowtext)
                if 'independent' in rowtext or '(i)' in rowtext:
                    if not m2: continue
                    p = float(m2.group(1))
                else:
                    p = round(100 - p, 2)
            key = 'senate_' + name.lower().replace(' ', '_')
            out.setdefault(key, p)
    return out

def load():
    if os.path.exists(HIST):
        return json.load(open(HIST))
    return {'note': 'Market history for trend lines. Senate series are P(Democrat wins).', 'series': {}}

def save(h):
    for k in h['series']: h['series'][k]['points'].sort()
    json.dump(h, open(HIST, 'w'), indent=1, ensure_ascii=False); open(HIST,'a').write('\n')

def cmd_update(args):
    h = load()
    for path in args.files:
        date = args.date or re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(path)).group(1)
        vals = parse_edition(path)
        for key, p in vals.items():
            label = MARKETS[key][0] if key in MARKETS else key.replace('senate_', '').replace('_', ' ').title() + ' Senate, P(Dem win)'
            ser = h['series'].setdefault(key, {'label': label, 'points': []})
            ser['points'] = [pt for pt in ser['points'] if pt[0] != date] + [[date, p]]
        print(f'{date}: {len(vals)} series from {os.path.basename(path)}', file=sys.stderr)
    save(h)

def cmd_set(args):
    h = load(); ser = h['series'].setdefault(args.key, {'label': args.label or args.key, 'points': []})
    if args.label: ser['label'] = args.label
    ser['points'] = [pt for pt in ser['points'] if pt[0] != args.date] + [[args.date, float(args.value)]]
    save(h)

def cmd_keys(args):
    h = load()
    for k, ser in sorted(h['series'].items()):
        pts = ser['points']; print(f"{k:32s} n={len(pts):2d} last={pts[-1][0]} {pts[-1][1]}")

def cmd_delta(args):
    pts = load()['series'][args.key]['points']
    now = pts[-1][1]; prev = pts[-2][1] if len(pts) > 1 else None
    print(now, prev, None if prev is None else round(now - prev, 2))

def cmd_spark(args):
    pts = [p for _, p in load()['series'][args.key]['points']]
    W, H = args.w, args.h
    if len(pts) < 2:
        print(f'<svg class="spark" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true"><circle cx="{W-2}" cy="{H/2}" r="2.2" fill="currentColor"></circle></svg>'); return
    lo, hi = min(pts), max(pts); r = (hi - lo) or 1.0
    xs = [(2 + i * (W - 4) / (len(pts) - 1), H - 2 - ((p - lo) / r) * (H - 4)) for i, p in enumerate(pts)]
    d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in xs); lx, ly = xs[-1]
    dot = 'var(--accent)' if args.mover else 'currentColor'
    print(f'<svg class="spark" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true"><title>{len(pts)} editions, {lo:g} to {hi:g}</title><polyline points="{d}" fill="none" stroke="var(--spark)" stroke-width="1.25" stroke-linejoin="round" stroke-linecap="round"></polyline><circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.2" fill="{dot}"></circle></svg>')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    u = sub.add_parser('update'); u.add_argument('files', nargs='+'); u.add_argument('--date'); u.set_defaults(f=cmd_update)
    s = sub.add_parser('spark'); s.add_argument('key'); s.add_argument('--w', type=int, default=64); s.add_argument('--h', type=int, default=16); s.add_argument('--mover', action='store_true'); s.set_defaults(f=cmd_spark)
    d = sub.add_parser('delta'); d.add_argument('key'); d.set_defaults(f=cmd_delta)
    k = sub.add_parser('keys'); k.set_defaults(f=cmd_keys)
    st = sub.add_parser('set'); st.add_argument('key'); st.add_argument('date'); st.add_argument('value'); st.add_argument('--label'); st.set_defaults(f=cmd_set)
    a = ap.parse_args(); a.f(a)
