# Prospect list — 601 / 769 (south & central Mississippi)

150 real local businesses, ranked as candidates for the same package quoted in
[`docs/proposal/fitness-depot-website-proposal.html`](../docs/proposal/fitness-depot-website-proposal.html)
($2,500 build + $600 optional photos + $25/mo care).

**Files**
| File | What |
|---|---|
| `prospects-601-769.csv` | The list. Open in Sheets/Excel. `status`, `contacted`, `notes` are blank for you to fill. |
| `prospects.json` | Same data, for the tracker page. |
| `build_prospects.py` | Regenerates both. Edit the table at the top to add or re-score prospects. |

---

## Read this before you call anyone

**Every business name here is real** — each came from a web search against Yelp,
YellowPages, the Marion County chamber directory (`business.mcdp.info`), BBB, Healthgrades
and similar. Same rule as the Fitness Depot build: nothing invented.

**But this is a starting list, not a verified call sheet.** Be honest with yourself about
what each column is worth:

- **35 of 150 rows have a phone number** and **49 have a street address** — the ones that
  appeared in a listing extract. The rest are blank *on purpose*. A made-up phone number is
  worse than no phone number, so blanks stayed blank.
- **`web_signal` is an inference, not an audit.** The network here blocks every site except
  search, so no prospect's website could actually be opened and judged. The column records
  whether the business's *own domain* surfaced in search results:

  | value | meaning | count |
  |---|---|---|
  | `none` | only directory listings surfaced — probably has no site | 21 |
  | `fb` | Facebook page only | 2 |
  | `dated` | own domain, on legacy tech (`.php` / `.aspx` / template host) | 3 |
  | `own` | own domain, looks self-managed | 24 |
  | `corp` | franchise/corporate site the local owner can't change | 3 |
  | `unknown` | name confirmed, web presence not established | 97 |

  **97 `unknown` rows is the honest weak spot in this list.** Those are real businesses whose
  web presence wasn't determined. Resolve them before spending a call — see below.

- **Some small-town rows say "Prentiss area" or "Purvis area" rather than a city.** Yelp's
  "near X" searches reach 25+ miles, so the exact town isn't established. Confirm before you
  drive.

- **Chains were deliberately excluded**, not missed: Walmart, Subway, Sonic, McDonald's,
  Zaxby's, Applebee's, Southern Tire Mart, Planet Fitness, Orangetheory, Roto-Rooter, Smile
  Doctors, Dignity Memorial and similar. A location manager cannot buy a website.

---

## Filling the gaps — 20 minutes, and you can do it, I can't

Google Maps has the one field that matters most and no search engine exposes: **whether the
Website button exists at all.**

1. Google Maps → search `hair salon Columbia MS` (or any category + town from the list).
2. Work the pins. A business with **no Website button** is your best possible lead — it is the
   `none` rows, except Maps knows for certain and I could only infer it.
3. For ones that do have a site, **tap it on your phone.** If it pinches-and-zooms, hides the
   phone number, or shows no prices/hours — that's the pitch, and it's the same pitch that's
   already written in your proposal.
4. Fill `phone`, `address`, `web_signal` in the CSV as you go.

That pass converts this from a name list into a call sheet, and it's the part that genuinely
needs a person with an unblocked phone.

---

## How the ranking works

`score = web signal + budget fit + proximity + relationship`

- **Web signal (0–40)** — `none` 40, `fb` 38, `dated` 34, `unknown` 22, `own` 12, `corp` 2.
  No website is the strongest buying signal there is.
- **Budget fit (7–25)** — funeral homes, dentists, vets, med spas, law firms, HVAC/plumbing/
  roofing and event venues score 25: one extra job pays for the whole site. Restaurants and
  cafés score 7 — they're the thinnest margins on the list and the hardest $2,500 to justify.
- **Proximity (8–20)** — Tier 1 Marion County 20, Tier 2 (20–50 min) 14, Tier 3 (50–90 min) 8.
  Weighted heavily because *"I'm in Columbia, we can talk at the gym"* is the strongest line in
  your proposal, and it stops being true past about an hour.
- **Relationship (45)** — applied to Fitness Depot only. An existing conversation with a
  finished spec build beats any cold lead, which is why it ranks #1 despite having a site.

---

## The three things worth doing first

**1. Fitness Depot is seven gyms, not one.** Columbia, Laurel, Meridian, McComb, Picayune,
Ellisville and Wiggins all sit on one corporate site (`fdgyms.com`) with one decision-maker.
You've already built the Columbia page for free. The pitch isn't a $2,500 site — it's seven
location pages, and every one of those towns is already on this list.

**2. The chamber is a better channel than any single row here.** Marion County Development
Partnership, 412 Courthouse Square, (601) 736-6385 — its member directory
(`business.mcdp.info`) is the qualified Marion County list, it's the source several of these
rows came from, and chambers routinely let a member present to the room. That's 30 qualified
prospects in an hour instead of 30 cold calls. Pike County has the same thing at
`business.pikeinfo.com`.

**3. Lead with the finished thing.** You have something almost nobody cold-calling a Columbia
business has: a real, finished, openable site for a business they know. `demo/` is a single
file you can text to someone. "I built this for the gym on 98 — here's what yours would look
like" is a different conversation from "do you need a website."

---

## The honest read on segment quality

The restaurant rows — roughly half the list, concentrated in Tiers 2 and 3 — are the weakest
segment, and they're numerous because small-town searches mostly return restaurants. They rank
low on purpose. **The top ~40 rows are worth more than the bottom 110 combined.** If you only
ever work Tier 1 (54 rows, all Marion County, all inside 20 minutes), that is a better use of a
week than driving to Wiggins.

---

## The tracker

`call-sheet.html` is the same 150 rows as a working call sheet — filter by drive time, by whether
they look like they have a site, and by call status; tap a row for the phone number and notes.
Published at the Artifact link from the session that built it; the local file works standalone too.

Rebuild both after editing `build_prospects.py`:

```bash
python3 prospects/build_prospects.py && python3 prospects/build_tracker.py
```
