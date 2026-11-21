# HANDOFF of kb

State (2026-11-21 ~00:00 UTC on 11-22, end of the kb lead session of wave 3 batch 9). The knowledge
base holds 744 papers (684 of brief section 17 plus 60 additions; gr-qc/0608095 dropped by
decision 0024 item 2) and 64 repositories; readers use `kb-data/db/current` ->
`kb-20261121-aa0a2ae.sqlite`, which carries ingest3's bibliography, claims 1-861 and the code
index of this repository at main 47ab19ab. KB-G0, KB-G1 and KB-G2 are signed (coord/GATES.md).
All four packages cut on 2026-11-20 (ingest3, claims_tracks, claims_brief, code_kb) have
finished and are reviewed (stage/REVIEW-wave3.md, last section). No package is in progress, no
run is going, no card job exists. The worktree is clean after the last commit.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show            # answers from orch, core, A, B, C, F
(cd kb && .venv/bin/python -m pytest -q)      # the whole kb suite (green at the end of batch 9)
python3 -I kb/bin/kb status                   # 744 papers, 861 claims, snapshot kb-20261121-aa0a2ae
```

Then, in this order:
1. KB-G3 stage package: `harness/bin/nrpic-stage collect KB-G3` (owner kb), criteria from the
   brief 12.10 gate line ("every statement in the evidence queue that bears on G1 of the six
   tracks has been processed"); evidence: tracks/kb/claims_tracks (159 queue claims: 98 read,
   19 kept with reasons, 42 annotated; AUDIT.md 37/40 right) and tracks/kb/claims_brief (112
   seeds, 48 defect claims). It needs an independent verifier package first (decision 0016
   item 4): a fresh session that re-reads a stratified sample of claims at their locators.
2. Ingest package (one fetch at a time through nrpic-fetch-arxiv; decision 0016 item 6 for papers
   not on arXiv): Krasinski-Bolejko 2012 on Szekeres apparent horizons, a source for conformal
   flatness of the Szekeres slices (A), one DSMC cell-size/time-step paper and the relativistic
   conductivity (C), and the 13 papers claims_tracks named (F: 2605.22525, 2609.20338,
   2608.22735, 2608.16986, 2610.27775, 2212.10891, 1303.1540, 2602.06961, 2610.20594; D:
   2307.02474, 2307.10708, 2306.08199, 1904.03781), each needing manifest rows with groups and
   orch's acceptance; the six old-style reference lists (astro-ph/0306304, astro-ph/9306009,
   astro-ph/9510056, astro-ph/9607124, gr-qc/9604001, gr-qc/9906015) and plain-TeX headings.
3. Claims upkeep: re-seed fragment claims (85, 620, 549, about 17 listed in
   claims_tracks/AUDIT.md); the 462 machine-located fulltext claims stay "located" until read;
   records for A's and C's locators once they say which they cite; M23 symbol
   (NrpicWriteConservation -> NrpicWriteHistory) and the five claimed links after core answers.

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; decisions 0016, 0019-0027; brief section 12
   (lines 1218-1461, with Read offset/limit).
2. `tracks/kb/stage/REVIEW-wave3.md` (last section: batch 9), `tracks/kb/JOURNAL.md` (last
   entry: predictions D1, K1, S1, Q1, B1, V1 and their outcomes), `tracks/kb/STATUS.md`.
3. Package READMEs: `tracks/kb/{ingest3,claims_tracks,claims_brief,code_kb}/README.md`.

## Decisions taken in batch 9 (lead)

- gr-qc/0608095: row commented out of kb/manifests/arxiv_additions.tsv, paper removed from the
  papers table (script tracks/kb/lead_b9/scripts/drop_paper.py, run kb-20261121-234427-d6031d4).
  The test counts 60 additions and 744 papers; the task and decision 0027 said 61/745, which
  still included the dropped paper (orch told).
- The 17 corrected but unlabelled brief statements (claims_brief/CHECK_UNJOINED.tsv) are not
  claims: brief 12.8 seeds labelled statements only; one becomes a claim when a track cites it.
- B's statement on 2312.12499 is claim 861 (judgement, locators v2 main.tex L325 and L582).

## Traps

- `kb claim add --locator` stores only the string; run `kb claim relocate N --locator ...` to
  write resolved locator rows (batch 9, outcome B1). After a relocate the check reports the
  claim as "pinned" and leaves it alone (kbtool/claims_db.py pinned_locator).
- `kb verify-downloads` checks only brief section 17 and lists additions as "extra" but records
  their download rows; exit 1 is the known gr-qc/9412071 (PDF only).
- `nrpic-run submit` refuses a dirty worktree: commit first. Production runs for G3 are refused
  until a G2 tag of the owner exists under stage/kb/; register kb runs as scouting.
- A re-ingest renumbers chunks and equations: use `kb ingest arxiv --remap-claims`, then
  `kb embed`, then a snapshot.
- `tracks/kb/verify_g2/heldout.yaml` is a held-out set: never tune retrieval on it.
- Use `kb/.venv/bin/python` for the test suite (yaml, torch) and `python3 -I kb/bin/kb` for
  the tool; never execute anything under kb-data/raw; paper text never goes into git.
- Snapshots about 1 GB each (eleven); keep f2fcda5, 621430e, 44b7406, a848a06, a782f1e,
  bbaafe5, aa0a2ae.
