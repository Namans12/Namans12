"""Pixel-art terminal chips for the contact row, plus an X logo tile.

Everything is drawn at 1:1 pixel scale and then upscaled with NEAREST, so the
result stays crisp and blocky. Antialiasing anywhere here would defeat the
point — a "pixelated" look means real pixels, not a smooth render shrunk down.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
FONT = os.path.join(HERE, "PressStart2P.ttf")

# Press Start 2P (SIL Open Font License). Fetched on demand rather than
# committed, so the repo doesn't carry a font binary.
if not os.path.exists(FONT):
    import urllib.request
    url = ("https://github.com/google/fonts/raw/main/ofl/"
           "pressstart2p/PressStart2P-Regular.ttf")
    print("downloading Press Start 2P …")
    urllib.request.urlretrieve(url, FONT)

INK = (13, 17, 23)
PANEL = (22, 27, 34)
CYAN = (34, 211, 238)
VIOLET = (124, 58, 237)
TEAL = (45, 212, 191)
WHITE = (230, 237, 243)
# 2x, not 3x: the chip must be displayed at its exact pixel size in the README.
# Any non-integer scaling in the browser reintroduces the blur this whole
# approach exists to avoid. 2x lands at a 40px row height, close to a badge.
SCALE = 2

os.makedirs(OUT, exist_ok=True)
f = ImageFont.truetype(FONT, 8)


def glyph_email(d, x, y, c):
    d.rectangle([x, y, x + 8, y + 6], outline=c)
    d.line([(x + 1, y + 1), (x + 4, y + 4)], fill=c)
    d.line([(x + 7, y + 1), (x + 4, y + 4)], fill=c)


def glyph_codepen(d, x, y, c):
    # CodePen's mark: a hexagon with a horizontal midline and a vertical spine.
    pts = [(x + 4, y), (x + 8, y + 2), (x + 8, y + 5),
           (x + 4, y + 7), (x, y + 5), (x, y + 2)]
    d.polygon(pts, outline=c)
    d.line([(x, y + 2), (x + 8, y + 2)], fill=c)
    d.line([(x, y + 5), (x + 8, y + 5)], fill=c)
    d.line([(x + 4, y), (x + 4, y + 7)], fill=c)


def glyph_globe(d, x, y, c):
    d.ellipse([x, y, x + 7, y + 7], outline=c)
    d.line([(x, y + 3), (x + 7, y + 3)], fill=c)
    d.line([(x + 3, y), (x + 3, y + 7)], fill=c)


def glyph_discord(d, x, y, c):
    d.rounded_rectangle([x, y + 1, x + 8, y + 6], radius=2, outline=c)
    d.point((x + 3, y + 3), fill=c)
    d.point((x + 5, y + 3), fill=c)
    d.point((x + 2, y + 6), fill=c)
    d.point((x + 6, y + 6), fill=c)


CHIPS = [
    ("chip-email.png",     "EMAIL",     glyph_email,   CYAN),
    ("chip-portfolio.png", "PORTFOLIO", glyph_globe,   VIOLET),
    ("chip-codepen.png",   "CODEPEN",   glyph_codepen, TEAL),
    ("chip-discord.png",   "DISCORD",   glyph_discord, VIOLET),
]

PAD_X, GAP, H = 6, 5, 20

for name, label, glyph, accent in CHIPS:
    prefix = "$ "
    text = prefix + label
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = int(tmp.textlength(text, font=f))
    w = PAD_X + 9 + GAP + tw + PAD_X

    im = Image.new("RGB", (w, H), PANEL)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, H - 1], outline=accent)
    glyph(d, PAD_X, (H - 7) // 2, WHITE)
    ty = (H - 8) // 2
    d.text((PAD_X + 9 + GAP, ty), prefix, font=f, fill=accent)
    d.text((PAD_X + 9 + GAP + int(tmp.textlength(prefix, font=f)), ty),
           label, font=f, fill=WHITE)

    im = im.resize((w * SCALE, H * SCALE), Image.NEAREST)
    im.save(os.path.join(OUT, name))
    print(f"{name:<22} {im.width}x{im.height}")

# ── X logo tile, to replace the outdated animated Twitter bird ──────────────
S = 44
xi = Image.new("RGBA", (S, S), (0, 0, 0, 0))
xd = ImageDraw.Draw(xi)
xd.rounded_rectangle([0, 0, S - 1, S - 1], radius=10, fill=(0, 0, 0, 255))
t = 4.6
for (ax, ay), (bx, by) in ((((12, 11)), (32, 33)), (((32, 11)), (12, 33))):
    xd.line([(ax, ay), (bx, by)], fill=(255, 255, 255, 255), width=int(t))
xi = xi.resize((S * 4, S * 4), Image.LANCZOS)
xi.save(os.path.join(OUT, "x-logo.png"))
print(f"{'x-logo.png':<22} {xi.width}x{xi.height}")
