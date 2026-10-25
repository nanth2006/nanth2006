"""Shared helpers: SMIL keyframes, vector text outlines, base64 images."""
import base64, random
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def f(v):
    if isinstance(v, float):
        s = ('%.2f' % v).rstrip('0').rstrip('.')
        return s if s not in ('', '-0') else '0'
    return str(v)


def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()


def _kf(pts, dur):
    pts = sorted(pts, key=lambda p: p[0])
    T = dur or pts[-1][0] or 1
    if pts[0][0] > 0:
        pts = [(0, pts[0][1])] + pts
    if pts[-1][0] < T:
        pts = pts + [(T, pts[-1][1])]
    kt = ';'.join('%.4f' % min(1, t / T) for t, _ in pts)
    vals = ';'.join(f(v) for _, v in pts)
    return T, kt, vals


def anim(attr, pts, dur=None, loop=False, discrete=False, begin='0s'):
    """Absolute-time keyframes (seconds, value). The BASE attribute must hold the FINAL state."""
    T, kt, vals = _kf(pts, dur)
    mode = 'discrete' if discrete else 'linear'
    rep = 'repeatCount="indefinite"' if loop else 'fill="freeze"'
    return (f'<animate attributeName="{attr}" dur="{f(float(T))}s" begin="{begin}" values="{vals}" '
            f'keyTimes="{kt}" calcMode="{mode}" {rep}/>')


def animT(kind, pts, dur=None, loop=False, discrete=False, begin='0s'):
    T, kt, vals = _kf(pts, dur)
    mode = 'discrete' if discrete else 'linear'
    rep = 'repeatCount="indefinite"' if loop else 'fill="freeze"'
    return (f'<animateTransform attributeName="transform" type="{kind}" dur="{f(float(T))}s" begin="{begin}" '
            f'values="{vals}" keyTimes="{kt}" calcMode="{mode}" {rep}/>')


def blink(period=1.0):
    return (f'<animate attributeName="opacity" dur="{period}s" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'calcMode="discrete" repeatCount="indefinite"/>')


class Outliner:
    """Converts text to SVG path data (vector outlines) via fontTools."""

    def __init__(self, path):
        self.font = TTFont(path)
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font['head'].unitsPerEm
        self.hmtx = self.font['hmtx']

    def _gn(self, c):
        return self.cmap.get(ord(c), '.notdef')

    def width(self, text, size, spacing=0):
        sc = size / self.upm
        return sum(self.hmtx[self._gn(c)][0] * sc + spacing for c in text) - spacing

    def glyphs(self, text, size, x, y, spacing=0, anchor='start'):
        w = self.width(text, size, spacing)
        if anchor == 'middle':
            x -= w / 2
        elif anchor == 'end':
            x -= w
        sc = size / self.upm
        out, cx = [], 0.0
        for ch in text:
            gn = self._gn(ch)
            adv = self.hmtx[gn][0] * sc
            pen = SVGPathPen(self.gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.'))
            self.gs[gn].draw(TransformPen(pen, (sc, 0, 0, -sc, x + cx, y)))
            d = pen.getCommands()
            if d:
                out.append((ch, d, x + cx, adv))
            cx += adv + spacing
        return out, w

    def path(self, text, size, x, y, spacing=0, anchor='start'):
        g, w = self.glyphs(text, size, x, y, spacing, anchor)
        return ''.join(d for _, d, _, _ in g), w


def rng(seed):
    return random.Random(seed)
