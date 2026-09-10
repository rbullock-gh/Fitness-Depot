# Launch checklist

Work top to bottom. Items 1–4 must be done before the site goes live; the rest drive the
local-search results the brief is aimed at.

## 1. Set the real domain (required)

The site ships with a placeholder domain. One command points everything at the real one:

```bash
./tools/set-domain.sh https://your-real-domain.com
```

That rewrites the canonical tag, the Open Graph and Twitter tags, the structured data,
`sitemap.xml` and `robots.txt` in one pass. Run it with no arguments to see the current
setting.

### Why this matters for link previews

When the site's address is pasted into Instagram, a text message, Facebook or Slack, the
app fetches the page and reads its `og:image` tag to build the preview card. That tag has
to be an **absolute, publicly reachable URL** — a relative path or a placeholder domain
gives the scraper nothing to fetch, and it falls back to a bare link or the host's own
branding.

Once the domain is set and the site is live, the card shows `assets/img/og-image.png` —
the Fitness Depot logo on white with the address and phone number.

Previews are **cached hard**. If a link was shared before the site went live, the old card
sticks. Force a refresh:

- Facebook / Instagram — <https://developers.facebook.com/tools/debug/>, paste the URL, *Scrape Again*
- X — <https://cards-dev.twitter.com/validator>
- iMessage / Slack caches expire on their own; adding `?v=2` to the URL forces a fresh fetch

## 2. Confirm the facts

Work through **`docs/CONTENT-SOURCES.md` → "Needs confirmation before launch"**. The
street number (805 vs 807) is the important one — it must match the Google Business
Profile and every directory listing exactly.

## 3. Add the real photos

See **`docs/PHOTO-CHECKLIST.md`**. The site is presentable with placeholders but will not
convert without real photos of the Columbia facility — the brief is built around them.

## 4. Supply a vector logo if one exists (optional)

The official logo and palette are already in place. The logo source is a raster image,
which is sharp at the sizes the site uses. If the original SVG/EPS is available it is
worth swapping in for future large-format use — see **`docs/BRAND-AND-ASSETS.md`**.

## 5. Check the "Join Now" destination

Every `JOIN NOW` currently points to the official `https://fdgyms.com/columbia`, and
`BOOK A TOUR` to `https://fdgyms.com/book-tour`. If there is a direct sign-up or checkout
URL, point the primary CTA straight at it — every extra click costs conversions. The links
are in `index.html`; search for `fdgyms.com`.

## 6. Add geo coordinates to the schema

Coordinates were left out rather than guessed. Get them by dropping a pin on the building
in Google Maps, then add inside the `HealthClub` block in `index.html`:

```json
"geo": { "@type": "GeoCoordinates", "latitude": 31.xxxxx, "longitude": -89.xxxxx },
```

## 7. Validate before and after deploy

- Rich results / schema: <https://search.google.com/test/rich-results> — expect
  **LocalBusiness** and **FAQ** to be detected.
- Page speed / Core Web Vitals: <https://pagespeed.web.dev/>
- HTML: <https://validator.w3.org/>
- Open the site on a real phone and tap every CTA, especially the sticky bottom bar.

## 8. Local search setup (this is where the rankings come from)

The on-page work is done — schema, headings, alt text, natural local phrasing. The rest is
off-page:

1. **Google Business Profile** is the single biggest factor for "gym near me" searches.
   Claim it, set the category to *Gym* (secondary: *Physical fitness program*, *Tanning
   salon* if applicable), and make the name, address and phone **character-for-character
   identical** to the site.
2. Set GBP hours as **open 24 hours**, and put the staffed desk hours in the description —
   the same distinction the site draws.
3. Upload the same real photos there. GBP photo volume correlates strongly with local
   visibility.
4. Add the website URL, and post the membership offer as a GBP "Offer".
5. Fix the NAP on Yelp, Apple Maps, Bing Places and the Marion County chamber listing.
6. Ask happy members for Google reviews, then publish the genuine ones on the site
   (see the testimonials section of `docs/CONTENT-SOURCES.md`).
7. Submit `sitemap.xml` in Google Search Console and watch which queries land.

## 9. Hosting notes

It is a static site — no build step, no server code. Any static host works (Netlify,
Cloudflare Pages, Vercel, GitHub Pages, or plain shared hosting).

- Serve over **HTTPS** and redirect `http://` and the non-canonical `www`/apex variant.
- Make sure `404.html` is wired up as the error page.
- Enable compression (gzip/brotli) and long `Cache-Control` on `/assets/`.
