# Lead ledger

`leads.csv` is Eson's working ledger — created on the first sweep, and **gitignored**.
This repo is public; a prospect list with phone numbers does not belong in it.

```bash
python3 tools/eson.py queries --niche roofing --city Columbia --state MS   # what to search
python3 tools/eson.py ingest sweep.json                                    # merge findings
python3 tools/eson.py report                                               # call sheet
python3 tools/eson.py export --tier AB > outreach.csv                      # working list
python3 tools/eson.py status                                               # counts and gaps
python3 tools/eson.py dnc "Business Name"                                  # never contact again
```

Back it up somewhere private before wiping a container — it is the accumulated
result of every sweep, and re-running them does not reproduce the call outcomes.

`do-not-contact.txt` is also gitignored and is absolute: ingest marks anyone on it `dnc`
and the report and export drop them.

See `docs/ESON-PROSPECTING.md` for the scoring rubric and `.claude/agents/eson.md` for
the method.
