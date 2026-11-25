# HANDOFF of kb

State (2026-11-25 ~12:55 UTC, end of the kb lead session of wave 3 batch 17). The knowledge base
holds 762 papers (684 of brief section 17 plus 78 additions in kb/manifests/arxiv_additions.tsv)
and 64 repositories; readers use `kb-data/db/current` -> kb-20261125-56c4b53 (895 claims; run kb-20261125-124304-2790a38).
All four gates of kb are signed: KB-G0, KB-G1, KB-G2, and KB-G3 (2026-11-24, pass with
reservations; coord/GATES.md, decision 0037 item 1). kb is in service mode. No package is in
progress, no run is going, no card job, no queue entry of kb. The worktree is clean after the
last commit.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show
(cd kb && .venv/bin/python -m pytest -q)      # the kb suite
python3 -I kb/bin/kb status                   # 762 papers, 895 claims, snapshot kb-20261125-56c4b53
```

Then, in this order:
1. Weak-class pass 2 (KB-G3 OPEN.md O7): about 400 machine-located claims (label set by the
   automatic seeder, never read against their wording) are right as worded about 4 times in 5
   (28/35 pooled, VERIFIER2.md section 2). Start with texts that begin with a cut ("and", "i.e.",
   "which", "see ...") and the short candidates 454, 465, 512, 134, 193, 352. Before reusing
   tracks/kb/claims3/scripts/weak_class.py make it exclude events of kb-claims3 and kb-lead-b17.
   Write a plan JSON like tracks/kb/lead_b17/plans/P1_verifier2.json and apply it with
   tracks/kb/claims3/scripts/apply.py (dry run first, both registered); supersede, never verify
   a wrong text; check with a script like lead_b17/scripts/check_a2.py; snapshot.
2. VERIFIER2 leftovers (REVIEW-wave3.md batch 17): 741's locator (Spin_PBH.tex L1206, relocate
   with --by); 428's author order (Ciarfella first, TBH.tex L37-47: supersede); 804 vs 805
   treated alike (both instructions: one rule); 313 locator debris, 430 cut at both ends; 864
   lists "Jena" among authors of 2602.06961; 877 splits into a paper claim and F's run result;
   OPEN O4 (409, 447, 449, 450, 448, 753, 765: fulltext label on abstract readings).
3. Bibliography parser (KB-G3 verifier item 3): \arXiv{id}{class}, "[HEP-PH 9610477]", bare
   trailing ids, \eprint{}, DOIs in \url/\href/\doibase; seeded misses in run
   kb-20261124-132849-3ebad97 `whole_missed_sample.tsv`; then `kb resolve-bib`, snapshot.
4. Paper-code links (core messages 20261123T020802Z and 20261124T130734Z): M23 symbol
   NrpicWriteConservation -> NrpicWriteHistory; M18 verified by T1 of
   tracks/core/interfaces/id_solver.md section 8; M20, M25 by the dust-collapse runs; M24 by A's
   periodic_diag runs (A-20261121-212800-d7f31a4); M19 stays claimed. Edit
   kb/curated/paper_code_links.tsv, re-ingest the links, snapshot.
5. Smaller: OPEN O9 (a label for repository facts and a locator form for metadata records: a
   schema change; 892-895 and 709, 844 wait on it); seeds 806, 807, 810-812 and now 892-895 in
   service mode; gr-qc/0608095 out of the downloads table if orch says so; 2505.00286 bare
   \abstract; plain-TeX front matter of six old papers; `kb ingest repo --this` for core-v0.7.

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; decisions 0016, 0019-0038; brief section 12
   (lines 1218-1461, with Read offset/limit).
2. `tracks/kb/stage/KB-G3/{OPEN,EVIDENCE,VERIFIER2}.md`; `tracks/kb/stage/REVIEW-wave3.md` (last
   section: batch 17); `tracks/kb/JOURNAL.md` (last entry: A1, A2, S3).
3. `tracks/kb/lead_b17/plans/P1_verifier2.json` (the form of a plan with evidence per action).

## Decisions taken in batch 17 (lead)

- A claim whose statement is about a repository or a tool, not a paper, is stored as to_verify
  with the check on record in the supersede evidence (892-895), in the class of seeds 810-812
  (decision 0035 item 5), until the label set has a class for it (O9).
- Metadata claims (709, 844) keep label abstract without locator rows; an annotate event with the
  record's fields is their processing.
- Headings with an evidence mark and no statement (710, 711, 715) are withdrawn.

## Traps

- `kb claim relocate` needs `--by`; `kb claim add --locator` writes no locator rows: relocate
  after every add. `kb claim supersede --text` (and apply.py's supersede) writes its rows itself.
- `kb show` reads db/current: use `--db /data/haiyangw/nrpic/kb-data/db/kb.sqlite` (where the
  subcommand takes it) to read work after the last snapshot.
- nrpic-fetch-arxiv writes no download rows: run `kb verify-downloads` after every fetch. Its
  exit 1 is the known gr-qc/9412071.
- `nrpic-run submit` refuses a dirty worktree; commit first. Never `nrpic-stage verify` with
  reruns for kb: the claims batches write to the database. Do not rerun the plans of claims3 or
  lead_b17 (they are applied; apply.py refuses a second supersede anyway).
- A re-ingest renumbers chunks and equations: `kb ingest arxiv --remap-claims`, `kb embed`,
  then a snapshot. `tracks/kb/verify_g2/heldout.yaml` is held out: never tune on it.
- Snapshots about 1 GB each; keep those cited in notes (f2fcda5, 621430e, 44b7406, a848a06,
  a782f1e, bbaafe5, aa0a2ae, 9872d21, 2f97258, and 56c4b53). Disk /data at 85 % on 2026-11-25.
