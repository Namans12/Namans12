"""Render the official X mark and animate a sheen across it.

The simple-icons X path is all straight-line commands (M/m L/l H/h V/v Z), no
curves, so it can be parsed and filled exactly rather than approximated. The
mark has two subpaths: the outer glyph and an inner counter that must be cut
back out.
"""
import os
import re
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE

# x.svg is the official mark from simple-icons, kept alongside so the render is
# reproducible without a network call:
#   https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/x.svg

svg = open(os.path.join(HERE, "x.svg"), encoding="utf-8").read()
d = re.search(r'\sd="([^"]+)"', svg).group(1)

TOKEN = re.compile(r"([MmLlHhVvZz])|(-?\d*\.?\d+)")


def parse(path):
    """Return a list of subpaths, each a list of (x, y) points."""
    toks = [(c, n) for c, n in TOKEN.findall(path)]
    subs, cur = [], []
    x = y = 0.0
    cmd = None
    i = 0
    nums = []

    def flush_point(px, py):
        cur.append((px, py))

    while i < len(toks):
        c, n = toks[i]
        if c:
            if c in "Zz":
                if cur:
                    subs.append(cur)
                    cur = []
            cmd = c
            i += 1
            continue
        # gather numbers for the active command
        nums = []
        need = {"M": 2, "m": 2, "L": 2, "l": 2, "H": 1, "h": 1, "V": 1, "v": 1}[cmd]
        while i < len(toks) and not toks[i][0] and len(nums) < need:
            nums.append(float(toks[i][1]))
            i += 1
        if cmd == "M":
            x, y = nums
            if cur:
                subs.append(cur)
            cur = []
            flush_point(x, y)
            cmd = "L"                      # extra pairs after M are linetos
        elif cmd == "m":
            x, y = x + nums[0], y + nums[1]
            if cur:
                subs.append(cur)
            cur = []
            flush_point(x, y)
            cmd = "l"
        elif cmd == "L":
            x, y = nums
            flush_point(x, y)
        elif cmd == "l":
            x, y = x + nums[0], y + nums[1]
            flush_point(x, y)
        elif cmd == "H":
            x = nums[0]
            flush_point(x, y)
        elif cmd == "h":
            x = x + nums[0]
            flush_point(x, y)
        elif cmd == "V":
            y = nums[0]
            flush_point(x, y)
        elif cmd == "v":
            y = y + nums[0]
            flush_point(x, y)
    if cur:
        subs.append(cur)
    return subs


subpaths = parse(d)
print("subpaths:", [len(s) for s in subpaths])

SIZE = 104          # delivered size; shown at 52 so it stays sharp
SS = 4              # supersample
S = SIZE * SS
MARK = 0.54         # mark size as a fraction of the tile
RADIUS = int(S * 0.22)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (34, 211, 238)


def mark_mask():
    """1-bit-ish mask of the X glyph at supersampled resolution."""
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    span = S * MARK
    off = (S - span) / 2
    def tx(p):
        return (off + p[0] / 24.0 * span, off + p[1] / 24.0 * span)
    md.polygon([tx(p) for p in subpaths[0]], fill=255)
    for hole in subpaths[1:]:
        md.polygon([tx(p) for p in hole], fill=0)
    return m


mask = mark_mask()
MARK_BBOX = mask.getbbox()
print("glyph bbox:", MARK_BBOX)

# Rounded black tile with transparent corners.
tile_alpha = Image.new("L", (S, S), 0)
ImageDraw.Draw(tile_alpha).rounded_rectangle([0, 0, S - 1, S - 1], radius=RADIUS, fill=255)

# Every frame sweeps — no idle frames. PIL drops any frame identical to the one
# before it, so a static tail would silently vanish and shorten the loop. The
# pause between sweeps comes from a long duration on the final frame instead.
FRAMES = 24
SWEEP = FRAMES
frames = []
for i in range(FRAMES):
    base = Image.new("RGB", (S, S), BLACK)
    glyph = Image.new("RGB", (S, S), WHITE)

    if True:
        # A diagonal band of cyan travelling across the glyph. The travel is
        # bounded to the mark's own span so each frame visibly differs.
        t = i / (FRAMES - 1)
        band = Image.new("L", (S, S), 0)
        bd = ImageDraw.Draw(band)
        width = S * 0.42
        # Bound the travel to the glyph's own bounding box. Each band line runs
        # from (pos, -S) to (pos + 1.6S, 2S), so at the mark's vertical centre
        # it sits at pos + 0.8S. Solving for that keeps the highlight on the
        # glyph in every single frame — which is what stops PIL discarding
        # frames as duplicates.
        x0, _, x1, _ = MARK_BBOX
        start = x0 - 0.8 * S - width
        end = x1 - 0.8 * S + width
        centre = start + t * (end - start)
        steps = 26
        for k in range(steps):
            frac = k / (steps - 1)
            pos = centre - width / 2 + frac * width
            intensity = int(255 * (1 - abs(frac - 0.5) * 2) ** 1.5)
            bd.line([(pos, -S), (pos + S * 1.6, S * 2)], fill=intensity, width=int(width / steps) + 2)
        glyph = Image.composite(Image.new("RGB", (S, S), CYAN), glyph, band)

    base.paste(glyph, (0, 0), mask)
    out = base.convert("RGBA")
    out.putalpha(tile_alpha)
    frames.append(out.resize((SIZE, SIZE), Image.LANCZOS))

os.makedirs(OUT, exist_ok=True)

# Static PNG (crisp, no animation) kept as a fallback/alternative.
frames[-1].save(os.path.join(OUT, "x-logo.png"))

# GIF needs a flat background behind the 1-bit alpha, or edges fringe white.
flats = []
for fr in frames:
    flat = Image.new("RGB", (SIZE, SIZE), (13, 17, 23))
    flat.paste(fr, (0, 0), fr)
    flats.append(flat)

# One shared palette for every frame, and optimize=False. Quantising each frame
# independently lets PIL treat near-identical frames as duplicates and silently
# drop them — that collapsed a 30-frame sweep down to 9 and made it stutter.
master = Image.merge("RGB", [
    Image.new("L", (SIZE, SIZE * len(flats))) for _ in range(3)
])
strip = Image.new("RGB", (SIZE, SIZE * len(flats)))
for i, f in enumerate(flats):
    strip.paste(f, (0, i * SIZE))
master = strip.convert("P", palette=Image.ADAPTIVE, colors=128)

gif = [f.quantize(palette=master, dither=Image.NONE) for f in flats]

gif[0].save(
    os.path.join(OUT, "x-logo.gif"),
    save_all=True, append_images=gif[1:],
    duration=[45] * (FRAMES - 1) + [1600],
    loop=0, optimize=False, disposal=1,
)
print("png", os.path.getsize(os.path.join(OUT, "x-logo.png")) // 1024, "KB")
print("gif", os.path.getsize(os.path.join(OUT, "x-logo.gif")) // 1024, "KB")
