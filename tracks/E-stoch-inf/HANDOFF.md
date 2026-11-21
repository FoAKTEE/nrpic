# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (signed 2026-11-20)
and is at G1. The slow-roll (SR) case of arXiv:2512.14649 passes A1-A3, A5-A7 up to 256^3 in
two realisations, confirmed by a fresh verifier (`stage/G1/VERIFIER.md`) and by the lead's
reruns; G1 still lacks orch's ruling on A4' and the note's G1 products (package `note`, cut).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show

Packages of wave 3 still in progress (cut by the usage limit on 2026-11-20 14:35 PST; their
files are uncommitted and were left alone by the lead of batch 2a; each next session commits
its own files first, path-limited):
- `note` (G1 products C8, C9, C13-C15): modified `note/scripts/{common,fig_background,ledger,
  run_all,schem_architecture,schem_timeline}.py`, new `note/scripts/{fig_sr_constraints,
  fig_sr_freezing,fig_sr_modes,fig_sr_order,schem_dataflow}.py`; predictions N4-N8 committed in
  `note/JOURNAL.md` (e2f926e3). Remains: run the figures in a registered `run_all`, write the G1
  sections of `note/main.tex` with ledger rows, checker with `--compile`, read the pages. Use
  the time-matched P256 number (odd/even 25 at N = 3.93, `ladder/results/final2/`), never 385;
  cite the verifier where it confirms.
- `usr` (G2, USR case): card job 4742 finished (run E-20261120-222621-ba66218, group 1); manifest
  still "submitted": `harness/bin/nrpic-run finish E-20261120-222621-ba66218`, then
  `usr/scripts/analyse_cards.py` (uncommitted, with `card_lib.py`); `usr/JOURNAL.md` entry 10
  (uncommitted, written 22:35Z, before the job started at 22:36:46Z by sacct) amends the bar of
  U-A4; commit it first and say so. Then the 256^3 production runs (`usr/inputs/card_u256.list`,
  `card_u256m.list`, pre-registered in `usr/JOURNAL.md` entry 9).
- `window` (G2, window sensitivity L9): card job 4740 finished (run E-20261120-222424-0eb754b);
  `nrpic-run finish`, then `window/scripts/analyse_window.py` (committed, 2c61e43a) against the
  predictions W1-W8 of `window/JOURNAL.md` entry 1.
- `a4res` (resolution test for strict A4): step 1 done (run E-20261120-222312-6ee4bc5);
  uncommitted `a4res/scripts/{a4lib,make_list,twin_predict}.py`; remains the twin predictions,
  the card list (cap 0.5 card-hours) and the analysis. Lower priority once orch rules on A4'.

Then, depending on answers:
- orch rules on A4' (`outbox/20261121T064752Z__to-orch__a4-ruling-with-verifier.md`): update
  `spec/scope/SCOPE.md` 4/4b, `stage/G1/STATUS.md`, `CHECKLIST.md` C6; `harness/bin/nrpic-stage
  collect E-stoch-inf G1`, `verify --no-checksums` (the full checksum pass reads ~150 GB),
  `report`. When C6, C8, C9, C13-C15 pass, the package is complete for the gate review.
- Card: P256 on the release card build `.work/build_gpu_v04/src/athena` with
  `ladder/inputs/jobA.list` (0.5 card-hours) against E-20261115-172618-f948386 (risk R1 on
  cards; the processor check at 32^3 is in `stage/REVIEW-wave3.md` section 3).

Files to read first: `STATUS.md`; `stage/G1/STATUS.md`, `OPEN.md`, `VERIFIER.md`;
`stage/REVIEW-wave3.md`; `PLAN-wave3.md`; `RISKS.md` (R1, R17-R20); `JOURNAL.md` (last entry).

Decisions pending: A4'/A5' (orch, now with the verifier's recommendation); scheduling of the
cut packages (orch, `outbox/20261121T064806Z__to-orch__resume-cut-packages.md`).

Traps:
- Executables: scalar-2 is in release core-v0.4 (`.work/build_{gpu,cpu}_v04`); scalar-3 (USR
  example, `con_signed`, mode entity) is only in `scratch/core/exe/core_scalar-3/` until
  core-v0.5. The threaded processor build has no `id = stochastic`.
- Pair dumps of two runs only at equal recorded times (|dt| <= 1e-9): runs with different `tlim`
  end with a shortened step (the "385" came from this).
- Cold 128^3-256^3 dumps: read sequentially (seek + fromfile), never through numpy's memmap.
- Large figure PDFs: `fig_lead3.pdf` is 6.4 MB (in the run directory only); commit PNGs.
- Commit path-limited (`git commit -- <paths>`); never commit another package's uncommitted
  files; `nrpic-run finish` commits manifests itself (wait for `index.lock` to clear).
- `$NRPIC_RUN_DIR` in a command: inside `bash -c '...'` (RULES.md).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004, M11 544-547.
