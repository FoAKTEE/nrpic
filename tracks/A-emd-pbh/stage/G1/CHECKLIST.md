# Checklist: A-emd-pbh G1

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G1` on 2026-11-15T13:12:42Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: stage/G1/STATUS.md section 2: expball exact solution and data sets (A-emd-pbh-20261115-121749-90764e1, -121753-90764e1, -130609-947c898), newton references (-113103-9832afd), criteria (-115120-2eb3117), gauge toys (-113614-374a41a, -113755-cac3c4b)
- [ ] **C2** The analysis pipeline validated on them
  - status: FAIL
  - evidence: partly: snapshot analysis validated on synthetic AthenaK-format snapshots (A-emd-pbh-20261115-113822-87cba08, rerun -130300-efc25b0); gauge analysis on existing cosmo runs; the invariant comparison script for SR-1/SR-2 does not exist yet
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox 20261115T1320Z__to-core__* (3), __to-orch__* (2), __to-kb__*, __to-B-emd-gw__*

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: expball/figures/, newton/figs/, gauge/figs/, scope/results/ from registered runs; data in scratch/A-emd-pbh/<run_id>/
- [x] **C5** Interface documents
  - status: PASS
  - evidence: stage/G1/STATUS.md section 3 (scouting-run specification); newton/SCAN.md sections 4-5; gauge/GAUGE.md, gauge/DIAGNOSTICS.md; outbox requests to core

## Track-specific criteria of A-emd-pbh for G1 (9.4 Track A: EMD primordial-black-hole formation (S1))

- [x] **C6** The constraint residuals of A-pre-1 converge at the expected order
  - status: PASS
  - evidence: stage/G1/STATUS.md T1: A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d, -122117-aa1c84d; rerun A-emd-pbh-20261115-130402-f5566fb identical; cross-checks A-20261115-130257-a7374a4
- [x] **C7** The prediction table of A-pre-2
  - status: PASS
  - evidence: stage/G1/STATUS.md T2: criteria/predict.py, runs A-emd-pbh-20261115-120425-80492f8, -115120-2eb3117 (33/37, failures on record); lead rerun A-20261115-130252-01e8b64
- [ ] **C8** The scan design from A-pre-3
  - status: FAIL
  - evidence: partly: newton/SCAN.md from validated references; the Newtonian precursor needs core/newton (decision 0010); acceptance asked of orch (outbox ...__to-orch__threshold-line-in-periodic-box.md item 2)

## Minimum figures at G1 (brief 13.4)

- [ ] **C9** Schematic: Updated architecture
  - status: OPEN
  - evidence: not drawn (G0 OPEN.md item 3)
- [ ] **C10** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: not drawn
- [x] **C11** Data figure: Baseline results
  - status: PASS
  - evidence: expball/figures/fig_exact_shells.png, fig_constraint_convergence.png; newton/figs/fig_scan_hoop_time.png; scouting predictions fig_scouting_predictions.png (A-20261115-130948-5a2b58a)
- [x] **C12** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: newton/figs/fig_axes_selftest.png; lead fig_crosscheck.png (A-20261115-130257-a7374a4)

## Package (brief 13.3; judged by the session)

- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: as G0 C13
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: as G0
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: as G0
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: as G0
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: as G0 C17
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in this session
