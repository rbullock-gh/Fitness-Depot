# Fitness Depot Columbia — website

A modern, mobile-first marketing site for **Fitness Depot Columbia**, the locally owned
24/7 gym at 805 Hwy 98 Bypass in Columbia, Mississippi, serving Marion County and the
surrounding South Mississippi area.

Static HTML, CSS and vanilla JavaScript — no build step, no dependencies, no framework.
Open `index.html` and it runs.

## See it now

`demo/fitness-depot-columbia-preview.html` is a **single self-contained file** — CSS,
JavaScript and every image inlined. Double-click it and it opens; no server, no assets
folder, nothing to install. Email it, drop it in a shared folder, or open it on a phone.
It is labelled as a preview in the footer so a forwarded copy is never mistaken for the
live site, and the interactive map is a static stand-in (a live map needs a real page).

Rebuild it after any change:

```bash
python3 tools/build-demo.py
```

## Run it locally

```bash
npx http-server -p 8000     # or: python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Before you deploy

Two things ship as placeholders and need real assets. **Start with
[`docs/LAUNCH-CHECKLIST.md`](docs/LAUNCH-CHECKLIST.md)** — it covers all of them in order.

| What | Why | Where |
|---|---|---|
| **Photography** | The build environment's network policy blocked `fdgyms.com` and every image CDN, so no authentic Fitness Depot photos could be downloaded. Rather than substitute stock photos, every slot is a labelled placeholder. | [`docs/PHOTO-CHECKLIST.md`](docs/PHOTO-CHECKLIST.md) |
| **Live domain** | The canonical URL, Open Graph tags, schema and sitemap use a placeholder domain. | [`docs/LAUNCH-CHECKLIST.md`](docs/LAUNCH-CHECKLIST.md) §1 |

Everything factual on the site — pricing, hours, amenities, equipment, Kid Care details —
is sourced and recorded in [`docs/CONTENT-SOURCES.md`](docs/CONTENT-SOURCES.md), including
the handful of items that still need confirmation and the claims deliberately left off.
**Nothing was invented.**

## Structure

```
index.html              The whole site — one page, all sections
404.html                Error page
site.webmanifest        PWA/app metadata
robots.txt, sitemap.xml Search engine directives
assets/
  css/styles.css        Design system + all styles (brand tokens at the top)
  js/main.js            Nav, scroll reveal, scrollspy, deferred map, desk status
  img/                  Photo placeholders — swap for real photos
  favicon/              Favicon + apple touch icon (placeholders)
demo/                   Self-contained single-file preview for sharing
tools/
  set-domain.sh         Points every absolute URL at the live domain
  install-logo.py       Regenerates the logo, icons and share card from a source file
  make-placeholders.sh  Regenerates the placeholder images
  apply-photos.sh       Swaps placeholders for real photos in one command
  build-demo.py         Rebuilds the single-file preview
docs/                   Launch checklist, photo checklist, brand notes, source record
```

## Page sections

Hero → About → Why Choose → **Memberships** → 24/7 Access → Equipment & Training →
Recovery & Wellness → Fitness Depot Kids → Gallery → Reviews → Location → FAQ →
Get Started.

The conversion path runs land → understand → see membership value → see the facility →
build trust → join. `JOIN NOW` is reachable from the sticky header on desktop, a sticky
bottom bar on mobile, and every major section.

## How it's built

- **No framework.** One stylesheet, one small script. Fast by default, and any web
  developer can maintain it.
- **Progressive enhancement.** Every section works with JavaScript disabled; the FAQ uses
  native `<details>`, the nav degrades to plain anchors.
- **Accessible.** Skip link, landmarks, one `h1` with a clean heading order, visible focus
  rings, `aria` on the nav toggle, alt text on every image, and full
  `prefers-reduced-motion` support.
- **Local SEO.** `LocalBusiness`/`HealthClub` + `FAQPage` structured data, location-aware
  headings and alt text, and a staffed-hours vs 24/7-access distinction carried through the
  copy, the schema and a live "front desk open now" indicator computed in Central time.
- **Responsive.** Verified with no horizontal overflow at 390px, 820px and 1440px.

## Editing common things

| Change | Where |
|---|---|
| Brand colours | `--fd-gold*` / `--fd-ink*` variables at the top of `assets/css/styles.css` (read the three-golds note in the brand doc first) |
| Phone number | Search `6013453344` and `(601) 345-3344` in `index.html` |
| Address | Search `805 Hwy 98 Bypass` in `index.html` |
| Hours | The Location section, the JSON-LD `openingHoursSpecification`, and `STAFFED` in `assets/js/main.js` |
| Membership pricing | The `#memberships` section **and** the `makesOffer` block in the JSON-LD **and** the FAQ answer |
| FAQ | Keep the visible `<summary>` text and the JSON-LD question identical — Google requires the answer to be visible on the page |
