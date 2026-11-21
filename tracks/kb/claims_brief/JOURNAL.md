# Journal of package claims_brief (kb, wave 3)

Predictions are written before the test or the database write they concern; outcomes after,
including failed predictions.

## Entry 0 (2026-11-21 23:15Z): restart state

- Nothing of this package was in git (`tracks/kb/HANDOFF.md` row `claims_brief`: "nothing in
  git; scratch/kb/claims_brief/ only"). The session cut on 2026-11-20 14:35 PST left in
  `scratch/kb/claims_brief/dev/` a module `kbtool/claims_brief.py` (seeder, CHECK.md parser and
  join, defect machinery; the table of defects empty), the subcommand in `claims_cli.py`, a test
  file of 9 tests, a dry-run table and a join table; no journal, no database writes (checked:
  0 claims with seed_key `brief:v2:%` or `brief-defect:%` in `kb-data/db/kb.sqlite`, 700 claims).
- The shared modules it builds on (`claims_db`, `claims_parse`, `claims_check`, `brief`,
  `meta_brief16`, `lock`, `paths`, `db`, `cli`, `conftest`) are unchanged in the worktree since
  that copy; `claims_cli.py` of the worktree differs from the copy only by the seed-brief
  additions. So I continue from that code in a fresh copy `scratch/kb/claims_brief/dev2/`
  (worktree `kb/` at 264e9423 plus the three files), reviewed line by line.
- Fixes on restart: (1) one test expected rule `lead-in` for "**Recommendation.** ... cheap.
  [JUDGEMENT]", where the label stands after the full stop of a block whose bold lead-in has
  closed; the rule of the module (after-stop: the whole block) is the documented one, so the
  test was wrong and now expects `after-stop`. (2) New rule: a bracket right after "marked" or
  "labelled" names a label and labels nothing (brief line 1751, item 7 of section 15,
  "Quantitative statements marked [BACKGROUND]"; read: its own line).

## Rule for the main text [JUDGEMENT]

Headings `## N.` of the brief (by code, `grep '^## '`): 0 how to use, 1 bottom line, 2 starting
point, 3 landscape, 4 criteria, 5 ranking, 6 method innovation, 7 open questions, 8 unknown
unknowns, 9 execution plan (track sheets), 10 verification suite, 11 harness, 12 knowledge base,
13 git discipline, 14 kick-off prompts, 15 items to verify, 16 references, 17 manifests. Main
text = 1 to 10 and 15: these hold statements about physics, the literature, the codes and the
plan; 0 is the legend of the labels; 11 to 14 are instructions for sessions (their [VERIFIED]
marks are about Claude Code documentation, not the literature); 16 and 17 are the reference
list and manifests (checked separately by `kb meta brief16`). Section 15 is a list of items to
verify; an item without a label of its own becomes a to_verify seed (its heading is the label).

## P1 (prediction before the dry run and the seed write)

Independent count of the label brackets with awk (not the module; fenced blocks skipped,
first keyword decides; output `scratch/kb/claims_brief/tmp/indep_count.txt`), brief sha256
9492261e...a48449: in the main text 98 explicit labels, by section 1:8, 2:8, 3:54, 5:14, 6:5,
7:1, 8:2, 9:4, 10:1, 15:1; families VERIFIED 51, BACKGROUND 18, JUDGEMENT 20, TO VERIFY 9.
Section 15 has 15 numbered items. With the mention rule the one bracket of section 15 (line
1751) is a mention, so the item becomes implicit.

Prediction: the seeder finds 112 statements = 97 explicit + 15 items of section 15;
VERIFIED 51 (abstract + title_only), background 17, judgement 20, to_verify 9 + 15 = 24; one
seed per label occurrence, 112 unique seed keys; the second write adds 0 and reports 112 "same".
Refuted if any count differs; then I find the cause before writing.

Outcome of the dry run (dev2, 23:14Z, not yet registered; `tmp/dry2.tsv`): 112 statements:
abstract 46, title_only 5, background 17, judgement 20, to_verify 24; by section 1:8, 2:8,
3:54, 5:14, 6:5, 7:1, 8:2, 9:4, 10:1, 15:15; 112 unique keys. Held. The registered dry run and
the write follow.
