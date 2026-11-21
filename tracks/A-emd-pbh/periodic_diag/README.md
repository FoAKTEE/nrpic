# periodic_diag: why the periodic set-up of periodic_threshold fails (Track A, batch 6)

Helper package of A-emd-pbh. Diagnosis on processors, without source changes, of the
constraint jump at t = 2.5 and the guard stops of card job 4799 (run
A-20261121-131600-02b5d41, deck `periodic_threshold/inputs/peak_leak.athinput`, release
core-v0.5): P0L stopped at t = 4.8, S1L at t = 15.1, and in both the norm of H jumped by
about 1e4 at t = 2.5. Everything here is analysis of AthenaK output, a reference stability
computation, decks and drivers; no source change and no simulation code (decision 0010).
Predictions and outcomes, also the refuted ones: `JOURNAL.md`.

## Verdict

**Cause [VERIFIED by runs in which it could have failed; R2 below adds the card deck itself]:**
the t = 2.5 jump of card job 4799 is a time-step instability of the Gamma-driver shift.
The deck runs `cfl_number = 1.0` with `<z4c> dt_lightspeed = 0.25`; the light-speed limit
(`athenak/src/z4c/z4c_newdt.cpp`, c = alpha sqrt(chi gt^dd) + |beta^d|) lets the step on the
finest level (dx = 0.0195) grow to 0.83 dx by t = 2.4, because the coordinate light speed
falls to about 0.3 in the expanding box. The Gamma-driver's longitudinal speed is
sqrt(4 shift_Gamma/3 gt^dd) = 1 in coordinates, independent of chi and alpha
(`z4c_calcrhs.cpp`: d_t beta = shift_Gamma Gam - eta beta; d_t Gam carries
gt^jk d_j d_k beta with the conformal inverse metric), and with the code's sixth-order
stencils, RK4 and `diss = 0.5` the discrete shift subsystem is unstable above dt/dx = 0.685,
first at the 3D grid-scale corner (Test B, run A-20261121-212800-d7f31a4).
- The card's level-4 step passed 0.685 at t = 1.70 (P0L) and 1.77 (S1L); the Test B
  amplification accumulated along the card's own steps reaches 10^8.4 (P0L) and 10^9.1 (S1L)
  at the first jump line and reproduces the rise of H_max and S1L's later jump (Test A,
  run A-20261121-222539-c4e42fe, `figures/fig_card_onset.png`).
- On the uniform 64^3 mesh with the lapse frozen: Gamma-driver at cfl 1.0 grows at the grid
  scale in beta^x and Gam^x (G0, G5); cfl 0.5 (G1), cfl 0.6 with a white-noise seed (G6) and
  zero shift (G2) stay smooth to t = 10-12 (runs A-20261121-212941-9e68be1,
  A-20261121-220510-6c46032, analysis A-20261121-222626-2cb28d0, `figures/fig_uniform.png`).
- R2 (the card deck on processors, zero shift, cfl 1.0): R2_SUMMARY

**Excluded as the cause:** a regrid (the mesh is static), the level boundaries as such (the
instability appears on a uniform mesh), the lapse relaxation (frozen lapse in G0/G5 still
fails; with leak 20 the level-4 relaxation is far from stiff, lapse_leak x dt <= 0.39), the
1+log lapse speed (Test B: stable to dt/dx = 0.97 on level 4), the matter (same onset in
P0L and S1L, which share the step history; the frozen-lapse runs fail with the same
particles only when the step is large), the deposit (unchanged between G0 and G1/G2), the
first shell crossing (none before t = 5 in the exact reference), outputs (none at 2.3-2.4),
and the guard (it fires at 4.8 and 15.1, after the jump).

**Second finding (not the card's cause):** the relaxation term of `lapse_leak` is stiff; on a
64^3 root mesh (dt up to 0.23, lapse_leak x dt up to 4.7) the relaxed lapse leaves its track
from t ~ 2 and blows up (U0, run A-20261121-212150-20ffbb6); Test B puts the limit at
lapse_leak x dt ~ 2.5 at the grid scale [consistent with U0; not isolated by a run of its own].

**Refuted predictions on record (JOURNAL.md):** U0 as a reproduction of the card's
mechanism (entry 1); the G0 onset time and "G0 grows from round-off" (entries 3, 6); Test B
threshold band [0.70, 0.78] (0.685); "level 4 far above outside" at t = 4.0 (entry 7: level 3
larger by then); shift_Gamma 0.3 making cfl 1.0 safe (entry 8, Test B': 0.94/0.90).

## What Track A can run in the periodic set-up meanwhile

The deck `periodic_threshold/inputs/peak_leak.athinput` with `cfl_number = 0.5` (keep
`dt_lightspeed = 0.25`, the Gamma-driver and the relaxed lapse): the finest step is then at
most 0.5 dx (Test B threshold 0.685; G1 and G6 stable at 0.5 and 0.6). Cost: the late step
halves, so P0L to t = 140 needs about 14,300 steps instead of 7,400 (at the card's 0.173 s
per step of job 4799, about 41 minutes; S1L to t = 220 about 65 minutes, two chain
segments). Not run on the refined deck in this package (R1 would take about 3.5 hours on 4
processor threads): the first card job with cfl 0.5 is its test. Margin: where the
conformal metric stretches in a collapse (gt^xx > 1) the shift speed exceeds 1; at 0.5 the
step stays stable up to gt^xx = (0.685/0.5)^2 = 1.9 [JUDGEMENT]. Alternatively zero shift at
cfl 1.0 (G2; R2 on the card deck), with the gauge consequences of no shift in a collapse.
Lowering shift_Gamma alone does not suffice (Test B': 0.3 gives a threshold of 0.94).

## Files

| File | Content |
|---|---|
| `JOURNAL.md` | candidates, predictions before each test, outcomes |
| `inputs/diag_uniform.athinput` | the card deck's physics on the 64^3 root mesh without the static levels |
| `inputs/diag_uniform_seed.athinput` | the same with white noise 1e-10 in every evolved field (`<problem> noise_amp`), tlim 10 |
| `outbox_draft/20261121T2300Z__to-core__periodic-gamma-driver-step.md` | the request to core with run ids, for the lead to post (this package may not write the outbox) |
| `scripts/run_uniform.sh` | uniform-mesh cases U0..U7 (relaxed lapse) and G0..G4 (lapse frozen) |
| `scripts/run_uniform2.sh` | the seeded frozen-lapse cases G5 (cfl 1.0), G6 (cfl 0.6), G7 (shift_Gamma 0.3; not run, entry 8) |
| `scripts/run_refined.sh` | the card deck itself on processors: R0 (as job 4799), R1 (cfl 0.5), R2 (zero shift) |
| `scripts/vonneumann.py` | Test B: RK4 amplification of the discrete Gamma-driver, 1+log/relaxation and light subsystems with the code's stencils |
| `scripts/card_onset.py` | Test A: the outputs of job 4799 read again (step against level 4, onset, grid-scale part of the line outputs, amplification of Test B along the card's own steps) |
| `scripts/analyse_runs.py` | histories, onset and grid-scale part of the processor runs |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `figures/` | copies of the figures cited here (made in the run directories) |

## Runs

| Run | What | Result |
|---|---|---|
| A-20261121-212150-20ffbb6 | U0: card physics, uniform 64^3, relaxed lapse | guard stop t = 10.76; jump t = 3.18 through the stiff lapse relaxation (entry 1) |
| A-20261121-212800-d7f31a4 | Test B: von Neumann | shift unstable above dt/dx 0.685 (level 4), 0.65 (root); light stable; lapse 0.97 (level 4), 0.405 (root, leak 20) |
| A-20261121-212941-9e68be1 | G0, G1, G2: frozen lapse, uniform | G0 grid-scale growth t = 8.1 at dt/dx 1; G1 (cfl 0.5), G2 (zero shift) smooth to 12 |
| A-20261121-220411-b7dd9ce | G5, G6 first attempt | failed: noise_amp not in the deck (no result) |
| A-20261121-220510-6c46032 | G5, G6: seeded 1e-10 | G5 grows (one cycle before G0); G6 (cfl 0.6) smooth to 10 |
| A-20261121-222439-65eebaa, A-20261121-222459-4cb257c | Test A, attempts 1-2 | script errors (onset search, level split), fixed |
| A-20261121-222539-c4e42fe | Test A: card job 4799 read again | threshold crossing t = 1.70/1.77; amplification 10^8.4/10^9.1 at the jump |
| A-20261121-222557-2d8e53c, A-20261121-222610-72ddd83 | uniform analysis, attempts 1-2 | figure overflow, colours; superseded |
| A-20261121-222626-2cb28d0 | uniform analysis | `figures/fig_uniform.png` |
| A-20261121-222713-efe9eb8 | Test B': shift_Gamma 0.3 | threshold 0.94 (level 4), 0.90 (root) |
| A-20261121-212853-4a52dea | R2: card deck, zero shift, cfl 1.0, processors | R2_ROW |

## How to rerun

From the worktree root, every run through `harness/bin/nrpic-run` (package committed first):

```
P=tracks/A-emd-pbh/periodic_diag/scripts
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/periodic_diag --launcher local"
$R --purpose "Test B" --cores 1 -- bash -c 'python -I '$P'/vonneumann.py --out "$NRPIC_RUN_DIR"'
$R --purpose "U0" --cores 6 -- bash -c ''$P'/run_uniform.sh "$NRPIC_RUN_DIR" 6 U0'
$R --purpose "G0-G2" --cores 2 -- bash -c ''$P'/run_uniform.sh "$NRPIC_RUN_DIR" 2 G0 G1 G2'
$R --purpose "G5-G6" --cores 2 -- bash -c ''$P'/run_uniform2.sh "$NRPIC_RUN_DIR" 2 G5 G6'
$R --purpose "R2" --cores 4 -- bash -c ''$P'/run_refined.sh "$NRPIC_RUN_DIR" 4 R2'
$R --purpose "Test A" --cores 1 -- bash -c 'python -I '$P'/card_onset.py --job /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-131600-02b5d41 --vn <Test B run dir> --out "$NRPIC_RUN_DIR"'
$R --purpose "analysis" --cores 1 -- bash -c 'python -I '$P'/analyse_runs.py --run G0=<dir>/G0 --run G1=<dir>/G1 ... --vn <Test B run dir> --out "$NRPIC_RUN_DIR"'
```

Costs on the threaded processor build of release core-v0.6
(`scratch/core/exe/core_nrpic_v06/athena_cpu_omp`): uniform 64^3 with the 262,144 particles
of P0L about 3.3 s per cycle on 6 threads, 9.6 s on 2 (60-120 cycles per case); the card
deck (288 blocks of 16^3) about 23 s per cycle on 4 threads.

## Requests

To the lead of A-emd-pbh:
- Post `outbox_draft/20261121T2300Z__to-core__periodic-gamma-driver-step.md` to core
  (outbox, type request; it closes our earlier request periodic-relaxed-lapse-blowup of
  20261121T204327Z and asks for a gauge-speed step limit, a lapse_leak stiffness limit and a
  one-word fix in scripts/cpu_run.sh).
- Change `periodic_threshold/inputs/peak_leak.athinput` to `cfl_number = 0.5` (its header
  comment on the 1+log speed being the risk is superseded: the Gamma-driver speed is) before
  the next periodic card job; that job is also the refined-mesh test of the remedy (R1 was
  not run here). Budget about 41 card-minutes for P0L to t = 140 and two segments for S1L.
- Not done in this package (cost on processors): R0 (the card deck with the Gamma-driver
  reproduced on processors, about 1.7 h on 4 threads) and R1 (cfl 0.5 on the card deck,
  about 3.5 h); the uniform-mesh variants U1-U7 (they carry the stiff relaxation of U0).

To core (in the draft message): (i) a step limit that counts the gauge speeds (Gamma-driver
sqrt(4 shift_Gamma/3 gt^dd), 1+log sqrt(2 alpha chi gt^dd)) with the RK4/KO threshold 0.685,
or at least the rule cfl_number <= 0.6 with a Gamma-driver in the dt_lightspeed interface
text; (ii) a limit or warning for lapse_leak x dt above about 2.5; (iii) `scripts/cpu_run.sh`
footer: `awk -v load=...` is refused by gawk (exit 2, no footer, after every run that athena
ends with status 0).
