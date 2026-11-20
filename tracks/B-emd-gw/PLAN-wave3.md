# PLAN of B-emd-gw for wave 3

Written by the owner's planner, one section per round (decision 0019 item 3). Each round
names the gate it aims at and, per package, the key (its directory under
`tracks/B-emd-gw/`), goal, deliverables, why now and the card cap. The complete briefs the
helpers receive are in the planner's structured output of the round; this file is the
record.

## Round 1 (2026-11-20, planned 14:00-14:10 PST)

State read by the planner (worktree after `git merge --no-edit main` at ada029a6):

- Gates: G0 PASS (`coord/GATES.md`, tag `stage/B-emd-gw/G0-pass-20261119`). G1 is the next
  gate; its package `stage/G1/` is still the lead's wave-2 version (2026-11-15). Since then
  wave 2b delivered: the G1 schematics and note sections (note2, run
  B-20261119-142957-ae8b4e2, `note/main.pdf` 17 pages), an independent verifier of the
  wave-2 first-source and Newtonian runs (`stage/G1/VERIFIER.md`, 12 claims confirmed, 3 in
  part, none wrong), and the track's own oblique and expanding-box linear waves with both
  diagnostics (`waves/`, analysis B-20261119-164402-7438a99; criterion 1 met in the
  helper's judgement, one rounding check open). No wave-2b lead session ran: `STATUS.md`,
  `HANDOFF.md`, `stage/G1/{OPEN,CHECKLIST,STATUS}.md` are stale.
- Runs that finished unattended (sacct and run directories, checked 14:03 PST): card job
  4655 = B-20261119-153655-2deca0a (first source, 1 and 27 per cell at 64^3, 1 per cell at
  128^3; all rc=0), card job 4662 = B-20261119-155758-458cf17 (waves, X at N = 64 with the
  amplitude x10; rc=0), processor companions B-20261119-143238-b7961ef,
  -144416-5f1ab7a, -153624-224805d (32^3; all rc=0). None is closed with `nrpic-run
  finish` and none is analysed. No job of the owner is queued now.
- Card time: 2.12 card-hours used in all (sacct, nine jobs named B-*), of the 40 allotted
  to the next gate (decision 0014).
- Executables: no merged core state (`scratch/core/exe/core_nrpic_v04/` absent);
  tested branch executables used here: `core_requests-b` (oblique generator, double-precision
  bin output, jitter tool), `core_build-openmp` (threaded processor build, 13-14x at 16
  threads; release-v0.3 options only), `core_cosmo-amr`, `core_mpi` (not needed this round).
- Inbox: four messages (core T8 card test of requests-b; kb claims 689-695 of B's key
  references; kb snapshot a782f1e; core's threaded build), all information; for the lead to
  acknowledge.
- Worktree clean, nothing stranded except the five unfinished manifests above.

Gate aimed at: G1 (close it: criterion 1 independently verified, the open rounding check
closed, the note carrying criterion 1, the first-source science items 7, 8, 11 of
`stage/G1/OPEN.md` judged); and the first two G2 legs that need no new core work
(particle FLRW convergence; the shearing-dust multi-code row of decision 0013).

| Key (directory) | Goal | Deliverables | Why now | Card cap |
|---|---|---|---|---|
| `first_source` | Close the cut-off second round: particle-number leg (1, 8, 27 per cell) and mesh leg (128^3) of P12/P13, the 32^3 companions (null, delta = 0.0025), the advance test of the (1 + eps^2) reading, then the P16 discriminating run (jittered lattice without a wave); 128^3 at 8 per cell only if the mesh leg is inconclusive | finished manifests of four runs; outcomes of P12, P13, P11/P14 at 32^3, (1 + eps^2) test, P16 in `JOURNAL.md` with figures; `README.md` state | runs finished unattended; G1 OPEN items 7, 8, 11; the convergence legs of G2 | 1.6 |
| `stage/G1/verifier3` | Independent verifier (fresh context, artefacts only) of G1 criterion 1 on the `waves` runs (TT projection and Psi_4 against own exact solutions, flat oblique and expanding box); second priority the spatial-gauge block of the note's ledger (G_tot) | own scripts, results, figures; `stage/G1/verifier3/VERIFIER.md` with a verdict per claim | the gate lacks an independent check of criterion 1 and of G_tot (verifier2 left them out) | 0 |
| `waves` (also `gw_diag/`) | Close the rounding check of X at N = 64 (x10 run), add a flat wave with nonzero discrete divergence k = 2pi(1,2,0), separate the time and space parts of the X error; adopt the two-precision reader and the gauge piece G_tot into `gw_diag` with tests | finished manifest of B-20261119-155758-458cf17; outcomes with figures; `gw_diag` functions and tests; `waves/README.md` | the one open sub-item of criterion 1; G1 OPEN item 9 | 0.3 |
| `note` (also `WRITING_GUIDE.md`, `NOTATION.md`) | Working note v2: criterion 1 (oblique and expanding-box waves) in Sec. IV A, the established round-2 results (noise-floor null, delta = 0.0025 window, run-to-run floor) in Sec. V; guide and notation additions of `note/README.md` Requests 1-2 | `note/main.pdf` compiled, checked, every page read; figures from a registered `run_all.py` run | G1 C17; the note lacks criterion 1 | 0 |
| `flrw_conv` (new) | G2 criterion (a): scale-factor error and linear growth rate of the particle FLRW run, sub-percent and converging in particle number (1, 8, 27 per cell, with and without position noise) and mesh, production configuration | `flrw_conv/` with predictions, runs, growth-rate extraction, figures, README | prerequisites exist (release v0.3, threaded build); `verify_cosmo/VERIFY.md` section 7 items 1-2 list exactly what is missing | 2.5 |
| `shear` (new) | G2 multi-code row (decision 0013): the shearing-dust test of arXiv:2003.08014 with AthenaK particles; the paper's sheared-Euclidean slice rewritten in the code's conformally flat form (psi = 1), exact initial data, thin periodic boxes, against the paper's linear prediction and reported code results | spec, reference, initial-data writer with tests, a resolution series, figures, README | the id=file format (psi, K, alpha, Ahat_ij) and thin boxes exist; the row is the replacement of the gevolution comparison | 1.0 |

Sum of the caps: 5.4 card-hours (2.12 used before; 40 allotted). The owner keeps at most two
card jobs queued or running: every helper counts the owner's jobs (`squeue -h -u haiyangw
-o %j | grep -c '^B-'`) before submitting, bundles its card runs into one batch list per job,
and does processor work when two are in the queue. Processors: six cores per helper at
most, the threaded executable for anything at 32^3 or below.

Independence: each package writes only its directories (named above); `gw_diag/` changes
are additive, so the analyses of `first_source` and `note` that import it are unaffected;
`note` uses only results committed before this round and leaves the legs now being
analysed out of its text; the verifier reads the `waves` runs' raw outputs read-only and
none of the packages' conclusions before its own numbers are committed.

Not planned this round, and why:
- `population` (wave 3a, partial; G3 design): card timing of the full-GR box at 128^3 and
  256^3 (about 0.3 card-hours), the `--outer` option and L = 8 initial data at three
  amplitudes, Newtonian runs at 128^3 on the threaded build, the pre-registration of the G3
  run list. Its results are G3 inputs, not G1 or G2 ones: first candidate for round 2.
- Verifier of the second-round first-source results and of `flrw_conv`: round 2, after the
  results exist.
- N2 (embedded ellipsoid): waits for core's per-species history (`core/newton2`, not
  published). York (covariant) TT part: after G1.

For the lead after this round (not helper work): acknowledge the four inbox messages; the
erratum line in `stage/REVIEW-wave2.md` (note README Request 5); the requests of the wave-2b
reports (verifier2: three rewordings; waves: the trap "never edit a running script" in
`HANDOFF.md`); `stage/G1/{OPEN,CHECKLIST,STATUS,EVIDENCE}.md` with the deliverables of
note2, verifier2, waves and this round; `nrpic-stage collect/verify/report B-emd-gw G1`;
`STATUS.md`, `HANDOFF.md`, `RISKS.md`, `JOURNAL.md`; the outbox posts the helpers request
(core: momentum-constraint residual of the jitter tool, in-situ low-k Fourier output,
release of requests-b).
