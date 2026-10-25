import re, sys, resvg_py
def strip(svg):
    svg = re.sub(r'<animate(Transform)?\b[^>]*?/>', '', svg)
    svg = re.sub(r'<style>.*?</style>', '', svg, flags=re.S)
    return svg
src, out = sys.argv[1], sys.argv[2]
bg = sys.argv[3] if len(sys.argv) > 3 else None
svg = strip(open(src).read())
if bg:  # put page colour behind (for transparent svgs)
    svg = re.sub(r'(<svg[^>]*>)', r'\1<rect width="100%" height="100%" fill="' + bg + r'"/>', svg, 1)
png = resvg_py.svg_to_bytes(svg_string=svg, font_dirs=['/home/claude/proj/assets/fonts'])
open(out, 'wb').write(bytes(png))
