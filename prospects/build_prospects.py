#!/usr/bin/env python3
"""
Build the 601/769 prospect list for the website service.

Every row below came from a web search performed while building this file.
NOTHING here is invented. Fields that could not be sourced are left EMPTY --
never guessed. See README.md for the method and the honesty rules.

web_signal is an INFERENCE, not a verified audit:
  none    only directory/aggregator listings surfaced -- no site of their own
  fb      a Facebook page surfaced, no own domain
  dated   own domain surfaced, but on legacy tech (.php/.aspx/template host)
  own     own domain surfaced and looks self-managed
  corp    franchise/corporate-controlled site -- owner usually cannot buy
  unknown name surfaced without enough signal to call it
"""
import csv, json, pathlib

# name, city, county, category, address, phone, web_signal, tier, chamber, warm
R = [
 # ---------- TIER 1: Columbia / Marion County ----------
 ("Fitness Depot (7-location group)","Columbia","Marion","gym","805 Hwy 98 Bypass","(601) 345-3344","own",1,0,1),
 ("Columbia Family Dental","Columbia","Marion","dental","430 Broad St","(601) 736-7125","none",1,0,0),
 ("Kimble Clinic - Chiropractic","Columbia","Marion","chiropractic","262 S High School Ave","(601) 736-2331","none",1,0,0),
 ("Fink Chiropractic Clinic","Columbia","Marion","chiropractic","230 S High School Ave","(601) 736-5031","none",1,0,0),
 ("Pope Tire Service","Columbia","Marion","tire","139 S High School Ave","(601) 736-2613","none",1,0,0),
 ("Griffith's Discount Tires","Columbia","Marion","tire","1110 Hwy 13 N","(601) 736-5369","none",1,0,0),
 ("Swank Salon","Columbia","Marion","salon","723 Main St","(601) 444-9700","none",1,1,0),
 ("Cuttin' Up","Columbia","Marion","salon","1145 Hwy 98 Ste 3","(601) 736-8686","none",1,1,0),
 ("Hair Designers","Columbia","Marion","salon","274 S High School Ave","","none",1,1,0),
 ("Entrigue Salon and Day Spa","Columbia","Marion","spa","622 Main St","","none",1,1,0),
 ("Nails 2000","Columbia","Marion","nails","312 Second St","","none",1,0,0),
 ("V I P Nails","Columbia","Marion","nails","105 S Highway 98 E","","none",1,0,0),
 ("Nails Spa","Columbia","Marion","nails","1207 US-98","","none",1,0,0),
 ("Barbara's","Columbia","Marion","salon","","","none",1,1,0),
 ("Hammond Plumbing","Columbia","Marion","plumbing","907 Park Ave","(601) 736-2999","none",1,0,0),
 ("Pierre's Air Conditioning & Heat","Columbia","Marion","hvac","518 S High School Ave","","none",1,0,0),
 ("The Flower Shop on Church Street","Columbia","Marion","florist","323 Church St","","fb",1,0,0),
 ("Southern Collective Upscale Market","Columbia","Marion","retail","615 Main St","","none",1,1,0),
 ("Hunt Insurance","Columbia","Marion","insurance","601 Broad St","(601) 736-8991","none",1,0,0),
 ("SouthGroup / James Bowman Agency, Inc.","Columbia","Marion","insurance","500 Broad St","(601) 736-4537","none",1,0,0),
 ("Berry Law Firm, PLLC","Columbia","Marion","law","329 Church St","(601) 736-3004","none",1,0,0),
 ("Foxworth, Shepard & Bruhl P.A.","Columbia","Marion","law","702 Main St","(601) 736-1122","none",1,0,0),
 ("Donovan McComb Attorney At Law","Columbia","Marion","law","718 Broad St","(601) 444-0000","none",1,1,0),
 ("Marion County Farm Bureau","Columbia","Marion","insurance","434 Broad St","(601) 736-3244","corp",1,0,0),
 ("Paul S. Broom - Allstate Agency","Columbia","Marion","insurance","262 S High School Ave","(601) 731-1616","corp",1,0,0),
 ("Strategic Insurance Professionals","Columbia","Marion","insurance","418 Sumrall Rd Ste 2","(769) 255-6332","corp",1,0,0),
 ("Berry Patch LLC (florist & gifts)","Columbia","Marion","florist","220 Second St","(601) 522-2946","dated",1,1,0),
 ("Columbia Animal Hospital","Columbia","Marion","veterinary","1409 Hwy 98 E","(601) 736-3041","dated",1,1,0),
 ("Moree's Florist & More","Columbia","Marion","florist","402 Lumberton Rd","","own",1,0,0),
 ("Smith Funeral Home","Columbia","Marion","funeral","","(601) 736-2257","own",1,0,0),
 ("Hathorn Funeral Home","Columbia","Marion","funeral","167 Old Highway 98 E","(601) 731-2000","own",1,0,0),
 ("Marion Pet Care","Columbia","Marion","veterinary","2132 Hwy 13 N","(601) 731-1232","own",1,1,0),
 ("BUMPERs Tires & Accessories","Columbia","Marion","tire","1310 Highway 98 E","(601) 731-5834","own",1,1,0),
 ("Leggett Orthodontics - Columbia","Columbia","Marion","orthodontic","620 Broad St","(601) 833-4912","own",1,0,0),
 ("Air Maintenance Inc.","Columbia","Marion","hvac","","(601) 270-2233","own",1,0,0),
 ("Watts Electric & AC","Columbia","Marion","hvac","","(601) 736-7362","own",1,0,0),
 ("L.K. Berry Law","Columbia","Marion","law","","","own",1,0,0),
 ("Encore Rehabilitation of Columbia","Columbia","Marion","physicaltherapy","","","unknown",1,0,0),
 ("First Place Physical Therapy","Columbia","Marion","physicaltherapy","","","unknown",1,0,0),
 ("Southern Bone & Joint Specialists PA","Columbia","Marion","physicaltherapy","","","unknown",1,0,0),
 ("Community Rehab Physical Therapy","Columbia","Marion","physicaltherapy","","","unknown",1,0,0),
 ("Gulf States Roofing & Construction","Columbia","Marion","roofing","","","unknown",1,0,0),
 ("C&C Home Improvements","Columbia","Marion","contractor","","","unknown",1,0,0),
 ("Hooker Roofing","Columbia","Marion","roofing","","","unknown",1,0,0),
 ("Elliot Bates Roofing","Columbia","Marion","roofing","","","unknown",1,0,0),
 ("Magnolia Grille","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("The Back Door","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Broad Street Restaurant","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Celina's Diner","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Milano's Pizza and Pasta","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Raquel's Family Restaurant","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Uptown Soulfood Diner","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Rajun Cajun's","Columbia","Marion","restaurant","","","unknown",1,0,0),
 ("Smoke Shack Barbecue","Columbia","Marion","restaurant","","","unknown",1,0,0),

 # ---------- TIER 2: 20-50 min (Jeff Davis, Lawrence, Walthall, Lamar, Covington) ----------
 ("Johnson's Funeral Home, Inc.","Prentiss","Jefferson Davis","funeral","1112 Fred St","","unknown",2,0,0),
 ("Laird Mortuary","Prentiss","Jefferson Davis","funeral","919 2nd St","","unknown",2,0,0),
 ("Longleaf Heating & Air","Prentiss","Jefferson Davis","hvac","","","unknown",2,0,0),
 ("Blackwell's AC & Heat","Tylertown","Walthall","hvac","","","unknown",2,0,0),
 ("Jefferson AC & Electrical","Tylertown","Walthall","hvac","","","unknown",2,0,0),
 ("43 General Store","Monticello","Lawrence","retail","","","unknown",2,0,0),
 ("Salem Opry House","Collins area","Covington","venue","","","unknown",2,0,0),
 ("Cowboy Jim's Riverside Restaurant","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Shivers Creek Fish House","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("The Shack On 184","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Dinner On Main","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Nanny's Diner","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Hamburger House","Prentiss","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Pearl's Diner","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Hog Heaven BBQ","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Downtown Burger","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Kuntry Fisherman Bar & Grill","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Mom & Dad's Country Cooking Buffet","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Mom & Pop's Soul Food Kitchen & Barbecue","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("GrateFull Soul","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Eastside Soul Food Restaurant","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Binke's Restaurant","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Vezlicious Daiquiris and Wings","Prentiss area","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Best Wok","Prentiss","Jefferson Davis","restaurant","","","unknown",2,0,0),
 ("Los Parrilleros","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("Collard Greens & Tortillas","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("Miss K's of Monticello","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("China Wok","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("Rustic Barrel","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("Catfish One","Monticello","Lawrence","restaurant","","","unknown",2,0,0),
 ("Finch & Fox Coffee Shop","Monticello area","Lawrence","cafe","","","unknown",2,0,0),
 ("Donut Time","Monticello area","Lawrence","bakery","","","unknown",2,0,0),
 ("Sumrall Donuts & Breakfast","Sumrall","Lamar","bakery","","","unknown",2,0,0),
 ("Katie's Restaurant & Bar","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("Whistle Stop Cafe","Purvis area","Lamar","cafe","","","unknown",2,0,0),
 ("Frosty Mug","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("Petunia's BBQ","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("R and K Kickin Lickin BBQ","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("L.T.'s Food","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("Chuck's SouthSide","Purvis area","Lamar","restaurant","","","unknown",2,0,0),
 ("Deli Diner","Collins","Covington","restaurant","","","unknown",2,0,0),
 ("Main Street Cafe","Collins","Covington","restaurant","","","unknown",2,0,0),
 ("Country Hix Boudin and Cracklins","Collins","Covington","restaurant","","","unknown",2,0,0),
 ("Red's","Collins","Covington","restaurant","","","unknown",2,0,0),
 ("Habanero Mexican Grill","Collins","Covington","restaurant","","","unknown",2,0,0),
 ("Graham's Fish Camp","Collins area","Covington","restaurant","","","unknown",2,0,0),
 ("Annie B's","Collins","Covington","restaurant","","","unknown",2,0,0),

 # ---------- TIER 3: 50-90 min (Lincoln, Pike, Forrest, Jones, Pearl River, Stone, Simpson) ----------
 ("Animal Health Center of Brookhaven","Brookhaven","Lincoln","veterinary","1697 Highway 84 E","(601) 833-7788","dated",3,0,0),
 ("Hartman-Harrigill Funeral Home","Brookhaven","Lincoln","funeral","101 W Chickasaw St","","unknown",3,0,0),
 ("Marshall Funeral Home","Brookhaven","Lincoln","funeral","412 N Second St","","unknown",3,0,0),
 ("Peoples Undertaking Co., Inc.","McComb","Pike","funeral","607 Elmwood St","","unknown",3,0,0),
 ("BAC Mechanical Services","Brookhaven","Lincoln","hvac","","","unknown",3,0,0),
 ("Ole Brook Heating & Cooling","Brookhaven","Lincoln","hvac","","","unknown",3,0,0),
 ("Opulent Aesthetics","Hattiesburg","Forrest","medspa","","(601) 476-1602","fb",3,0,0),
 ("Le Nail Day Spa","Brookhaven","Lincoln","nails","939 Brookway Blvd","","unknown",3,0,0),
 ("Bertha's Flower Shop","Brookhaven","Lincoln","florist","103 W Chickasaw St","","unknown",3,0,0),
 ("601 Boutique","Laurel","Jones","boutique","327 N Magnolia St","","unknown",3,0,0),
 ("Bella Bella","Laurel","Jones","boutique","","","unknown",3,0,0),
 ("The Cotton Boll","Laurel","Jones","boutique","","","unknown",3,0,0),
 ("Southern Antique & Gift Mall","Laurel","Jones","retail","","","unknown",3,0,0),
 ("HAND+made","Laurel","Jones","retail","","","unknown",3,0,0),
 ("Revolution Fitness","Hattiesburg","Forrest","gym","","","unknown",3,0,0),
 ("Anatomies","Hattiesburg","Forrest","gym","","","unknown",3,0,0),
 ("Pure Performance Gym","Hattiesburg","Forrest","gym","","","unknown",3,0,0),
 ("The Red Barn","South Mississippi","","venue","","","unknown",3,0,0),
 ("Brookhaven Animal Hospital","Brookhaven","Lincoln","veterinary","1210 US-51","(601) 833-1223","own",3,0,0),
 ("Animal Medical Center","Brookhaven","Lincoln","veterinary","","","own",3,0,0),
 ("Brookway Dental","Brookhaven","Lincoln","dental","706 Brookway Blvd","(601) 823-3200","own",3,0,0),
 ("Belk Ditcharo Dental","Brookhaven","Lincoln","dental","","","own",3,0,0),
 ("Brookhaven Dental Center","Brookhaven","Lincoln","dental","","","own",3,0,0),
 ("Dr. Mac L. Baker Dentistry","Brookhaven","Lincoln","dental","","(601) 833-7241","own",3,0,0),
 ("Comfort Zone Heating & Cooling LLC","Brookhaven","Lincoln","hvac","2218 New Sight Rd","(601) 833-3131","own",3,0,0),
 ("Brookhaven Funeral Home","Brookhaven","Lincoln","funeral","","","own",3,0,0),
 ("Radiant Reflections Medspa","Hattiesburg","Forrest","medspa","","(601) 268-7777","own",3,0,0),
 ("Plastic Surgery Center of Hattiesburg","Hattiesburg","Forrest","medspa","","(601) 293-3405","own",3,0,0),
 ("FSFIT (Fourth Street CrossFit)","Hattiesburg","Forrest","gym","120 98th Place Blvd","(601) 602-3269","own",3,0,0),
 ("Bridlewood Event Venue","Hattiesburg","Forrest","venue","","","own",3,0,0),
 ("Brookside Barn","Ellisville","Jones","venue","","","own",3,0,0),
 ("The White Barn","South Mississippi","","venue","","","own",3,0,0),
 ("Shop The Nine","Laurel","Jones","boutique","","","own",3,0,0),
 ("The Depot On Canal","Picayune","Pearl River","restaurant","","","own",3,0,0),
 ("Melba's Place","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("Magnolia Blues BBQ","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("Betty's Eat Shop","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("Friend's Kitchen","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("Chickn' Coop","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("The Old Koke Plant","Brookhaven","Lincoln","venue","","","unknown",3,0,0),
 ("K & B Seafood","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("Chism's Diner","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("The Fish Fry","Brookhaven","Lincoln","restaurant","","","unknown",3,0,0),
 ("The Dinner Bell","McComb","Pike","restaurant","229 5th Ave","","unknown",3,0,0),
 ("Le Pointe","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Al Dente","McComb","Pike","restaurant","2101 Veterans Blvd","","unknown",3,0,0),
 ("Vine's","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("La Mariposa","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Mr Whiskers Family Catfish Restaurant","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Double E BBQ","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Buddy's","McComb","Pike","restaurant","821 Delaware Ave","","unknown",3,0,0),
 ("Tortilla Soup","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Cypress Landing","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Nona Lynn's Kitchen","McComb","Pike","restaurant","","","unknown",3,0,0),
 ("Cuevas's Fish House","Picayune","Pearl River","restaurant","","","unknown",3,0,0),
 ("Fatty's Seafood Restaurant","Picayune","Pearl River","restaurant","3320 Highway 11 N","","unknown",3,0,0),
 ("Don's Seafood Restaurant","Picayune","Pearl River","restaurant","800 Highway 11 S","","unknown",3,0,0),
 ("Pericos Mexican Restaurant","Wiggins","Stone","restaurant","","","unknown",3,0,0),
 ("Southern Turnings","Wiggins","Stone","restaurant","","","unknown",3,0,0),
 ("Bill's Catfish & Steaks","Wiggins","Stone","restaurant","","","unknown",3,0,0),
 ("Hibachi Express","Wiggins","Stone","restaurant","","","unknown",3,0,0),
 ("Thorny Oyster","Wiggins area","Stone","restaurant","","","unknown",3,0,0),
 ("Crawfish Connection","Wiggins area","Stone","restaurant","","","unknown",3,0,0),
 ("Wild Bill's BBQ","Wiggins","Stone","restaurant","","","unknown",3,0,0),
 ("Berry's Seafood & Catfish House","Magee","Simpson","restaurant","","","unknown",3,0,0),
 ("Joses Restaurant & Grill","Magee","Simpson","restaurant","","","unknown",3,0,0),
 ("Oscar's by Fernandos","Magee","Simpson","restaurant","","","unknown",3,0,0),
 ("T-Bones Records & Cafe","Hattiesburg","Forrest","cafe","","","unknown",3,0,0),
]

SIGNAL = {"none":40,"fb":38,"dated":34,"unknown":22,"own":12,"corp":2}
BUDGET = {"funeral":25,"dental":25,"orthodontic":25,"veterinary":25,"medspa":25,"law":25,
          "hvac":25,"plumbing":25,"roofing":25,"contractor":25,"venue":25,
          "chiropractic":18,"physicaltherapy":18,"insurance":18,"gym":18,"tire":18,
          "salon":13,"spa":13,"nails":13,"boutique":13,"retail":13,"florist":13,
          "restaurant":7,"cafe":7,"bakery":7}
PROX = {1:20, 2:14, 3:8}

def why(cat, web, warm, chamber):
    bits = []
    if warm: bits.append("existing relationship - spec site already built")
    if web == "none": bits.append("no website of its own found")
    elif web == "fb": bits.append("Facebook page only, no website")
    elif web == "dated": bits.append("has a site, but on legacy tech - redesign angle")
    elif web == "own": bits.append("has a site - lead with local search/Google profile")
    elif web == "corp": bits.append("franchise site - owner may not control it")
    else: bits.append("web presence not established - check before calling")
    if BUDGET.get(cat,7) >= 25: bits.append("high-ticket service, one job pays for the site")
    if chamber: bits.append("chamber-listed")
    return "; ".join(bits)

rows = []
for (n,city,cty,cat,addr,ph,web,tier,chamber,warm) in R:
    score = SIGNAL[web] + BUDGET.get(cat,7) + PROX[tier] + (45 if warm else 0) + (8 if chamber else 0)
    rows.append({
        "business": n, "city": city, "county": cty, "category": cat,
        "address": addr, "phone": ph, "web_signal": web,
        "tier": tier, "chamber_listed": "yes" if chamber else "",
        "score": score, "why": why(cat, web, warm, chamber),
        "verify": "confirm phone/address + open their site on a phone before calling",
        "status": "", "contacted": "", "notes": "",
    })

rows.sort(key=lambda r: (-r["score"], r["tier"], r["business"]))
rows = rows[:150]
for i, r in enumerate(rows, 1):
    r["rank"] = i

cols = ["rank","business","city","county","category","address","phone","web_signal",
        "tier","chamber_listed","score","why","verify","status","contacted","notes"]
out = pathlib.Path(__file__).parent
with open(out/"prospects-601-769.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in cols})
(out/"prospects.json").write_text(json.dumps(rows, indent=1))

print(f"{len(rows)} prospects written")
from collections import Counter
print("by tier:   ", dict(sorted(Counter(r['tier'] for r in rows).items())))
print("by signal: ", dict(Counter(r['web_signal'] for r in rows).most_common()))
print("with phone:", sum(1 for r in rows if r['phone']))
print("with addr: ", sum(1 for r in rows if r['address']))
