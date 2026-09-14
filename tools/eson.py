#!/usr/bin/env python3
"""Eson the Searcher — the lead ledger behind the prospecting agent.

    python3 tools/eson.py queries --niche roofing --city Columbia --state MS
    python3 tools/eson.py ingest candidates.json     # add/merge a sweep's findings
    python3 tools/eson.py add --name "..." --city "..." --presence none --evidence "..."
    python3 tools/eson.py report                     # markdown, grouped by tier
    python3 tools/eson.py export --tier A            # CSV for outreach
    python3 tools/eson.py status
    python3 tools/eson.py dnc "Business name"        # never contact again

The ledger is a CSV. It is the only place leads live, so a sweep run next month
merges into last month's work instead of starting over. Rows are deduped on
phone number, falling back to name+city.

Every row must carry evidence. A lead with no source is a guess, and a guess in
a call list is worse than an empty call list — see the accuracy rule in
docs/ESON-PROSPECTING.md.

Exit code is 0 on success, 1 when a row is rejected or a file is missing.
"""
import argparse
import csv
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "leads" / "leads.csv"
DNC_FILE = ROOT / "leads" / "do-not-contact.txt"

FIELDS = [
    "name", "category", "city", "state", "phone", "email", "address",
    "presence", "url", "evidence", "defects", "signals", "pitch", "notes",
    "score", "tier", "status", "first_seen", "last_seen",
]

# How weak is the web presence? This is the bulk of the score, because it is
# the thing being sold. Ordered strongest opportunity first.
PRESENCE = {
    "none":           (40, "no website found anywhere"),
    "facebook_only":  (38, "a Facebook page is the whole web presence"),
    "broken":         (36, "domain is dead, parked or erroring"),
    "directory_only": (34, "only listed on Yelp/YP/chamber directories"),
    "social_only":    (33, "Instagram or similar only, no site"),
    "outdated":       (22, "has a site, but it is failing the basics"),
    "ok":             (0,  "site is fine — not a lead"),
}

# Observable faults. Each must be something that was actually checked.
DEFECTS = {
    "no_mobile":        10,  # no viewport meta / fixed-width layout
    "builder_default":   8,  # "Your site title", lorem ipsum, template stock copy
    "no_https":          8,
    "parked":            8,
    "stale_copyright":   6,  # footer year 3+ years old
    "frames_or_flash":   6,
    "thin":              5,  # under ~3 real pages, no service detail
    "no_gbp_website":    5,  # Google Business Profile has no website button
    "no_phone_link":     4,  # phone on page but not tap-to-call
    "slow":              4,
}

# Is this a business worth selling to, and can it be reached?
SIGNALS = {
    "phone_known":      6,
    "active_social":    8,   # posted within ~6 months — proof it is trading
    "reviews_50plus":   7,
    "reviews_10plus":   5,
    "address_known":    4,
    "gbp_claimed":      3,
    "email_known":      3,
    "paid_ads":         6,   # already spends money on marketing
    "agency_built":   -10,   # someone else has the account
    "chain":          -15,   # a franchisee cannot buy its own site
    "closed_maybe":   -40,   # the number one false positive
}

TIERS = [(70, "A"), (50, "B"), (30, "C"), (0, "D")]
STATUSES = ["new", "queued", "contacted", "replied", "meeting", "won", "lost", "dnc"]
# A lead never walks backwards through the funnel on a re-sweep.
STATUS_RANK = {s: i for i, s in enumerate(STATUSES)}

FAKE_DOMAINS = {"example.com", "example.org", "example.net", "test.com", "domain.com"}

QUERY_BANK = [
    ("Chamber & civic lists — real trading businesses, often no site at all", [
        '"{city}" "{state}" chamber of commerce member directory',
        '"{city} {state}" "{niche}" chamber of commerce',
        '"{city}" {state} business license list {niche}',
    ]),
    ("Facebook-only shops — read what search engines surface, never crawl the platform", [
        'site:facebook.com "{niche}" "{city}, {state}"',
        'site:facebook.com "{city}, {state}" "{niche}" "Message" OR "Call Now"',
        'site:m.facebook.com "{niche}" "{city}"',
    ]),
    ("Directory-only — a business whose entire footprint is someone else's site", [
        'site:yelp.com "{city}, {state}" {niche}',
        'site:yellowpages.com "{city}" "{state}" {niche}',
        'site:manta.com OR site:chamberofcommerce.com "{city}" {niche}',
        'site:bbb.org "{city}, {state}" {niche}',
        'site:nextdoor.com "{city}" {niche} recommendations',
    ]),
    ("Broken or parked — they bought a domain and it lapsed", [
        '"{niche}" "{city}, {state}" "this domain is for sale"',
        '"{niche}" "{city}" "under construction" OR "coming soon"',
        '"{niche}" "{city}, {state}" "site temporarily unavailable"',
    ]),
    ("Dated builds — a site exists, but it is a decade old", [
        '"{niche}" "{city}, {state}" "copyright 2014" OR "copyright 2015" OR "copyright 2016"',
        '"{niche}" "{city}" "best viewed in" OR "click here to enter"',
        '"{niche}" "{city}, {state}" site:*.wixsite.com OR site:*.godaddysites.com',
    ]),
    ("Money already in motion — these convert best", [
        '"{city} {state}" {niche} sponsor OR sponsors 2025 OR 2026',
        '"{city}" "{state}" {niche} "now hiring"',
        '"{city} {state}" {niche} grand opening',
    ]),
]


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def today():
    return datetime.date.today().isoformat()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def norm_phone(raw):
    """Return a 10-digit NANP number, or '' — rejecting anything invented.

    Fabricated numbers are the classic way a lead sheet rots: they look right,
    they waste a call, and they cost the caller credibility. Every rule here
    rejects a number that cannot exist rather than one that is merely unusual.
    """
    if not raw:
        return ""
    d = re.sub(r"\D", "", str(raw))
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    if len(d) != 10:
        raise ValueError(f"phone {raw!r} is not a 10-digit number with area code")
    area, exch, line = d[:3], d[3:6], d[6:]
    if area[0] in "01" or exch[0] in "01":
        raise ValueError(f"phone {raw!r} is not a valid NANP number")
    if area == "555":
        raise ValueError(f"phone {raw!r} uses the fictional 555 area code")
    if exch == "555" and 100 <= int(line) <= 199:
        raise ValueError(f"phone {raw!r} is in the reserved fictional range")
    if len(set(d)) == 1 or d in ("1234567890", "0123456789"):
        raise ValueError(f"phone {raw!r} is placeholder digits")
    return d


def fmt_phone(d):
    return f"({d[:3]}) {d[3:6]}-{d[6:]}" if len(d) == 10 else d


def csv_set(value, sep=r"[;,]"):
    """Split a delimited list into a clean, ordered, deduped list.

    Evidence is split on semicolons only — a search query routinely contains a
    comma ("Columbia, MS") and splitting on it shreds the source record.
    """
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        parts = [str(v) for v in value]
    else:
        parts = re.split(sep, str(value))
    out = []
    for p in (x.strip() for x in parts):
        if p and p not in out:
            out.append(p)
    return out


def score_row(row):
    """Score 0-100 from presence + observed defects + reachability signals."""
    presence = row.get("presence", "")
    if presence not in PRESENCE:
        raise ValueError(f"presence {presence!r} not one of {', '.join(PRESENCE)}")
    total = PRESENCE[presence][0]
    for d in csv_set(row.get("defects")):
        if d not in DEFECTS:
            raise ValueError(f"unknown defect {d!r} (known: {', '.join(DEFECTS)})")
        total += DEFECTS[d]
    for s in csv_set(row.get("signals")):
        if s not in SIGNALS:
            raise ValueError(f"unknown signal {s!r} (known: {', '.join(SIGNALS)})")
        total += SIGNALS[s]
    total = max(0, min(100, total))
    tier = next(t for cut, t in TIERS if total >= cut)
    return total, tier


def clean(raw):
    """Validate and normalise one incoming lead. Raises ValueError if unusable."""
    row = {f: "" for f in FIELDS}
    for k, v in raw.items():
        if k in FIELDS:
            row[k] = "" if v is None else str(v).strip()

    if not row["name"]:
        raise ValueError("name is required")
    if not row["city"]:
        raise ValueError(f"{row['name']}: city is required")
    if not csv_set(row["evidence"], ";"):
        raise ValueError(f"{row['name']}: evidence is required — where did this come from?")

    row["phone"] = norm_phone(row["phone"])
    url = row["url"].strip()
    if url:
        host = re.sub(r"^https?://", "", url).split("/")[0].lower().lstrip("www.")
        if host in FAKE_DOMAINS:
            raise ValueError(f"{row['name']}: {url} is a placeholder domain")
    if row["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", row["email"], re.I):
        raise ValueError(f"{row['name']}: {row['email']} is not an email address")
    if row["status"] and row["status"] not in STATUSES:
        raise ValueError(f"{row['name']}: status must be one of {', '.join(STATUSES)}")

    row["evidence"] = "; ".join(csv_set(row["evidence"], ";"))
    for f in ("defects", "signals"):
        row[f] = "; ".join(csv_set(row[f]))
    row["status"] = row["status"] or "new"
    row["first_seen"] = row["first_seen"] or today()
    row["last_seen"] = today()
    try:
        row["score"], row["tier"] = (str(x) for x in score_row(row))
    except ValueError as e:
        raise ValueError(f"{row['name']}: {e}") from None
    return row


def key_of(row):
    return row["phone"] or f"{slug(row['name'])}|{slug(row['city'])}"


def load(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as fh:
        return [{f: r.get(f, "") for f in FIELDS} for r in csv.DictReader(fh)]


def save(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda r: (-int(r["score"] or 0), r["name"].lower()))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def merge(old, new):
    """Fold a re-sighting into an existing row without losing what we knew."""
    out = dict(old)
    for f in FIELDS:
        if f == "evidence":
            # csv_set again over the concatenation, or a re-sweep duplicates every entry
            out[f] = "; ".join(csv_set(csv_set(old[f], ";") + csv_set(new[f], ";")))
        elif f in ("defects", "signals"):
            out[f] = "; ".join(csv_set(csv_set(old[f]) + csv_set(new[f])))
        elif f == "first_seen":
            out[f] = min(x for x in (old[f], new[f]) if x)
        elif f == "status":
            out[f] = max(old[f] or "new", new[f] or "new", key=lambda s: STATUS_RANK.get(s, 0))
        elif new.get(f):
            out[f] = new[f]
    out["score"], out["tier"] = (str(x) for x in score_row(out))
    return out


def dnc_names():
    if not DNC_FILE.exists():
        return set()
    return {slug(l) for l in DNC_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")}


def upsert(ledger_path, incoming):
    rows = load(ledger_path)
    index = {key_of(r): i for i, r in enumerate(rows)}
    blocked = dnc_names()
    added = updated = skipped = 0
    problems = []

    for raw in incoming:
        try:
            row = clean(raw)
        except ValueError as e:
            problems.append(str(e))
            continue
        if slug(row["name"]) in blocked:
            row["status"] = "dnc"
            skipped += 1
        k = key_of(row)
        if k in index:
            rows[index[k]] = merge(rows[index[k]], row)
            updated += 1
        else:
            index[k] = len(rows)
            rows.append(row)
            added += 1

    save(ledger_path, rows)
    print(f"{added} added, {updated} updated, {len(rows)} total"
          + (f", {skipped} on do-not-contact" if skipped else ""))
    for p in problems:
        print(f"  rejected: {p}", file=sys.stderr)
    return 1 if problems else 0


def cmd_ingest(args):
    path = pathlib.Path(args.file)
    if not path.exists():
        die(f"{path} not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("leads", [data])
    return upsert(pathlib.Path(args.ledger), data)


def cmd_add(args):
    row = {f: getattr(args, f, None) for f in FIELDS if hasattr(args, f)}
    return upsert(pathlib.Path(args.ledger), [row])


def cmd_report(args):
    rows = load(pathlib.Path(args.ledger))
    if not rows:
        print("Ledger is empty. Run a sweep first.")
        return 0
    live = [r for r in rows if r["status"] not in ("lost", "dnc", "won")]
    print(f"# Prospects — {len(live)} live of {len(rows)} tracked\n")
    print(f"_Ledger: `{args.ledger}` · generated {today()}_\n")
    for cut, tier in TIERS:
        group = [r for r in live if r["tier"] == tier]
        if not group:
            continue
        label = {"A": "Call this week", "B": "Worth a call",
                 "C": "Keep warm", "D": "Low priority"}[tier]
        print(f"\n## Tier {tier} — {label} ({len(group)})\n")
        for r in group:
            where = ", ".join(x for x in (r["city"], r["state"]) if x)
            head = f"**{r['name']}**"
            if r["category"]:
                head += f" · {r['category']}"
            print(f"- {head} · {where} · **{r['score']}/100** · {r['status']}")
            print(f"  - Presence: {PRESENCE[r['presence']][1]}"
                  + (f" — {r['url']}" if r["url"] else ""))
            if r["defects"]:
                print(f"  - Faults: {r['defects']}")
            contact = " · ".join(x for x in (fmt_phone(r["phone"]), r["email"], r["address"]) if x)
            if contact:
                print(f"  - Contact: {contact}")
            if r["pitch"]:
                print(f"  - Angle: {r['pitch']}")
            print(f"  - Source: {r['evidence']}")
    return 0


def cmd_export(args):
    rows = load(pathlib.Path(args.ledger))
    if args.tier:
        rows = [r for r in rows if r["tier"] in set(args.tier.upper())]
    if not args.include_dead:
        rows = [r for r in rows if r["status"] not in ("lost", "dnc")]
    cols = ["name", "category", "city", "state", "phone", "email", "presence",
            "url", "score", "tier", "status", "pitch"]
    w = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        r = dict(r, phone=fmt_phone(r["phone"]))
        w.writerow(r)
    return 0


def cmd_status(args):
    rows = load(pathlib.Path(args.ledger))
    if not rows:
        print("Ledger is empty.")
        return 0
    print(f"{len(rows)} leads in {args.ledger}\n")
    for label, field in (("By tier", "tier"), ("By status", "status"), ("By presence", "presence")):
        counts = {}
        for r in rows:
            counts[r[field]] = counts.get(r[field], 0) + 1
        print(label)
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {k or '(blank)':<16} {v}")
        print()
    missing = [r["name"] for r in rows if not r["phone"] and not r["email"]]
    if missing:
        print(f"No way to reach ({len(missing)}): {', '.join(missing[:8])}"
              + (" ..." if len(missing) > 8 else ""))
    return 0


def cmd_dnc(args):
    DNC_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DNC_FILE.exists():
        DNC_FILE.write_text("# Businesses that asked not to be contacted. One name per line.\n",
                            encoding="utf-8")
    with DNC_FILE.open("a", encoding="utf-8") as fh:
        fh.write(args.name.strip() + "\n")
    rows = load(pathlib.Path(args.ledger))
    for r in rows:
        if slug(r["name"]) == slug(args.name):
            r["status"] = "dnc"
    save(pathlib.Path(args.ledger), rows)
    print(f"{args.name} will not be contacted again.")
    return 0


def cmd_queries(args):
    sub = {"niche": args.niche, "city": args.city, "state": args.state}
    print(f"# Sweep: {args.niche} in {args.city}, {args.state}\n")
    print("Run each through WebSearch. Read results for businesses whose only hits are")
    print("someone else's site — that absence is the signal.\n")
    for heading, queries in QUERY_BANK:
        print(f"\n## {heading}\n")
        for q in queries:
            print(f"    {q.format(**sub)}")
    print("\n\n## Then verify every candidate before it becomes a lead\n")
    print("    curl -sS -o /dev/null -w '%{http_code} %{url_effective}\\n' -L <domain>")
    print("    curl -sSL <domain> | grep -iEo 'viewport|copyright[^<]{0,20}|domain is for sale'")
    print("\nNo domain, dead domain, or no viewport tag → it is real. See docs/ESON-PROSPECTING.md.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Eson the Searcher — lead ledger.")
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="ledger CSV path")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("queries", help="print the search query bank for a niche/town")
    s.add_argument("--niche", required=True)
    s.add_argument("--city", required=True)
    s.add_argument("--state", required=True)
    s.set_defaults(fn=cmd_queries)

    s = sub.add_parser("ingest", help="merge a JSON array of leads into the ledger")
    s.add_argument("file")
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("add", help="add one lead from the command line")
    for f in ("name", "category", "city", "state", "phone", "email", "address",
              "presence", "url", "evidence", "defects", "signals", "pitch", "notes", "status"):
        s.add_argument(f"--{f}", default="")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("report", help="markdown call sheet, grouped by tier")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("export", help="CSV to stdout")
    s.add_argument("--tier", default="", help="filter, e.g. AB")
    s.add_argument("--include-dead", action="store_true")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("status", help="counts and gaps")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("dnc", help="mark a business do-not-contact")
    s.add_argument("name")
    s.set_defaults(fn=cmd_dnc)

    args = p.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
