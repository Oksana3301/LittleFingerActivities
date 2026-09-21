# Astra workbook revamp — 2026-09-18

The current product is an illustrated workbook with 2,496 practice worksheets, 104 categories and 9,984 playable rounds. These are practice variations using ten engines, not 2,496 unique learning objectives. A curated introductory worksheet is additional.

The earlier 48 activities, common catalogue and original roadmap files are retained as legacy material. They are accessible through the caregiver area. See `workbook-catalogue-report.json`, `workbook-semantic-audit.json` and `workbook-qa-report.json` for the current implementation and verification scope.

The 20 supplied reference images informed the new layout and interaction style. The final art comprises original generated sprite sheets and a parent/child vignette; the UI is live HTML/React, not a flattened reference screenshot.

Use with a caregiver. The content has automated checks but is not independently educator-reviewed. No claim of child-development assessment or real-world mastery is made.


## Additional subjects — September 2026

Added 480 four-part practice worksheets across 20 categories: planets, planet facts, space matching; body parts, senses, body care; family terms and matching; kind words and taking turns; room and school objects and their uses; living/nonliving, plant needs, weather choices; quantity comparison, equal groups, neighboring numbers and arithmetic stories. New categories are grouped by subject. All previous catalogue IDs and browser storage keys are retained.

The three new atlases contain 48 separate illustrations. Planet illustrations identify subjects, but do not represent relative sizes or distances. Family terms are labels in an example family, not assumptions about the child’s household. Social stories are practice invitations, not behavioral or developmental assessment. Longer story choices use wide cards on phones.

## Vehicles, workshop and hobbies

Added 384 four-part worksheets in 16 categories, with 48 new original illustrations. Activities include sorting into groups, matching tools, identifying vehicles and machine parts, ordering explicitly shown toy assembly cards, counting vehicles, tracing paths, drawing robots, sports matching, camping memory, hobby patterns, dinosaur names, comparing quantities and adventure sorting. The current catalogue contains 2,208 worksheets across 92 categories. Existing catalogue files and worksheet IDs are preserved.

Question and answer speakers use device speech synthesis on explicit taps. Known female voice names are preferred within the chosen language; caregivers can choose an installed voice and adjust reading speed. There is no standardized maternal recording: voices and availability depend on the device. No prerecorded audio files are loaded. Some device voices require a network connection. Hidden memory cards have no audio label until turned over. A missing voice shows a readable fallback, and cancellation prevents queued or stale speech on navigation, pause or hiding the tab.

Validation covered all 8,832 rounds, the new semantic audit, a 12-case mocked speech-control harness, representative browser interactions, and phone/tablet iframe layouts. The test browser provided no speech voices, so actual audible voice quality and physical-device playback remain unverified. See the current QA report for scope.

## Mandarin audio and good habits

The audio language is now independent of the interface language: Indonesian, English or Mandarin. Translated text is used for Mandarin speech; changing the voice locale alone is never treated as translation. Coverage includes all worksheet questions and pictured choices plus legacy caregiver activities, with listening controls for examples, patterns, count pictures, drawing subjects, legacy story steps and checklists. Mandarin text is loaded once on demand and kept in memory. The female-voice preference includes verified Mandarin names, with Cantonese excluded from the Mandarin voice picker.

Added 288 four-part worksheets in 12 good-habit and kindness categories, illustrated by 32 new object/action images. Positive routines include toothbrushing with help, supported bathing, handwashing, toilet care, meals, bedtime, tidying, kind words and considerate social actions. Sequencing stories explicitly name the three steps being practised. Children may ask for help or decline touch; hygiene is explained through concrete cleaning rather than threats or shame. Existing family routines offer optional quick-add habits.

All translated speech still depends on the device speech engine. The browser test environment had no installed speech voices; control behavior and written translations were verified, but actual audible playback and perceived maternal voice quality were not.


## Arabic, adjectives and responsive update — 18 September 2026

Catalogue: 2,784 worksheets / 116 categories / 11,136 short rounds, plus the introductory worksheet and 48 retained family activities. Added 288 adjective worksheets in 12 categories with 32 original illustrations. Modern Standard Arabic questions/picture descriptions are available across the catalogue, alongside ID/EN/Mandarin. Arabic RTL applies only to text; positional lessons retain their coordinate system.

The adjective group also exposes earlier height, direction, size, length, thickness and position lessons. Appearance vocabulary is used as optional quoted compliments without ranking people. Generators have independent semantic checks and deliberate corruptions.

Layout uses measured header height, responsive grids, fluid artwork, wrapping toolbars/tabs, scrollable dialogs, 44px listening controls and picture-measured matching paths. Seven-card patterns scroll within their own rail on narrow phones.

Validation: workbook structure, four-language narration coverage, 36 speech-control checks, eight asynchronous narration tests, independent adjective audit (73,315 checks and 22 negative fixtures), TypeScript and production build. Preview covered 320, 375, 768, 1024, 1440 and 1920 widths, 740×360 landscape, Arabic pair completion, all ten engine layouts on narrow screens, collection discovery and simulated doubled text. No physical mobile devices or audible voices were available; native-speaker editorial review remains outstanding.

## Activity variety — 18 September 2026

All 116 categories now offer at least four activity kinds through at least three interaction engines. The total stays at 2,784 worksheets / 11,136 rounds. Revised 1,164 worksheets / 4,656 rounds with subject-appropriate combinations of picture matching, clue matching, memory, three-or-more selections, explicit-rule exceptions, shadows, patterns, sequencing, sorting, counting, tracing and drawing. Every revised worksheet has four distinct semantic tasks, and revised worksheets within a category have distinct task sets. Cross-category practice reuse remains intentional; 78 retained worksheets with repeated rounds are recorded as audit warnings.

The collection alternates activity kinds, labels each card and offers a type filter. Player feedback distinguishes single and multiple selection. Revised progress has its own content revision without deleting previous history or changing favorite IDs. Round fields are normalized to prevent a previous example or equation from leaking into a different task. Questions and pictured options retain four-language listening text.

Format research used the public descriptions of Etsy's [animal shadow matching](https://www.etsy.com/listing/1143988349/farm-animal-shadow-matching-cards-12), [odd-one-out](https://www.etsy.com/listing/1711667828/find-the-odd-one-outocean-animals), and [picture patterns](https://www.etsy.com/listing/1722771688/ocean-animals-patternswhat-comes). No listing artwork or worksheet files were copied. These are format references, not evidence of developmental effectiveness.

Validation: full catalogue structure and four-language narration coverage; independent variety audit with 18 negative fixtures, 936 additional formal relations and 660 creative matching/pattern relations; four transition and progress checks; TypeScript and production build. Preview play-throughs checked incorrect/complete multi-selection, exception selection, clue matching, arithmetic groups and a nine-position grid; collection type filtering and 320, 768, 1440, 1920 widths plus 740×360 landscape had no page-level horizontal overflow. Visual checks covered the mobile shadow reference and clue-matching cards. Device audio quality and physical devices were not tested. Automated and sampled editorial checks do not constitute independent educator or native-language review.

## Visual/spatial reference and discovery update — 18 September 2026

Added five categories with 120 worksheets / 480 rounds, bringing the catalogue to 2,904 worksheets / 121 categories / 11,616 rounds. Transport play includes shadow pairs, explicit exceptions, three-answer selection, cropped detail guessing, picture assembly and ordered routes. New detail, puzzle, spatial-copy and path categories also mix established formats. The bicycle is included in the reference's wheeled-vehicle answer set. Assembly is described as picture completion, not exact wheel-part replacement.

Discovery uses 14 illustrated subject themes, 17 activity kinds and seven optional focus tags. Theme and kind filters combine; categories show actual counts and distinct ways to play. Existing IDs, favorites, notes and progress are preserved. New rounds carry spatial-1 revisions.

Independent audit: 120 worksheets / 480 rounds, zero structural or semantic findings, zero same-category duplicate task sets or repeated rounds, all cropped pieces visibly contain illustration. Question, picture, checkpoint and positional-cell narration has ID/EN/ZH/AR text. Automated checks do not certify language quality or developmental benefit.

Preview verified empty-answer rejection, correct puzzle tap placement, pointer drag placement with selection cleared, incorrect and corrected spatial layouts, moved pieces, endpoint-only route rejection, ordered-route completion, cropped image recognition, combined discovery filters, and 320/768/1440/1920 widths plus 740×360 landscape without page-level horizontal overflow. Visual review covered cropped artwork, themes and mobile controls. Physical-device and audible speech testing remain unavailable.


## September 2026 topic expansion

Added weather, seasons, Indonesian/world food, countries/flags, toys/kind play, and professions/tools: twelve categories, 288 worksheets and 1,152 rounds. Catalogue total: 3,192 worksheets, 133 categories, 12,768 rounds; 20 discovery themes, 18 activity kinds and 14 engines. Existing worksheet IDs and progress keys are preserved.

New world-map engine supports numbered map markers and equivalent flag-card selection, exact-set checking, four-language audio labels and translated captions, printable blank maps and responsive 44px controls. Country combinations use physical map spacing with a minimum 54.41px between markers at a 244px map width. Weather/seasons have eight activity kinds, food/jobs six, and geography/games four per category.

Added three original 4×4 illustration atlases (48 subjects) and 24 locally served flag SVGs. Natural Earth geography is public domain; flag-icons is MIT. Geography verification confirms each marker lies within its source polygon. Sources and licenses are retained under specs/geography. Questions avoid fixed season calendars, exclusive food origin claims and gender-based job classifications.

Validation passed: complete catalogue structure (3,192 worksheets / 12,768 rounds), 78,434 narration-text checks with no missing translations, TypeScript, and saved-progress/round-transition checks. Browser QA confirmed wrong/right map answers, next-round reset, three-answer food selection, topic filtering, 44px map targets, and no horizontal page overflow at 320, 768, 1440 and 1920px plus 740×360 landscape. Independent review found no concrete food/job or flag-clue errors. Physical devices and audible pronunciation were not certified.
