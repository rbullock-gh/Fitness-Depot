#!/usr/bin/env bash
# Point the site at its real address.
#
#   ./tools/set-domain.sh https://fitnessdepotcolumbia.com
#
# Rewrites every absolute URL in one pass: the canonical tag, the Open Graph and
# Twitter tags (including the share image), the structured data, sitemap.xml and
# robots.txt.
#
# Until this is run, link previews fall back to the host's own branding, because
# og:image must be an absolute, publicly fetchable URL -- a relative path or a
# placeholder domain gives the scraper nothing to fetch.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -lt 1 ]; then
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
  echo
  echo "Current domain: $(grep -oE 'rel="canonical" href="[^"]+"' index.html | sed 's/.*href="//;s/"//')"
  exit 1
fi

NEW="${1%/}"
case "$NEW" in
  https://*) ;;
  http://*) echo "warning: use https:// -- some scrapers ignore insecure images" ;;
  *) echo "error: include the scheme, e.g. https://example.com"; exit 1 ;;
esac

OLD="$(grep -oE 'rel="canonical" href="[^"]+"' index.html | sed 's/.*href="//;s/"//;s#/$##')"
if [ -z "$OLD" ]; then echo "error: no canonical tag found in index.html"; exit 1; fi
if [ "$OLD" = "$NEW" ]; then echo "Already set to $NEW -- nothing to do."; exit 0; fi

FILES="index.html 404.html sitemap.xml robots.txt"
for f in $FILES; do
  [ -f "$f" ] || continue
  sed -i "s#${OLD}#${NEW}#g" "$f"
done

echo "Domain set: $OLD  ->  $NEW"
echo
echo "Occurrences now pointing at the live domain:"
for f in $FILES; do
  [ -f "$f" ] || continue
  printf '  %-14s %s\n' "$f" "$(grep -c "$NEW" "$f" || true)"
done
echo
echo "Next: deploy, then paste the URL into"
echo "  https://developers.facebook.com/tools/debug/   (Facebook / Instagram)"
echo "  https://cards-dev.twitter.com/validator        (X)"
echo "and hit Scrape Again -- previews are cached, so a link shared before"
echo "deploying keeps showing the old card until the cache is refreshed."
