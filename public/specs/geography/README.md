# Astra geography assets

Prepared 2026-09-18. These are locally downloaded, licensed source assets, not generated flag or map drawings.

## Ready to copy

- `world.svg`: quiet world basemap, `viewBox="0 0 1000 500"`, pale blue sea (`#e7f0ef`) and muted green land (`#c3d0b9`); no visible labels. Paths are projected directly from Natural Earth data.
- `world-map-paths.json`: same 177 source geographic features as separate paths; 177 is a feature count, not a claimed number of countries in the world.
- `countries.json`: 24 country records with lowercase ISO alpha-2 `code`, `iso3`, four-language `name`, four-language `region`, `regionId`, `lng`, `lat`, projected `x`, `y`, and proposed local `flag` path.
- `flags/{code}.svg`: 24 unmodified upstream flag-icons 4:3 icons; keep their flags unmirrored in RTL layouts.
- `FLAGS-LICENSE.txt`: full upstream MIT license. Distribute alongside the flags.
- `manifest.json`: source URLs, retrieval date, source hashes and verified upstream code/name mappings.
- `validation.json`: schema, geometry and point validation summary.

Suggested application IDs are `flag-id`, `flag-jp`, etc. Suggested public URLs in country records are `/assets/flags/id.svg`, `/assets/flags/jp.svg`, etc.; these may be changed to match the application's folder structure.

## Coordinates

Projection: `x = (longitude + 180) / 360 * 1000`, `y = (90 - latitude) / 180 * 500`.

Marker positions are representative interior points, not capitals and not mathematical national centroids. Twenty-three points use Natural Earth's supplied label point. New Zealand's source label is offshore, so its marker is on the North Island at longitude 175.6, latitude -39.2. All 24 points were verified by a point-in-polygon calculation to fall inside the corresponding downloaded geometry. These are appropriate point markers for a simple world introduction, not territorial boundary or capital quizzes.

`regionId` is a convenient map grouping based on the source label location. Türkiye and Egypt span more than one continent, so do not use these fields to state that all their territory lies on only one continent. Use the marker coordinates for geographical-position exercises. GB is the United Kingdom flag, not the flag of England; use English "United Kingdom" and Indonesian "Britania Raya" rather than "Inggris" alone.

## Sources and attribution

Natural Earth map geometry is public domain. Suggested credit: **Made with Natural Earth.**

- Dataset overview: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/
- Raw source: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson
- License terms: https://www.naturalearthdata.com/about/terms-of-use/

Natural Earth describes its default boundaries as de facto. The provided basemap uses all land in one color with no emphasized political borders. Keep the low-detail map for location discovery rather than exact border claims.

Flag assets are from the official flag-icons repository and use its ISO alpha-2 country IDs. These assets use the collection's normalized 4:3 icon format, not a lesson in official national flag aspect ratios.

- Project: https://github.com/lipis/flag-icons
- Upstream country/code list: https://github.com/lipis/flag-icons/blob/main/country.json
- License: https://github.com/lipis/flag-icons/blob/main/LICENSE

Country identifiers and English/Chinese/Arabic names were cross-checked with the United Nations M49 table. Child-facing labels use common short forms (for example United States, United Kingdom and Saudi Arabia); current English Türkiye is retained. Indonesian labels are editorial translations. The source table names are not being used to assert political or territorial affiliation.

- UN M49: https://unstats.un.org/unsd/methodology/m49/

## Reproduction and checks

Run `python prepare.py` then `python verify_and_render.py` from this folder. Existing downloaded files are reused. `prepare.py` downloads any missing flags and licenses, projects the existing raw GeoJSON, and verifies the 24 SVG/code associations. The raw map source is retained as `world-countries.geojson` for faithful reproduction. `verify_and_render.py` checks every marker against the source polygon and produces `world.svg`.

`flags-preview.png` and `world-preview.png` are local visual QA artifacts, not required website assets. The 24 flags and world outline have been visually reviewed.
