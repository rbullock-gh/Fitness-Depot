#!/usr/bin/env bash
# Generates branded photo placeholders for every image slot on the site.
# Each placeholder is replaced by dropping a real Fitness Depot photo with the
# same basename into assets/img/ and running tools/apply-photos.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=assets/img

make_svg () {
  local name="$1" w="$2" h="$3" label="$4" note="$5"
  cat > "$OUT/$name.svg" <<SVG
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $w $h" width="$w" height="$h" role="img" aria-label="$label">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1c1a14"/>
      <stop offset="0.55" stop-color="#0d0d0d"/>
      <stop offset="1" stop-color="#231f16"/>
    </linearGradient>
    <pattern id="stripes" width="34" height="34" patternUnits="userSpaceOnUse" patternTransform="rotate(-24)">
      <rect width="34" height="34" fill="none"/>
      <rect width="9" height="34" fill="#FFFFFF" opacity="0.022"/>
    </pattern>
  </defs>
  <rect width="$w" height="$h" fill="url(#g)"/>
  <rect width="$w" height="$h" fill="url(#stripes)"/>
  <rect x="0" y="0" width="$w" height="6" fill="#c9a227"/>
  <g transform="translate($((w/2)) $((h/2)))" text-anchor="middle" font-family="'Barlow Condensed','Arial Narrow',Arial,sans-serif">
    <g transform="translate(0 -74)">
      <rect x="-46" y="-46" width="92" height="92" rx="10" fill="none" stroke="#c9a227" stroke-width="4"/>
      <text y="18" font-size="52" font-weight="700" fill="#FFFFFF" letter-spacing="2">FD</text>
    </g>
    <text y="10" font-size="34" font-weight="700" fill="#FFFFFF" letter-spacing="3">$label</text>
    <text y="52" font-size="21" font-weight="500" fill="#a8a49a" letter-spacing="1.5">$note</text>
    <text y="96" font-size="17" font-weight="500" fill="#6d6a63" letter-spacing="2">PHOTO PLACEHOLDER &#183; ${w}&#215;${h}</text>
  </g>
</svg>
SVG
  echo "  $OUT/$name.svg"
}

echo "Generating placeholders:"
make_svg hero-facility            1600 1100 "COLUMBIA GYM FLOOR"    "Wide hero shot of the Columbia facility"
make_svg about-community          1200 900  "MEMBERS TRAINING"      "Real members on the Columbia gym floor"
make_svg access-247               1200 900  "24/7 ACCESS"           "Entry / fingerprint reader / night floor"
make_svg equipment-cardio         1100 800  "CARDIO"                "Treadmills, stepmills, ellipticals, spin bikes"
make_svg equipment-strength       1100 800  "FREE WEIGHTS"          "Dumbbells, barbells, squat racks, plate loaded"
make_svg equipment-functional     1100 800  "FUNCTIONAL TRAINING"   "Turf area and full-body circuit"
make_svg training-personal        1200 900  "PERSONAL TRAINING"     "Trainer working with a member"
make_svg recovery-hydromassage    1200 900  "HYDROMASSAGE"          "Private recovery room"
make_svg recovery-tanning          900 700  "TANNING"               "Tanning room"
make_svg kids-area                1200 900  "FITNESS DEPOT KIDS"    "Kid Care room at Columbia"
make_svg gallery-gym-floor        1000 750  "GYM FLOOR"             "Main training floor"
make_svg gallery-free-weights     1000 750  "FREE WEIGHT AREA"      "Dumbbell racks and benches"
make_svg gallery-cardio-deck      1000 750  "CARDIO DECK"           "Cardio row with TVs"
make_svg gallery-turf             1000 750  "TURF AREA"             "Functional training turf"
make_svg gallery-squat-racks      1000 750  "SQUAT RACKS"           "Racks and platforms"
make_svg gallery-recovery         1000 750  "RECOVERY ROOM"         "HydroMassage / recovery space"
make_svg gallery-kids             1000 750  "KIDS ROOM"             "Fitness Depot Kids area"
make_svg gallery-exterior         1000 750  "EXTERIOR SIGNAGE"      "Building and Fitness Depot sign"
make_svg og-image                 1200 630  "FITNESS DEPOT COLUMBIA" "805 Hwy 98 Bypass &#183; Open 24/7"
echo "Done."
