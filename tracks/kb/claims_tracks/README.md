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
| `scripts/read_claim.py` | read-only: a claim, its locator rows, history and the cited lines of the stored source (terminal only) |
| `scripts/counts.py` | read-only counts by track x label x status and the figures (baseline, after, before/after) |
| `scripts/annotate.py` | inserts claim_events rows (action `annotate`) and refreshes statuses of hand-added claims, inside the writer lock |
| `scripts/batch_*.sh` | one registered run per batch of database writes (kb claim verify/refute/relocate/check) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py`, unchanged |
| `figures/` | figures copied from registered runs |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/claims_tracks/scripts/read_claim.py 166 167      # read a claim at its source
harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/kb/claims_tracks --cores 1 \
  --purpose 'claims_tracks counts' -- python3 tracks/kb/claims_tracks/scripts/counts.py --tag after
```

## Results

(written at the end of the package)

## Requests

(written at the end of the package)
