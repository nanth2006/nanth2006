#!/usr/bin/env python3
"""Generates stats.svg, langs.svg and trophies.svg locally (no third-party card service).

Usage:
  python scripts/generate_cards.py              # fetch live data from the GitHub API, cache it, render
  python scripts/generate_cards.py --offline    # render from data/github-stats.json only (no network)

Env: GH_USER (default nanth2006), GH_TOKEN / GITHUB_TOKEN (recommended - raises rate limits).
Only the Python standard library is used. Values the API could not provide stay None and render as "-".
"""
import json, math, os, sys, time, urllib.request, urllib.error, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'github-stats.json')
USER = os.environ.get('GH_USER', 'nanth2006')
DISPLAY = 'Nanthakumar K'
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
PINK, PURPLE, MUTED, TEXT = '#ff4fa3', '#a066ff', '#b7a0d8', '#f6ebff'

LANG_COLORS = {'JavaScript': '#f1e05a', 'TypeScript': '#3178c6', 'Python': '#3572A5', 'Java': '#b07219', 'C': '#7c8cf0',
               'C++': '#f34b7d', 'HTML': '#e34c26', 'CSS': '#a066ff', 'SCSS': '#c6538c', 'Shell': '#89e051', 'SQL': '#00a3e0',
               'Jupyter Notebook': '#DA5B0B', 'EJS': '#a91e50', 'Dockerfile': '#384d54', 'PHP': '#4F5D95', 'Kotlin': '#A97BFF'}

# ---------------------------------------------------------------- fetch
def api(path, token, graphql=None):
    url = 'https://api.github.com' + path
    hdr = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-cards', 'X-GitHub-Api-Version': '2022-11-28'}
    if token:
        hdr['Authorization'] = 'Bearer ' + token
    body = json.dumps(graphql).encode() if graphql else None
    req = urllib.request.Request(url, data=body, headers=hdr)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def safe(fn, default=None):
    try:
        return fn()
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, TimeoutError) as e:
        print('  warn:', e, file=sys.stderr)
        return default


def fetch(user, token):
    d = {'user': user, 'synced': None}
    u = api(f'/users/{user}', token)
    d.update(public_repos=u['public_repos'], followers=u['followers'], following=u['following'], created_at=u['created_at'],
             name=u.get('name'))
    repos, page = [], 1
    while True:
        chunk = api(f'/users/{user}/repos?per_page=100&type=owner&page={page}', token)
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r['fork']]
    d['stars'] = sum(r['stargazers_count'] for r in own)
    langs = {}
    for r in own[:80]:
        for k, v in (safe(lambda: api(f"/repos/{user}/{r['name']}/languages", token), {}) or {}).items():
            langs[k] = langs.get(k, 0) + v
    d['languages'] = dict(sorted(langs.items(), key=lambda kv: -kv[1]))
    d['commits'] = safe(lambda: api(f'/search/commits?q=author:{user}&per_page=1', token)['total_count'])
    d['prs'] = safe(lambda: api(f'/search/issues?q=author:{user}+type:pr&per_page=1', token)['total_count'])
    d['issues'] = safe(lambda: api(f'/search/issues?q=author:{user}+type:issue&per_page=1', token)['total_count'])
    if token:
        q = {'query': 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions}}}}', 'variables': {'u': user}}
        d['contributions'] = safe(lambda: api('/graphql', token, q)['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'])
    d['synced'] = dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    return d


def load():
    if os.path.exists(DATA):
        return json.load(open(DATA))
    return {'user': USER, 'synced': None}

# ---------------------------------------------------------------- scoring
def clamp(v): return max(0.0, min(1.0, v))

def score(d):
    g = lambda k: d.get(k) or 0
    return (clamp(g('commits') / 500) * .25 + clamp(g('prs') / 50) * .15 + clamp(g('issues') / 50) * .10 +
            clamp(g('stars') / 100) * .25 + clamp(g('followers') / 100) * .15 + clamp(g('contributions') / 1000) * .10)

def grade(s, known):
    if not known: return '?'
    for t, gname in ((.85, 'S'), (.65, 'A+'), (.45, 'A'), (.30, 'B+'), (.15, 'B'), (.05, 'C+')):
        if s >= t: return gname
    return 'C'

def fmt(v):
    if v is None: return '-'
    return f'{v / 1000:.1f}k' if v >= 10000 else f'{v:,}'

# ---------------------------------------------------------------- svg bits
def wrap(w, h, inner, title, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">'
            f'<title>{title}</title><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b0a31"/><stop offset="1" stop-color="#0d0618"/></linearGradient>'
            f'<linearGradient id="pg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>'
            f'<filter id="gl" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3.5"/></filter>{defs}</defs>'
            f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="18" fill="url(#bg)" stroke="url(#pg)" stroke-width="1.5"/>{inner}</svg>')

def anim(attr, vals, keys, dur, begin='0s', loop=False):
    rep = 'repeatCount="indefinite"' if loop else 'fill="freeze"'
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keys}" dur="{dur}s" begin="{begin}" {rep}/>'

def slide(delay, inner):
    """Fade + slide in from the left. Base state is the final state."""
    t = f'{delay}s'
    return (f'<g>{anim("opacity", "0;0;1", f"0;{delay / (delay + .6):.3f};1" if delay else "0;0;1", delay + .6)}'
            f'<animateTransform attributeName="transform" type="translate" values="-24,0;-24,0;0,0" keyTimes="0;{delay / (delay + .6) if delay else 0:.3f};1" dur="{delay + .6}s" fill="freeze"/>{inner}</g>')

def sync_note(d, w, h):
    s = d.get('synced')
    txt = f'synced {s}' if s else 'waiting for first sync - run the "Update profile cards" workflow'
    return f'<text x="{w - 18}" y="{h - 12}" text-anchor="end" font-family="{SANS}" font-size="9.5" fill="{MUTED}" opacity=".6">{txt}</text>'

# ---------------------------------------------------------------- stats.svg
def render_stats(d):
    w, h = 520, 250
    known = d.get('synced') is not None
    s = score(d) if known else 0
    gr = grade(s, known)
    rows = [('Total Stars', d.get('stars')), ('Total Commits', d.get('commits')), ('Pull Requests', d.get('prs')),
            ('Issues', d.get('issues')), ('Contributions (last year)', d.get('contributions')), ('Public Repos', d.get('public_repos'))]
    inner = f'<text x="26" y="40" font-family="{SANS}" font-size="17" font-weight="700" fill="url(#pg)">{DISPLAY}\'s GitHub Stats</text>'
    colors = [PINK, '#ff8bd0', PURPLE, '#6fb7ff', '#7be3a6', '#ffb86c']
    for i, (lab, val) in enumerate(rows):
        y = 78 + i * 28
        inner += slide(.3 + i * .18, f'<circle cx="32" cy="{y - 4}" r="4.5" fill="{colors[i]}"/>'
                       f'<text x="46" y="{y}" font-family="{SANS}" font-size="13.5" fill="{TEXT}">{lab}</text>'
                       f'<text x="318" y="{y}" text-anchor="end" font-family="{SANS}" font-size="14" font-weight="700" fill="{TEXT}">{fmt(val)}</text>')
    cx, cy, r = 426, 128, 54
    C = 2 * math.pi * r
    p = C * s
    inner += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{PURPLE}" stroke-opacity=".18" stroke-width="9"/>'
              f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#pg)" stroke-width="9" stroke-linecap="round" transform="rotate(-90 {cx} {cy})" stroke-dasharray="{p:.1f} {C:.1f}">'
              f'{anim("stroke-dasharray", f"0 {C:.1f};{p:.1f} {C:.1f}", "0;1", 1.8, "0.4s")}</circle>'
              f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{PINK}" stroke-width="9" opacity=".35" filter="url(#gl)" transform="rotate(-90 {cx} {cy})" stroke-dasharray="{p:.1f} {C:.1f}">'
              f'{anim("stroke-dasharray", f"0 {C:.1f};{p:.1f} {C:.1f}", "0;1", 1.8, "0.4s")}{anim("opacity", ".15;.5;.15", "0;.5;1", 3, "2.2s", True)}</circle>'
              f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" fill="{TEXT}">{gr}'
              f'{anim("opacity", "0;0;1", "0;.5;1", 1.4)}</text>'
              f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-family="{SANS}" font-size="9.5" letter-spacing="2" fill="{MUTED}">RANK</text>')
    inner += sync_note(d, w, h)
    return wrap(w, h, inner, f'{DISPLAY} GitHub stats')

# ---------------------------------------------------------------- langs.svg
def render_langs(d):
    w, h = 520, 250
    langs = d.get('languages') or {}
    tot = sum(langs.values()) or 1
    top = list(langs.items())[:6]
    inner = f'<text x="26" y="40" font-family="{SANS}" font-size="17" font-weight="700" fill="url(#pg)">Most Used Languages</text>'
    if not top:
        inner += f'<text x="26" y="110" font-family="{SANS}" font-size="13" fill="{MUTED}">No language data yet.</text>'
    for i, (name, b) in enumerate(top):
        y = 76 + i * 27; pct = b / tot * 100; bw = 250 * pct / 100; col = LANG_COLORS.get(name, PURPLE)
        d0 = .3 + i * .15
        inner += (f'<text x="26" y="{y + 4}" font-family="{SANS}" font-size="13" fill="{TEXT}">{name}</text>'
                  f'<rect x="150" y="{y - 6}" width="250" height="10" rx="5" fill="{PURPLE}" fill-opacity=".16"/>'
                  f'<clipPath id="lc{i}"><rect x="150" y="{y - 6}" width="250" height="10" rx="5"/></clipPath>'
                  f'<g clip-path="url(#lc{i})"><rect x="150" y="{y - 6}" width="{bw:.1f}" height="10" fill="{col}">{anim("width", f"0;0;{bw:.1f}", f"0;{d0 / (d0 + 1.2):.3f};1", d0 + 1.2)}</rect>'
                  f'<rect x="150" y="{y - 6}" width="30" height="10" fill="#fff" opacity="0">{anim("x", "120;400", "0;1", 2.4, f"{d0 + 1.4}s", True)}{anim("opacity", "0;.55;.55;0", "0;.2;.8;1", 2.4, f"{d0 + 1.4}s", True)}</rect></g>'
                  f'<text x="{w - 26}" y="{y + 4}" text-anchor="end" font-family="{SANS}" font-size="12.5" font-weight="700" fill="{MUTED}">{pct:.1f}%</text>')
    inner += sync_note(d, w, h)
    return wrap(w, h, inner, 'Most used languages')

# ---------------------------------------------------------------- trophies.svg
RANKS = ['C', 'B', 'A', 'AA', 'AAA', 'S', 'SS', 'SSS']
RCOL = {'SSS': '#ffd700', 'SS': '#ffb347', 'S': '#ff8c42', 'AAA': '#ff4fa3', 'AA': '#d65bff', 'A': '#a066ff', 'B': '#6fb7ff', 'C': '#9a9ab5', '?': '#555570'}
TROPHIES = [('Commits', 'commits', [1, 50, 150, 300, 500, 1000, 2000, 4000]), ('Stars', 'stars', [1, 5, 15, 30, 60, 120, 250, 500]),
            ('Followers', 'followers', [1, 5, 15, 30, 60, 120, 250, 500]), ('Repositories', 'public_repos', [1, 5, 10, 20, 30, 50, 80, 120]),
            ('Pull Requests', 'prs', [1, 10, 30, 60, 100, 200, 400, 800]), ('Issues', 'issues', [1, 5, 15, 30, 60, 100, 200, 400]),
            ('Languages', 'nlang', [1, 2, 3, 4, 5, 7, 9, 12]), ('Account Age', 'years', [.1, 1, 2, 3, 4, 6, 8, 10])]
CUP = 'M-11 -14h22v7c0 8-5 13-11 14-6-1-11-6-11-14zM-11 -11h-6c0 6 3 9 7 9M11 -11h6c0 6-3 9-7 9M-3 3h6v7h5v4h-16v-4h5z'

def rank_of(val, th):
    if val is None or val < th[0]:
        return '?'
    r = 'C'
    for name, t in zip(RANKS, th):
        if val >= t:
            r = name
    return r

def render_trophies(d):
    cw, ch, gap, cols = 200, 124, 14, 4
    w = cols * cw + (cols + 1) * gap; h = 2 * ch + 3 * gap
    d = dict(d)
    d['nlang'] = len(d['languages']) if d.get('languages') is not None and d.get('synced') else None
    if d.get('created_at'):
        d['years'] = round((dt.datetime.utcnow() - dt.datetime.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days / 365.25, 1)
    inner = ''
    defs = '<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    style = '<style>.pop{transform-box:fill-box;transform-origin:50% 50%}@keyframes pp{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.08)}100%{opacity:1;transform:none}}</style>'
    for i, (title, key, th) in enumerate(TROPHIES):
        col, row = i % cols, i // cols
        x = gap + col * (cw + gap); y = gap + row * (ch + gap)
        val = d.get(key)
        rk = rank_of(val, th); c = RCOL[rk]
        delay = .2 + i * .14
        vtxt = '-' if val is None else (f'{val:g}' if key == 'years' else fmt(val))
        if key == 'years' and val is not None: vtxt += ' yrs'
        inner += (f'<g class="pop" style="animation:pp .6s cubic-bezier(.34,1.56,.64,1) {delay:.2f}s backwards">'
                  f'<clipPath id="tc{i}"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="16"/></clipPath>'
                  f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="16" fill="#ffffff" fill-opacity=".04" stroke="{c}" stroke-opacity=".55" stroke-width="1.3"/>'
                  f'<g transform="translate({x + 62},{y + 44}) scale(1.35)"><path d="{CUP}" fill="{c}" fill-opacity=".9" stroke="{c}" stroke-width="1"/></g>'
                  f'<text x="{x + 128}" y="{y + 56}" text-anchor="middle" font-family="{SANS}" font-size="{34 if len(rk) < 3 else 28}" font-weight="900" fill="{c}" opacity=".7" filter="url(#gl)">{rk}'
                  f'{anim("opacity", ".4;.9;.4", "0;.5;1", 2.6, f"{delay + .6:.2f}s", True)}</text>'
                  f'<text x="{x + 128}" y="{y + 56}" text-anchor="middle" font-family="{SANS}" font-size="{34 if len(rk) < 3 else 28}" font-weight="900" fill="{c}">{rk}</text>'
                  f'<text x="{x + cw / 2}" y="{y + 92}" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="{TEXT}">{title}</text>'
                  f'<text x="{x + cw / 2}" y="{y + 110}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="{MUTED}">{vtxt}</text>'
                  f'<g clip-path="url(#tc{i})"><path d="M{x - 70} {y}h40l-24 {ch}h-40z" fill="url(#sh)" opacity="0">'
                  f'<animateTransform attributeName="transform" type="translate" values="0,0;{cw + 160},0;{cw + 160},0" keyTimes="0;.28;1" dur="6s" begin="{delay + 1:.2f}s" repeatCount="indefinite"/>'
                  f'{anim("opacity", "0;1;1;0;0", "0;.02;.26;.28;1", 6, f"{delay + 1:.2f}s", True)}</path></g></g>')
    inner += (f'<text x="{w - 18}" y="{h - 5}" text-anchor="end" font-family="{SANS}" font-size="9" fill="{MUTED}" opacity=".6">'
              f'{"synced " + d["synced"] if d.get("synced") else "waiting for first sync"}</text>')
    # trophies card: transparent outer, no big frame
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub trophies">'
            f'<title>GitHub trophies</title><defs><filter id="gl" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="4"/></filter>{defs}</defs>{style}{inner}</svg>')

# ---------------------------------------------------------------- main
def main():
    offline = '--offline' in sys.argv
    d = load()
    if not offline:
        token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        try:
            d = fetch(USER, token)
            os.makedirs(os.path.dirname(DATA), exist_ok=True)
            json.dump(d, open(DATA, 'w'), indent=2)
            print('fetched live data for', USER)
        except Exception as e:  # keep previous cache on failure
            print('fetch failed, using cached data:', e, file=sys.stderr)
    for fn, fnc in (('stats.svg', render_stats), ('langs.svg', render_langs), ('trophies.svg', render_trophies)):
        open(os.path.join(ROOT, fn), 'w').write(fnc(d))
        print('wrote', fn)

if __name__ == '__main__':
    main()
