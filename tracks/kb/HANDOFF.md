# HANDOFF of kb

State (2026-11-25 ~03:55 UTC, end of the kb lead session of wave 3 batch 15). The knowledge base
holds 762 papers (684 of brief section 17 plus 78 additions in kb/manifests/arxiv_additions.tsv)
and 64 repositories; readers use `kb-data/db/current` -> `kb-20261125-2f97258.sqlite` (762
papers, 881 claims; run kb-20261125-033718-3405697). KB-G0, KB-G1, KB-G2 are signed
(coord/GATES.md). The KB-G3 package (tracks/kb/stage/KB-G3/) is complete for the second fresh
verifier of decision 0036 item 3: criterion C1 is met, `nrpic-stage verify --no-rerun` PASS,
STAGE_REPORT.md written. No package is in progress, no run is going, no card job, no queue
entry of kb. The worktree is clean after the last commit.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show            # orch's answer on the second verifier and gr-qc/0608095
(cd kb && .venv/bin/python -m pytest -q)      # the kb suite
python3 -I kb/bin/kb status                   # 762 papers, 881 claims, snapshot kb-20261125-2f97258
```

Then, in this order:
1. When the second KB-G3 verifier has written its report (tracks/kb/stage/KB-G3/, second
   VERIFIER file): act on each WRONG or NOT CONFIRMED item (supersede, never edit a claim text),
   then `nrpic-stage verify kb KB-G3 --no-rerun` and `report` again. What it should read is in
   OPEN.md O6 and the message to orch of batch 15 (869, 865-868, 870-881, 862-864, the 30
   sample verdicts, 805's annotation, the reservation on 877).
2. Weak-class pass 2 (OPEN.md O7): 543 claims labelled as supported by a pipeline step and
   never read against their wording; estimated 86.5 % right (about 70 wrong). Start with stratum
   WA (404 left), texts starting with a cut ("and", "i.e.", "which", "see ..."), and the short
   candidates 454, 465, 512, 134, 193, 352. Before using tracks/kb/claims3/scripts/weak_class.py
   again, make it exclude events by `kb-claims3` (it counts 548 = 543 + 5 annotated sample
   claims; run kb-20261125-033530-5a1ac43).
3. Bibliography parser (KB-G3 verifier item 3): \arXiv{id}{class}, "[HEP-PH 9610477]", bare
   trailing ids, \eprint{}, DOIs in \url/\href/\doibase; seeded misses in run
   kb-20261124-132849-3ebad97 `whole_missed_sample.tsv`; then `kb resolve-bib`, snapshot.
4. Paper-code links (core messages 20261123T020802Z and 20261124T130734Z): M23 symbol
   NrpicWriteConservation -> NrpicWriteHistory; M18 verified by T1 of
   tracks/core/interfaces/id_solver.md section 8; M20, M25 by the dust-collapse runs; M24 by
   A's periodic_diag runs (A-20261121-212800-d7f31a4); M19 stays claimed. Edit
   kb/curated/paper_code_links.tsv, re-ingest the links, snapshot.
5. Smaller: O4 (a person-set "abstract" label or flag; 448, 753, 765, 409, 447, 449, 450);
   gr-qc/0608095 out of the downloads table if orch says so (one line in
   kb/manifests/downloads_excluded.tsv); 2505.00286 bare \abstract; plain-TeX front matter of
   six old-style papers; index the parameters of release core-v0.7 (`kb ingest repo --this`).

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; decisions 0016, 0019-0036; brief section 12
   (lines 1218-1461, with Read offset/limit).
2. `tracks/kb/stage/KB-G3/{OPEN,EVIDENCE,CHECKLIST,VERIFIER}.md`; `tracks/kb/stage/REVIEW-wave3.md`
   (last section: batch 15); `tracks/kb/JOURNAL.md` (last entry: V1, V2, R2, S2).
3. `tracks/kb/claims3/README.md` (the package of batch 14) and `tracks/kb/lead_b15/scripts/`
   (review_claims3.py: ledger vs database and changed claims vs the last snapshot; reuse it in
   every review of a claims package).

## Decisions taken in batch 15 (lead)

- Superseding a claim with an existing one (`--to`) is not a reading of the successor: its
  checked_by/checked_at stay (kb/kbtool/claims_db.py; test
  test_supersede_to_existing_keeps_successor_checked_by). Five rows restored from snapshot
  kb-20261124-9872d21 (run kb-20261125-033703-3bd4386).
- KB-G3 C1 is judged on to_verify claims with a processing event; the five brief seeds left are
  those decision 0035 item 5 rules out of G1. The weak class is a known limit, not a C1 item.

## Traps

- `kb claim relocate` needs `--by`; `kb claim add --locator` writes no locator rows: relocate
  after every add. `kb claim supersede --text` writes its locator rows itself.
- `kb show` reads db/current: use `--db /data/haiyangw/nrpic/kb-data/db/kb.sqlite` (where the
  subcommand takes it) to read work after the last snapshot.
- nrpic-fetch-arxiv writes no download rows: run `kb verify-downloads` after every fetch. Its
  exit 1 is the known gr-qc/9412071.
- `nrpic-run submit` refuses a dirty worktree; commit first. Never `nrpic-stage verify` with
  reruns for kb: the claims batches write to the database. Do not rerun claims3's apply plans.
- A re-ingest renumbers chunks and equations: `kb ingest arxiv --remap-claims`, `kb embed`,
  then a snapshot. `tracks/kb/verify_g2/heldout.yaml` is held out: never tune on it.
- Snapshots about 1 GB each; keep those cited in notes (f2fcda5, 621430e, 44b7406, a848a06,
  a782f1e, bbaafe5, aa0a2ae, 9872d21, 2f97258). Disk /data at 85 % on 2026-11-25.
