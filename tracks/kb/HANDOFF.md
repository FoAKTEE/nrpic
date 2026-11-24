# HANDOFF of kb

State (2026-11-24 ~23:50 UTC, end of the kb lead session of wave 3 batch 13). The knowledge base
holds 762 papers (684 of brief section 17 plus 78 additions in kb/manifests/arxiv_additions.tsv)
and 64 repositories; readers use `kb-data/db/current` -> `kb-20261124-9872d21.sqlite` (762
papers, 864 claims, download rows of every addition). KB-G0, KB-G1, KB-G2 are signed
(coord/GATES.md). The KB-G3 stage package exists (tracks/kb/stage/KB-G3/) and is NOT complete:
criterion C1 fails on two brief seeds (803, 805). No package is in progress, no run is going, no
card job exists, no queue entry of kb. The worktree is clean after the last commit.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show            # answers of orch (KB-G3, manifest question), A, D, F
(cd kb && .venv/bin/python -m pytest -q)      # the kb suite
python3 -I kb/bin/kb status                   # 762 papers, 864 claims, snapshot kb-20261124-9872d21
```

Then, in this order:
1. Claims package (closes KB-G3 C1; stage/KB-G3/OPEN.md O1-O3): seed 803 (stability of
   matter-dominated FLRW under Einstein-Vlasov; 1709.00267 and 1706.09501/claim 752 are in the
   store); seed 805 (S1 expanding-ball relations, Einstein-Straus bubble, strong-field Hills
   scale: ask A, D, F which run or note derived each, then annotate); re-seed fragment claims
   (85 and about 17 in claims_tracks/AUDIT.md). Add `kb claim supersede` (new claim + old one
   refuted as worded + link), the step that 682 lacked.
2. A fresh verifier session for KB-G3 (decision 0016 item 4), then `nrpic-stage verify kb
   KB-G3 --no-rerun` and `report` again. Do not rerun kb runs blindly: the claims batches write
   to the database.
3. Bibliography parser (verifier item 3): \arXiv{id}{class}, "[HEP-PH 9610477]", bare trailing
   ids, \eprint{}, DOIs in \url/\href/\doibase; seeded misses in run
   kb-20261124-132849-3ebad97 `whole_missed_sample.tsv`; then `kb resolve-bib`, snapshot.
4. Paper-code links (core messages 20261123T020802Z and 20261124T130734Z, acknowledged, not yet
   applied): M23 symbol NrpicWriteConservation -> NrpicWriteHistory; M18 verified by T1 of
   tracks/core/interfaces/id_solver.md section 8 (not by the monitor after the solve); M20, M25
   verified by the dust-collapse runs; M24 by A's periodic_diag runs (A-20261121-212800-d7f31a4);
   M19 stays claimed. Edit kb/curated/paper_code_links.tsv, re-ingest the links, snapshot.
5. Smaller: 2505.00286 bare \abstract (no abstract chunk); plain-TeX front matter of the six
   old-style papers (status review); 0707.4654, 1006.1632 on disk in no manifest (asked orch).

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; decisions 0016, 0019-0034; brief section 12
   (lines 1218-1461, with Read offset/limit).
2. `tracks/kb/stage/KB-G3/{VERIFIER,EVIDENCE,OPEN,SCOPE}.md`; `tracks/kb/stage/REVIEW-wave3.md`
   (last section: batch 13); `tracks/kb/JOURNAL.md` (last entry: R1, C1-C3, S1, Q2).
3. Package READMEs: `tracks/kb/{ingest4,claims_tracks,claims_brief}/README.md`;
   `tracks/kb/lead_b13/scripts/` (the claims batches of this session, each run registered).

## Decisions taken in batch 13 (lead)

- A claim whose text is wrong is superseded, not edited: new claim with the right text, old one
  refuted with "the claim text is wrong, not the paper" (682 -> 862).
- A seed that is a question is answered by an annotation; when the answer is a statement with a
  locator, it becomes a new fulltext claim (714 -> 863). 781 and 804 were verified directly
  (positive answer, or parts all carried by checked claims).
- Abstract-level readings were verified to fulltext with "abstract lines" in the evidence (the
  tool has no person-set "abstract" label); OPEN.md O4.
- KB-G3 scope (stage/KB-G3/SCOPE.md): seeds 806, 807, 810, 811, 812 do not bear on G1 [JUDGEMENT].

## Traps

- `kb claim relocate` needs `--by` (run kb-20261124-233445-89478ae failed on it); `kb claim
  add --locator` writes no locator rows: relocate after every add. `kb claim verify --locator`
  writes rows itself.
- `kb show` reads db/current: use `--db /data/haiyangw/nrpic/kb-data/db/kb.sqlite` to read
  papers ingested after the last snapshot.
- nrpic-fetch-arxiv writes no download rows: run `kb verify-downloads` after every fetch, or
  QA C1 says the counts disagree. Its exit 1 is the known gr-qc/9412071.
- `nrpic-run submit` refuses a dirty worktree; commit first. Never `nrpic-stage verify` with
  reruns for kb: the claims batches write to the database.
- A re-ingest renumbers chunks and equations: `kb ingest arxiv --remap-claims`, `kb embed`,
  then a snapshot. `tracks/kb/verify_g2/heldout.yaml` is held out: never tune on it.
- Snapshots about 1 GB each; keep those cited in notes (f2fcda5, 621430e, 44b7406, a848a06,
  a782f1e, bbaafe5, aa0a2ae, 9872d21). Disk /data at 84 % on 2026-11-24.
