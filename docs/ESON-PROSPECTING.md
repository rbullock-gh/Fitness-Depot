# Eson the Searcher — prospecting reference

The operator's manual for the lead-finding agent in `.claude/agents/eson.md`. That file
tells the agent how to hunt; this one explains the scoring, the vocabularies, and how to
run and tune a sweep yourself.

---

## 1. What is actually being sold

A business with no website is not necessarily a customer. A business that is **already
being found and cannot convert the traffic** is. That distinction drives the whole rubric.

The strongest lead in this system looks like: forty reviews at 4.7, an active Facebook
page, a Google listing with no website button, and a phone number. Demand exists, the
business is trading, and every searcher hits a dead end. The pitch writes itself, and it
is a fact rather than a claim.

The weakest lead is a business with no web presence *because nobody looks for it*. It
scores well on paper and never converts. That is why `active_social`, reviews and
`paid_ads` carry weight — they are proof that demand exists.

---

## 2. The scoring rubric

Score is `presence + defects + signals`, clamped to 0–100. All weights live at the top of
`tools/eson.py`; edit them there and re-ingest to rescore.

### Presence — how weak is the web presence (the bulk of the score)

| Value | Points | Means |
|---|---|---|
| `none` | 40 | No website found anywhere |
| `facebook_only` | 38 | A Facebook page is the whole web presence |
| `broken` | 36 | Domain is dead, parked or erroring |
| `directory_only` | 34 | Only on Yelp / Yellow Pages / chamber listings |
| `social_only` | 33 | Instagram or similar, no site |
| `outdated` | 22 | Has a site, but it fails the basics |
| `ok` | 0 | Not a lead |

`facebook_only` scores near the top deliberately. The business has already decided a web
presence matters — it just built it on rented land it does not control and cannot rank.
That is a much shorter conversation than convincing someone who has never wanted one.

### Defects — faults you actually observed

| Flag | Points | How you check it |
|---|---|---|
| `no_mobile` | 10 | No `name="viewport"` in the HTML |
| `builder_default` | 8 | "Your site title", lorem ipsum, untouched template copy |
| `no_https` | 8 | `http://` only, or a certificate error |
| `parked` | 8 | "This domain is for sale", registrar parking page |
| `stale_copyright` | 6 | Footer year three or more years old |
| `frames_or_flash` | 6 | `<frameset>`, Flash embeds, "best viewed in" |
| `thin` | 5 | Under ~3 real pages, no service detail |
| `no_gbp_website` | 5 | Google Business Profile has no website button |
| `no_phone_link` | 4 | Phone shown as text, not `tel:` |
| `slow` | 4 | Visibly slow to load |

`no_mobile` is the heaviest because it is the easiest thing in the world to demonstrate
on a call: ask them to open their own site on their phone.

### Signals — is it worth selling to, and can you reach it

| Flag | Points | Means |
|---|---|---|
| `active_social` | +8 | Posted within ~6 months — proof it is trading |
| `reviews_50plus` | +7 | Substantial existing demand |
| `paid_ads` | +6 | Already spends money on marketing |
| `phone_known` | +6 | Reachable |
| `reviews_10plus` | +5 | Some existing demand |
| `address_known` | +4 | |
| `gbp_claimed` | +3 | Someone tends the listing |
| `email_known` | +3 | |
| `agency_built` | −10 | Someone else has the account |
| `chain` | −15 | A franchisee cannot buy its own site |
| `closed_maybe` | −40 | Effectively disqualifying |

### Tiers

| Tier | Score | Meaning |
|---|---|---|
| **A** | 70+ | Call this week |
| **B** | 50–69 | Worth a call |
| **C** | 30–49 | Keep warm |
| **D** | under 30 | Low priority |

---

## 3. Running a sweep

```bash
# 1. Get the query bank
python3 tools/eson.py queries --niche "hvac" --city "Columbia" --state MS

# 2. Hand it to Eson, or run the queries yourself and write findings to JSON

# 3. Merge — scores, tiers and dedupe happen here
python3 tools/eson.py ingest sweep.json

# 4. Work the sheet
python3 tools/eson.py report
python3 tools/eson.py export --tier AB > outreach.csv
```

Deduplication is on phone number, falling back to name+city, so running the same sweep
twice costs nothing and a sweep next month merges into this one. Evidence, defects and
signals union across sightings; status never walks backwards through the funnel.

Track outcomes by editing `status` in the CSV: `new → queued → contacted → replied →
meeting → won | lost`. `report` hides `won`, `lost` and `dnc`.

---

## 4. The guards, and why they are there

`tools/eson.py` rejects a row rather than storing something unusable:

- **No evidence → rejected.** A lead with no source is a guess, and a guess in a call
  list is worse than a short call list.
- **Impossible phone numbers → rejected.** Invalid NANP area or exchange codes, the
  fictional 555 range, repeated or sequential digits. Fabricated numbers are the classic
  way a lead sheet rots: they look right, waste a call, and cost the caller credibility.
- **Placeholder domains → rejected.** `example.com` and friends.
- **Unknown presence / defect / signal → rejected**, with the valid values printed.

Do not work around a rejection. Fix the row, or drop the lead.

---

## 5. Legal and practical rails

- **Public sources only.** No logged-in scraping, no bypassing robots.txt or paywalls.
  Facebook's terms forbid automated collection — read what search engines surface instead,
  which is sufficient and is where the "no Website field" signal comes from anyway.
- **Business contact details only**, as published for customers to use. Not personal data.
- **Cold email is regulated.** In the US, CAN-SPAM requires accurate sender identification,
  a physical postal address, and a working opt-out honoured promptly. Cold *calling* is
  regulated separately — business-to-business rules differ by state, and the federal
  Do Not Call registry covers personal numbers. Know which one you are dialling.
- **`leads/do-not-contact.txt` is absolute** and gitignored along with the ledger.

---

## 6. Sources ranked by hit rate

Observed while building the query bank, best first:

1. **Chamber of commerce member directories.** Businesses currently paying dues, listed
   with a phone number, often with no site. Nothing else comes close.
2. **Google Business Profile listings with no website button.** The single cleanest
   signal, and the easiest pitch.
3. **Facebook pages with no Website field in the About tab.** Same signal, and the page
   itself shows whether the business is still trading.
4. **Sponsor lists** — little league teams, festivals, school programmes. Businesses that
   already spend on local marketing and can be shown a better use of the money.
5. **Yelp and Yellow Pages.** High volume, heavily stale. Verify everything; these
   directories keep listings for businesses that closed years ago.

---

## 7. The close

The strongest close is not a pitch, it is the site. Build a speculative preview with the
`local-business-site` skill, package it with `tools/build-demo.py` as one double-clickable
file, and send that.

Its accuracy rule is the same as Eson's and matters more here, not less: on a spec build
you have no client to check the facts with, so source every price and every hour, and ship
an empty section rather than a plausible invention. `docs/PLAYBOOK.md` §1 has the detail.
