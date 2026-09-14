# Lead database

Eson's output. A JSON array of business leads, managed through `tools/leads.py` so that
deduplication and the schema are enforced by code rather than by remembering.

## Where the data lives

`$ESON_DB`, falling back to `leads/leads.json`.

**This repository is public.** A prospect list — named local businesses with notes about
what is wrong with their websites — should not be in it. `leads/*.json` and `leads/*.csv`
are gitignored for that reason, which also means lead data does not survive a remote
container. For a database that persists, point `ESON_DB` at a private repo or a local path:

```bash
export ESON_DB=~/avengers/leads.json          # local
export ESON_DB=../lead-research/leads.json    # a private repo checked out alongside
```

## Commands

```bash
python3 tools/leads.py add --file new-leads.json   # dedupes, records status changes
python3 tools/leads.py find "Mack's Heating"       # already known?
python3 tools/leads.py list --min-score 75         # highest score first
python3 tools/leads.py list --city Columbia --json
python3 tools/leads.py export --csv leads/export.csv
python3 tools/leads.py set-status <id> contacted --note "left voicemail"
python3 tools/leads.py stats
```

## Deduplication

Two records are the same business when **either** the last 10 phone digits match, **or**
the folded name and city match. Folding lowercases, strips punctuation, and drops `llc`,
`inc`, `co`, `company`, `corp`, `the` and `and`, so `ACME HEATING AND AIR, INC.` and
`Acme Heating & Air LLC` in the same town are recognised as one business.

Re-adding a known business is a no-op **unless its `website_status` changed** — that is a
real finding, not a duplicate. The change is written to the record's `history` and the
business is re-scored. A prospect who built a site since you last looked is worth knowing
about; so is one whose site went down.

## Fields

| Field | Notes |
|---|---|
| `id` | Generated from name + city + state |
| `business_name` | **Required.** Official name |
| `industry` | HVAC, roofing, plumbing… |
| `city` / `state` | **Required** |
| `phone` | Public business number, or `Unknown` |
| `website` | URL, or `None Found` |
| `facebook` / `google_profile` | URLs when public |
| `website_status` | **Required.** One of: `No Website`, `Social Only`, `Poor Website`, `Weak Presence`, `Unknown — not inspected`, `Has Good Website` |
| `lead_score` | **Required.** 1–100 |
| `opportunity` | What is wrong or missing |
| `evidence` | What was actually found that supports it |
| `suggested_pitch` | One sentence, specific to this business |
| `source_urls` | URLs used to verify |
| `date_checked` | Date verified |
| `status` | `new` → `reviewed` → `contacted` → `won` / `lost` / `revisit` |
| `first_seen` / `last_checked` | Set automatically |
| `history` | Status and website-status changes over time |

`Unknown` is always a valid value and is always better than a guess. Eson only ever writes
`status: new`; moving a lead down the pipeline is a human decision.
