# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of batch 4a, wave 3,
2026-11-21 07:45-08:30 PST). Rewritten at the end of every session.

State in three lines: G0 is signed (2026-11-19). G1 criteria 1 and 2 are met and checked
independently (criterion 1 now also for k = 2 pi (1,2,0) and the time/space split of X),
criterion 3 is struck; the G1 package lacks only the rest of C18 (ledger lines 34-36, 49-63,
70-71, 124, 199, 217 not yet recomputed by an independent agent) and the note v3 wordings.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show && git status --short`

Files to read first: `STATUS.md`; `stage/G1/OPEN.md` (what G1 lacks, exact ledger lines and
wordings); `stage/REVIEW-wave3.md` section "Batch 4a"; `stage/G1/VERIFIER-C18.md`;
`stage/G1/CHECKLIST.md`; `stage/G1/STAGE_REPORT.md`.

Finished and reviewed (batch 4a): `first_source` round 3, `waves` round 1 (with gw_diag's gauge
and reader modules), `stage/G1/verifier_c18`. Nothing of them is left uncommitted.

Packages still in progress (not touched this session; what remains):
- `flrw_conv` (G2 criterion a): J1 (B-20261120-222955-c8e16e3, card job 4746) and P1
  (-223006-24448ac) ran and are closed, not analysed; J2 and J3 not submitted (lists in
  `flrw_conv/inputs/`, 0.6 and 0.65 card-h; use the release core-v0.6 card executable,
  `.work/build_gpu_v06`). Remains: runs.json, analyze_f.py / analyze_b.py, outcomes against
  PF1-PF6, PB1-PB5, README.
- `shear` (G2 multi-code row): spec, references and tests done (P1-P3 met); the smoke run failed
  on `nprobe = 1` without probe lines (B-20261120-223445-3686145). Remains: `nprobe = 0`, smoke
  run, series S1-S4, M1-M2, L1-L2, outcomes P4-P12 (`shear/JOURNAL.md` end).
- `population` (G3 design, partial): full-GR timing at 128^3 and 256^3 (0.3 card-h), L = 8
  initial data with the id solver of core-v0.6 on the torus, the G3 run list; figure defects
  of pop_gw_fid.png (legend over the red curve; the square "halos of a = 20" sits at a = 30).

Next work, in order: (1) verifier_c18b (fresh agent, artefacts only, processors only) on
the ledger lines of OPEN.md item 1, unless orch rules that the wave-1 scouting rows move to
G2; then `nrpic-stage collect/verify/report B-emd-gw G1` and the gate request; (2) note v3
(OPEN.md item 2; can run beside (1)); (3) flrw_conv and shear (G2); (4) the Newtonian
embedded ellipsoid with core-v0.6's group moments (core ran it: +2.56 ... -0.14 per cent at
64^3-256^3; short axes 0.02 R_L below the ODE before the crossing at every resolution, to be
read by the track).

Decisions pending: orch on c18-remaining-rows, next-batch-packages-of-b (20261121T155410Z) and
note-pdf-size (20261121T0654*); core: insitu-fourier-modes accepted as W18, no branch yet; kb
on the 2312.12499 claim (waits for its claims package). No card job of the owner is queued
or running. Inbox: all messages acknowledged (A's Szekeres files for the G2 legs are in run
A-20261120-223422-8cc4241; its periodic spherical peak data in A-20261120-223123-f436c39).

Traps:
- Runs go through `harness/bin/nrpic-run submit --kind scouting --gate G1|G2 [--package <dir>]
  ... -- python3 <script>` with the worktree `.venv` (exists). Commit scripts first.
- Background and card runs need `harness/bin/nrpic-run finish <run_id>`; after a usage-limit cut
  check `nrpic-run status` and the run directories' `.nrpic/result.json`.
- Never edit a script while a run executes it (bash reads scripts incrementally).
- Chain a pause check with `&&`, never `;`.
- Numbers below 1e-7 relative depend on the measure: say whether an amplitude is the modulus
  of the complex mode amplitude or its part in phase with the exact solution.
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; report raw and
  G_tot-corrected values (`gw_diag/gwdiag/gauge.py`); new decks write double-precision bin.
- New runs use the release core-v0.6 executables (CLAUDE.md); a comparison with older runs
  accounts for the changes listed in the release messages (guard exit status 3 from v0.5).
- `nrpic-stage verify B-emd-gw G1` checksums every run directory (about 200 GB, over half an
  hour); run it in the background with the tree clean (it checks `clean` at the start).
- Never kill by pattern; numeric pid, `scancel`, or the chain helper.
