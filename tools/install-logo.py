#!/usr/bin/env python3
"""Turn the official Fitness Depot logo into every asset the site needs.

    python3 tools/install-logo.py path/to/logo.png

Handles a logo supplied on a solid white background: the background is removed
by flood-filling inward from the border, so white highlights INSIDE the mascot
and the counters of the letters survive. Re-run this whenever a better-quality
original turns up.

Writes:
    assets/img/logo-fitness-depot.png    transparent wordmark + mascot
    assets/img/logo-mark.png             mascot only, for small sizes
    assets/img/og-image.png              1200x630 social share card
    assets/favicon/favicon-32.png        browser tab
    assets/favicon/apple-touch-icon.png  180x180 home-screen icon
    assets/favicon/icon-512.png          PWA / manifest
"""
import sys
import pathlib
from collections import deque

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
GOLD = (201, 162, 39)
INK = (13, 13, 13)
TOL = 22


def strip_background(im: Image.Image) -> Image.Image:
    """Flood-fill transparency inward from the border only.

    A 2px frame is shaved first: lossy encoders often leave a stray dark line on
    an edge, and a single stray pixel would anchor the crop box to the full
    canvas and defeat the trim.
    """
    im = im.convert("RGB")
    if im.width > 8 and im.height > 8:
        im = im.crop((2, 2, im.width - 2, im.height - 2))
    w, h = im.size
    px = im.load()
    visited = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))

    while q:
        x, y = q.popleft()
        i = y * w + x
        if visited[i]:
            continue
        p = px[x, y]
        if not (p[0] >= 255 - TOL and p[1] >= 255 - TOL and p[2] >= 255 - TOL):
            continue
        visited[i] = 1
        if x: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    alpha = Image.frombytes("L", (w, h), bytes(0 if v else 255 for v in visited))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop(out.getbbox())


def save_compact(img: Image.Image, path: pathlib.Path, colors: int = 128) -> None:
    """Flat artwork only needs a small palette; this cuts file size ~5x."""
    pal = img.quantize(colors=colors, method=Image.FASTOCTREE)
    pal.save(path, optimize=True)


def fit(img: Image.Image, box: int, pad: float = 0.86) -> Image.Image:
    """Scale img to fit a square of `box`, covering `pad` of it."""
    target = int(box * pad)
    scale = min(target / img.width, target / img.height)
    return img.resize((max(1, round(img.width * scale)),
                       max(1, round(img.height * scale))), Image.LANCZOS)


def on_ground(img: Image.Image, box: int, ground) -> Image.Image:
    canvas = Image.new("RGBA", (box, box), ground)
    art = fit(img, box)
    canvas.alpha_composite(art, ((box - art.width) // 2, (box - art.height) // 2))
    return canvas


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = pathlib.Path(sys.argv[1])
    if not src.exists():
        print(f"error: {src} not found")
        return 1

    logo = strip_background(Image.open(src))
    print(f"background removed, trimmed to {logo.width}x{logo.height}")

    (ROOT / "assets" / "img").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "favicon").mkdir(parents=True, exist_ok=True)

    # --- full lockup, sized for retina in the header/footer ---
    master = logo.copy()
    master.thumbnail((720, 720), Image.LANCZOS)
    save_compact(master, ROOT / "assets/img/logo-fitness-depot.png")
    print(f"  logo-fitness-depot.png  {master.width}x{master.height}")

    # --- mascot only: the lockup is unreadable below ~100px ---
    w, h = logo.size
    mark = logo.crop((int(w * 0.24), int(h * 0.36), int(w * 0.78), h))
    mark = mark.crop(mark.getbbox())
    mark.thumbnail((384, 384), Image.LANCZOS)
    save_compact(mark, ROOT / "assets/img/logo-mark.png")
    print(f"  logo-mark.png           {mark.width}x{mark.height}")

    # --- favicons: the artwork is black-on-light, so it gets a light ground ---
    for name, box in (("favicon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-512.png", 512)):
        art = mark if box <= 64 else logo
        icon = on_ground(art, box, (255, 255, 255, 255))
        icon.convert("RGB").save(ROOT / "assets/favicon" / name, optimize=True)
        print(f"  {name:<23} {box}x{box}")

    # --- social share card ---
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.rectangle([0, H - 90, W, H], fill=INK)

    art = logo.copy()
    art.thumbnail((760, 360), Image.LANCZOS)
    card.paste(art, ((W - art.width) // 2, 70), art)

    def font(size):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except OSError:
            return ImageFont.load_default()

    def centered(text, y, f, fill):
        tw = d.textbbox((0, 0), text, font=f)[2]
        d.text(((W - tw) // 2, y), text, font=f, fill=fill)

    centered("24/7 GYM IN COLUMBIA, MISSISSIPPI", 470, font(38), INK)
    centered("805 Hwy 98 Bypass  ·  (601) 345-3344", H - 62, font(26), GOLD)
    card.save(ROOT / "assets/img/og-image.png", optimize=True)
    print(f"  og-image.png            {W}x{H}")

    old = ROOT / "assets/img/og-image.svg"
    if old.exists():
        old.unlink()
        print("  removed placeholder og-image.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
