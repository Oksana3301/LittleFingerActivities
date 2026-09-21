# Mandarin translation review

Reviewed 40 representative instruction strings against the English source and their actual worksheet contexts, plus picture-label edge cases. The arithmetic, pattern order, direction, alphabet, Indonesian initial-letter, science, and social examples preserve their learning goals. No label-map changes were needed.

## Required context correction

`Choose the shortest one.` currently maps to `选出最短的那个。`. This is correct for length, but the same exact English string appears in height activities too. The public worksheets contain 48 length and 48 height instances of this instruction.

- For category `height`: **`Choose the shortest one.` → `选出最矮的那个。`**
- For category `length`: retain **`Choose the shortest one.` → `选出最短的那个。`**

Root confirmed this will be handled by a category-aware `worksheetInstruction` helper used for narration and coverage checks. A global exact-string replacement would break one of the two contexts.

## Minor clarity improvements

Family labels intentionally retain unspecified relationships: Grandmother = 奶奶或外婆; Older sibling = 哥哥或姐姐; Younger sibling = 弟弟或妹妹. When two card labels are joined, quote each target so “or” cannot be mistaken for an alternative answer. Proposed exact replacements:

| English | Mandarin |
|---|---|
| Choose the Grandmother and Family cards. | 选出“奶奶或外婆”和“家人”这两张卡片。 |
| Choose the Younger sibling and Grandmother cards. | 选出“弟弟或妹妹”和“奶奶或外婆”这两张卡片。 |
| Choose the Older sibling and Father cards. | 选出“哥哥或姐姐”和“爸爸”这两张卡片。 |

The instruction author was notified to apply the same quoted-label template to other family pairs. These are clarity improvements, not incorrect family translations.

## Sample coverage

| Area | Examples reviewed | Assessment |
|---|---:|---|
| Arithmetic and quantities | 8 | Meaning and task preserved |
| Patterns and order | 4 | Meaning and task preserved |
| Letters and Indonesian learning targets | 4 | Meaning and task preserved |
| Comparatives | 6 | Context correction above |
| Position and direction | 6 | Meaning and task preserved |
| Family | 4 | Quoted labels recommended |
| Science | 4 | Meaning and task preserved |
| Social dialogue | 4 | Meaning and task preserved |

## Picture labels

- `Spring` → 弹簧, `Nut` → 螺母, `Crane` → 起重机, and `Orange` → 橙色 match actual machine/construction/color contexts.
- `Blue circle number 2` → 2号蓝色圆形 preserves option identity without revealing size. Bar-based height/length/thickness labels use 长条 consistently.
- Arrow directions and image positions preserve their distinction, e.g. `Brown arrow down` → 指向下的棕色箭头; positional labels put the location before the object.
- Quantity labels retain all quantities; object-specific count labels use natural Mandarin classifiers. Arabic numeral and Latin letter learning targets remain unchanged deliberately.
- Nia is 妮娅 consistently in dialogue labels and instructions. Scientific labels use common Mandarin names (霸王龙、三角龙、剑龙 and the eight planet names).

The exact 40 bilingual review records are saved in `translation-review-samples.json`. This was a bounded semantic review, not a full native-editor review of every translation. No Site files were edited.
