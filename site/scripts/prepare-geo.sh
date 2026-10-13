#!/usr/bin/env bash
# Downloads the official City Wards boundaries (Toronto Open Data, package "city-wards")
# and writes a simplified copy for the story map. Re-run if the city republishes wards.
set -euo pipefail
URL="https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/5e7a8234-f805-43ac-820f-03d7c360b588/resource/737b29e0-8329-4260-b6af-21555ab24f28/download/city-wards-data-4326.geojson"
TMP="$(mktemp -d)"
curl -sSL "$URL" -o "$TMP/wards.geojson"
npx -y mapshaper "$TMP/wards.geojson" \
  -each 'ward=+AREA_SHORT_CODE, name=AREA_NAME' -filter-fields ward,name \
  -simplify 4% keep-shapes -o precision=0.00001 format=geojson src/lib/geo/wards.json
rm -rf "$TMP"
