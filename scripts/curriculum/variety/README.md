# Activity variety reproduction

Inputs: a separate checkout/export of the prior catalogue at Git commit `0856128936fb7f4d7fa5e228122ee0658a28a6db`. Do not use the already-revised catalogue as the baseline. Generators read that source and write to three separate temporary directories.

```sh
python generate_realworld.py --site BASELINE_CHECKOUT --out REALWORLD_OUTPUT
python generate_formal.py BASELINE_CHECKOUT FORMAL_OUTPUT
python generate_creative.py --source BASELINE_CHECKOUT --out CREATIVE_OUTPUT
```

From the current Site root, merge with `python scripts/merge-variety.py REALWORLD_OUTPUT FORMAL_OUTPUT CREATIVE_OUTPUT`. This preserves every worksheet ID while writing content revisions. Run `node scripts/curriculum/variety/validate-variety.cjs . --report public/specs/variety-semantic-audit.json`, `node scripts/validate-workbook.mjs`, `node scripts/validate-narration.cjs` and `node scripts/verify-workbook-transitions.cjs`. The independent validator also supports `--self-test`.

The three content manifests document ownership and checks. Cross-category use of the same practice is intentional; revised worksheets within a category have distinct task sets. Older repeated rounds remain reported as warnings. Checks are not educator review, translation certification, or developmental assessment.
