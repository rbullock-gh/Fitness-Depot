# Launch checklist

Work top to bottom. Items 1–4 must be done before the site goes live; the rest drive the
local-search results the brief is aimed at.

## 1. Set the real domain (required)

The site ships with the placeholder `https://www.fitnessdepotcolumbia.com`. Replace it
everywhere with the live domain:

```bash
grep -rl "www.fitnessdepotcolumbia.com" . --exclude-dir=.git \
  | xargs sed -i "s#https://www.fitnessdepotcolumbia.com#https://YOUR-REAL-DOMAIN#g"
```

That covers the canonical tag, Open Graph/Twitter URLs, the JSON-LD `@id`s and URLs,
`sitemap.xml` and `robots.txt`. Verify with `grep -r "fitnessdepotcolumbia" .` afterwards.

## 2. Confirm the facts

Work through **`docs/CONTENT-SOURCES.md` → "Needs confirmation before launch"**. The
street number (805 vs 807) is the important one — it must match the Google Business
Profile and every directory listing exactly.

## 3. Add the real photos

See **`docs/PHOTO-CHECKLIST.md`**. The site is presentable with placeholders but will not
convert without real photos of the Columbia facility — the brief is built around them.

## 4. Add the real logo artwork

The palette is already the official gold and black. Only the logo artwork is still a
placeholder — see **`docs/BRAND-AND-ASSETS.md`**.

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
