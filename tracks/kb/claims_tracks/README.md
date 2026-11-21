# claims_tracks: the tracks' evidence queue toward KB-G3 (kb, wave 3 round 1)

Gate KB-G3 (brief 12.10, line 1458): every statement of the evidence queue that bears on G1
of the six tracks has been processed. This package processes the claims of the six science
tracks and of core in the claims layer of `kb-data/db/kb.sqlite` (brief 12.8, K8), answers the
requests of B and D to kb, and audits 40 machine-located fulltext claims.

## Definitions

A claim is **processed** when it reaches one of these states:

- (a) fulltext with a resolved locator that this package read: status `checked`, checked by
  `kb-claims_tracks`;
- (b) refuted with evidence (a locator or a run id), the citing track notified;
- (c) relocated (locator corrected), then (a);
- (d) not findable in the full text: the label becomes `abstract` or `title_only` when only the
  abstract or the title carries it; otherwise it stays `to_verify` with a recorded reason (paper
  not in the corpus, statement absent, inference of the track that the text does not settle);
- (e) judgement or background: annotated with the evidence that bears on it (a claim_events row,
  action `annotate`), label unchanged. A judgement is never upgraded to fulltext (brief 12.8).

The **queue** is every claim whose label is `to_verify`, `judgement` or `background`.

## What is here

| Path | What |
|---|---|
| `JOURNAL.md` | predictions and outcomes, in order |
| `LEDGER.tsv` | one row per decision: claim id, track, label and status before and after, locator, evidence, reason (my words), run id |
| `AUDIT.md` | the audit of 40 machine-located fulltext claims |
| `decisions/<batch>.tsv` | one decision per claim (action, locator, evidence, reason) read by `make_batch.py`; `<batch>_annot.tsv` are the annotation rows it derives |
| `scripts/read_claim.py` | read-only: a claim, its locator rows, history and the cited lines of the stored source (terminal only) |
| `scripts/counts.py` | read-only counts by track x label x status and the figures (baseline, after, before/after) |
| `scripts/annotate.py` | inserts claim_events rows (action `annotate`) and refreshes statuses of hand-added claims, inside the writer lock |
| `scripts/make_batch.py`, `scripts/ledger.py` | decisions table -> batch script; ledger rows of a batch (before/after state, read-only) |
| `scripts/batch_*.sh` | one registered run per batch of database writes (kb claim verify/refute/relocate/check): A1, B1, C1, D1, E1, F1a, F1b, K1, AU1, L1 |
| `scripts/check_697.py` | numerical check of D's sign correction of 1707.06302 eq. lmax (claim 697) |
| `scripts/draw_audit.py` | stratified, seeded draw of the audit sample |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py`, unchanged |
| `figures/` | figures copied from registered runs |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/claims_tracks/scripts/read_claim.py --window 2 166 167      # read claims at their sources (terminal only)
# counts and figures (read-only on kb.sqlite):
harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/kb/claims_tracks --cores 1 --allow-no-venv \
  --purpose 'claims_tracks counts' -- python3 tracks/kb/claims_tracks/scripts/counts.py --tag after \
  --before /data/haiyangw/nrpic/scratch/kb/kb-20261120-222240-f9db7eb/counts.json
# a new batch: write decisions/<name>.tsv, then
python3 -I tracks/kb/claims_tracks/scripts/make_batch.py tracks/kb/claims_tracks/decisions/<name>.tsv
git add tracks/kb/claims_tracks && git commit -m '...' -- tracks/kb/claims_tracks      # commit before the run
harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/kb/claims_tracks --cores 1 --allow-no-venv \
  --purpose '...' -- bash tracks/kb/claims_tracks/scripts/batch_<name>.sh
# then append $RUN_DIR/ledger_rows.tsv to LEDGER.tsv
# audit draw: python3 -I tracks/kb/claims_tracks/scripts/draw_audit.py --seed 20261121 --n 40 (inside nrpic-run)
```

Batches never refute or relabel silently. Every write is a `kb claim` command or a
claim_events row from `annotate.py`, made under the writer lock. Re-running a batch would
add duplicate events, so do not rerun a batch that has already been applied (LEDGER.tsv
names its run).

## Results (KB-G3 ledger summary, 2026-11-21)

Every claim of the tracks' evidence queue (labels to_verify, judgement, background; 159
claims on 2026-11-20) is processed. Baseline run `kb-20261120-222240-f9db7eb`, after-counts
run `kb-20261121-213126-ee2e15a`, figure `figures/fig_queue_before_after.png`.

| Track | Queue before | (a)/(c) read, now fulltext/checked | (d) still to_verify, reason recorded | (e) judgement/background annotated | Batches (runs) |
|---|---|---|---|---|---|
| A-emd-pbh | 17 | 14 | 1 (9) | 2 | A1 `kb-20261120-222903-226b273` |
| B-emd-gw | 15 | 4 | 0 | 11 | B1 `kb-20261120-223013-5330e45`; 186 in L1 |
| C-sidm | 14 | 5 | 0 | 9 | C1 `kb-20261121-211743-d9dfe56` |
| D-bh-dress | 28 | 9 | 9 (346, 381, 409, 412, 413, 414, 416, 699, 700) | 10 | D1 `kb-20261121-211759-c80bb03` |
| E-stoch-inf | 7 | 0 | 0 | 7 | E1 `kb-20261121-211809-38a04d0` |
| F-hills | 54 | 47 | 5 (447, 449, 450, 452, 687) | 2 | F1a `kb-20261121-212452-61968d0`, F1b `kb-20261121-212459-e68e5f8`, L1 `kb-20261121-213033-484dc64` |
| core | 24 | 19 | 4 (456, 538, 549, 601) | 1 | K1 `kb-20261121-212503-d466d18` |
| **all** | **159** | **98** (26 at a corrected or added locator) | **19** | **42** | |

- (b) Refuted: none. No passage that I read contradicts a claim of the queue, so no
  refutation message went to any track.
- Why the 19 stay to_verify:
  - paper not in the store: 409, 447, 449, 450, 452;
  - original predates arXiv: 413, 416;
  - a to-do, deferral or repository statement of the track, not a literature claim: 9, 346,
    381, 412, 414, 538, 601, 687;
  - a fragment with no content: 549;
  - needs a second recomputation: 699, 700;
  - metadata not stored: 456.
  The reasons are in LEDGER.tsv and in each claim's events.
- Database after the package (kb.sqlite, run `kb-20261121-213126-ee2e15a`): 700 claims;
  fulltext 639 (175 checked by a person, 464 located by machine), to_verify 19, judgement
  41, background 1.
- Requests answered:
  - D (spike-annotations-run-ids): run ids on 682 and 683, which are now checked; the
    statuses of 697-700 refreshed; the 697 sign correction checked numerically (run D1,
    `check_697.tsv`). Reply `tracks/kb/outbox/20261121T213157Z__to-D-bh-dress__spike-claims-run-ids.md`.
  - B (key-reference claims): 689-695 answer it completely; only the relevance column is
    left out, on purpose. The same reply carries my reading of the 2312.12499 delta factor:
    `tracks/kb/outbox/20261121T213157Z__to-B-emd-gw__key-reference-claims-complete.md`.
  - orch: `tracks/kb/outbox/20261121T213157Z__to-orch__kb-g3-tracks-queue.md`.
- Audit (AUDIT.md, runs `kb-20261121-212635-c33885e` draw and `kb-20261121-212918-9b5b9df`
  writes): 40 of the 502 machine-located claims. 37 are right, 1 had an incomplete locator
  (fixed), 0 are wrong statements, and 2 are fragments. 38 are now checked.
- Prediction Q (JOURNAL, start): verified 98 of 117 to_verify. I had predicted 55-80, so the
  prediction failed on the high side. I underestimated how many "TO VERIFY" items the full
  text settles once read: most were open only because nobody had read the passage. Refuted
  0 (predicted 2-8); 19 kept (predicted 30-55); all 42 judgements and backgrounds annotated
  (held).
- An error of mine, caught in the audit: my K1 evidence for 525 said 2611.12831 gives no
  shift-damping profile, but the profile is at L388-397. The verdict stands for the claim's
  real subject, the absence of an ablation; the correction is an annotation (AU1, JOURNAL).

## Requests

- **kb lead (claims tooling, not this package's to change):**
  1. `kb claim check --id` rewrites the locator rows of a seeded claim from the note. It must
     not run after `verify --locator` or `relocate`; the batches here never did. Please guard
     it in `claims_cli.py`.
  2. The seeder splits a note row into fragments at its locators, for example 85
     ("and L550-563"), 620 ("Abstract") and 549. A lookup finds about 17 among the
     machine-located claims (AUDIT.md). Please re-seed by joining the rows. `kb claim check`
     also skips `served:` and `manual-*` claims (658-662, 689-700); `scripts/annotate.py
     refresh` covers the manual ones.
  3. Record B's new claim on 2312.12499 (L324 against L581-582). This package writes only
     claims that already exist. My reading is in the reply to B.
- **ingest3:** after the chunk remap of the 20 papers, run `kb claim check --id` on the 21
  claims there (171-186, 658-662). This package verified 183, 186 (annotated) and 658-662
  last, before the remap.
- **orch (manifest):** papers that queue claims need and that are not in the store:
  2605.22525, 2609.20338, 2608.22735, 2608.16986, 2610.27775, 2212.10891, 1303.1540,
  2602.06961, 2610.20594 (F); 2307.02474, 2307.10708, 2306.08199, 1904.03781 (D).
- **Tracks:**
  - D: restate or drop 346 and 414.
  - F: 687 is your test design.
  - core: 538 and 549 are fragments of SECTION2_CORRECTIONS.md rows.
- **Not done here (round 2):**
  - the kb-requests of A (Szekeres conformal flatness, 20261121T080816Z) and C (conductivity
    sources, 20261121T081156Z), which need searches and maybe downloads;
  - the 462 machine-located claims that were not drawn.
