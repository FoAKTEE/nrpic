# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of batch 2a, wave 3,
2026-11-20 22:29-23:30 PST). Rewritten at the end of every session.

State in three lines: G0 is signed (2026-11-19). G1 criteria 1 and 2 are met and checked
three ways (waves, verifier3, the lead's own reading), criterion 3 is struck; the G1
package lacks only C18, an independent recomputation of the remaining ledger rows. Four
packages of round 1 were cut by the usage limit on 2026-11-20 14:35 and are still open.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show && git status --short`

Files to read first: `STATUS.md`; `stage/REVIEW-wave3.md` (what is confirmed, the
plus-amplitude dispute and its resolution); `stage/G1/OPEN.md` (what G1 lacks);
`stage/G1/CHECKLIST.md`; `stage/G1/verifier3/VERIFIER.md`; `PLAN-wave3.md` (round 1 briefs);
the JOURNAL.md of each open package below.

Packages still in progress (left as found; what remains):
- `waves` round 1: done: x10 check (rounding confirmed), predictions of F2 and XS
  (`waves/JOURNAL.md` 2026-11-20 22:30), binio reader in gw_diag (5499ec6c). Ran unattended,
  closed by the lead, NOT analysed: F2 at N = 16, 32, 48 (B-20261120-222849-3b921b7), XS at
  N = 16, 32 (B-20261120-222849-e5673dc), F2 at N = 64 and XS at N = 16-64 on the card
  (B-20261120-222841-acfe21d, job 4745). Uncommitted, untested by the lead:
  `gw_diag/gwdiag/gauge.py`, `gw_diag/tests/test_gauge.py`, `waves/scripts/check_gauge.py`
  (G_tot into gw_diag). Remains: analyse F2/XS against F2-1..6, XS-1..4; finish and test the
  gauge module; README: x10 outcome, verifier3 wordings (F5 forward combination, X1 moduli
  with a rounding share, Weyl-6 construction), `stage/G1/OPEN.md` items 3, 5, 8.
- `first_source` round 3: predictions of the (1 + eps^2) advance test and the 32^3 nulls
  written (`first_source/JOURNAL.md` 2026-11-20 14:35); scan analyses of the 128^3 and the
  1 and 27 per cell runs done unattended (B-20261120-223236-e213594, -223241-f1efd4f; JSON
  in their run directories), outcomes not written. Remains: P12, P13, the (1 + eps^2) test,
  the 32^3 nulls, README wordings of verifier2 (OPEN item 4), the definition behind
  rho_GW/rho_bar = 3.5e-6 (note helper's question), the jitter-without-wave run (P16).
- `flrw_conv` (G2 criterion a): J1 (B-20261120-222955-c8e16e3, job 4746) and P1
  (-223006-24448ac) ran, closed, not analysed; J2 and J3 not submitted (lists in
  `flrw_conv/inputs/`, 0.6 and 0.65 card-h; use the core-v0.4 card executable or say why
  not). Remains: runs.json, analyze_f.py / analyze_b.py, outcomes against PF1-PF6, PB1-PB5.
- `shear` (G2 multi-code row): spec, references and tests done (P1-P3 met); smoke run
  failed on `nprobe = 1` without probe lines (B-20261120-223445-3686145). Remains: set
  `nprobe = 0`, smoke run, series S1-S4, M1-M2, L1-L2, outcomes P4-P12.
- `population` (G3 design, wave 3a, partial): full-GR timing at 128^3 and 256^3 (0.3
  card-h), L = 8 initial data at three amplitudes (try core-v0.4 `<particles> id_solve` on
  the torus; READY of core_nrpic_v04), the G3 run list; figure defects of pop_gw_fid.png.

Next work, in order: (1) verifier4 for C18 (fresh agent, artefacts only, every ledger row
not yet recomputed: the second-round table, gauge rows 120-125, eps 0.1/0.3 of rows 116-117,
wave-1 rows outside the G0 claims), then `nrpic-stage collect/verify/report B-emd-gw G1`
and the gate request; (2) close waves and first_source round 1 and note v3 (ledger rows
101, 118-119, 168); (3) flrw_conv and shear (G2).

Decisions pending: orch on the C18 verifier package and on the note PDF above 1 MB
(outbox 20261121T0654*); core on in-situ Fourier output, per-species Newtonian history,
fourth-order Laplacian; kb on the 2312.12499 claim. No card job of the owner is queued.

Traps:
- Runs go through `harness/bin/nrpic-run submit --kind scouting --gate G1|G2 --package
  <dir> ... -- python3 <script>` with the worktree `.venv` (exists). Untracked files of an
  open package are allowed outside `--package`; commit your own scripts first.
- Background and card runs need `harness/bin/nrpic-run finish <run_id>`; after a usage-limit
  cut check `nrpic-run status` and the run directories' `.nrpic/result.json`.
- Never edit a script while a run executes it: bash reads scripts incrementally and a git
  restore writes a new inode the running bash never sees (waves lost run -142234-85da208
  that way).
- Chain a pause check with `&&`, never `;` (shear started a run after the flag was set).
- Numbers below 1e-7 relative depend on the measure: say whether an amplitude is the modulus
  of the complex mode amplitude or its part in phase with the exact solution (REVIEW-wave3).
- The flat TT strain of zero-shift runs carries a spatial-gauge piece; report raw and
  G_tot-corrected values; new scans write double-precision bin output (float32 floor 3-7e-6).
- New runs use the core-v0.4 release executables (`.work/build_{gpu,cpu}_v04`); a comparison
  with core-v0.3 runs accounts for the corrections listed in the release message.
- `nrpic-stage verify B-emd-gw G1` checksums every run directory (about 200 GB): it takes
  over half an hour; run it in the background.
- Never kill by pattern; numeric pid, `scancel`, or the chain helper.
