#!/usr/bin/env python3
"""Generate the call-sheet tracker page from prospects.json."""
import json, pathlib
d = pathlib.Path(__file__).parent
rows = json.loads((d/"prospects.json").read_text())
slim = [{"r":r["rank"],"b":r["business"],"c":r["city"],"co":r["county"],"cat":r["category"],
         "a":r["address"],"p":r["phone"],"w":r["web_signal"],"t":r["tier"],
         "ch":bool(r["chamber_listed"]),"s":r["score"],"y":r["why"]} for r in rows]
payload = json.dumps(slim, separators=(",",":")).replace("<","\\u003c")

tpl = (d/"tracker.tpl.html").read_text()
(d/"call-sheet.html").write_text(tpl.replace("/*__DATA__*/[]", payload))
print("call-sheet.html written,", len(slim), "rows")
