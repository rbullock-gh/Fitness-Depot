#!/usr/bin/env python3
"""Build a single self-contained HTML preview of the site.

Everything is inlined -- CSS, JavaScript and every image as a data URI -- so the
result is one file that can be emailed, opened by double-clicking, or hosted
anywhere, with no assets folder and no web server. Used for client previews.

    python3 tools/build-demo.py

Output: demo/fitness-depot-columbia-preview.html
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "fitness-depot-columbia-preview.html"
ARTIFACT_OUT = ROOT / "demo" / "artifact-fitness-depot-columbia.html"

html = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "assets" / "css" / "styles.css").read_text(encoding="utf-8")
js = (ROOT / "assets" / "js" / "main.js").read_text(encoding="utf-8")

# ---- inline the stylesheet -------------------------------------------------
html = html.replace(
    '<link rel="stylesheet" href="assets/css/styles.css">',
    "<style>\n" + css + "\n</style>",
)

# ---- inline the script -----------------------------------------------------
html = html.replace(
    '<script src="assets/js/main.js" defer></script>',
    "<script>\n" + js + "\n</script>",
)

# ---- inline every image as a data URI --------------------------------------
MIME = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif"}
inlined = 0


def to_data_uri(match):
    global inlined
    path = ROOT / match.group(1)
    if not path.exists():
        return match.group(0)
    mime = MIME.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    inlined += 1
    return 'src="data:%s;base64,%s"' % (mime, b64)


html = re.sub(r'src="(assets/img/[^"]+)"', to_data_uri, html)

# ---- drop references that need a server ------------------------------------
for dead in (
    '<link rel="icon" href="assets/favicon/favicon-32.png" sizes="32x32" type="image/png">',
    '<link rel="apple-touch-icon" href="assets/favicon/apple-touch-icon.png">',
    '<link rel="manifest" href="site.webmanifest">',
):
    html = html.replace(dead, "")

# ---- the map needs a live frame, so the preview shows a static stand-in ----
map_block = re.search(r'<div class="map-frame">.*?</div>', html, re.S)
if map_block:
    html = html.replace(map_block.group(0), """<div class="map-frame map-frame--static">
            <div class="map-static">
              <svg width="34" height="34" aria-hidden="true"><use href="#i-pin"></use></svg>
              <p class="map-static__addr">805 Hwy 98 Bypass<br>Columbia, MS 39429</p>
              <p class="map-static__note">The live site shows an interactive map here.</p>
              <a class="btn btn--sm" href="https://www.google.com/maps/dir/?api=1&amp;destination=Fitness+Depot%2C+805+Hwy+98+Bypass%2C+Columbia%2C+MS+39429" target="_blank" rel="noopener">Get Directions</a>
            </div>
          </div>""")

html = html.replace("</style>", """
/* preview-only: static stand-in for the interactive map */
.map-frame--static { background: var(--fd-ink); border-color: var(--fd-ink); }
.map-static {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  padding: 2rem 1.5rem;
  text-align: center;
  color: var(--white);
}
.map-static svg { color: var(--fd-gold); }
.map-static__addr {
  font-family: var(--display);
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin: 0;
}
.map-static__note { color: var(--steel-light); font-size: 0.9rem; margin: 0 0 0.4rem; }
.preview-note { color: var(--fd-gold); }
</style>""")

# ---- label it, so a shared copy is never mistaken for the live site --------
html = re.sub(
    r"<p>\s*Gym in Columbia MS[^<]*</p>",
    '<p class="preview-note">Design preview &mdash; not the live Fitness Depot website.</p>',
    html,
)
html = html.replace(
    "<title>Fitness Depot Columbia MS | 24/7 Gym in Columbia, Mississippi</title>",
    "<title>Fitness Depot Columbia — website preview</title>",
)
html = html.replace('<meta name="robots" content="index, follow, max-image-preview:large">',
                    '<meta name="robots" content="noindex, nofollow">')

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(html, encoding="utf-8")
kb = OUT.stat().st_size // 1024
print(f"{OUT.relative_to(ROOT)} written — {kb} KB, {inlined} image(s) inlined")

# ---- second output: a body-only fragment for a hosted Artifact page ---------
# The host wraps the file in its own document skeleton, so no doctype/html/head
# /body tags may appear; the title, font link and styles ride at the top.
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
fonts = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', html).group(0)
styles = re.findall(r"<style>.*?</style>", html, re.S)
noscript = re.findall(r"<noscript>.*?</noscript>", html, re.S)
body = re.search(r"<body>(.*)</body>", html, re.S).group(1)

fragment = "\n".join(
    ["<title>Fitness Depot Columbia</title>", fonts] + styles + noscript + [body.strip()]
)
ARTIFACT_OUT.write_text(fragment, encoding="utf-8")
akb = ARTIFACT_OUT.stat().st_size // 1024
print(f"{ARTIFACT_OUT.relative_to(ROOT)} written — {akb} KB (body-only, for hosting)")
