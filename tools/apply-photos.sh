#!/usr/bin/env bash
# Swap generated placeholders for real Fitness Depot photographs.
#
# Usage:
#   1. Save each real photo into assets/img/ using the SAME basename as the
#      placeholder it replaces (see docs/PHOTO-CHECKLIST.md), e.g.
#         assets/img/hero-facility.jpg
#         assets/img/gallery-turf.webp
#   2. Run:  ./tools/apply-photos.sh
#
# Every reference to <name>.svg in the HTML is rewritten to the real file, and
# the placeholder .svg is moved to assets/img/_placeholders/ (not deleted).
# Re-run any time you add more photos. Safe to run repeatedly.
set -euo pipefail
cd "$(dirname "$0")/.."

IMG=assets/img
ARCHIVE="$IMG/_placeholders"
PAGES=(index.html 404.html)
swapped=0

shopt -s nullglob
for real in "$IMG"/*.jpg "$IMG"/*.jpeg "$IMG"/*.png "$IMG"/*.webp "$IMG"/*.avif; do
  base="$(basename "${real%.*}")"
  ext="${real##*.}"
  placeholder="$IMG/$base.svg"

  [ -f "$placeholder" ] || continue

  for page in "${PAGES[@]}"; do
    [ -f "$page" ] || continue
    sed -i "s#$IMG/$base\.svg#$IMG/$base.$ext#g" "$page"
  done

  mkdir -p "$ARCHIVE"
  mv "$placeholder" "$ARCHIVE/"
  echo "  swapped: $base.svg -> $base.$ext"
  swapped=$((swapped + 1))
done

if [ "$swapped" -eq 0 ]; then
  echo "No matching photos found in $IMG/."
  echo "Drop real photos there using the placeholder basenames, then re-run."
  echo "Remaining placeholders:"
  for f in "$IMG"/*.svg; do echo "  - $(basename "$f")"; done
else
  echo "Done — $swapped image(s) swapped."
  echo "NOTE: check the width/height attributes in index.html still match the"
  echo "      real photo dimensions, and update the alt text if the shot differs."
fi
