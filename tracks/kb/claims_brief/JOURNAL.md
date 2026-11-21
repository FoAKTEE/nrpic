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

Outcome of the write (run kb-20261121-231800-1988829; dry run kb-20261121-231750-f313add):
first call "new 112", second call "same 112"; database: 112 claims with seed_key
`brief:v2:%`, claim ids 701-812, abstract 46, title_only 5, background 17, judgement 20,
to_verify 24. P1 held in every count; the seeder is idempotent.

## P2 (prediction before the join of the CHECK.md rows, read only)

The eleven CHECK.md files on kb/brief-check at 476a1763 all use the one header
`| # | Brief line | Quotation | Label | Verdict | Locator | Note |` (checked by grep). awk count
of their table rows: novelty 33, s310 74, s311 66, s31_32 61, s33 53, s34_36 66, s35 52,
s37_38 60, s39_frontier 44, s5_s6 69, s7_s8 42; total 620, equal to BRIEF_ERRATA section 7.
Prediction: the parser reads 620 rows with 0 problems. Most rows of sections 3.1 to 3.11 stand
on labelled paragraphs whose bold lead-in rule covers the paragraph, so I expect at least half
of the rows of the section-3 packages to join a seed; rows of sections 5 to 8 stand more often
on unlabelled lines ("no seed on the line"). Refuted if the parser count differs from 620 or
reports a problem, or if fewer than half of the section-3 rows join.

Outcome of P2 (run kb-20261121-231835-5f7d281): 620 rows, 0 problems (held). Joined to a seed:
316 rows (label and quotation 244, only seed of its label 49, quotation 23); not joined: 219
"no seed on the line" (the line has no label: s39_frontier all 44 rows, s5_s6 54, s7_s8 37,
s34_36 30), 85 "quotation outside the labelled statements" (an unlabelled sentence of a
labelled line). Section-3 packages: 289 of 476 rows joined (61 per cent): held overall, but not
per package (s34_36 14 of 66, s37_38 17 of 60, s39_frontier 0 of 44). 65 of the 112 seeds have
at least one row.

## Rules of step 2 [JUDGEMENT]

Script `scripts/plan_outcomes.py` (read only) turns the join into one action per seed:
judgement seed -> annotate (never verified or refuted from the literature, brief 12.8);
a row CORRECTED whose errata row stands in section 1 or 3 of coord/BRIEF_ERRATA.md -> refute
(evidence: the package rows and the errata row ids); CORRECTED only with a section-2 errata row
(an imprecision) -> annotate, status partial; all rows CONFIRMED or CONFIRMED (precision) and
every row with at least one TeX locator that resolves in the database -> verify (fulltext) with
the first resolving locator of each row; otherwise -> annotate, status located. A seed is
verified only when every row on it supports it, so one unsupported part keeps the label.
Review sample: 30 rows, seed 20261121, 3 per package and 2 for novelty, s7_s8, s39_frontier,
drawn from rows with a TeX locator, joined rows first.

## P3 (prediction before the review sample)

Each package's locators were range-checked by its own registered run (BRIEF_ERRATA section 7),
not their content. I expect at most 3 of the 30 to disagree (the threshold of the task), most
likely through a locator that is on the right topic but does not carry the number or the
wording the row claims. Refuted if 4 or more disagree; then no row of the remaining set is
upgraded and they go in as located, not checked.

Outcome of P3 (REVIEW_SAMPLE.md, sample of run kb-20261121-232142-3378910): 30 of 30 agree,
0 disagree; held. Two remarks (novelty #31: "closest work" not rechecked; s7_s8 #22: content
right, class CORRECTED strong, errata row 2.101 an imprecision). Side observation: 2002.12778
CKSY2021.tex:287 prints R_H^{-3} where the volume needs R_H^3 [TO VERIFY], for the lead.

## P4 (prediction before the writes of step 2)

Plan of run kb-20261121-232142-3378910, commands generated by `scripts/gen_apply.py` into
`apply_step2/` (committed before the run): 42 verify, 11 refute, 12 annotate (11 located, 1
partial). Expected: every command exits 0 (no verify on a judgement or refuted seed; every
locator resolves, as the plan found 595 of 595 TeX locators in the database); after the run
the 112 seeds count fulltext 42, refuted 11, abstract 14, background 6, title_only 0,
judgement 20, to_verify 19. A second run of `--annotate` writes nothing (idempotent). Refuted
if any command fails or any count differs.

Outcome of P4 (run kb-20261121-232417-80127f0): 42 "fulltext, checked", 11 "refuted", annotate
"written 12", and the second annotate "same 12"; seeds now fulltext 42, refuted 11, abstract
14, background 6, judgement 20, to_verify 19; statuses checked 42, refuted 11, located 11,
partial 1, unlocated 47; 159 locator rows on the seeds, 159 resolved. Held in every count.

## Step 3: defects of cited papers (DEFECTS table in kbtool/claims_brief.py)

Sources: the 17 rows of coord/BRIEF_ERRATA.md section 5 (r1-r17 in table order; r11-r17 are
the seven section-5 rows of the brief-check ERRATA_ROWS.md files, checked identical by
extraction) and three claims the brief-check reports ask for (q1 Burnett conjecture proven
without symmetry, 2403.03470; q2 lattice horizon masses constant to 0.1 per cent,
1903.01490:653-657; q3 both seed estimates of 2506.17641 v3). I read every printed locator
(and the right-value locators labelled fulltext) myself; where a row's evidence is another
owner's run I cite the run and did not redo it. Rows split where one row holds several
printed statements: 28 entries, 24 refuted printed statements, 20 superseding right values, 4
facts without a printed statement to refute (r12 metadata divergence of 1203.6185, q1-q3).
All papers named are now in the database (ingest3), so no raw-store locator is needed.
Before writing: claims 603-618 and 679-683 of other writers already hold some of the same
findings (as judgement or "as printed" fulltext); they are named in `existing`, not changed.
A rule changed in add_defect: a right value whose locators resolve is 'checked' only when it
is fulltext, otherwise 'located' (a judgement is not a checked passage); test added.

P5 (prediction before the write): 48 new claims; labels refuted 24, judgement 14, fulltext 8,
abstract 2; statuses refuted 24, located 15, checked 8, unlocated 1 (r11's INSPIRE value, a
metadata locator only); every TeX locator part resolves; 20 claims with supersedes set, each
pointing to the printed claim of its entry; a second run adds nothing. Refuted if any count
differs or a TeX locator stays unresolved.

Outcome of P5 (run kb-20261121-233151-3bb85dc): "new 48", then "same 48"; claims 813-860:
refuted 24, judgement 14, fulltext 8, abstract 2; statuses refuted 24, located 15, checked 8,
unlocated 1; 20 claims with supersedes, all pointing to the refuted printed claim of their
entry; 64 locator rows, 64 resolved; recheck: 46 claims with TeX locators, 0 unresolved.
Held in every count. `kb claim check --id` was not run: it re-checks only the wave-1 seeds
(claims_cli.cmd_check walks claims_parse.wave1_sources()), so for these claims the package's
`seed-brief --recheck` is the check, and it found nothing unresolved.

## P6 (prediction before the ledger and figures run, read only)

Ledger from the database and the plan: 112 seed rows with outcomes verified 42, refuted 11,
annotated located 8, annotated partial 1, judgement annotated 3, judgement without a CHECK row
17, open without a CHECK row 30; 48 defect rows; 304 unjoined CHECK rows (219 on unlabelled
lines, 85 outside the labelled statements). Refuted if any count differs from the database
counts of P4 and P5.
