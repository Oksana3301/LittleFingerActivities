# Curriculum integration

Use `curriculum.json` for 56 category cards and `worksheets-flat.json` for 1,344 selectable worksheets. Each worksheet contains four rounds using one engine. UI copy should say **56 kategori · 1.344 lembar latihan**, not “1,344 activity types.” There are nine interaction engines. Do not count rounds as worksheets.

All records contain `id`, `category`, bilingual `title`, `engine`, `age: [minimum, maximum]`, `minAge`, `difficulty: 1..6`, `variant: 1..24`, and `rounds`. For convenience the first round's fields are also duplicated at top level; the player should still advance through all four rounds. Age ranges are guidance, not a developmental assessment.

## Round and option contract

Every round has `instruction: {id, en}`, `options`, and `answer`. Each option has `id`, `kind`, and `label: {id, en}`. `hideLabel: true` means do not print the label below the artwork. Quantity labels deliberately omit the answer; `ariaLabel` contains the quantity for assistive technology.

| Engine | Data | Completion |
|---|---|---|
| identify | `options`, `answer` | Select **every** correct option, then check the set. Many rounds have multiple answers. |
| compare | `options`, `answer` | Select the unique greatest/least value. |
| count | `scene`, `options`, `answer`, `countTarget` | Render the entire scene and choose the correct numeral. |
| pair | `options` (left), `rightOptions`, `pairs: [[leftId,rightId]]` | Connect all pairs. Right side is shuffled. `pairId`, `pairLabel`, `pairedSymbol`, `pairedAsset`, `pairedValue` are convenience properties on left options. |
| pattern | `patternItems` (visual items; one null), `options`, `answer` | Display the entire strip; replace its gap with the selected option. |
| sequence | `options`, ordered `answer` IDs | Reorder all the cards to match the requested ascending/descending order. |
| memory | `options` with `pairKey` | Flip two at a time; match equal pairKey. Some have `previewSeconds: 2`. |
| trace | `canvas`, `trace` | Trace the guides. Completion based on coverage is optional; never grade handwriting stroke order from glyph outlines. |
| draw | `canvas`, `completion.goals`, optional `modelAnswer` | Free drawing plus a child/caregiver self-check. Do not claim automatic correctness for these tasks. |

## Six option visual kinds

| Kind | Fields | Rendering requirement |
|---|---|---|
| asset | `asset`, optional `silhouette`, `showLabel` | Use matching atlas crop. `silhouette` needs a true alpha-mask silhouette; a black CSS filter on a solid white tile produces an unusable rectangle. If transparency is unavailable, remove the white background or use a contour/edge-derived silhouette. `showLabel` is required for Indonesian initial-letter rounds. |
| shape | `shape`, `color` (hex), `colorName` | SVG geometry; support circle, square, triangle, rectangle, oval, diamond, pentagon, hexagon, star, heart. A diamond must have equal side lengths. |
| glyph | `symbol` | Render a legible numeral or letter, respecting case. |
| quantity | `value`, `groupAsset`, `layout` | Render exactly value individual pictures. Never print the numeric answer as the visible caption. |
| measurement | `measure`, `value`, `shape`, `scale` | Use a common fixed viewport for all options. `scale`: both axes; `width`: horizontal bar length; `height`: vertical bar height; `strokeWidth`: thickness of a fixed-length horizontal bar. Do not auto-fit each option independently. |
| arrow | `direction`, `rotation`, `color` | Arrow points **up at rotation 0°**, rotates clockwise. Includes diagonal arrows (45°,135°,225°,315°). |

Positions rounds use `layout: 'fixed-3-by-3'` and option `position`, with exactly one card in each of top-left/top-center/top-right/middle-left/center/middle-right/bottom-left/bottom-center/bottom-right. Preserve this placement. Some questions request an entire row/column, so allow three selections. Hiding fixed placement makes the questions invalid.

Some rounds contain `reference` or `referenceText`; display these above the choices. Same/different needs its reference; initial-letter rounds need the reference letter. For color/shape pairing, matching deliberately ignores the other attribute, using `criterion`. Initial-letter tasks explicitly use Indonesian vocabulary even in the English interface, indicated by `languageOfTask: 'id'` and English instructions.

## Scenes

`scene.kind: 'quantity'` has `count`, `item: {asset, ...}`, `layout: 'row'|'grid'|'scattered'`, and `seed`. Place every object without overlap, preferably regular enough for younger children to count. Scattered layouts must remain deterministic and within bounds.

`scene.kind: 'arithmetic'` has `operation: 'add'|'subtract'`, `a`, `b`, `item`, and `crossOutRemoved`.

* Add: show `a` pictures, a plus sign, and a separate group of `b` pictures.
* Subtract: show `a` pictures total and visibly cross out exactly `b` of those pictures. Do not draw `a + b` pictures for subtraction. The remaining count is `a - b`.
* Show zero as an empty outlined group or empty-set marker. Zero is a legitimate operand and result.

Pattern strips contain **flat** visual items, but `canvas.guide` pattern-strip `items` contain the **canonical nested visual schema**, such as `{kind:'shape',shape:'circle',color:'red'}` where color is a color ID, not hex. Normalize these through the curriculum colors table.

## Canvas guide kinds

All canvases use a `viewBox: [0,0,400,300]`. Scale coordinates with the drawing surface and translate pointer coordinates back into that viewBox.

| Kind | Fields |
|---|---|
| line | `x1,y1,x2,y2`, optional `strokeWidth`, `dashed` |
| circle | `cx,cy,r,fill` |
| path | SVG `d`, `stroke`, `strokeWidth`, `fill` |
| shape-outline | `shape,cx,cy,width,height` |
| trace-glyph | `text,x,y,fontSize`; centered text with outline/dotted styling |
| asset | `asset,x,y,width,height` |
| pattern-strip | `items,x,y,width`; preserve full sequence and leave drawing room below |

`trace.paths` are actual SVG paths for line/curve activities. Shape/glyph tracing uses `trace.source: 'shape-outline'|'glyph-outline'`; use the rendered outline as the coverage target. Glyphs are font outlines, not a claim about educational handwriting stroke direction.

Mirror drawing displays a dashed center axis and dots on its left. `modelAnswer` gives reflected right-hand coordinates; keep it hidden until a caregiver requests the example. Open imagination tasks use `openEnded: true`. These have valid task objectives but no single correct drawing.

## Content and verification

41 sourced image asset IDs are referenced; fish, penguin, teapot, pot, sock, drum, and heart image assets were removed. The geometry named heart is drawn with SVG. `raindrop` consistently replaces the earlier rain asset name. No habitat, diet, or baby-animal classification assumptions are used.

`generate_catalogue.py` deterministically regenerates the two exports and `validation-report.json`. `audit_catalogue.py` reads the generated exports and independently checks answer semantics, producing `semantic-audit.json`. The audit passed all 5,376 rounds. It cannot verify the supplied illustrations' identity, actual crop fidelity, real silhouette transparency, rendering proportions, or pointer behavior; those require browser checks after integration.

Recommended implementation: load category metadata eagerly; load worksheets on category/player entry. Centralize one `Visual` renderer and one normalized `CanvasGuide` renderer. Keep engine state separate from content and derive score only from correct sets/pairs/order or explicit self-check completion. Do not merge those pedagogically different success modes into a falsely objective accuracy score.
