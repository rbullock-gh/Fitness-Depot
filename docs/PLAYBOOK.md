# Build playbook — hard-won notes

Specific, reusable lessons from building this site. Written for the next local-business
site, and for anyone picking this repo up cold. Everything here was learned by hitting it,
not by reading about it.

---

## 1. Accuracy: the rule that shaped the whole build

The brief said *do not invent prices, hours, amenities, testimonials*. That is easy to agree
with and easy to violate by accident, because plausible filler is exactly what a language
model produces when a fact is missing.

**What worked:** a source ledger — [`CONTENT-SOURCES.md`](CONTENT-SOURCES.md) — with three
sections: *verified and used*, *needs confirmation*, *deliberately excluded*. Every factual
claim on the page traces to a row. The third section matters most; it is the record of what
was **left out** and why, which is the part a reviewer cannot reconstruct later.

**Concrete calls made here, worth repeating:**

- **Two sources disagreed** on the street number (805 official vs 807 on Yelp/Giftly). Do not
  silently pick one. Use the official value, then surface the conflict as a launch blocker —
  address consistency directly affects local ranking.
- **Brand-wide ≠ location-specific.** Group fitness classes and red light therapy appear on
  the parent site but were unconfirmed for this location, so they are absent from the page.
- **No `aggregateRating` in schema.** A 4.4 rating existed on a third-party site. Publishing
  someone else's rating as first-party review markup is a policy violation; the section became
  an explicit placeholder instead.
- **No testimonials at all.** The reviews section is built and empty by design, with paste-in
  markup documented. An invented quote is the fastest way to lose a client's trust.

> If a fact cannot be sourced, the honest options are *leave it out* or *mark it unconfirmed*.
> There is no third option, and "it sounds right" is not sourcing.

---

## 2. Environment gotchas

### Egress is allowlisted, and the blocklist is most of the internet

`fdgyms.com` and every image CDN returned `403 CONNECT` through the agent proxy. Only
`fonts.googleapis.com` and `maps.googleapis.com` resolved.

- **Diagnose with** `curl -sS "$HTTPS_PROXY/__agentproxy/status"` — it names the blocked host
  under `recentRelayFailures`. A 403/407 is an org policy denial: report it, do not retry.
- **`WebSearch` still works** and returns extracts of blocked pages. That is how the official
  membership, hours and equipment facts were sourced. Slower than fetching, but sufficient.
- **PyPI is exempt.** `pip install Pillow` succeeded while general egress was blocked, because
  `pypi.org` and `files.pythonhosted.org` sit in the proxy's `noProxy` list. Same for npm,
  crates, Go modules. Reach for a library before concluding you are stuck.

### Getting a user-supplied image out of the conversation

An image pasted into chat is **not written to disk**. It arrives as a content block, so
`find` turns up nothing and there is no upload directory.

It *is* in the session transcript:

```
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

Walk each line's JSON for `{"type": "image", "source": {"media_type": ..., "data": <base64>}}`.
The user's uploads and images you read back with the Read tool are both in there — tell them
apart by media type and size, or by taking the one that appears most recently.

This is how the real logo got into the repo instead of being approximated. **Check the
transcript before telling a user you cannot use the file they just sent you.**

### This container is ephemeral

Anything outside the git repo is gone when the session ends — including `~/.claude/skills/`.
Durable work is committed work. Skills that should survive live in the repo's `.claude/skills/`.

---

## 3. Verification gotchas — where a green check lied

### `isVisible()` returns true for `opacity: 0`

The scroll-reveal blocks start transparent and are un-hidden by an IntersectionObserver. A
Playwright JS-disabled test asserting `isVisible()` **passed** on a page that rendered
nothing below the hero — the elements have a bounding box, so Playwright calls them visible.

```js
// wrong — passes on invisible content
expect(await page.locator('.card').isVisible()).toBe(true);

// right — assert on what the eye actually gets
const faded = await page.evaluate(() =>
  [...document.querySelectorAll('.reveal')]
    .filter(e => parseFloat(getComputedStyle(e).opacity) < 0.99).length);
```

Any opacity/visibility-driven animation needs a `<noscript>` fallback, and the test must
assert on computed style. Both are now enforced by `tools/check.py`.

### Lazy-loaded images report "broken" if you measure too early

`document.images` filtered on `!complete || naturalWidth === 0` reported **15 of 17 broken** —
twice — purely because the scroll pass was faster than decoding. Both times the images were
fine.

Force the issue instead of sleeping longer:

```js
await page.evaluate(() => [...document.images].forEach(i => (i.loading = 'eager')));
await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : i.decode().catch(() => 0))));
```

### Measure, don't guess, when layout overflows

The header nav overlapped the JOIN NOW button. Guessing at padding would have burned several
cycles. Measuring took one:

```
shell=1220  logo=247  nav needs 848  cta=270  ->  needs 1457, overflows by 237
```

That immediately showed the shell cap — not the padding — was the constraint, and that eight
uppercase nav items simply do not fit. Fix was a wider header track plus six items.

**Measure the natural width of each part against the available width.** The number tells you
which lever to pull.

---

## 4. Layout gotchas

### Sibling elements fall into implicit grid columns

The worst-looking bug of the build. In a two-column grid row:

```html
<li>            <!-- grid-template-columns: 3.1rem 1fr -->
  <strong>They land</strong>   <!-- column 2 -->
  <span>The headline …</span>  <!-- column 3 — implicit, ~50px wide -->
</li>
```

`::before` took column 1, `<strong>` took column 2, and `<span>` created an **implicit third
column** about 50px wide, setting roughly one word per line. It looks like a text-wrapping
problem; it is a grid-placement problem.

Fix: place both children explicitly, or wrap them in one element.

```css
.path li::before { grid-column: 1; }
.path strong, .path span { grid-column: 2; }
```

**Rule of thumb:** if a grid row has more children than declared columns, the extras get
squeezed into implicit tracks. Count children against columns.

### Placeholder labels ghost through full-bleed backgrounds

Photo placeholders carried a "PHOTO PLACEHOLDER · 1600×1100" label — useful for standalone
slots, wrong for images sitting *behind* headline copy, where it reads as a rendering bug.

Generate two placeholder variants: labelled for content images, plain texture for background
images. Record what belongs in the unlabelled ones in the photo checklist.

---

## 5. Brand and colour

### A mid-tone brand accent needs three shades, not one

The brand gold `#c9a227` measured:

| Combination | Ratio | Verdict |
|---|---|---|
| gold on black | 8.0:1 | excellent |
| black text on a gold button | 8.0:1 | this is why buttons take black text |
| **white text on a gold button** | **2.4:1** | fails — never |
| **gold text on white** | **2.4:1** | fails — never |
| `--fd-gold-deep` on white | 3.5:1 | large/bold text and icons only |
| `--fd-gold-text` on white | 4.9:1 | small text |

So the palette carries `--fd-gold` (fills and dark-surface accents), `--fd-gold-deep` (large
text on light), `--fd-gold-text` (small text on light). Components pick per surface.

**Run the numbers before designing.** A dark or saturated brand colour usually works as one
token; a mid-tone (gold, orange, mid-green, tan) will not, and discovering that after the
build means touching every component.

### The logo's own ground dictates the header colour

The real logo is black lettering with a gold outline on white — so it needs a light ground.
The header had been made black for gold contrast; the logo reversed that decision. On the
dark footer the artwork sits on a **white plate** rather than being recoloured, because
recolouring is altering the brand.

**Get the logo before choosing surface colours.** It is an input, not a decoration.

---

## 6. Delivery gotchas

### You cannot brand a `claude.ai` artifact's link preview

Fetching a published artifact URL shows the shell's own tags:

```
og:title  "Claude Artifact"
og:image  https://claude.ai/images/claude_ogimage.png
```

The page content loads client-side, so a scraper never sees meta tags written into the
artifact. Sending that link to a client shows a generic Claude card.

**For a branded preview the site must be on its own host**, where `og:image` resolves.
`tools/set-domain.sh` rewrites every absolute URL in one pass. Previews cache hard — re-scrape
via the Facebook sharing debugger after deploying.

`og:image` must be **absolute and publicly fetchable**. A relative path or placeholder domain
gives the scraper nothing. Declare `og:image:width/height/type` too; some scrapers skip
images they cannot pre-size.

### Full-page screenshots are too tall to send

`SendUserFile` rejected full-page captures with HTTP 400 — they were **17,271px** and
**25,778px** tall. Send viewport-sized captures or per-section element screenshots instead.

### A single self-contained file is the most portable deliverable

`tools/build-demo.py` inlines the stylesheet, the script and every image as data URIs into one
HTML file that opens by double-clicking — no server, no assets folder. It emailed, opened
offline and worked from `file://`.

Two adaptations were needed: the map `<iframe>` became a static panel (a frame needs a live
page), and the footer was relabelled so a forwarded copy is not mistaken for the live site.

---

## 7. The order that worked

1. **Source the facts first** and write the ledger. Content decisions drive layout.
2. **Get the real logo and brand colours** before choosing surfaces (see §5).
3. Build content and structure; keep every image slot a labelled placeholder.
4. **Validate continuously** — `python3 tools/check.py --browser`.
5. Publish a single-file preview for review; only put it on a real domain when previews matter.
6. Keep the launch blockers in a checklist, not in your head.

## Commands

```bash
python3 tools/check.py --browser              # validate everything
python3 tools/install-logo.py logo.png        # logo -> icons, share card
./tools/make-placeholders.sh                  # regenerate photo placeholders
./tools/apply-photos.sh                       # swap in real photos
python3 tools/build-demo.py                   # single-file preview
./tools/set-domain.sh https://example.com     # point URLs at the live domain
```
