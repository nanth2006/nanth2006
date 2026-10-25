"""Builds lanyard.svg - swinging ID badge, pure SVG (SMIL), damped pendulum physics sampled to keyframes."""
import math, os
from svgkit import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 560, 830
PX = 280  # pivot x (pivot y = 0)
NAME, ROLE, HANDLE = 'Nanthakumar K', 'FULL STACK DEVELOPER', '@nanth2006'
FPS = 30


def samples(fn, t_end):
    n = int(t_end * FPS)
    return [(i / FPS, fn(i / FPS)) for i in range(n + 1)]


def build():
    pac = Outliner(os.path.join(ROOT, 'assets/fonts/Pacifico.ttf'))
    jb = Outliner(os.path.join(ROOT, 'assets/fonts/JetBrainsMono-Bold.ttf'))
    face = b64(os.path.join(ROOT, 'assets/face.png'))
    r = rng(11)

    # ---------- physics ----------
    T_DROP = 0.8            # free-fall time (s)
    A, TAU, OM = 12.0, 1.9, 2 * math.pi / 2.5   # initial swing deg, damping time const, angular freq
    T_SWING = 8.0

    def drop(t):
        if t <= T_DROP:
            return -900 + 900 * (t / T_DROP) ** 2
        u = t - T_DROP                       # rebound after the strap goes taut
        return -34 * math.exp(-u / .16) * abs(math.sin(math.pi * u / .34)) if u < 1.2 else 0.0

    drop_pts = [(t, '0,%s' % f(round(drop(t), 2))) for t, _ in samples(lambda t: 0, 1.9)]

    def theta(t):  # strap pendulum
        return A * math.exp(-t / TAU) * math.cos(OM * t)

    def phi(t):    # card lags behind strap (coupled pendulum feel)
        return 0.6 * A * math.exp(-t / (TAU * .85)) * math.cos(OM * 1.32 * t - 0.8)

    swing = [(t, f'{f(round(theta(t), 3))} {PX} 0') for t, _ in samples(lambda t: 0, T_SWING)]
    cswing = [(t, f'{f(round(phi(t), 3))} {PX} 372') for t, _ in samples(lambda t: 0, T_SWING)]
    PER = 5.2
    sway = [(t, f'{f(round(1.7 * math.sin(2 * math.pi * t / PER), 3))} {PX} 0') for t, _ in samples(lambda t: 0, PER)]
    csway = [(t, f'{f(round(1.2 * math.sin(2 * math.pi * t / PER - 0.9), 3))} {PX} 372') for t, _ in samples(lambda t: 0, PER)]
    t_sw0 = T_DROP + 0.05

    # ---------- text outlines ----------
    name_g, nw = pac.glyphs(NAME, 31, PX, 628, anchor='middle')
    name_d = ''.join(d for _, d, _, _ in name_g)
    role_d, _ = jb.path(ROLE, 11.5, PX, 656, 1.6, 'middle')
    hand_d, _ = jb.path(HANDLE, 14, PX, 680, 0.5, 'middle')
    head_d, _ = jb.path('DEVELOPER ID', 10, PX, 424, 3, 'middle')
    strap_txt = 'NANTHAKUMAR K  \u2022  FULL STACK DEVELOPER  \u2022  '
    strap_txt = strap_txt.replace('\u2022', '*')
    st_d, st_w = jb.path(strap_txt, 12, 0, 0, 1.2)

    # barcode seeded from the handle
    br = rng(sum(ord(c) for c in HANDLE))
    bars, bx = [], 196.0
    while bx < 364:
        w = br.choice([1.5, 1.5, 2.5, 3.5]); g = br.choice([1.5, 2, 3])
        bars.append(f'M{f(bx)} 700h{f(w)}v34h-{f(w)}z')
        bx += w + g
    bar_d = ''.join(bars)
    code_d, _ = jb.path('NANTH2006', 8, PX, 752, 4, 'middle')

    strap_text = ''.join(f'<use xlink:href="#st" transform="translate({PX + 4},{f(-880 + i * (st_w + 10))}) rotate(90)"/>'
                         for i in range(int((300 + 880) / (st_w + 10)) + 2))
    ring_dash = f'<circle cx="{PX}" cy="500" r="72" fill="none" stroke="url(#ringG)" stroke-width="4" stroke-linecap="round" stroke-dasharray="330 122">{animT("rotate", [(0, f"0 {PX} 500"), (6, f"360 {PX} 500")], loop=True)}</circle>'
    sparks = ''.join(
        f'<use xlink:href="#star" x="{f(r.uniform(165, 395))}" y="{f(r.uniform(390, 750))}" fill="#fff" opacity=".0" transform="scale(.6)">'
        f'{anim("opacity", [(0, 0), (1, .9), (2, 0)], loop=True, begin=f"{f(r.uniform(0, 4))}s")}</use>' for _ in range(0))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Nanthakumar K ID badge">
<title>Nanthakumar K - ID badge</title>
<defs>
<linearGradient id="strapG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c2105f"/><stop offset=".18" stop-color="#ff4fa3"/><stop offset=".5" stop-color="#ff7bbd"/><stop offset=".82" stop-color="#ff4fa3"/><stop offset="1" stop-color="#c2105f"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f8fafc"/><stop offset=".35" stop-color="#9ca3af"/><stop offset=".6" stop-color="#e5e7eb"/><stop offset="1" stop-color="#6b7280"/></linearGradient>
<linearGradient id="cardG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#26103f"/><stop offset=".5" stop-color="#150a28"/><stop offset="1" stop-color="#0c0517"/></linearGradient>
<linearGradient id="edgeG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff4fa3"/><stop offset=".5" stop-color="#a066ff"/><stop offset="1" stop-color="#ff4fa3"/></linearGradient>
<linearGradient id="ringG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff4fa3"/><stop offset=".5" stop-color="#ffd0ec"/><stop offset="1" stop-color="#a066ff"/></linearGradient>
<linearGradient id="nameG" gradientUnits="userSpaceOnUse" x1="{PX - 120}" y1="0" x2="{PX + 120}" y2="0" spreadMethod="reflect"><stop offset="0" stop-color="#ff4fa3"/><stop offset="1" stop-color="#b78bff"/>{anim("x1", [(0, PX - 120), (4, PX + 20)], loop=True)}{anim("x2", [(0, PX + 120), (4, PX + 260)], loop=True)}</linearGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#7dd3fc" stop-opacity=".35"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset=".65" stop-color="#ff7ac2" stop-opacity=".4"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="glowR"><stop offset=".6" stop-color="#ff4fa3" stop-opacity=".55"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>
<pattern id="weave" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="2" fill="#000" fill-opacity=".10"/></pattern>
<clipPath id="strapClip"><rect x="{PX - 24}" y="-900" width="48" height="1200"/></clipPath>
<clipPath id="cardClip"><rect x="150" y="372" width="260" height="400" rx="26"/></clipPath>
<clipPath id="avClip"><circle cx="{PX}" cy="500" r="62"/></clipPath>
<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="shadow" x="-20%" y="-10%" width="140%" height="130%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#000" flood-opacity=".4"/></filter>
<path id="star" d="M0-7L1.6-1.6L7 0L1.6 1.6L0 7L-1.6 1.6L-7 0L-1.6-1.6Z"/>
<path id="st" d="{st_d}" fill="#fff" fill-opacity=".92"/>
</defs>
<g>{animT("translate", drop_pts)}
<g>{animT("rotate", swing, begin=f"{t_sw0}s")}{animT("rotate", sway, loop=True, begin=f"{t_sw0 + T_SWING}s")}
  <!-- strap -->
  <g clip-path="url(#strapClip)">
    <rect x="{PX - 24}" y="-900" width="48" height="1200" fill="url(#strapG)"/>
    <rect x="{PX - 24}" y="-900" width="48" height="1200" fill="url(#weave)"/>
    {strap_text}
    <rect x="{PX - 20}" y="-900" width="1" height="1200" fill="#fff" fill-opacity=".45"/><rect x="{PX + 19}" y="-900" width="1" height="1200" fill="#fff" fill-opacity=".45"/>
    <path d="M{PX - 21} -900V300M{PX + 21} -900V300" stroke="#fff" stroke-opacity=".5" stroke-width="1" stroke-dasharray="5 4" fill="none"/>
  </g>
  <!-- clasp -->
  <path d="M{PX - 24} 296h48l-6 22h-36z" fill="url(#metal)" stroke="#4b5563" stroke-width="1"/>
  <rect x="{PX - 8}" y="312" width="16" height="30" rx="6" fill="url(#metal)" stroke="#4b5563" stroke-width="1"/>
  <circle cx="{PX}" cy="305" r="3.2" fill="#374151"/>
  <g>{animT("rotate", cswing, begin=f"{t_sw0}s")}{animT("rotate", csway, loop=True, begin=f"{t_sw0 + T_SWING}s")}
    <!-- ring -->
    <ellipse cx="{PX}" cy="352" rx="15" ry="22" fill="none" stroke="url(#metal)" stroke-width="5"/>
    <ellipse cx="{PX}" cy="352" rx="15" ry="22" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1" transform="translate(-1.5,-1)"/>
    <!-- card -->
    <g filter="url(#shadow)"><rect x="150" y="372" width="260" height="400" rx="26" fill="url(#cardG)"/></g>
    <rect x="150" y="372" width="260" height="400" rx="26" fill="url(#cardG)" fill-opacity=".92"/>
    <rect x="151.5" y="373.5" width="257" height="397" rx="25" fill="none" stroke="url(#edgeG)" stroke-width="2"><animate attributeName="stroke-opacity" values=".6;1;.6" dur="3s" repeatCount="indefinite"/></rect>
    <rect x="156" y="378" width="248" height="385" rx="21" fill="none" stroke="#fff" stroke-opacity=".08"/>
    <path d="M150 372h120l-150 400h0v-374a26 26 0 0 1 26-26z" fill="#fff" fill-opacity=".045" clip-path="url(#cardClip)"/>
    <rect x="252" y="382" width="56" height="12" rx="6" fill="#06020c" stroke="#ff4fa3" stroke-opacity=".5"/>
    <path d="{head_d}" fill="#c8b3e6" fill-opacity=".8"/>
    <!-- avatar -->
    <circle cx="{PX}" cy="500" r="82" fill="url(#glowR)" opacity=".7">{anim("r", [(0, 78), (1.8, 90), (3.6, 78)], loop=True)}{anim("opacity", [(0, .45), (1.8, .9), (3.6, .45)], loop=True)}</circle>
    <circle cx="{PX}" cy="500" r="69" fill="#0b0414"/>
    <image x="{PX - 62}" y="438" width="124" height="124" xlink:href="data:image/png;base64,{face}" clip-path="url(#avClip)" preserveAspectRatio="xMidYMid slice"/>
    <circle cx="{PX}" cy="500" r="62" fill="none" stroke="#fff" stroke-opacity=".18"/>
    <circle cx="{PX}" cy="500" r="72" fill="none" stroke="#ff4fa3" stroke-opacity=".25" stroke-width="4"/>
    {ring_dash}
    <!-- text -->
    <path d="{name_d}" fill="url(#nameG)"/>
    <path d="{role_d}" fill="#ffffff" fill-opacity=".92"/>
    <path d="{hand_d}" fill="#ff7ac2"/>
    <rect x="196" y="690" width="168" height="1" fill="#ff4fa3" fill-opacity=".35"/>
    <path d="{bar_d}" transform="translate(0,2)" fill="#f6ebff" fill-opacity=".9"/>
    <path d="{code_d}" fill="#b7a0d8" fill-opacity=".8"/>
    <!-- holographic shine sweep -->
    <g clip-path="url(#cardClip)" style="mix-blend-mode:screen">
      <path d="M0 372h110l-130 400h-110z" fill="url(#shine)" transform="translate(-200,0)" opacity="0">
        {animT("translate", [(0, "-200,0"), (1.8, "640,0"), (5.5, "640,0")], loop=True, begin="3s")}{anim("opacity", [(0, 0), (.1, 1), (1.7, 1), (1.8, 0), (5.5, 0)], loop=True, begin="3s")}
      </path>
    </g>
  </g>
</g>
</g>
</svg>'''
    return svg


if __name__ == '__main__':
    s = build()
    open(os.path.join(ROOT, 'lanyard.svg'), 'w').write(s)
    print('lanyard.svg', len(s) // 1024, 'KB')
