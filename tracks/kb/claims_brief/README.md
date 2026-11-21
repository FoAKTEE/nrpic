# claims_brief: the brief's labelled statements as claims, the brief-check outcomes, defects of cited papers

Package of owner kb, wave 3 (batch 8, 2026-11-21). It feeds gate KB-G3 (brief 12.10, L1458) and
answers decision 0016 item 8: the rows of `coord/BRIEF_ERRATA.md` section 5 now have claims.
A session cut on 2026-11-20 left a module in `scratch/kb/claims_brief/dev/`. It was restarted
from that module (JOURNAL entry 0), with nothing of it in git and nothing in the database.

## What is here

| File | Content |
|---|---|
| `JOURNAL.md` | predictions P1-P6 written before each test or write, and their outcomes |
| `REVIEW_SAMPLE.md` | second-agent review of 30 CHECK.md rows (30 agree) |
| `LEDGER.tsv` | one row per brief seed: brief line, section, label as written, seed label, claim id, outcome, label and status now, paper, tracks, evidence (CHECK.md rows, errata ids, locator) |
| `DEFECTS.tsv` | one row per defect claim: entry, part (printed, right, fact), claim id, paper, label, status, supersedes, errata row, locator |
| `CHECK_UNJOINED.tsv` | the 304 CHECK.md rows that joined no seed, with the reason |
| `counts.json` | the counts of the ledger run |
| `apply_step2/` | the generated commands of step 2 (`apply.sh`, `annotate.tsv`), committed before they ran |
| `scripts/` | `plan_outcomes.py` (join to actions, review sample), `gen_apply.py`, `make_ledger.py`, `make_figures.py`, `figstyle.py` (copied unchanged from `harness/style/`) |
| `figures/` | `fig_seeds_by_section` (seeds per section by outcome), `fig_check_review` (CHECK.md rows joined per package; review agreement) |

Code, in `kb/` (committed here):
- `kb/kbtool/claims_brief.py`: the seeder, the CHECK.md parser and join, and the `DEFECTS` table with its writer.
- `kb/kbtool/claims_cli.py`: the subcommand `kb claim seed-brief` (`--dry-run`, `--tsv`, `--join`, `--annotate`, `--defects`, `--recheck`).
- `kb/tests/test_claims_brief.py`: 11 tests on a synthetic brief and CHECK.md.

## Rules (decided here) [JUDGEMENT]

- **Main text.** Sections 1-10 and 15 are the main text.
  - Section 0 is the legend of the labels.
  - Sections 11-14 are instructions for sessions.
  - Sections 16-17 are the reference list and the manifests.
  - Code blocks are skipped.
  - In section 15, an item without a label of its own is a to_verify seed, because its heading labels it.
  - A bracket right after "marked" or "labelled" names a label and labels nothing (line 1751).
- **Mapping (brief 12.8).**
  - [VERIFIED] becomes title_only when the bracket names titles, otherwise abstract.
  - [BACKGROUND] becomes background, [JUDGEMENT] becomes judgement (including "JUDGEMENT + TO VERIFY"), and [TO VERIFY] becomes to_verify.
  - Paper id: the first arXiv id of the statement; all ids go into the evidence.
  - Track tags come from the section (S1-S12, 3.10, 3.11, 9.3-9.9, section 2 core), otherwise from the tracks that cite the ids.
  - Origin is `brief v2 L<n>`; the seed key is `brief:v2:L<n>:<k>`.
- **Outcome per seed (step 2).**
  - Judgement seeds are annotated only.
  - A seed is refuted when a row on it is CORRECTED and its errata row stands in section 1 or 3 of BRIEF_ERRATA.
  - A seed whose only CORRECTED row is a section-2 imprecision is annotated partial.
  - A seed is verified when every row on it is CONFIRMED or CONFIRMED (precision) and has a TeX locator that resolves in the database. The locator is the first resolving locator of each row.
  - Every other seed is annotated located.
- **Defect claims (step 3).**
  - Each printed statement is a claim labelled refuted, in our wording.
  - The right value becomes a second claim with `supersedes` pointing to the printed one:
    - fulltext, if I read the value at the locator;
    - judgement, if it was computed or read off a figure;
    - abstract, if it comes from a metadata record.
  - Status is 'checked' only for fulltext; a judgement or record-level claim whose locators resolve is 'located'.

## Results

| Step | Run | Result |
|---|---|---|
| dry run | kb-20261121-231750-f313add | 112 statements; abstract 46, title_only 5, background 17, judgement 20, to_verify 24; equal to an independent awk count (P1) |
| seed | kb-20261121-231800-1988829 | claims 701-812; a second run gave "same 112" |
| join | kb-20261121-231835-5f7d281 | 620 CHECK.md rows of 11 packages (kb/brief-check 476a1763), 0 parse problems; 316 joined to 65 seeds; 219 on unlabelled lines; 85 outside the labelled sentence |
| plan and sample | kb-20261121-232142-3378910 | 595 of 595 TeX locators of the rows resolve in the database; plan 42 verify, 11 refute, 12 annotate; review sample of 30 (seed 20261121) |
| review | REVIEW_SAMPLE.md | 30 agree, 0 disagree (P3) |
| write step 2 | kb-20261121-232417-80127f0 | 42 verified, 11 refuted, 12 annotated; annotate again: "same 12" |
| defects | kb-20261121-233151-3bb85dc | 48 claims (813-860): 24 refuted, 20 superseding, 4 facts; second run "same 48"; recheck: 0 unresolved |
| ledger, figures | kb-20261121-233339-f153821 | LEDGER.tsv, DEFECTS.tsv, CHECK_UNJOINED.tsv, counts.json, the two figures |

State of the 112 seeds now:
- verified 42
- refuted 11
- open 39, of which:
  - 8 located;
  - 1 partial;
  - 30 with no CHECK.md row.
- judgement 20, of which 3 are annotated.

Locator rows on the seeds: 159, all resolved. The claim ids of each section-5 row are in
the outbox message `tracks/kb/outbox/20261121T233354Z__to-orch__errata-section5-claims.md`.

**Failed predictions.** P2 held overall: 289 of the 476 rows of the section-3 packages joined
(61 per cent). It failed per package:
- s34_36: 14 of 66 rows joined;
- s37_38: 17 of 60;
- s39_frontier: 0 of 44, because lines 239-256 carry no label.

The first test of the restarted module failed because the test itself was wrong (it expected
the rule lead-in for a label written after the full stop); JOURNAL entry 0 records this.
Every other prediction held.

## How to rerun

From the worktree root:

1. Dry run: `kb/.venv/bin/python -I kb/bin/kb claim seed-brief --brief einstein_vlasov_pic_cosmology_agent_brief.en.md --dry-run --tsv OUT`
2. Seed (idempotent): the same command without `--dry-run`.
3. Join: `... claim seed-brief --brief ... --join novelty s310 s311 s31_32 s33 s34_36 s35 s37_38 s39_frontier s5_s6 s7_s8 --check-ref 476a1763 --tsv OUT`
4. Plan: `python3 -I tracks/kb/claims_brief/scripts/plan_outcomes.py --join JOIN --kb kb --repo . --ref 476a1763 --out DIR`
5. Generate the step-2 commands: `python3 -I tracks/kb/claims_brief/scripts/gen_apply.py DIR/plan_seeds.tsv OUTDIR`, then `bash OUTDIR/apply.sh`.
6. Defects: `... claim seed-brief --defects` (`--dry-run` lists them), then `... claim seed-brief --recheck`.
7. Ledger and figures: `scripts/make_ledger.py`, then `scripts/make_figures.py` (commands are in the manifest of run kb-20261121-233339-f153821).

Every database write goes through `kbtool.lock.writer_lock`. Every command is idempotent.

## Open items

- **`kb claim check --id` was not run on the new claims.** It re-checks only the wave-1 seeds. `seed-brief --recheck` is the check for the claims of this package, and it found 0 unresolved.
- **17 CORRECTED rows of the brief check have no claim** (CHECK_UNJOINED.tsv): s39_frontier 7, s5_s6 4, s31_32 2 (CHECK #40 and #51, which the s31_32 report asks for), s34_36 2, novelty 1, s33 1. The statements they correct carry no label, and brief 12.8 seeds only labelled statements. Whether to add them is for the kb lead.
- **30 seeds have no CHECK.md row.** They sit in sections 1, 2, 9, 10 and 15 and parts of 5, which the brief check did not cover. 8 seeds are only located: some rows confirm at metadata records only.
- **Review depth.** The review covers 2-3 rows per package. It shows no systematic error in the packages, but it is not a check of each package [JUDGEMENT].
- **Remarks for the lead:**
  - 2002.12778 CKSY2021.tex:287 prints R_H^{-3} where the volume needs R_H^3 [TO VERIFY]. It is not a section-5 row and was not entered.
  - Claims 603-618 and 679-683 of other writers duplicate some defect findings. They were not changed: they are not this package's claims.

## Requests

- **To the kb lead:**
  - decide on the 17 corrected but unlabelled brief statements (above);
  - pass the refutations to F-hills (claims 766, 767) and A-emd-pbh (claim 742);
  - `kb/tests/test_meta_papers.py::test_additions_file_is_valid` fails in the worktree without this package (ingest3's request).
- **To orch:** the claim ids of section 5 of `coord/BRIEF_ERRATA.md` are in the outbox message. The errata file may now point to them.
