#!/usr/bin/env python3
"""Validate the site before publishing or handing it to a client.

    python3 tools/check.py              # static checks, no dependencies
    python3 tools/check.py --browser    # also render in Chromium (needs Playwright)

Static checks run anywhere. The browser pass catches the two classes of bug that
only appear once the page is actually laid out: horizontal overflow, and content
left invisible when JavaScript is off.

Exit code is 0 when everything passes, 1 when any check fails.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ["index.html", "404.html"]

# void elements plus the SVG shapes that are legitimately self-closing
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
    "path", "circle", "rect", "use", "stop", "line", "polygon", "polyline", "ellipse",
}

failures: list[str] = []
warnings: list[str] = []


def fail(msg): failures.append(msg)
def warn(msg): warnings.append(msg)


class TagBalance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.problems.append(f"line {self.getpos()[0]}: unexpected </{tag}>")

    def report(self):
        return self.problems + [f"line {ln}: <{t}> never closed" for t, ln in self.stack]


def check_page(page: str) -> None:
    path = ROOT / page
    if not path.exists():
        fail(f"{page}: missing")
        return
    html = path.read_text(encoding="utf-8")
    print(f"\n  {page}")

    # --- structured data -------------------------------------------------
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            fail(f"{page}: JSON-LD block {i} is invalid — {e}")
            continue
        graph = data.get("@graph", [data])
        print(f"    schema           {[n.get('@type') for n in graph]}")

        # Google requires every FAQ answer to be visible on the page, so the
        # schema questions must match the rendered ones exactly.
        faqs = [n for n in graph if n.get("@type") == "FAQPage"]
        if faqs:
            visible = {norm(s) for s in re.findall(r"<summary>(.*?)</summary>", html, re.S)}
            asked = [q["name"] for q in faqs[0]["mainEntity"]]
            missing = [q for q in asked if norm(q) not in visible]
            if missing:
                fail(f"{page}: FAQ schema questions with no visible counterpart: {missing}")
            else:
                print(f"    faq parity       {len(asked)} questions match the page")

    # --- local files actually exist --------------------------------------
    refs = {
        r for r in re.findall(r'(?:src|href)="((?!https?:|tel:|mailto:|#|data:)[^"]+)"', html)
        if r != "/" and not r.startswith("/#")
    }
    missing = sorted(r for r in refs if not (ROOT / r.lstrip("/")).exists())
    if missing:
        fail(f"{page}: references missing files: {missing}")
    print(f"    asset refs       {len(refs)} checked, {len(missing)} missing")

    # --- icon sprite -----------------------------------------------------
    defined = set(re.findall(r'<symbol id="([^"]+)"', html))
    used = set(re.findall(r'<use href="#([^"]+)"', html))
    if used - defined:
        fail(f"{page}: <use> references undefined icons: {sorted(used - defined)}")
    if defined - used:
        warn(f"{page}: unused icon symbols: {sorted(defined - used)}")

    # --- markup ----------------------------------------------------------
    balance = TagBalance()
    balance.feed(html)
    for problem in balance.report()[:10]:
        fail(f"{page}: {problem}")

    # --- images ----------------------------------------------------------
    imgs = re.findall(r"<img\s[^>]*>", html)
    no_alt = [i for i in imgs if "alt=" not in i]
    no_dims = [i for i in imgs if "width=" not in i or "height=" not in i]
    if no_alt:
        fail(f"{page}: {len(no_alt)} <img> without alt")
    if no_dims:
        warn(f"{page}: {len(no_dims)} <img> without width/height (causes layout shift)")
    print(f"    images           {len(imgs)}, {len(no_alt)} without alt")

    # --- headings --------------------------------------------------------
    levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])[\s>]", html)]
    h1s = levels.count(1)
    if h1s != 1:
        fail(f"{page}: expected exactly one <h1>, found {h1s}")
    jumps = [f"h{levels[i-1]}->h{levels[i]}" for i in range(1, len(levels)) if levels[i] > levels[i-1] + 1]
    if jumps:
        warn(f"{page}: heading level jumps: {jumps}")
    print(f"    headings         {h1s} h1, {len(jumps)} level jumps")

    # --- in-page links ---------------------------------------------------
    anchors = {a for a in re.findall(r'href="#([^"]+)"', html) if a}
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    broken = sorted(anchors - ids)
    if broken:
        fail(f"{page}: anchors point at ids that do not exist: {broken}")

    # --- unfinished content ----------------------------------------------
    for marker in ("[ your", "[ fee", "[ date", "[ timeline", "lorem ipsum", "TODO:", "FIXME:"):
        if marker.lower() in html.lower():
            fail(f'{page}: unfinished placeholder text left in the page: "{marker}"')

    # --- search metadata (index only) ------------------------------------
    if page == "index.html":
        title = re.search(r"<title>(.*?)</title>", html)
        desc = re.search(r'<meta name="description" content="(.*?)"', html)
        if not title:
            fail("index.html: no <title>")
        elif len(title.group(1)) > 65:
            warn(f"index.html: title is {len(title.group(1))} chars (search results cut off near 60)")
        if not desc:
            fail("index.html: no meta description")
        elif not 120 <= len(desc.group(1)) <= 165:
            warn(f"index.html: meta description is {len(desc.group(1))} chars (aim for 120-165)")
        if not re.search(r'rel="canonical"', html):
            fail("index.html: no canonical tag")
        if "<noscript>" not in html and "reveal" in html:
            fail("index.html: scroll-reveal is used with no <noscript> fallback — "
                 "content stays invisible when JavaScript is off")
        print(f"    title            {len(title.group(1)) if title else 0} chars")
        print(f"    description      {len(desc.group(1)) if desc else 0} chars")


def norm(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    for a, b in (("&rsquo;", "'"), ("&amp;", "&"), ("&mdash;", "—"), ("&ndash;", "–")):
        text = text.replace(a, b)
    return " ".join(text.split()).lower()


def check_domain() -> None:
    """A placeholder domain silently breaks link-preview cards."""
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'rel="canonical" href="([^"]+)"', html)
    if not m:
        return
    domain = m.group(1)
    print(f"\n  domain\n    canonical        {domain}")
    if "fitnessdepotcolumbia.com" in domain:
        warn("index.html: still on the placeholder domain — run tools/set-domain.sh "
             "before launch or link previews will not resolve")
    og = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if og and not og.group(1).startswith("http"):
        fail("og:image must be an absolute URL or scrapers cannot fetch it")


def check_browser() -> None:
    """Render the page: catch overflow and JS-off invisibility."""
    print("\n  browser")
    script = r"""
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const url = process.argv[2];
const b = await chromium.launch();
const out = { overflow: [], hiddenNoJs: null, errors: [] };
for (const w of [390, 820, 1440]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  p.on('pageerror', e => out.errors.push(`${w}px: ${e.message}`));
  await p.goto(url, { waitUntil: 'load' });
  await p.evaluate(async () => { for (let y=0;y<document.body.scrollHeight;y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,20));} });
  await p.waitForTimeout(400);
  const over = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (over) out.overflow.push(w);
  await p.close();
}
const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
const np = await ctx.newPage();
await np.goto(url, { waitUntil: 'load' });
await np.waitForTimeout(300);
// isVisible() reports true for opacity:0, so assert on computed opacity instead
out.hiddenNoJs = await np.evaluate(() =>
  [...document.querySelectorAll('.reveal')].filter(e => parseFloat(getComputedStyle(e).opacity) < 0.99).length);
await b.close();
console.log(JSON.stringify(out));
"""
    if not pathlib.Path("/opt/node22/lib/node_modules/playwright/index.mjs").exists():
        warn("Playwright not found — skipped the browser pass")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as f:
        f.write(script)
        script_path = f.name
    url = (ROOT / "index.html").as_uri()
    try:
        res = subprocess.run(["node", script_path, url], capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            warn(f"browser pass could not run: {res.stderr.strip().splitlines()[-1] if res.stderr.strip() else '?'}")
            return
        data = json.loads(res.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001
        warn(f"browser pass could not run: {e}")
        return
    finally:
        os.unlink(script_path)

    if data["overflow"]:
        fail(f"horizontal overflow at {data['overflow']} px — the page scrolls sideways")
    print(f"    overflow         none at 390/820/1440px" if not data["overflow"] else "")
    if data["hiddenNoJs"]:
        fail(f"{data['hiddenNoJs']} reveal blocks stay transparent with JavaScript off")
    else:
        print("    javascript off   all content visible")
    for e in data["errors"]:
        fail(f"page error {e}")


def main() -> int:
    print("Checking site")
    for page in PAGES:
        check_page(page)
    check_domain()
    if "--browser" in sys.argv:
        check_browser()

    print("\n" + "-" * 60)
    for w in warnings:
        print(f"  warn  {w}")
    for f_ in failures:
        print(f"  FAIL  {f_}")
    print("-" * 60)
    if failures:
        print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
        return 1
    print(f"All checks passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
