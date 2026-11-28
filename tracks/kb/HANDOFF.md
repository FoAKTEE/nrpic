# HANDOFF of kb

State (2026-11-28 ~03:05 UTC = 2026-11-27 19:05 PST, end of the kb lead session of batch 37, a
short one). The knowledge base holds 762 papers (684 of brief section 17 plus 78 additions in
kb/manifests/arxiv_additions.tsv) and 64 repositories; readers use `kb-data/db/current` ->
kb-20261128-bd57a33 (936 claims; run kb-20261128-024540-477cbc9; QA in kb/QA_REPORT.md). All
four gates of kb are signed (KB-G0, KB-G1, KB-G2, KB-G3 pass with reservations; coord/GATES.md).
kb is in service mode. No package is in progress, no run is going, no card job, no queue entry of
kb. The worktree is clean after the last commit and pushed.

## What the last packages did

- claims4 (batch 34; tracks/kb/claims4/): took the 389 machine-located claims nobody had read and
  put them in a seeded order (run kb-20261128-003945-e1d65ba, order.tsv: class C cut texts k=1-34,
  T cited by a track k=35-178, R the rest k=179-389); read C (34) and the first 13 of T and of R.
  No lead session of its own: its C census and R sample have not been re-checked by a lead.
- claims5 (batch 35; tracks/kb/claims5/): read the remaining 131 of T (k=48-178). T census 124/144
  right as worded; 17 corrected; snapshot bd57a33. Reviewed by the lead in batch 37 (REVIEW-wave3.md,
  last section): five verdicts hold at their lines, census and provenance confirmed. Its six owner
  notes are posted (tracks/kb/outbox/20261128T0258*Z__to-*__claims5-cited-claims-read.md).

## Run next (in this order)

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show
python3 -I kb/bin/kb status                   # 762 papers, 936 claims, snapshot kb-20261128-bd57a33
```

1. Second-agent sample of claims5's verdicts (decision 0049 item 6). A FRESH agent that did not
   write claims5, given only tracks/kb/claims5/work/verdicts_T.tsv, the reader
   tracks/kb/claims5/scripts/show.py and the database (read-only), draws with its own committed
   seed about 20 verdicts stratified by right / not right / borderline, reads each at its lines and
   writes VERIFIER-claims5.md with CONFIRMED / WRONG per row and the successor texts it read. The
   lead already read five (71, 195, 5, 329, 352; run kb-20261128-025758-95806ac): exclude them.
2. The uncited class R: the 198 unread of 211 (claims4 order.tsv from k = 192). Package like
   claims5: predictions in its JOURNAL first (claims4 measured R 8/13; expect about 60-70 % right
   as worded, CP wide), read at locators with claims5/scripts/show.py, plan JSON built by a
   make_plan.py like claims5's, dry run then apply with tracks/kb/claims3/scripts/apply.py (both
   registered), rates and figure, snapshot and QA, owner notes only where a track cites a changed
   claim. Put in the same plan an annotation of 931 with its own line's hedge (1901.08528
   PBH-UCMH-ArXiv-v2.tex L468: the integral should stop at matter-radiation equality, so the real
   correction is smaller than 53 per cent). Afterwards run the provenance diff
   (tracks/kb/lead_b37/scripts/provdiff.py: change BEFORE/AFTER to the snapshots around the
   package) as the lead check.
3. Borderline cleaning: 33 rows of claims5 (37 flagged, LEDGER.tsv column borderline) and
   claims4's 10, verified as they stand (noun phrases, locator debris such as "| 2108.11967
   `main.tex:283`", glosses): supersede with whole sentences. Then the VERIFIER2 leftovers: 741's
   locator (Spin_PBH.tex L1206, relocate with --by); 428's author order; 804 vs 805 one rule;
   313/430 debris; 864 "Jena"; 877 split; OPEN O4 (409, 447-450, 448, 753, 765).
4. Smaller, service mode: bibliography parser formats (KB-G3 verifier item 3; seeded misses in run
   kb-20261124-132849-3ebad97 whole_missed_sample.tsv); paper-code links M18-M25 (core messages
   20261123T020802Z, 20261124T130734Z); `kb ingest repo --this` for core-v0.8 and v0.9 options;
   OPEN O9 schema change (label 'repository', locator forms 'repo:', 'meta:'); 928 has status
   unlocated although its locator resolves (apply.py add path); successors have origin_line empty.

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; decisions 0016, 0019, 0035, 0037, 0048, 0049;
   brief section 12 (lines 1218-1461, with Read offset/limit).
2. `tracks/kb/stage/KB-G3/OPEN.md` (O7: census and what remains); `tracks/kb/stage/REVIEW-wave3.md`
   (last two sections); `tracks/kb/claims5/README.md` (how to rerun, open points).

## Traps

- `kb claim relocate` needs `--by`; `kb claim add --locator` writes no locator rows: relocate after
  every add. Supersedes write their own rows. Do not rerun the plans of claims3, lead_b17, claims4
  or claims5 (applied; apply.py refuses a second supersede, even in a dry run).
- `kb show` reads db/current: pass `--db /data/haiyangw/nrpic/kb-data/db/kb.sqlite` to read work
  after the last snapshot. Every write to kb.sqlite under locks/kb-writer.lock (kb does it).
- `nrpic-run submit` refuses a dirty worktree; commit first. Never `nrpic-stage verify` with
  reruns for kb: the claims packages write to the database.
- A re-ingest renumbers chunks and equations: `kb ingest arxiv --remap-claims`, `kb embed`, then a
  snapshot. `tracks/kb/verify_g2/heldout.yaml` is held out: never tune on it.
- Snapshots about 1 GB each; keep those cited in notes (f2fcda5, 621430e, 44b7406, a848a06,
  a782f1e, bbaafe5, aa0a2ae, 9872d21, 2f97258, 56c4b53, fcd969d, bd57a33). /data was at 89 % on 2026-11-27: check `df -h /data`
  before a new one.
- Copies of figstyle.py in tracks/kb/note/scripts/ must equal harness/style/figstyle.py
  (harness/style/SHA256SUMS), or nrpic-stage verify reports style FAIL.
