# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20), G1
(2026-11-21) and G2 (2026-11-24), the last two with reservations (coord/GATES.md; decision 0038).
U-A4'(a) stays FAILED as written in the G2 record. G3 (tail statistics) is scoped in
`spec/scope/SCOPE.md` section 4d (fixed before any G3 run); its pilot is in the shared queue.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- G2 (signed): `stage/G2/` (GATE_REVIEW.md = the orchestrator's review; its findings F1-F4 were
  corrected in batch 17, see `stage/REVIEW-wave3.md` Part G; OPEN.md items 3 and 7 updated).
- Working note: `repro/note/manuscript/main.pdf` (32 pages). Rebuild recipe: `repro/note/README.md`
  "How to rerun and rebuild". Last run_all: R17 E-20261125-115608-b9c1b59 (repro/note/JOURNAL.md 27-28).
  The PDF is about 5.05 MB, just under the hook's 5 MiB (R31).
- Floor test (R28): `floor/` (floor_read.py, JOURNAL entries 1-3). At 128 the floor is second order.
- G3: `spec/scope/SCOPE.md` 4d (statistic, estimator, S = 256 seeds, reference, criteria C, R, G,
  L2, budget); `g3/` (power.py, inputs/pilot.list, JOURNAL entry 1 = power estimate outcome,
  entry 2 = predictions for the pilot and for G3); reference `langevin/results/ref_inflection_n32.json`
  (128^3 band, 2e5 paths, run E-20261125-115707-b845282; `ref_spec.py` takes the band from
  NRPIC_REF_NLAT, other bands get the suffix _n<NLAT>, never overwriting the 256 files).

## Runs in flight

| What | Queue / job | Run id | Read by |
|---|---|---|---|
| FL256h, SR 256^3 at s = 1/2 (card, priority 2) | q0038, job 5284 (pending at 04:10 PST) | E-20261125-115534-8414659 | `floor/floor_read.py` (below); outcome as floor/JOURNAL.md entry 4 |
| G3P pilot: 10 baseline seeds + 2 kdriver + 2 level 2, 128^3, build_gpu_v07 (card, priority 5) | q0045 (waiting) | given by `nrpic-queue show q0045` once dispatched | the g3 reader (to write); predictions g3/JOURNAL.md entry 2 (G3P-1..3) |

Card runs are closed with `harness/bin/nrpic-run finish <run_id>` (the queue does not finish them).
Reading FL256h: commit nothing first, then
`harness/bin/nrpic-run submit --kind production --gate G2 --preregistered tracks/E-stoch-inf/floor/JOURNAL.md#entry-1 --package tracks/E-stoch-inf/floor --launcher local --cores 2 --background --purpose "..." -- python3 tracks/E-stoch-inf/floor/floor_read.py '$NRPIC_RUN_DIR' --pair FL256:/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261124-130952-4be980b:/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261125-115534-8414659`
(CL256S's last dump 17 lives in E-20261124-130952-4be980b, the continuation; check that its
sr.sf.00017.modes exists there, else point to the directory that has dump 17). The reader checks
the record ratio (must be 0.5) and reads the s = 1/2 run with --scale 1 (R32). 256^3 passes take
minutes each (2 cores). Judge F1 at 256 (ratios in [1.6, 2.5]), F2, F3, F4 (medians at 128 and 256
within 15 per cent), F5 (cost <= 1.0). Then replace the note's sentence "Whether it scales with the
square of the amplitude ... would show" (main.tex Sec. on Fig. 7 and the 'Open:' sentence) with
the result, rerun run_all, compile.

## Next, in order

1. FL256h when it has run (above).
2. The g3 reader (`g3/read_seed.py`): R^NR via `ladder/scripts/ladder_lib.curvature`, zeta (SCOPE
   4d.1), exceedance fractions per seed into a small npz; its two processor tests first (32^3,
   homogeneous run and s = 1/4 run on .work/build_cpu_v07). Then read the pilot against G3P-1..3
   and put the measured cost per seed into SCOPE 4d.8 (as a dated addition, not a rewrite).
3. G3 reference for the 128 band: 4e6 paths direct + importance sampling at nu = 4, 4.5; the model
   check of 4d.3 [TO VERIFY]; R33 (the lattice variant at 0.980 of linear).
4. Then the full G3 set through the queue (baseline 256 seeds in batch jobs of about 20 seeds; the
   three-amplitude and 160^3 runs of 4d.4/4d.5; 32 seeds kdriver; 32 seeds level 2), priority 5,
   at most four new entries per session. Ask orch first if it has not looked at SCOPE 4d.

## Traps

- Card runs only through `harness/bin/nrpic-queue add` (decision 0033: five jobs for the account);
  no own sequencers; give `--package` so edits elsewhere do not hold the entry.
- `nrpic-run submit` refuses when its `--package` has uncommitted files; production runs need
  `--preregistered <file#anchor>`.
- A run with noise_mode_scale = s has a .modes record that already carries s: read it with
  dumppass `--scale 1` (R32; floor entry 2).
- The pre-commit hook refuses files above 5 MiB (the note PDF is at 5.05 MB).
- In the note the noise amplitude is lambda; s is the window steepness. The program's records call
  the amplitude s.
- Pair dumps only at equal recorded times. analyse_cards.py has no seed option (seed B:
  analyse_g2.py --seed 20261116).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004.
