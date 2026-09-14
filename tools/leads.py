#!/usr/bin/env python3
"""Eson's lead database — add, dedupe, query and export business leads.

Python standard library only, matching the other tools in this repo. The database is a
JSON array of lead records; CSV export is for spreadsheets and CRM imports.

    python3 tools/leads.py add --file new-leads.json
    python3 tools/leads.py list --min-score 75
    python3 tools/leads.py find "Mack's Heating"
    python3 tools/leads.py export --csv leads/export.csv
    python3 tools/leads.py set-status <id> contacted --note "left voicemail"
    python3 tools/leads.py stats

The database path comes from $ESON_DB, falling back to leads/leads.json. Point ESON_DB at
a private location so a prospect list never lands in a public repo.
"""
import argparse
import csv
import datetime
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = pathlib.Path(os.environ.get("ESON_DB") or ROOT / "leads" / "leads.json")

FIELDS = [
    "id", "business_name", "industry", "city", "state", "phone", "website",
    "facebook", "google_profile", "website_status", "lead_score", "opportunity",
    "evidence", "suggested_pitch", "source_urls", "date_checked",
    "status", "first_seen", "last_checked", "history",
]
REQUIRED = ["business_name", "city", "state", "website_status", "lead_score"]

STATUSES = ["new", "reviewed", "contacted", "won", "lost", "revisit"]
WEBSITE_STATUSES = [
    "No Website", "Social Only", "Poor Website", "Weak Presence",
    "Unknown — not inspected", "Has Good Website",
]


def today():
    return datetime.date.today().isoformat()


def norm(s):
    """Fold a name for comparison: lowercase, drop punctuation and company suffixes."""
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(llc|inc|incorporated|co|company|corp|the|and|&)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def digits(s):
    return re.sub(r"\D", "", s or "")


def load():
    if not DB.exists():
        return []
    try:
        data = json.loads(DB.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError as e:
        sys.exit("leads: %s is not valid JSON (%s)" % (DB, e))
    if not isinstance(data, list):
        sys.exit("leads: %s must contain a JSON array" % DB)
    return data


def save(rows):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_id(rec):
    base = "%s-%s-%s" % (norm(rec.get("business_name")), norm(rec.get("city")),
                         (rec.get("state") or "").lower())
    return re.sub(r"\s+", "-", base).strip("-")[:80]


def same_business(a, b):
    """Two records are the same business if the phone matches, or name+city match."""
    pa, pb = digits(a.get("phone")), digits(b.get("phone"))
    if pa and pb and len(pa) >= 10 and pa[-10:] == pb[-10:]:
        return True
    return (norm(a.get("business_name")) == norm(b.get("business_name"))
            and norm(a.get("city")) == norm(b.get("city")))


def validate(rec, i):
    missing = [f for f in REQUIRED if not str(rec.get(f) or "").strip()]
    if missing:
        sys.exit("leads: record %d is missing required field(s): %s" % (i, ", ".join(missing)))
    try:
        score = int(rec["lead_score"])
    except (TypeError, ValueError):
        sys.exit("leads: record %d has a non-numeric lead_score: %r" % (i, rec["lead_score"]))
    if not 1 <= score <= 100:
        sys.exit("leads: record %d lead_score %d is outside 1-100" % (i, score))
    rec["lead_score"] = score
    ws = rec.get("website_status")
    if ws not in WEBSITE_STATUSES:
        sys.exit("leads: record %d has website_status %r; expected one of: %s"
                 % (i, ws, " | ".join(WEBSITE_STATUSES)))
    if isinstance(rec.get("source_urls"), str):
        rec["source_urls"] = [u.strip() for u in rec["source_urls"].split(",") if u.strip()]
    return rec


def cmd_add(args):
    incoming = json.loads(pathlib.Path(args.file).read_text(encoding="utf-8"))
    if isinstance(incoming, dict):
        incoming = [incoming]
    rows = load()
    added = updated = skipped = 0
    changes = []

    for i, raw in enumerate(incoming):
        rec = validate(dict(raw), i)
        match = next((r for r in rows if same_business(r, rec)), None)

        if match is None:
            rec.setdefault("id", make_id(rec))
            rec.setdefault("status", "new")
            rec.setdefault("date_checked", today())
            rec["first_seen"] = today()
            rec["last_checked"] = today()
            rec.setdefault("history", [])
            rows.append({k: rec.get(k, "" if k != "history" else []) for k in FIELDS})
            added += 1
            continue

        # Known business. A changed website status is a real finding, not a duplicate.
        old = match.get("website_status")
        new = rec.get("website_status")
        match["last_checked"] = today()
        if old != new:
            match.setdefault("history", []).append(
                {"date": today(), "from": old, "to": new,
                 "note": rec.get("evidence", "")[:300]})
            match["website_status"] = new
            match["lead_score"] = rec["lead_score"]
            match["evidence"] = rec.get("evidence", match.get("evidence", ""))
            changes.append("%s (%s): %s -> %s" % (match["business_name"], match["city"], old, new))
            updated += 1
        else:
            skipped += 1

    rows.sort(key=lambda r: int(r.get("lead_score") or 0), reverse=True)
    save(rows)
    print("added %d, status-changed %d, duplicate %d -> %s (%d total)"
          % (added, updated, skipped, DB, len(rows)))
    for c in changes:
        print("  CHANGED: " + c)


def matches_filters(r, args):
    if args.min_score and int(r.get("lead_score") or 0) < args.min_score:
        return False
    if args.status and r.get("status") != args.status:
        return False
    if args.website_status and r.get("website_status") != args.website_status:
        return False
    if args.city and norm(args.city) not in norm(r.get("city")):
        return False
    return True


def cmd_list(args):
    rows = [r for r in load() if matches_filters(r, args)]
    rows.sort(key=lambda r: int(r.get("lead_score") or 0), reverse=True)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("no leads match")
        return
    print("%-5s %-34s %-16s %-18s %-22s %s" % ("SCORE", "BUSINESS", "CITY", "INDUSTRY", "WEBSITE STATUS", "STATUS"))
    for r in rows[: args.limit]:
        print("%-5s %-34s %-16s %-18s %-22s %s" % (
            r.get("lead_score"), (r.get("business_name") or "")[:34],
            (r.get("city") or "")[:16], (r.get("industry") or "")[:18],
            (r.get("website_status") or "")[:22], r.get("status")))
    print("\n%d lead(s)" % len(rows))


def cmd_find(args):
    q = norm(args.query)
    hits = [r for r in load()
            if q in norm(r.get("business_name")) or digits(args.query) and digits(args.query) in digits(r.get("phone"))]
    if not hits:
        print("not in database — safe to research")
        return
    for r in hits:
        print("ALREADY KNOWN: %s (%s, %s) score=%s status=%s website=%s last_checked=%s"
              % (r.get("business_name"), r.get("city"), r.get("state"), r.get("lead_score"),
                 r.get("status"), r.get("website_status"), r.get("last_checked")))


def cmd_export(args):
    rows = load()
    rows.sort(key=lambda r: int(r.get("lead_score") or 0), reverse=True)
    out = pathlib.Path(args.csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = [f for f in FIELDS if f != "history"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r = dict(r)
            if isinstance(r.get("source_urls"), list):
                r["source_urls"] = " ".join(r["source_urls"])
            w.writerow(r)
    print("wrote %d lead(s) to %s" % (len(rows), out))


def cmd_set_status(args):
    if args.new_status not in STATUSES:
        sys.exit("leads: status must be one of: %s" % ", ".join(STATUSES))
    rows = load()
    hit = next((r for r in rows if r.get("id") == args.id), None)
    if not hit:
        sys.exit("leads: no lead with id %r" % args.id)
    hit.setdefault("history", []).append(
        {"date": today(), "from": hit.get("status"), "to": args.new_status, "note": args.note or ""})
    hit["status"] = args.new_status
    save(rows)
    print("%s -> %s" % (hit["business_name"], args.new_status))


def cmd_stats(args):
    rows = load()
    if not rows:
        print("database is empty (%s)" % DB)
        return
    by_ws, by_status, by_city = {}, {}, {}
    for r in rows:
        by_ws[r.get("website_status")] = by_ws.get(r.get("website_status"), 0) + 1
        by_status[r.get("status")] = by_status.get(r.get("status"), 0) + 1
        by_city[r.get("city")] = by_city.get(r.get("city"), 0) + 1
    print("%d lead(s) in %s\n" % (len(rows), DB))
    print("by website status:")
    for k, v in sorted(by_ws.items(), key=lambda kv: -kv[1]):
        print("  %-24s %d" % (k, v))
    print("\nby pipeline status:")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print("  %-24s %d" % (k, v))
    print("\ntop cities:")
    for k, v in sorted(by_city.items(), key=lambda kv: -kv[1])[:10]:
        print("  %-24s %d" % (k, v))
    hot = [r for r in rows if int(r.get("lead_score") or 0) >= 90]
    print("\n%d lead(s) scoring 90+" % len(hot))


def main():
    ap = argparse.ArgumentParser(description="Eson's lead database")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add leads from a JSON file, deduping against the database")
    a.add_argument("--file", required=True)
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="list leads, highest score first")
    l.add_argument("--min-score", type=int, default=0)
    l.add_argument("--status", choices=STATUSES)
    l.add_argument("--website-status")
    l.add_argument("--city")
    l.add_argument("--limit", type=int, default=50)
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=cmd_list)

    f = sub.add_parser("find", help="check whether a business is already known")
    f.add_argument("query")
    f.set_defaults(func=cmd_find)

    e = sub.add_parser("export", help="write a CRM-ready CSV")
    e.add_argument("--csv", required=True)
    e.set_defaults(func=cmd_export)

    s = sub.add_parser("set-status", help="move a lead along the pipeline")
    s.add_argument("id")
    s.add_argument("new_status", choices=STATUSES)
    s.add_argument("--note")
    s.set_defaults(func=cmd_set_status)

    st = sub.add_parser("stats", help="summarise the database")
    st.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
