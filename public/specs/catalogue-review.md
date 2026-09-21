# Caregiver demo catalogue implementation review

Date: 2026-09-17. Scope: the scratch `activities.json` content asset only. This is an AI-assisted content consistency and implementation review. It is not human editorial approval, professional early-childhood assessment, certified translation review, or evidence that the website renderer works.

## Exact counts and states

- 48 authored demo records with 48 distinct stable IDs.
- 12 interaction engine kinds; exactly 4 records per engine.
- 48 records have `editorialState: pending` and `publicationState: demo`.
- 48 records explicitly require caregiver selection and co-play and state that human editorial and language review has not occurred.
- 0 editorially approved records and 0 published learning activities in this asset.
- English and Bahasa Indonesia are present for every required localized content field, option label, group label, and checklist/story step.
- The count is 48 authored activity scripts, not 48 interaction types or 48 independently validated learning objectives. These records must not support a claim of 1,000+ available activities.

| Engine | Records | Main distinctions within the four records |
|---|---:|---|
| identify | 4 | Curved outline; three corners; capital A form; zero as absence |
| pair | 4 | Shape outline; printed letter form; quantity group; arrow direction |
| sort | 4 | Corner presence; letters versus numerals; one versus more; three versus four sides |
| sequence | 4 | Forward numeral order; backward numeral order; growing quantities; alphabet order |
| count | 4 | One-to-one correspondence; naming the total; order invariance; planning a counting route |
| compare | 4 | Clearly different amounts; fewer via matching; neighboring amounts; comparison involving zero |
| pattern | 4 | AB, AAB, ABC, and ABBA repeating units |
| memory | 4 | Outline/location; numeral naming as a cue; letter features; arrow orientation/location |
| draw | 4 | Optional feeling expression; imaginary composition; route representation; varied mark making |
| trace | 4 | Continuous curve; straight segments and turns; letter form; mixed numeral curve and lines |
| checklist | 4 | Small household task; optional seated movement; observation; preparing belongings |
| story | 4 | Requesting help; agreed turns; entering a new setting; mixed feelings about changing attention |

| Suggested starting age | Records |
|---|---:|
| 2 | 7 |
| 3 | 12 |
| 4 | 14 |
| 5 | 15 |

| Pack | Records |
|---|---:|
| little-discoveries | 6 |
| abc-and-words | 6 |
| numbers-and-shapes | 14 |
| everyday-adventures | 4 |
| feelings-and-friends | 4 |
| ready-for-school | 7 |
| rainy-day-play | 4 |
| nature-noticing | 3 |

## Answer-key review

All answer IDs exist. Sort membership agrees with the stated category rule. Sequence answer lists contain each option exactly once. Pair options contain one unique definition per matching identity, intended for duplication into two columns. Memory definitions contain three or four distinct identities, intended for exactly two copies each. Count targets are 2, 3, 4, and 6. All geometric counting sets should use the first option as their repeated object.

| Pattern ID | Repeating unit | Displayed prefix | Correct next item |
|---|---|---|---|
| circle-square-repeat | circle, square | circle, square, circle, square, circle | square |
| two-then-one | circle, circle, triangle | circle, circle, triangle, circle, circle | triangle |
| three-shape-loop | circle, square, triangle | circle, square, triangle, circle, square | triangle |
| four-part-repeat | circle, triangle, triangle, circle | circle, triangle, triangle, circle, circle, triangle, triangle | circle |

Three pattern instructions and their identical `prompt` values were clarified during this review to state “Repeat this group” in both languages: `circle-square-repeat`, `two-then-one`, and `three-shape-loop`. This makes the intended repetition rule explicit. Their prefixes, options, and answer keys did not change. `four-part-repeat` already explicitly names the group and the following group.

| Sequence ID | Intended order | Review result |
|---|---|---|
| one-two-three | 1 → 2 → 3 | Matches instruction and all three options |
| count-back-to-one | 4 → 3 → 2 → 1 | Matches explicit backward direction |
| growing-dot-groups | 1 dot → 2 dots → 3 dots → 4 dots | Each successive set increases by one |
| first-four-letters | A → B → C → D | Conventional shared Latin alphabet order; does not teach letter sounds |

| Compare ID | Stated question | Answer |
|---|---|---|
| which-has-more | More: 1 or 3 | 3 |
| fewer-to-count | Fewer: 2 or 4 | 2 |
| just-one-more | More: 5 or 6 | 6 |
| none-is-fewer | Fewer: 0 or 2 | 0 |

For comparison, the numeral in each option is authoritative for its represented quantity. The `countTarget` is not universally the correct answer: `none-is-fewer` has `countTarget: 2` and correct option `zero`. A renderer must use the actual `answer` ID. If quantities accompany numerals, zero must show an empty set rather than a substituted dot or decoration.

## Objective overlap and distinctness limits

The four records in each engine deliberately share an interaction mechanic. Most differ by concept, response demand, representation, strategy, or real-world application. Pattern variants differ structurally rather than through color swaps. Draw, checklist, and story records have different purposes and prompts.

There is meaningful objective overlap across the catalogue. Shape recognition recurs in identification, matching, sorting, tracing, patterns, and memory. Numeral/quantity representations recur in counting, comparison, sequencing, matching, and memory. Letter matching overlaps with letter-memory practice. The two forward quantity sequences overlap with counting practice; the four counting records share one-to-one counting as a foundation. Memory variants have the greatest overlap in core objective: all use location recall, differentiated by visual discrimination and suggested strategies. They should be described as four authored memory demos, not four unrelated memory skills.

The `nature-noticing` pack includes an imaginary shape garden and a counting-route activity alongside an actual observation invitation. These are thematic/editorial assignments, not claims that they teach plant recognition or natural science. Pack balance is intentionally uneven, and pack labels do not establish curriculum coverage.

## Readiness and suitability review

Age values are suggested navigation starting points. They are not developmental standards, prerequisites, assessments, or promises of benefit. The content offers caregiver assistance, pointing and looking alternatives, stopping, and simplified choices. Children do not need to read the instructions independently. The engine must keep those adaptations accessible rather than converting the age filter into a pass/fail test.

The age-2 records emphasize small sets, simple distinctions, free marks, optional tracing, and supported movement. `one-or-more` shows four cards but only two categories; an adult should introduce one card at a time and simplify as needed. Memory begins at the age-3 starting filter with three pairs and requires adult help if hiding/revealing is unfamiliar. Numeral comparison at age 3 explicitly allows the adult to show quantities; displaying only numerals must not imply independent numeral knowledge is required. Longer patterns, backward counts, directional memory, and mixed-feeling stories use older starting filters and remain optional.

Tracing and drawing are exploration rather than handwriting assessments. Capital I varies between print fonts; its content explicitly acknowledges optional top and bottom bars. Letter activities concern visible glyphs or alphabet order, not translated phonics. No story grades a child's own feeling or requires personal disclosure. No routine auto-completes by elapsed time; caregivers should record only actual participation. Any checklist steps can be skipped.

## Safety and review limits

Every record includes materials, preparation, an off-screen invitation, a safety note, and an adaptation. The content avoids loose small sensory fillers, chemicals, hot liquids, sharp tools, tasting plants, open windows, forced touch, and unsupervised baby care. Movement invitations put the device away first and offer seated or imagined alternatives. Adults remain responsible for selecting appropriate materials and evaluating the real setting.

The asset contains no religious instruction, real-world recognition photograph substitutes, claims of human review, developmental diagnosis, or claims of real-world mastery from taps. Exact shapes, letters, numerals, and arrows remain renderer obligations: this content review did not inspect actual SVG geometry, chosen font glyphs, layout, color contrast, touch targets, state transitions, randomized solvability, count-once behavior, audio, or accessibility.

This simplified app catalogue does not implement the complete supplied `activity.schema.json` editorial envelope. Production expansion still requires that full contract or a documented mapping, engine-specific validation, asset provenance and checks, implementation verification, genuine editorial review, and qualified Bahasa Indonesia review. Programmatic consistency checks and this report do not satisfy those publication gates.

Reviewed content changes are limited to the three explicit repetition-rule clarifications above. No answer key, count, suggested age, publication state, or editorial state changed. The deliverable reviewed here is `activities.json`; the earlier drafting helper script was not rerun and is not the reviewed source of truth.
