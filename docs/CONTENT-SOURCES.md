# Content accuracy record

Every factual claim on the site is listed here with where it came from. Nothing on the
site was invented. Anything that could not be verified was left off the site entirely and
is listed under **Deliberately excluded** at the bottom.

> **Research constraint:** this site was built in an environment whose network policy
> blocks `fdgyms.com`, so the official pages could not be opened directly. Facts below were
> confirmed through search-engine extracts of the official Fitness Depot pages
> (`fdgyms.com/columbia`, `/faq`, `/about-us`) plus the brief supplied by the owner.
> **Before launch, someone with access to the official site should re-check the table below.**

## Verified and used on the site

| Claim | Source |
|---|---|
| Locally owned, serving South Mississippi | fdgyms.com (about/home) |
| Locations: Laurel, Meridian, McComb, Columbia, Picayune, Ellisville, Wiggins | fdgyms.com |
| "No matter your level of fitness, you'll find your place with us." | fdgyms.com/columbia |
| 805 Hwy 98 Bypass, Columbia, MS 39429 | fdgyms.com/columbia + owner brief |
| (601) 345-3344 | fdgyms.com/columbia, third-party listings |
| Staffed desk: Mon–Thu 8:00 AM–7:00 PM, Fri 8:00 AM–5:00 PM | fdgyms.com (Columbia + Picayune) |
| 24/7 member access | fdgyms.com/columbia |
| 24-hour fingerprint safe access; fingerprint issued to members 16+ | fdgyms.com/columbia, fdgyms.com/faq |
| 24-hour security | fdgyms.com/columbia |
| Month-to-month, no contract, no annual fee | fdgyms.com |
| 30-day notice to cancel; cannot cancel by phone | fdgyms.com/faq |
| Live 2 Lead: $20 biweekly (ACH) | fdgyms.com |
| Live 2 Lead: $50 joining fee, first two weeks free | owner brief |
| Live 2 Lead benefits (app, nutrition tracking, set routine, guest, 2 daily HydroMassage, multi-location access, 24/7 tanning, showers, Kid Care 1st child) | owner brief; app / multi-location / showers / HydroMassage corroborated on fdgyms.com |
| Neighborhood: $99 joining fee, $15 biweekly, 24/7 home-club access, unlimited tanning, showers | owner brief |
| Kid Care: Mon–Thu 4–7 PM, walking age–12, 1st child included, +$10 biweekly, 2 hrs/day | fdgyms.com + owner brief |
| Cardio: treadmills, stepmills, elliptical cross-trainers, spin bikes, cardio TVs | fdgyms.com/columbia |
| Strength: free weights, squat racks, plate-loaded, barbells, dumbbells | fdgyms.com/columbia |
| Turf functional training area | fdgyms.com/columbia |
| Private recovery rooms with HydroMassage | fdgyms.com/columbia |
| Tanning, showers | fdgyms.com |
| Personal training available | fdgyms.com |
| Convenient parking | fdgyms.com/columbia |
| Photo ID + visit during staffed hours to complete signup | fdgyms.com/faq |

## Needs confirmation before launch

1. **Street number — 805 vs 807.** The official Columbia page and the owner brief say
   **805** Hwy 98 Bypass (used site-wide). Several third-party directories (Yelp, Giftly)
   list **807**. Confirm the correct number and make it identical everywhere — the site,
   Google Business Profile, and all directory listings. NAP consistency directly affects
   local ranking.
2. **Neighborhood membership** figures came only from the owner brief; confirm they are
   current for Columbia.
3. **Full-body circuit** — listed in the brief under functional training; confirm it exists
   at Columbia.
4. **Geo coordinates** are intentionally absent from the LocalBusiness schema rather than
   guessed. Add exact lat/long once known (see `docs/LAUNCH-CHECKLIST.md`).

## Deliberately excluded

These appear in Fitness Depot brand-wide material but were **not** confirmed for the
Columbia location, so they are not claimed anywhere on the site:

- **Group fitness classes** — listed brand-wide on fdgyms.com; not confirmed for Columbia.
- **Red light therapy** — listed brand-wide; not confirmed for Columbia.
- **Pickleball** — appears on the McComb page, not Columbia.
- **7-day free trial** — a `fdgyms.com/columbia-7daytrial` page exists, but the Columbia
  offer described in the brief is "first two weeks free", so only that is stated.
- **Equipment brands/models** — no brand names are used anywhere, as instructed.
- **Star ratings / review counts** — a third-party 4.4 rating exists, but aggregate ratings
  from other platforms must not be published as first-party review schema, so no rating is
  shown and no `aggregateRating` is in the schema.
- **Trainer names and bios**, **class schedules**, **email address** — none verified.

## Testimonials

The reviews section (`#reviews` in `index.html`) is an intentional placeholder. **No
testimonials were written**, per the accuracy rule. To publish real ones, replace the two
`.review-slot` blocks with:

```html
<figure class="review-slot">
  <div class="review-slot__stars">
    <svg><use href="#i-star"></use></svg><!-- one per star awarded -->
  </div>
  <blockquote><p>Exact quote, unedited.</p></blockquote>
  <figcaption>First name L. &middot; Member since 2023</figcaption>
</figure>
```

Only publish reviews you have permission to use, quoted accurately. If you add
`Review` schema, it must be first-party reviews collected by Fitness Depot — do not copy
Google or Yelp ratings into `aggregateRating`.
