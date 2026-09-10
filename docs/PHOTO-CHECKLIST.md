# Photo checklist

Every image on the site is currently a **generated placeholder**, not a photograph. The
build environment's network policy blocked `fdgyms.com` and every image CDN, so no
authentic Fitness Depot photography could be downloaded. Per the accuracy rule, no stock
photos were substituted — each slot is a labelled placeholder instead.

## How to drop in the real photos

1. Save each photo into `assets/img/` using **the same basename** as the placeholder it
   replaces. Any of `.jpg`, `.jpeg`, `.png`, `.webp`, `.avif` works.
   Example: `assets/img/hero-facility.jpg`
2. Run:

   ```bash
   ./tools/apply-photos.sh
   ```

   Every reference is rewritten to the real file and the placeholder is moved to
   `assets/img/_placeholders/`. Safe to run repeatedly as more photos arrive.
3. Update the `width`/`height` attributes in `index.html` for any photo whose proportions
   differ from the placeholder, and adjust the `alt` text if the shot differs from what
   was planned.

## The slots

| Filename (basename) | Where it appears | Target size | What to shoot |
|---|---|---|---|
| `hero-facility` | Hero background | 1600×1100 | Widest, strongest shot of the Columbia floor. It sits under a dark gradient, so favour depth and equipment over faces. |
| `about-community` | "Who We Are" | 1200×900+ | Real members mid-workout. Shown as a tall crop — a **vertical or square original works best here**. |
| `access-247` | 24/7 Access band | 1200×900 | Entry door, fingerprint reader, or the floor lit at night. Also sits under a dark gradient. |
| `equipment-cardio` | Equipment card 01 | 1100×800 | Treadmills / stepmills / ellipticals / spin bikes. |
| `equipment-strength` | Equipment card 02 | 1100×800 | Dumbbell racks, barbells, squat racks, plate-loaded. |
| `equipment-functional` | Equipment card 03 | 1100×800 | The turf functional training area. |
| `training-personal` | Personal training banner | 1200×900 | A trainer working with a member. |
| `recovery-hydromassage` | Recovery feature | 1200×900 | A private HydroMassage recovery room. |
| `recovery-tanning` | (spare) | 900×700 | Tanning room — not currently placed; available if you want it. |
| `kids-area` | Fitness Depot Kids | 1200×900 | The Kid Care room. **No identifiable children without written parental consent.** |
| `gallery-gym-floor` | Gallery (wide) | 1000×750 | Main training floor. |
| `gallery-free-weights` | Gallery | 1000×750 | Free weight area. |
| `gallery-cardio-deck` | Gallery | 1000×750 | Cardio row with TVs. |
| `gallery-squat-racks` | Gallery | 1000×750 | Racks and platforms. |
| `gallery-turf` | Gallery (wide) | 1000×750 | Functional training turf. |
| `gallery-recovery` | Gallery | 1000×750 | HydroMassage / recovery space. |
| `gallery-kids` | Gallery | 1000×750 | Kids room. |
| `gallery-exterior` | Gallery (wide) | 1000×750 | Building exterior and Fitness Depot signage. |
| `og-image` | Social share card | 1200×630 | Best single image of the gym; it is what shows in Facebook/text previews. |

## Shooting and prep notes

- **Landscape** for everything except `about-community`, which renders as a tall crop.
- Export at roughly **2× the target size**, then compress. Aim for **under 300 KB** each
  (WebP at quality ~80 is ideal); the hero and OG image matter most for load speed.
- Shoot when the gym is **clean, lit and genuinely in use**. Empty-gym photos read as
  closed; a handful of real members training reads as busy and welcoming.
- Get **written model releases** from anyone recognisable, and never publish images of
  children without a parent's written consent.
- Keep the natural look — crop and colour-correct, but don't over-filter. The brief calls
  for a real local gym, not a stock-photo gym.
