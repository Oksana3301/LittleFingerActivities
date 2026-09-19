# Littlefinger Activities

A calm illustrated activity workbook in Indonesian and English. The existing Little World Site has been redesigned around the user's September 2026 workbook references: sage surroundings, cream paper, large individual illustrations, simple instructions, matching lines, pencil controls and an optional sticker tray.

## Implemented catalogue

- 3,365 practice worksheets in 159 categories: 3,192 four-part practice sheets plus 173 new one-part learning activities (12,941 parts).
- Added 20 categories covering planets, the body and senses, family terms, everyday objects, science, social situations, and early mathematics (480 additional worksheets).
- Fifteen interaction engines, including guided exploration: identify, compare, pair, count/arithmetic, pattern, sequence, memory, trace, draw, sort, puzzle assembly, spatial placement, ordered routes and world-map markers.
- The original 133 categories offer at least four activity kinds across three interaction engines. New learning paths use formats appropriate to each task. The catalogue includes matching, explicit-rule exceptions, three-or-more selections, shadows, clue guessing, memory, patterns, ordering, sorting, counting, tracing and drawing. Categories show alternating kinds and an activity-type filter.
- Added another 16 categories with 384 worksheets covering vehicles, mechanical parts, tools, robots, sports, camping, dinosaurs and construction play. Sorting supports tapping a card then a group, or dragging it.
- Added 12 categories with 288 worksheets about toothbrushing, bathing, handwashing, toilet care, mealtimes, bedtime, tidying, polite words, helping family, younger children, friendship and daily routines. All new content includes Indonesian, English and simplified Mandarin.
- One additional curated introductory egg/animal worksheet.
- These are practice variations; they are not represented as 3,365 distinct learning objectives or activity types.
- 249 original illustrated objects on fifteen imagegen sprite sheets, plus a mother/child vignette. Original generation prompts and font licenses accompany assets.
- All 48 previous caregiver activities remain accessible under For grown-ups → About → Previous family activities. Existing notes, family routines, countdowns and saved data are preserved.

## Experience

The app opens directly on an illustrated worksheet. Categories and favorites are available in the left navigation. Completed parts can be repeated or skipped without penalties. Selecting a sticker and tapping the sheet (or the keyboard-accessible Place in corner control) adds a decoration. The caregiver area contains language, age, mute, reduced-motion and session settings, notes, routines, trip countdowns, data export and daily reports.

Worksheet data is served in 159 category files and loaded on demand; fetched categories are cached in memory. Progress, strokes, favorites and stickers use versioned browser storage (`astra-workbook-v2`); previous family data remains in `little-world-v1`. Learning progress has no cloud backup, child accounts or external analytics. Parent audio alone is stored privately per authenticated account. Network access is required for uncached assets and categories. The app reports load/storage errors and supports retry.

## Content and review

The catalogue is generated deterministically from authored content rules. Automated structural and semantic checks validate every round, including unique answers, pair matching, quantity/arithmetic values and pattern rules. The content has not received independent educator or language review; this status is stated in the caregiver area. Drawing and tracing completion is self-reported exploration, not accuracy grading. Counts and journal notes do not assess developmental milestones. All off-screen activities require a caregiver.

## Development

Use the configured Sites execution profile and standard project scripts. `node scripts/validate-workbook.mjs` checks all shipped catalogue records. `npx tsc --noEmit` checks TypeScript. `scripts/curriculum/generate_catalogue.py` and `audit_catalogue.py` contain the reproducible catalogue authoring and semantic checks. Run `python scripts/import-workbook.py <generated-catalogue-directory>` to normalize generated data and emit the original category bundles and compact client index. Then run the expansion generator in a temporary output directory and `python scripts/import-expansion.py <expansion-output-directory>` to merge the additional catalogue. Existing worksheet IDs and browser storage keys stay unchanged. Asset IDs and sprite positions are shared through `app/data/art-atlases.json`.

The optional WebMCP search tool (`search_worksheets`) registers when `document.modelContext` is available. It exposes catalogue search only; all normal UI functionality works without it.

Printing uses a dedicated blank worksheet layout, not the completed on-screen state. Memory worksheets print pairs; subtraction prints crossed-out removed items. Choose Print → Save as PDF in browsers that support it. Device speech is user initiated: questions and each answer have separate listening controls. A listening tap explicitly enables sound; muting cancels speech. Known female voices are preferred within the selected language, with a caregiver voice picker and three reading speeds. Voice availability and sound vary by device; a consistent maternal voice is not guaranteed. Memory cards reveal their listening control only when face-up. When enabled, parent recordings are downloaded privately on demand. Missing recordings use device speech.

Generate the latest expansion with `python scripts/curriculum/generate_vehicle_hobbies.py --out <temporary-directory>`, then import that directory with `python scripts/import-expansion.py <temporary-directory>`. The generator runs its independent semantic audit. `node scripts/verify-device-voice.cjs` checks speech control logic with a mock synthesis engine; it does not verify audible quality.

## Multilingual listening

Each worksheet and legacy activity has an audio-language selector independent from its Indonesian/English interface. Questions, picture labels, examples, pattern cards, count pictures and legacy story/checklist steps support Indonesian, English, Mandarin and Modern Standard Arabic. Mandarin narration uses translated text, with visible Hanzi for questions and answer captions, and an on-demand cached dictionary. Alphabet/number targets remain the target symbols. Mandarin voice selection accepts verified Mandarin locale forms and excludes Cantonese. Caregivers can pick the installed voice and pace. Audible playback still depends on installed device voices; this test browser supplied none.

`node scripts/validate-narration.cjs` verifies all playable question/picture/step translations and checks the context-specific height translation. `node scripts/verify-device-voice.cjs` includes 36 mocked control checks; neither substitutes for physical-device listening or a full native-language editorial review. Good-habit content uses encouraging, specific actions; no hygiene fear, forced touch, food pressure or demand for unquestioning obedience.

Generate the habits expansion with `python scripts/curriculum/generate_habits.py --out <temporary-directory>`, then use the same expansion importer. The accompanying independent validator verifies answer meanings and mutations. New question/label text must be added to `public/audio/mandarin.json` and `public/audio/arabic.json`, or carry its own `zh` and `ar` fields; run the narration coverage check before publishing.

## Arabic and adjective expansion

Added 288 practice worksheets in 12 categories: hot/cold, soft/hard, smooth/rough, wet/dry, open/closed, full/empty, heavy/light, bright/dim, fast/slow, loud/quiet, tidy/messy, and kind describing words. The adjective filter also includes existing height, length, size, thickness, direction, position and same/different categories. Handsome/beautiful are quoted vocabulary and optional compliments, never a judgment of a child's appearance, body or background. New content has four-language text and 32 illustrations.

`python scripts/curriculum/generate_adjectives.py --out <temporary-directory>` creates the expansion and runs an independent semantic audit, including 22 deliberate corruption fixtures. Import with the shared expansion importer.

Arabic text has local RTL direction while diagrams and gameplay retain their original order. Narration dictionaries load separately and cannot overwrite each other during rapid language switching. Arabic voices accept regional locales and keep the selected voice's exact locale. Known female names have token boundaries to avoid false matches. `node scripts/verify-narration-races.cjs` checks asynchronous dictionary loading, caching, retry and stale-response behavior.

Responsive changes include 44px listening controls, fluid artwork, wrapping toolbars and tabs, dynamic header offsets, scrollable dialogs and matching lines measured from actual card positions. Preview checks cover 320–1920px widths, short landscape and simulated doubled text. This is not a physical-device or audible-pronunciation certification.

## Activity variety across all categories

Revised 1,164 existing worksheets (4,656 rounds), preserving the catalogue's 2,784 IDs and favorites. Each revised worksheet has four different tasks; no revised worksheets within a category repeat the same task set. Formats are selected for their subject, rather than requiring every format in every category. The remaining content keeps established practice, including 78 worksheets with repeated rounds that the audit reports explicitly.

Questions and picture descriptions in revised content carry Indonesian, English, Mandarin and Arabic. Multiple-selection tasks explain that several pictures may be selected, show the selection count, and require the exact correct set. Exception tasks name their classification rule. Clue matching presents readable and playable clues. Hidden memory cards do not disclose their audio labels.

Updated content uses a revision in its progress key so a previous answer cannot complete a changed task. Previous history is retained. Round resolution clears incompatible optional game fields before applying the next round. Drawing remains self-reported exploration.

The reproducible generators and independent validator are in `scripts/curriculum/variety`; its README specifies the preserved baseline input. `public/specs/activity-variety-report.json` records per-category coverage, and `variety-semantic-audit.json` records independent structural and semantic findings. `node scripts/verify-workbook-transitions.cjs` checks progress isolation, round field cleanup, selection semantics and alternating category order.

## Visual discovery and spatial games

The catalogue now separates 26 learning areas, 19 ways to play, and seven optional learning-focus tags. Illustrated theme and play cards replace the mixed list of themes and interaction types. Filters combine and carry the chosen play type into a category. Nineteen category titles were clarified while IDs and prior progress stay unchanged.

Added 120 worksheets / 480 rounds in five categories: six-format transport play, picture details, picture puzzles, spatial layouts, and route adventures. Cropped guessing uses a neutral reference audio label; puzzle pieces use clipped portions of existing illustrations. Puzzle assembly and spatial copying support pointer dragging, tap-to-place, and keyboard buttons. Completion requires correct positions. Routes require checkpoints in order; jumping to the end cannot finish. Drawing remains exploration. Blank print views and four-language narration text cover the new games.

The transport set follows the reference's six formats. Wheeled vehicles correctly include bicycles. Its assembly game is a picture puzzle, not a wheel-shaped replacement part; labels say “Lengkapi gambar.” Existing illustrations are reused without a new image download.

Reproduce content with `python scripts/curriculum/generate_spatial.py --site . --output TEMP_DIRECTORY`, then `python scripts/import-expansion.py TEMP_DIRECTORY`. The separately authored discovery mapping is `app/data/discovery-taxonomy.json`. Its category IDs must cover the catalogue exactly.

Validation: `python scripts/curriculum/validate_spatial.py --report public/specs/spatial-audit.json` checks all 480 new rounds, source-asset crop coverage, puzzle tiles, layout models, route geometry, exact answer meanings and duplicate tasks. This optional editorial audit needs Pillow and NumPy. `node scripts/verify-spatial-games.cjs` checks completion and relocation semantics; run the existing catalogue, narration and transition validators as well. Preview checks include tap and pointer drag, wrong/correct placements, moving pieces, ordered-route completion, cropped guessing, combined filters and 320–1920px layouts. No physical-device or audible-language certification is claimed.


## Weather, seasons, food, world discovery, games and jobs

Added 288 practice worksheets / 1,152 rounds in twelve categories: weather signs and equipment; four seasons and Indonesian rainy/dry seasons; Indonesian and world foods; countries and flags; toys and kind play; jobs and their tools. Each new category has 24 worksheets, four different rounds per worksheet, at least four ways to play and at least three engines. New content includes complete Indonesian, English, Mandarin and Arabic narration text. Audio uses the established device-voice selection and fallback flow.

The world map offers 32 location rounds across 24 countries. Numbered 44px markers and flag cards select the same answer. Marker combinations remain separated on narrow layouts; country markers indicate approximate interior locations, not capitals or exact borders. Flags retain their orientation when Arabic is selected. Exact locally served flag SVGs come from flag-icons (MIT); the world silhouette uses Natural Earth geometry (public domain). Attribution and licenses are in `public/specs/geography` and `public/assets/geography/FLAGS-LICENSE.txt`.

There are 48 new original illustrations: 16 foods, 16 weather/season objects and scenes, 12 professions, and four traditional or familiar games. Seasonal wording avoids universal four-season or fixed-month claims. Food clues describe the illustrations without exclusive-origin claims. Jobs are introduced by their work and tools, not gender.

Source generators are in `scripts/curriculum/topics/{nature,food-work,world-games}`. They generate output beside the script by default; world-games also accepts an output directory and country metadata path. Import each output with `python scripts/import-expansion.py OUTPUT_DIRECTORY`. The discovery taxonomy is maintained separately. Per-group audit reports in `public/specs/topics-*-audit.json` record four-language coverage, distinct round tasksets and answer integrity.


## Littlefinger mobile, daily reports and preorder

The Littlefinger Activities wordmark replaces the former product branding. Mobile uses a compact header, direct report navigation, readable worksheet text, search before filters, and six initial themes with all twenty-six accessible on expansion. Existing IDs and local-storage keys remain intact.

The daily report (`/#report`) tracks local-date worksheet openings, distinct answer submissions, correct scored rounds, first-check success, completed parts, newly completed parts and newly completed full worksheets. Repeated unchanged submissions do not inflate metrics. Drawing and tracing count as creative completion, not correctness. Category strengths require at least three attempted parts and 70% first-check success; interests require repeat openings plus at least two correct parts. These are descriptive play indicators, not developmental assessments. Reports cover the main workbook, use one local browser profile and have no cloud synchronization. Undated earlier progress remains undated.

`node scripts/verify-daily-report.cjs` covers deduplication, replay, midnight continuation, fresh next-day attempts, historical progress, content revisions, creative work, full-sheet accomplishments and cross-tab merging.

`/preorder` is a parent-facing registration page: Rp39,000 annually (Rp55,000 reference price), twelve months from activation, with manual renewal. Registration is unpaid; payment collection, billing, customer entitlement enforcement and automatic renewal are not implemented. Four-language speech remains device-dependent. Ten introductory Islamic activities are optional in parent settings; they do not provide Quran recitation audio or a complete ritual manual. Share metadata is configured for this page.

Registrations persist in native D1 using the `DB` binding and the checked-in Drizzle migration. Name and normalized WhatsApp are validated server-side; duplicate numbers retain one entry. Consent is required. Requests are bounded and rate-limited. No WhatsApp or email is automatically sent.

`/admin` and `/api/admin/preorders` require trusted Sites authentication and a case-insensitive match to the server-only `LITTLEFINGER_OWNER_EMAIL` environment variable. The owner can view/export registrations and set an HTTPS `chat.whatsapp.com` group invite. Until supplied, the success screen explicitly says the group link is pending. Never place contact lists or owner credentials in public assets. Source archives are not shipped as public assets.

Local verification: successful production build and TypeScript check; 20 report regression cases; browser checks at phone, tablet and desktop sizes; correct/incorrect worksheet-to-report flow; successful persistent registration; duplicate registration; invalid number and missing-consent rejection; anonymous admin denial. Local QA registration was removed. Owner-authenticated admin interaction and physical-device voice quality were not verified by the test browser.


## Learning pathways and personal parent narration

The attached A–Z brief is mapped into 26 learning areas and 583 exact subtopics. The audit connects 175 subtopics to established content and introduces 402 through 173 substantive new sheets; six retain explicit partial notes (profession tools for every role, broader traffic signs, additional extreme-weather hazards, full wudu, full salah, and a dedicated worship calendar). This is introductory coverage, not certification of mastery. The four age routes are guidance. There are 89 guided explorations, 26 pairs, 21 selection tasks, 16 sequences, 14 drawing tasks, and seven sorts among the new sheets. Related objectives intentionally share a task instead of cloning variants. Original illustrated assets remain unchanged.

Sources are in `scripts/curriculum/learning-paths`. Run `python scripts/integrate-learning-paths.py` to regenerate new category bundles, catalogue metadata, learning areas, and coverage. `python scripts/verify-learning-paths.py` verifies all 583 source entries, four-language authored text, asset references, engine contracts and no duplicate new task prompts. Guidance involving current geography and optional faith retains source URLs in the authored coverage notes. Parent-led practical work has checkboxes and optional observations; completion is self-reported and excluded from answer accuracy.

Parent settings offer **Use parent recordings** and **Recording mode**. Recording mode reveals a microphone beside each speakable question, face-up label, and retry/success/creative response. Read the exact displayed sentence, including the child's current name. Each language and personalized sentence has its own recording; changing a name therefore falls back to device speech until that exact sentence is recorded. Recordings are not cloned or automatically translated. Indonesian, English, Mandarin, and Arabic questions and feedback address the child by name; Arabic spoken text uses RTL. Blank names produce natural unnamed responses.

`/parent-voice` requires trusted ChatGPT identity. Audio objects use the native private `AUDIO` R2 binding; owner/language/text-hash metadata uses D1 `voice_recordings`. The new append-only migration is `0001_chilly_yellow_claw.sql`. API reads and writes derive ownership only from trusted authentication. Same-origin writes, size/signature checks, replace-on-success storage, cache invalidation, per-language deletion, and no-store responses protect private clips. UI recording stops after 60 seconds; uploads must have a readable duration at most 60 seconds and be at most 5 MB. Server storage is bounded to 2,000 recordings and 250 MB per account. No third-party voice service is used.

Verification for this update: 173 authored activity contracts and all 583 subtopic mappings; 79,269 four-language narration checks across 12,942 playable parts including the introduction; 21 daily-report cases; 12 parent-voice API cases using real SQLite migrations with mocked identity/object transport; TypeScript and production build. Browser checks cover personalized feedback in four languages, guided completion/report exclusion, subtopic navigation, 320/390px phone layout and 768px tablet layout, recording dialog controls, and Arabic direction. No real microphone was captured and no authenticated production recording was created during QA; physical-device audio quality remains unverified. The additional palette image/HEX was absent in the latest message, so existing UI colors and all artwork are preserved.

## Dedicated Supabase project and requested GitHub mirror

The Site now has a server-only connection to the dedicated Little Finger Activities Supabase project. Account schema, ownership policies and transactional regression checks live under `supabase/`. See [connection status and launch boundaries](docs/SUPABASE_CONNECTION.md) for verified behavior, environment names, migration details and remaining launch work.

The requested external mirror is `Oksana3301/LittleFingerActivities`. Its current GitHub installation needs access to that repository before the complete source and artwork can be pushed. The existing Site repository remains the authoritative saved source until that handoff succeeds.
