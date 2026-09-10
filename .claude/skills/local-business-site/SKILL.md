---
name: local-business-site
description: Build or overhaul a marketing website for a local bricks-and-mortar business — gym, salon, contractor, restaurant, clinic, shop — where the goal is turning local searches into walk-ins, calls and signups. Covers sourcing real business facts without inventing any, local SEO and LocalBusiness/FAQ structured data, a placeholder photography system for when real photos aren't available yet, brand colour and logo handling, a single-file shareable preview, and pre-launch validation. Use when asked to build, redesign, pitch or preview a website for a named local business, or when a brief mentions a street address, opening hours, memberships or service pricing for one location.
---

# Local business website

A repeatable pipeline for a site whose job is: someone nearby searches, finds the business,
trusts it, and comes in. Optimised for correctness and conversion, not for novelty.

Read `docs/PLAYBOOK.md` in this repo for the detailed gotchas behind each step.

## The rule that outranks everything else

**Never invent a business fact.** Not prices, hours, amenities, equipment, staff, addresses,
phone numbers, or testimonials. Plausible filler is the default failure mode here, and a
wrong price or a fabricated review is worse for the client than a blank section.

Maintain a source ledger (`docs/CONTENT-SOURCES.md`) with three sections:

- **Verified and used** — claim → where it came from
- **Needs confirmation** — including any conflicts between sources
- **Deliberately excluded** — what was left out and why

Specific traps, all of which came up in a real build:

- **Sources conflict.** Two directories listed different street numbers. Use the official one,
  then raise the conflict as a launch blocker — for local SEO, the address must match
  character-for-character across the site, Google Business Profile and every directory.
- **Brand-wide ≠ this location.** A chain's amenities list is not this branch's amenities list.
- **Third-party ratings are not yours.** Never put a Google/Yelp rating into `aggregateRating`;
  that markup is for first-party reviews. Build the section as an explicit placeholder.
- **No testimonials without real ones.** Ship the section empty with paste-in markup documented.

## Steps

### 1. Source the facts

Get the address, phone, hours, services and pricing from official sources. If the official
site is unreachable, `WebSearch` returns usable extracts. Record every claim in the ledger as
you go — reconstructing sources afterwards does not happen.

Watch for a distinction most local businesses have and most sites blur: **staffed hours vs
access hours**. A 24-hour gym listed with 8–7 hours loses every late-night searcher. Carry the
distinction through the copy, the structured data, and ideally a live "open now" indicator
computed in the business's timezone.

### 2. Get the logo and brand colours before designing surfaces

The artwork dictates the design, not the other way round. A logo with dark lettering on white
needs a light header; a reversed logo allows a dark one. On the opposite ground, put the logo
on a plate rather than recolouring it — recolouring is altering someone's brand.

If the logo arrives pasted into chat rather than as a file, it is not on disk. It *is* in the
session transcript at `~/.claude/projects/<slug>/<session-id>.jsonl` as a base64 image block —
extract it from there rather than approximating it.

**Check contrast before committing to an accent.** A mid-tone brand colour (gold, orange, tan,
mid-green) will fail as text on white while working perfectly on black, and needs three tokens
— fill, large-text-on-light, small-text-on-light. Discovering this after the build means
touching every component. Buttons in such a colour take **dark** text.

### 3. Structure the page around the decision, not the org chart

Order sections the way a decision gets made, each answering the objection the last one raises:

land → understand the business → see the price → picture yourself there → trust it → act

The first screen must answer four silent questions without scrolling: *what is this, where is
it, is it for me, what do I do now.* Keep the primary CTA reachable throughout — sticky header
on desktop, fixed bottom bar on mobile, plus tap-to-call.

### 4. Local SEO that is not keyword stuffing

- `LocalBusiness` (or a subtype like `HealthClub`) structured data: address, phone,
  `openingHoursSpecification`, `amenityFeature`, `areaServed`, `makesOffer`.
- `FAQPage` markup — **the schema questions must match the visible questions exactly**, or the
  markup is invalid. Enforce this in validation, not by eye.
- Omit `geo` coordinates rather than guessing them.
- Work the town and county into headings and alt text naturally. Stuffed pages get filtered.
- Say plainly that the Google Business Profile matters more than the site for map results.

### 5. Photography: placeholders, never stock

If real photos are not available, do **not** substitute stock — it is exactly what visitors
scroll past, and the brief usually forbids it. Generate labelled placeholders at the real
dimensions, with a checklist mapping each slot to the shot it needs.

Two variants: **labelled** for standalone content images, **plain texture** for images sitting
behind headline copy, where a label ghosts through the text and reads as a bug.

Provide a one-command swap (`tools/apply-photos.sh` pattern): drop a real file in with the
placeholder's basename, run it, references rewrite.

### 6. Validate continuously

`tools/check.py` in this repo is the reusable harness. It checks structured-data validity,
FAQ schema/visible parity, missing assets, tag balance, alt text, heading order, broken
anchors, leftover placeholder text, title/description length, and — with `--browser` —
horizontal overflow at 390/820/1440px plus content visibility with JavaScript disabled.

**Assert on computed opacity, not `isVisible()`** — Playwright reports a fully transparent
element as visible, which will hand you a green check on a page that renders nothing.

### 7. Deliver

- **Single-file preview** (`tools/build-demo.py` pattern): inline CSS, JS and images as data
  URIs into one HTML file that opens by double-clicking. The most portable thing to send.
  Replace live iframes with static panels, and label it as a preview.
- **Link previews need a real domain.** `og:image` must be absolute and publicly fetchable; a
  hosted-artifact URL serves the host's own OG tags and cannot be branded. Ship a
  `set-domain.sh` that rewrites canonical, OG, Twitter, schema, sitemap and robots in one pass.
- **Screenshots**: send viewport or per-section captures. Full-page ones run 17,000–25,000px
  tall and get rejected by upload size limits.

## Deliverables checklist

- [ ] Source ledger with all three sections filled in
- [ ] Launch checklist with blockers named (domain, photos, fact conflicts)
- [ ] Logo → favicons, touch icon, social share card
- [ ] `LocalBusiness` + `FAQPage` structured data, validated
- [ ] Sitemap, robots.txt, 404 page
- [ ] `check.py` passing, including the browser pass
- [ ] Single-file preview built
- [ ] README documenting how to edit prices, hours and phone number without a developer
