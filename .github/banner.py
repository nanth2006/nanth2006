"""Builds banner.svg (dark) and banner-light.svg. Base attributes = final state; SMIL/CSS drive the intro."""
import re, math, os
from svgkit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1280, 740
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono','Courier New',monospace"
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
CW = 0.6  # monospace advance in em; textLength pins it on every OS

CFG = dict(
    name='Nanthakumar K',
    roles=['Full Stack Developer', 'MERN Stack Engineer', 'Java & Python Coder', 'Problem Solver', 'Lifelong Learner'],
    tagline='Turning coffee into code & ideas into products.',   # <- change me
    skills=[('React', '#61DAFB'), ('Node.js', '#6CC24A'), ('Express.js', '#9AA0A6'), ('MongoDB', '#47A248'),
            ('Java', '#F89820'), ('C', '#7C8CF0'), ('C++', '#659AD2'), ('Python', '#FFD43B'), ('SQL', '#00A3E0')],
    about=['> 3rd-year B.Tech IT student', '> EGS Pillay Engineering College', '> MERN full-stack developer',
           '> Java/C/C++/Python/SQL', '> Class of 2028', '> Open to SWE & web dev roles'],
    stats=[('9', 'SKILLS'), ('5', 'LANGUAGES'), ('MERN', 'STACK'), ('2028', 'CLASS OF')],
    code=["const buildDreams = () => {", "  const me = { stack: 'MERN' };", "  while (alive) {",
          "    coffee.refill();", "    learn(); build(); ship();", "  }", "  return <Dream coming=\"soon\" />;", "};"],
)

DARK = dict(bg1='#0a0512', bg2='#1b0a31', bg3='#2b0f4a', text='#f6ebff', muted='#b7a0d8', pink='#ff4fa3',
            pink2='#ff8bd0', purple='#a066ff', card='#140a24', cardop='.78', line='#ff4fa3', grid='#ff4fa3',
            gridop='.05', orb1='#ff3d9a', orb2='#7a3cff', heart='#ff5fae', spark='#ffd6f0', code_bg='#0f0720',
            kw='#c792ff', fn='#6fb7ff', st='#7be3a6', tag='#ff7ac2', num='#ffb86c', pun='#9d8bbb', scan='#ff4fa3',
            dark=True)
LIGHT = dict(bg1='#ffffff', bg2='#fdf2fb', bg3='#f1e8ff', text='#2a1244', muted='#6c5a88', pink='#e0157a',
             pink2='#f0549f', purple='#7a35e8', card='#ffffff', cardop='.9', line='#e0157a', grid='#a066ff',
             gridop='.07', orb1='#ff8fc8', orb2='#b99aff', heart='#f2599f', spark='#c783ff', code_bg='#fbf5ff',
             kw='#7a35e8', fn='#1a73c9', st='#0f9a5c', tag='#d6126f', num='#c76a00', pun='#7d6a99', scan='#e0157a',
             dark=False)

_n = [0]
def uid(p='i'):
    _n[0] += 1
    return f'{p}{_n[0]}'

def type_pts(t0, cps, n, cwpx, x0=0.0):
    return [(t0 + i / cps, x0 + i * cwpx) for i in range(n + 1)]

def mono_text(spans, x, y, fs, weight='normal', extra=''):
    n = sum(len(t) for t, _ in spans)
    inner = ''.join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in spans)
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{MONO}" font-size="{fs}" font-weight="{weight}" '
            f'textLength="{f(n * CW * fs)}" lengthAdjust="spacing" xml:space="preserve" {extra}>{inner}</text>'), n

def typed(spans, x, y, fs, t0, cps, cursor_color=None, cursor_hide=None, weight='normal', extra='', loop_pts=None, loop_T=None):
    """Typing reveal. Clip window is 3x font height so no OS font can clip glyphs."""
    txt, n = mono_text(spans, x, y, fs, weight, extra)
    cwpx = CW * fs
    cid = uid('t')
    if loop_pts:
        pts = loop_pts
        a = anim('width', pts, dur=loop_T, loop=True, discrete=True)
        base_w = [v for _, v in pts][-1] if False else n * cwpx
    else:
        pts = [(0, 0)] + type_pts(t0, cps, n, cwpx)
        a = anim('width', pts, discrete=True)
        base_w = n * cwpx
    h = fs * 3
    clip = (f'<clipPath id="{cid}"><rect x="{f(x - 4)}" y="{f(y - fs * 2)}" width="{f(base_w + 8)}" height="{f(h)}">{a}</rect></clipPath>')
    out = clip + f'<g clip-path="url(#{cid})">{txt}</g>'
    if cursor_color:
        cpts = [(t, x + v) for t, v in pts]
        ax = anim('x', cpts, dur=loop_T, loop=bool(loop_pts), discrete=True)
        end = pts[-1][0]
        if cursor_hide is not None and not loop_pts:
            op = anim('opacity', [(0, 1), (end + cursor_hide, 1), (end + cursor_hide + 0.01, 0)], discrete=True)
            cur = (f'<rect x="{f(x + n * cwpx)}" y="{f(y - fs * 0.92)}" width="{f(cwpx * 0.8)}" height="{f(fs * 1.15)}" '
                   f'fill="{cursor_color}" opacity="0">{ax}<g>{op}</g></rect>')
            # opacity-driven cursor with blink: two nested elements
            cur = (f'<g opacity="0">{op}<rect x="{f(x + n * cwpx)}" y="{f(y - fs * 0.92)}" width="{f(cwpx * 0.8)}" '
                   f'height="{f(fs * 1.15)}" fill="{cursor_color}">{ax}{blink(0.9)}</rect></g>')
        else:
            cur = (f'<rect x="{f(x + n * cwpx)}" y="{f(y - fs * 0.92)}" width="{f(cwpx * 0.8)}" height="{f(fs * 1.15)}" '
                   f'fill="{cursor_color}">{ax}{blink(0.9)}</rect>')
        out += cur
    return out, n

def tokenize(line, P):
    toks = re.findall(r"\s+|[A-Za-z_]\w*|'[^']*'|\"[^\"]*\"|[^\sA-Za-z_]", line)
    spans, prev = [], ''
    kws = {'const', 'while', 'return', 'let', 'if', 'else', 'function'}
    for i, t in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else ''
        if t.isspace(): c = P['pun']
        elif t in kws: c = P['kw']
        elif t[0] in '\'"': c = P['st']
        elif t[0].isalpha() or t[0] == '_':
            if prev == '<' or prev == '/': c = P['tag']
            elif nxt == '(' or t == 'buildDreams': c = P['fn']
            else: c = P['text']
        elif t.isdigit(): c = P['num']
        else: c = P['pun']
        if not t.isspace(): prev = t
        spans.append((t, c))
    return spans

def build(P, name, glyph_outliner, mono_outliner, char_b64, light=False):
    _n[0] = 0
    r = rng(7)
    D = []  # defs
    B = []  # body
    pink, purple, text, muted = P['pink'], P['purple'], P['text'], P['muted']

    D.append(f'''<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{P['bg1']}"/><stop offset=".55" stop-color="{P['bg2']}"/><stop offset="1" stop-color="{P['bg3']}"/></linearGradient>
<linearGradient id="nameG" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="420" y2="0" spreadMethod="reflect"><stop offset="0" stop-color="{pink}"/><stop offset=".5" stop-color="{purple}"/><stop offset="1" stop-color="{P['pink2']}"/>{anim('x1', [(0, 48), (6, 460)], loop=True)}{anim('x2', [(0, 420), (6, 832)], loop=True)}</linearGradient>
<linearGradient id="pg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{pink}"/><stop offset="1" stop-color="{purple}"/></linearGradient>
<linearGradient id="scanV" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P['scan']}" stop-opacity="0"/><stop offset=".92" stop-color="{P['scan']}" stop-opacity="{'.22' if P['dark'] else '.16'}"/><stop offset="1" stop-color="{P['scan']}" stop-opacity=".9"/></linearGradient>
<linearGradient id="formG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{pink}" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".55"/><stop offset="1" stop-color="{pink}" stop-opacity="0"/></linearGradient>
<radialGradient id="o1"><stop offset="0" stop-color="{P['orb1']}" stop-opacity="{'.38' if P['dark'] else '.30'}"/><stop offset="1" stop-color="{P['orb1']}" stop-opacity="0"/></radialGradient>
<radialGradient id="o2"><stop offset="0" stop-color="{P['orb2']}" stop-opacity="{'.42' if P['dark'] else '.32'}"/><stop offset="1" stop-color="{P['orb2']}" stop-opacity="0"/></radialGradient>
<clipPath id="bn"><rect width="{W}" height="{H}" rx="26"/></clipPath>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{P['grid']}" stroke-opacity="{P['gridop']}" stroke-width="1"/></pattern>
<pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#fff" fill-opacity=".35"/></pattern>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="glow2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="nameSh" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="{pink}" flood-opacity="{'.45' if P['dark'] else '.25'}"/></filter>
<filter id="holo" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values=".27 .53 .1 0 .22  .135 .265 .05 0 .1  .3 .59 .11 0 .32  0 0 0 1 0"/></filter>
<path id="heart" d="M0 4C-10-4-5-10 0-4C5-10 10-4 0 4Z"/>
<path id="star" d="M0-7L1.6-1.6L7 0L1.6 1.6L0 7L-1.6 1.6L-7 0L-1.6-1.6Z"/>''')

    css = f'''<style>
.l{{transform-box:fill-box;transform-origin:50% 100%}}
.pill{{transition:transform .25s;transform-box:fill-box;transform-origin:center;cursor:pointer}}
.pill:hover{{transform:translateY(-4px) scale(1.07)}}
.pill:hover rect{{stroke-opacity:1;fill-opacity:1}}
.stat:hover{{opacity:.85}}
@keyframes pop{{0%{{opacity:0;transform:scale(0) rotate(-14deg)}}60%{{opacity:1;transform:scale(1.25) rotate(4deg)}}100%{{opacity:1;transform:none}}}}
@keyframes wave{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.bob{{animation:bob 5s ease-in-out infinite}}
</style>'''

    # ---- background layers
    B.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>')
    for cx, cy, rr, g, ph in ((190, 190, 190, 'o1', 0), (1060, 520, 260, 'o2', 2), (600, 650, 200, 'o1', 4), (1180, 120, 150, 'o2', 1)):
        B.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="url(#{g})">{anim("r", [(0, rr), (3, rr * 1.18), (6, rr)], loop=True, begin=f"-{ph}s")}{anim("opacity", [(0, .7), (3, 1), (6, .7)], loop=True, begin=f"-{ph}s")}</circle>')

    # rising particles
    for i in range(34):
        x = r.uniform(10, W - 10); rr = r.uniform(1, 2.6); d = r.uniform(7, 16); col = pink if i % 2 else purple
        bg_ = f"-{f(r.uniform(0, d))}s"
        B.append(f'<circle cx="{f(x)}" cy="{H - 100}" r="{f(rr)}" fill="{col}" opacity="0">'
                 f'{anim("cy", [(0, H + 10), (d, -10)], loop=True, begin=bg_)}'
                 f'{anim("opacity", [(0, 0), (d * .15, .75), (d * .85, .55), (d, 0)], loop=True, begin=bg_)}</circle>')
    # floating hearts
    for i in range(11):
        x = r.uniform(20, W - 20); d = r.uniform(10, 18); s = r.uniform(.8, 1.7); b = r.uniform(0, d)
        B.append(f'<g opacity="0"><use xlink:href="#heart" fill="{P["heart"]}" transform="scale({f(s)})"/>'
                 f'{animT("translate", [(0, f"{f(x)},{H + 20}"), (d / 2, f"{f(x + r.uniform(-30, 30))},{H / 2}"), (d, f"{f(x + r.uniform(-30, 30))},-30")], loop=True, begin=f"-{f(b)}s")}'
                 f'{anim("opacity", [(0, 0), (d * .12, .5), (d * .8, .4), (d, 0)], loop=True, begin=f"-{f(b)}s")}</g>')
    # twinkling sparkles
    for i in range(16):
        x = r.uniform(20, W - 20); y = r.uniform(20, H - 20); p = r.uniform(2.2, 4.5); b = r.uniform(0, p); s = r.uniform(.5, 1.1)
        B.append(f'<g transform="translate({f(x)},{f(y)})"><use xlink:href="#star" fill="{P["spark"]}" opacity=".7" transform="scale({f(s)})">'
                 f'{animT("scale", [(0, f"{f(s * .2)}"), (p / 2, f"{f(s * 1.2)}"), (p, f"{f(s * .2)}")], loop=True, begin=f"-{f(b)}s")}'
                 f'{anim("opacity", [(0, .1), (p / 2, 1), (p, .1)], loop=True, begin=f"-{f(b)}s")}</use></g>')

    # ---- character: hologram formation
    CX, CY, CWd, CH = 800, 42, 466, 690
    D.append(f'<clipPath id="form"><rect x="{CX - 20}" y="0" width="{CWd + 40}" height="{H}">{anim("height", [(0, 0), (.8, 0), (3.6, H)])}</rect></clipPath>')
    img = f'<image x="{CX}" y="{CY}" width="{CWd}" height="{CH}" xlink:href="data:image/png;base64,{char_b64}" preserveAspectRatio="xMidYMid meet"/>'
    B.append(f'<ellipse cx="{CX + 235}" cy="{CY + 600}" rx="230" ry="26" fill="{pink}" opacity="{".25" if P["dark"] else ".15"}" filter="url(#glow2)"/>')
    B.append(f'<g class="bob"><g clip-path="url(#form)">'
             f'<g>{img}{anim("opacity", [(0, 0), (.8, .25), (3.6, .55), (4.5, 1)])}</g>'
             f'<g filter="url(#holo)" opacity="0">{img}{anim("opacity", [(0, 0), (.8, .95), (1.2, .55), (1.5, 1), (2.1, .6), (2.7, .95), (3.4, .55), (3.9, .85), (4.15, .25), (4.4, .6), (4.8, 0)])}</g>'
             f'<rect x="{CX}" y="{CY}" width="{CWd}" height="{CH}" fill="url(#lines)" opacity="0">{anim("opacity", [(0, 0), (.8, .5), (3.8, .5), (4.6, 0)])}</rect>'
             f'</g></g>')
    sy = f'{anim("y", [(0, -40), (.8, -40), (3.6, H - 40)])}'
    B.append(f'<rect x="{CX - 20}" y="{H - 40}" width="{CWd + 40}" height="40" fill="url(#formG)" opacity="0">{sy}{anim("opacity", [(0, 0), (.8, 1), (3.5, 1), (3.8, 0)])}</rect>')
    B.append(f'<rect x="{CX - 20}" y="{H - 21}" width="{CWd + 40}" height="3" fill="#fff" opacity="0" filter="url(#glow)">{anim("y", [(0, -21), (.8, -21), (3.6, H - 21)])}{anim("opacity", [(0, 0), (.8, 1), (3.5, 1), (3.8, 0)])}</rect>')

    # ---- terminal bar
    B.append(f'<rect x="40" y="22" width="430" height="52" rx="13" fill="{P["card"]}" fill-opacity="{P["cardop"]}" stroke="{pink}" stroke-opacity=".5"/>')
    for i, c in enumerate((pink, P['pink2'], purple)):
        B.append(f'<circle cx="{62 + i * 20}" cy="48" r="5.5" fill="{c}"/>')
    term, _ = typed([('user@dev', pink), (' :- ', muted), ('$ ', purple), ('cat README.md', text)], 124, 55, 17, 0.4, 16, cursor_color=pink, weight='bold')
    B.append(term)

    # ---- name (vector outlines, per-letter pop)
    fs = 100
    gl, wd = glyph_outliner.glyphs(CFG['name'], fs, 48, 188)
    sc = min(1, 660 / wd)
    if sc < 1:
        gl, wd = glyph_outliner.glyphs(CFG['name'], fs * sc, 48, 188)
    letters = []
    for i, (ch, d, gx, adv) in enumerate(gl):
        delay = 2.0 + i * 0.09
        letters.append(f'<path class="l" d="{d}" style="animation:pop .55s cubic-bezier(.34,1.56,.64,1) {delay:.2f}s backwards,wave 3.4s ease-in-out {delay + 1.5:.2f}s infinite"/>')
    B.append(f'<g fill="url(#nameG)" filter="url(#nameSh)">{"".join(letters)}</g>')

    # ---- cycling roles
    ry, rfs, rx = 232, 24, 48
    B.append(f'<text x="{rx}" y="{ry}" font-family="{MONO}" font-size="{rfs}" font-weight="bold" fill="{purple}" textLength="{f(2 * CW * rfs)}" lengthAdjust="spacing" xml:space="preserve">&gt; </text>')
    rx0 = rx + 2 * CW * rfs
    roles = CFG['roles']; P_ = 3.6; T = P_ * len(roles); cwpx = CW * rfs
    for k, role in enumerate(roles):
        n = len(role); a0 = k * P_
        pts = [(0, 0)]
        if k > 0: pts.append((a0, 0))
        pts += type_pts(a0 + 0.2, 20, n, cwpx)
        e0 = a0 + 0.2 + n / 20 + 1.6
        pts += [(e0 + i / 40, (n - i) * cwpx) for i in range(1, n + 1)]
        pts.append((T, 0))
        txt, _ = mono_text([(role, 'url(#pg)')], rx0, ry, rfs, 'bold')
        cid = uid('r')
        base = n * cwpx if k == 0 else 0
        B.append(f'<clipPath id="{cid}"><rect x="{f(rx0 - 4)}" y="{f(ry - rfs * 2)}" width="{f(base)}" height="{f(rfs * 3)}">{anim("width", pts, dur=T, loop=True, discrete=True, begin="3.2s")}</rect></clipPath>'
                 f'<g clip-path="url(#{cid})">{txt}</g>')
    cur_pts = [(0, 0)]
    for k, role in enumerate(roles):
        n = len(role); a0 = k * P_
        if k > 0: cur_pts.append((a0, 0))
        cur_pts += type_pts(a0 + 0.2, 20, n, cwpx)
        e0 = a0 + 0.2 + n / 20 + 1.6
        cur_pts += [(e0 + i / 40, (n - i) * cwpx) for i in range(1, n + 1)]
    cur_pts.append((T, 0))
    B.append(f'<rect x="{f(rx0)}" y="{ry - rfs * .92}" width="{f(cwpx * .8)}" height="{f(rfs * 1.15)}" fill="{pink}" opacity="0">{anim("x", [(t, rx0 + v) for t, v in cur_pts], dur=T, loop=True, discrete=True, begin="3.2s")}{anim("opacity", [(0, 0), (3.2, 0), (3.21, 1)], discrete=True)}</rect>')

    # ---- quote box
    qt = CFG['tagline']
    B.append(f'<g>{anim("opacity", [(0, 0), (3.2, 0), (3.7, 1)])}<rect x="48" y="256" width="692" height="46" rx="12" fill="{P["card"]}" fill-opacity="{P["cardop"]}" stroke="url(#pg)" stroke-width="1.4"/>'
             f'<rect x="48" y="256" width="6" height="46" rx="3" fill="url(#pg)"/>'
             f'<text x="68" y="288" font-family="{SANS}" font-size="30" font-weight="bold" fill="{pink}" opacity=".7">&#8220;</text></g>')
    qfs = 16 if len(qt) <= 52 else 14
    q, _ = typed([(qt, text)], 96, 285, qfs, 3.7, 22, cursor_color=pink, cursor_hide=1.0, extra='font-style="italic"')
    B.append(q)

    # ---- tech pills
    rows = [CFG['skills'][:5], CFG['skills'][5:]]
    for ri, row in enumerate(rows):
        px = 48; py = 322 + ri * 44
        for ci, (nm, col) in enumerate(row):
            pw = 40 + 8.6 * len(nm); k = ri * 5 + ci; t0 = 3.9 + k * .16
            B.append(f'<g opacity="1">{anim("opacity", [(0, 0), (t0, 0), (t0 + .5, 1)])}{animT("translate", [(0, "0,14"), (t0, "0,14"), (t0 + .5, "0,0")])}'
                     f'<g class="pill"><rect x="{f(px)}" y="{py}" width="{f(pw)}" height="34" rx="17" fill="{P["card"]}" fill-opacity="{P["cardop"]}" stroke="url(#pg)" stroke-opacity=".75" stroke-width="1.4">'
                     f'{anim("stroke-opacity", [(0, .45), (2 + k * .2, 1), (4, .45)], loop=True, begin=f"{f(t0 + 1)}s")}</rect>'
                     f'<circle cx="{f(px + 18)}" cy="{py + 17}" r="5" fill="{col}"/>'
                     f'<text x="{f(px + 31)}" y="{py + 22}" font-family="{SANS}" font-size="14" font-weight="600" fill="{text}">{esc(nm)}</text></g></g>')
            px += pw + 12

    # ---- stats bar
    sx, sy_, sw, sh = 48, 410, 692, 62
    B.append(f'<g>{anim("opacity", [(0, 0), (4.6, 0), (5.1, 1)])}<rect x="{sx}" y="{sy_}" width="{sw}" height="{sh}" rx="14" fill="{P["card"]}" fill-opacity="{P["cardop"]}" stroke="{pink}" stroke-opacity=".4"/></g>')
    cw_ = sw / 4
    for i, (val, lab) in enumerate(CFG['stats']):
        cx0 = sx + i * cw_; mid = cx0 + cw_ / 2; t0 = 4.9 + i * .25
        if i: B.append(f'<rect x="{f(cx0)}" y="{sy_ + 12}" width="1" height="{sh - 24}" fill="{pink}" opacity=".3"/>')
        if val.isdigit() and i != 3 or val == '2028':
            target = int(val); start = max(0, target - 8) if target > 100 else 0
            seq = list(range(start, target + 1)) if target < 100 else list(range(target - 8, target + 1))
            step = .09 if target < 100 else .12
            for j, v in enumerate(seq):
                ts = t0 + j * step
                if j == len(seq) - 1: pts = [(0, 0), (ts, 1)]
                else: pts = [(0, 0), (ts, 1), (ts + step, 0)]
                op = 1 if j == len(seq) - 1 else 0
                B.append(f'<text x="{f(mid)}" y="{sy_ + 30}" text-anchor="middle" font-family="{SANS}" font-size="25" font-weight="800" fill="url(#pg)" opacity="{op}">{v}{anim("opacity", pts, discrete=True)}</text>')
        else:
            B.append(f'<text x="{f(mid)}" y="{sy_ + 30}" text-anchor="middle" font-family="{SANS}" font-size="25" font-weight="800" fill="url(#pg)" opacity="1">{esc(val)}{anim("opacity", [(0, 0), (t0, 0), (t0 + .5, 1)])}</text>')
        B.append(f'<text x="{f(mid)}" y="{sy_ + 47}" text-anchor="middle" font-family="{SANS}" font-size="10.5" font-weight="700" letter-spacing="2" fill="{muted}">{lab}</text>')
        tid = uid('s'); bw = cw_ - 56
        B.append(f'<clipPath id="{tid}"><rect x="{f(cx0 + 28)}" y="{sy_ + 54}" width="{f(bw)}" height="3" rx="1.5"/></clipPath>'
                 f'<rect x="{f(cx0 + 28)}" y="{sy_ + 54}" width="{f(bw)}" height="3" rx="1.5" fill="{pink}" opacity=".18"/>'
                 f'<g clip-path="url(#{tid})"><rect x="{f(cx0 + 28)}" y="{sy_ + 54}" width="{f(bw)}" height="3" fill="url(#pg)">{anim("width", [(0, 0), (t0, 0), (t0 + 1.2, bw)])}</rect>'
                 f'<rect x="{f(cx0 + 28)}" y="{sy_ + 54}" width="26" height="3" fill="#fff" opacity="0">{anim("x", [(0, cx0 + 14), (2.6, cx0 + 28 + bw)], loop=True, begin=f"{f(t0 + 1.4)}s")}{anim("opacity", [(0, .0), (.3, .8), (2.3, .8), (2.6, 0)], loop=True, begin=f"{f(t0 + 1.4)}s")}</rect></g>')

    # ---- about card
    ax, ay, aw, ah = 48, 492, 316, 224
    B.append(f'<g>{anim("opacity", [(0, 0), (5.2, 0), (5.7, 1)])}<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="16" fill="{P["card"]}" fill-opacity="{P["cardop"]}" stroke="{purple}" stroke-opacity=".5"/>'
             f'<rect x="{ax}" y="{ay}" width="{aw}" height="34" rx="16" fill="{purple}" fill-opacity=".14"/></g>')
    hd, _ = typed([('// ', muted), ('about_me', pink)], ax + 18, ay + 23, 14, 5.4, 18, weight='bold')
    B.append(hd)
    for i, ln in enumerate(CFG['about']):
        t, _ = typed([(ln, text)], ax + 18, ay + 66 + i * 26, 13, 6.0 + i * 1.0, 24)
        B.append(t)

    # ---- code editor card
    kx, ky, kw, kh = 380, 492, 360, 224
    B.append(f'<g>{anim("opacity", [(0, 0), (5.2, 0), (5.7, 1)])}<rect x="{kx}" y="{ky}" width="{kw}" height="{kh}" rx="16" fill="{P["code_bg"]}" fill-opacity="{".92" if P["dark"] else "1"}" stroke="{pink}" stroke-opacity=".55"/>'
             f'<rect x="{kx}" y="{ky}" width="{kw}" height="32" rx="16" fill="{pink}" fill-opacity=".14"/></g>')
    for i, c in enumerate((pink, P['pink2'], purple)):
        B.append(f'<circle cx="{kx + 20 + i * 17}" cy="{ky + 16}" r="4.6" fill="{c}"/>')
    B.append(f'<text x="{kx + 100}" y="{ky + 20}" font-family="{MONO}" font-size="12" fill="{muted}" textLength="{f(len("dreams.jsx") * 12 * CW)}" lengthAdjust="spacing">dreams.jsx</text>')
    CT = 20.0; cfs = 13; ccw = CW * cfs; t_cur = 6.2
    for i, ln in enumerate(CFG['code']):
        n = len(ln)
        pts = [(0, 0), (t_cur, 0)] + type_pts(t_cur, 30, n, ccw) + [(CT - 1.2, n * ccw), (CT - 1.19, 0), (CT, 0)]
        t_cur += n / 30 + .25
        if i == len(CFG['code']) - 1:
            pass
        spans = tokenize(ln, P)
        txt, _ = mono_text(spans, kx + 18, ky + 58 + i * 20.5, cfs)
        cid = uid('c')
        B.append(f'<clipPath id="{cid}"><rect x="{kx + 14}" y="{f(ky + 58 + i * 20.5 - cfs * 2)}" width="{f(n * ccw + 8)}" height="{cfs * 3}">{anim("width", pts, dur=CT, loop=True, discrete=True)}</rect></clipPath><g clip-path="url(#{cid})">{txt}</g>')
    B.append(f'<text x="{kx + kw - 14}" y="{ky + kh - 12}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{muted}" opacity=".7">JSX  UTF-8</text>')

    # ---- neon sign
    nx, ny, nw, nh = 1078, 40, 178, 96
    l1, w1 = mono_outliner.path('KEEP CODING', 19, nx + nw / 2, ny + 42, 1, 'middle')
    l2, w2 = mono_outliner.path('KEEP GROWING', 19, nx + nw / 2, ny + 72, 1, 'middle')
    fl = [(0, .1), (3.0, .1), (3.06, 1), (3.18, .15), (3.3, 1), (3.42, .25), (3.6, 1), (7.0, 1), (7.08, .3), (7.16, 1), (7.28, .5), (7.38, 1), (8, 1)]
    B.append(f'<line x1="{nx + 30}" y1="0" x2="{nx + 30}" y2="{ny}" stroke="{muted}" stroke-width="1.5"/><line x1="{nx + nw - 30}" y1="0" x2="{nx + nw - 30}" y2="{ny}" stroke="{muted}" stroke-width="1.5"/>'
             f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="14" fill="#12061f" stroke="#3a1f58" stroke-width="2"/>'
             f'<g opacity="1">{anim("opacity", fl, dur=8, loop=True)}'
             f'<rect x="{nx + 6}" y="{ny + 6}" width="{nw - 12}" height="{nh - 12}" rx="10" fill="none" stroke="{pink}" stroke-width="2.4"/>'
             f'<rect x="{nx + 6}" y="{ny + 6}" width="{nw - 12}" height="{nh - 12}" rx="10" fill="none" stroke="{pink}" stroke-width="5" opacity=".55" filter="url(#glow)"/>'
             f'<path d="{l1}{l2}" fill="#ff7ac2" opacity=".8" filter="url(#glow)"/><path d="{l1}{l2}" fill="#ffe3f3"/></g>')

    # ---- continuous scanner (clipped by banner rounded rect)
    B.append(f'<g transform="translate(0,-130)"><rect width="{W}" height="120" fill="url(#scanV)" opacity="1"/>{animT("translate", [(0, "0,-130"), (3.5, f"0,{H + 10}")], loop=True, begin="4.2s")}</g>')

    body = ''.join(B)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Nanthakumar K - Full Stack Developer">'
           f'<title>Nanthakumar K - Full Stack Developer</title><defs>{"".join(D)}</defs>{css}'
           f'<g clip-path="url(#bn)">{body}</g>'
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="25" fill="none" stroke="url(#pg)" stroke-width="2" stroke-opacity=".8"/></svg>')
    return svg


def main():
    out = os.path.join(ROOT)
    gl = Outliner(os.path.join(ROOT, 'assets/fonts/Pacifico.ttf'))
    mo = Outliner(os.path.join(ROOT, 'assets/fonts/JetBrainsMono-Bold.ttf'))
    cb = b64(os.path.join(ROOT, 'assets/character.png'))
    for P, fn in ((DARK, 'banner.svg'), (LIGHT, 'banner-light.svg')):
        s = build(P, fn, gl, mo, cb)
        open(os.path.join(out, fn), 'w').write(s)
        print(fn, len(s) // 1024, 'KB')

if __name__ == '__main__':
    main()
