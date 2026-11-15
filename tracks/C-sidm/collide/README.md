# collide: specification, references and tests of the collision operator (C-pre-1, C-pre-2)

Work package of owner C-sidm under decision 0010: core writes the relativistic Monte Carlo
collision operator into `athenak/src/particles/` (branch `core/collisions`, on top of
`core/rng`); this package specifies it, supplies the reference solutions and the tests,
and checks core's implementation. No collision code is written here.

State on 2026-11-15: `core/collisions` has no commit beyond main; `core/rng` has an
uncommitted draft. So nothing of the operator has been checked yet. Done: specification,
references with 62 passing tests, test plan with pass criteria fixed before any run,
analysis scripts tested on synthetic data, and the collisionless limit of the step test
run with the existing code (passed). See `JOURNAL.md` for every prediction and outcome.

## Contents

| Path | What |
|---|---|
| `SPEC.md` | the algorithm: invariant rate with the Moller speed, pair kinematics, random pairing per cell, probability (N - 1) sigma_m M_max v_Mol alpha dt / (sqrt(gamma) dV), unequal masses, sub-cycling and time step, cell size, curved-spacetime frame, option names, outputs; derivations and source locators |
| `TESTS.md` | tests T0-T12 in a Minkowski periodic box (and T12 in a static curved metric) with pass criteria and the options they need |
| `RNG_REQUIREMENTS.md` | what the operator needs from the shared random numbers (keys K1-K3 on stream 2, reproducibility, tags) |
| `REFERENCES/mj.py` | Maxwell-Juttner moments (<W>, h, c_v, c_p), inversion theta(<W - 1>), inverse-CDF sampler, drifting gas |
| `REFERENCES/rate.py` | <v_Mol>(theta) = 4 K3(2 zeta)/(zeta K2(zeta)^2), its integral form, Monte Carlo check, two-temperature average |
| `REFERENCES/kinematics.py` | the kinematics oracle: exact pair scattering, robust gamma_rel - 1, Moller speed, metric triad, Nanbu-Yonemura rule, 60-digit twin, test-vector writer |
| `REFERENCES/relax.py` | two-temperature start: exact initial rate (quadrature), non-relativistic closed form, Monte Carlo collision integral, theta_eq, guide model |
| `REFERENCES/conduction.py` | one-sided fluxes, exact collisionless step in a periodic box, diffusive step, kappa_1 (and the Balberg et al. value), isobaric-mode rate, collisionless mode |
| `REFERENCES/entropy.py` | Maxwell-Juttner entropy, mixture entropy, histogram estimator with Miller-Madow correction |
| `REFERENCES/test_vectors.json` | 209 pair-scattering cases for the kernel unit test T0 (inputs exact, outputs from 60 digits) |
| `REFERENCES/tests/` | pytest suite of the references (predictions R1-R7 of JOURNAL.md) |
| `REFERENCES/make_figures.py` | the reference figures and key numbers (`figs/ref_*.png`, `figs/ref_numbers.json`) |
| `analysis/make_box.py` | particle files and metadata for the box tests (mj, twotemp, step, mode, boosted, unequal) |
| `analysis/snap.py` | readers and writers of `NRPIC001`, `NRPSNAP1`, history files |
| `analysis/an_step.py` | T6: step in the box against the exact collisionless and the diffusive solutions |
| `analysis/an_box.py` | T1-T5, T7, T9, T10, T11: relax, mode, rate, conserve, repro |
| `analysis/tests/` | pipeline tests on synthetic snapshots |
| `analysis/register_run.py` | hand registration of runs (manifest, scratch directory, checksums) |
| `analysis/run_step_collisionless.sh` | the collisionless step run (T6 at sigma = 0) |
| `inputs/box_step_collisionless.athinput` | Minkowski periodic box deck (flat kerr_schild metric) |
| `figs/` | figures of the references, of the pipeline test and of run T6-0 |

## How to rerun

    cd /data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/collide
    OMP_NUM_THREADS=4 python3 -m pytest -q REFERENCES/tests      # 62 tests, ~1 min
    OMP_NUM_THREADS=4 python3 -m pytest -q analysis/tests        # 3 tests, ~1.5 min
    cd /data/haiyangw/nrpic/wt/C-sidm
    python3 tracks/C-sidm/collide/analysis/register_run.py --purpose "..." --cores 4 \
        -- python3 tracks/C-sidm/collide/REFERENCES/make_figures.py @OUT
    python3 tracks/C-sidm/collide/analysis/register_run.py --purpose "..." --cores 4 \
        -- bash tracks/C-sidm/collide/analysis/run_step_collisionless.sh 100000

Python: system numpy 2.2, scipy 1.15, matplotlib 3.10, mpmath 1.3, pytest 9 (no venv
needed). Figures use `python/nrpic/figstyle.py`.

## Runs of this package

| Run id | What | Result |
|---|---|---|
| C-sidm-20261115-120703-9b3e868 | reference figures and numbers | `figs/ref_*`, outcomes R1-R7 |
| C-sidm-20261115-121302-313d399 | T6 at sigma = 0 with the existing processor executable | passed: positions exact to 1.8e-12 L, slab sums within 1.85 noise units of the exact curve |

## Pending runs (need `core/collisions`; none can run before it exists)

T0 (core's unit test with `test_vectors.json`), T0b (replay; `analysis/replay.py` still to
be written against core's dump format), T1, T2 (processors, minutes); T3-T5, T11
(1e6 particles, ~1e3 steps; processors with 16 cores or < 0.5 card-hour); T6-T8 (the
short-mean-free-path runs: 1e6-1e7 particles over 1e3-1e4 collision times, several
card-hours in total, estimate to be refined after T2 measures the cost per pair); T9, T10
(processors; MPI variant if the build has MPI); T12 after a static curved-metric option
exists. This package had no card-hours.

## Findings so far

1. arXiv:2602.17487, which the brief names as the cross-check for collisions (lines 520
   and 852), is a collisionless Vlasov-Maxwell solver (`results.tex` line 18); it cannot
   cross-check collisional relaxation or conduction. [VERIFIED]
2. The conduction constant b of the short-mean-free-path flux appears with two values in
   the SIDM literature, 25 sqrt(pi)/32 = 1.385 (Koda & Shapiro; 2601.17117; 2010.15132's
   2.1) and 25 pi/(32 sqrt 6) = 1.002 (Balberg et al.); they differ by 1.38. T7 measures
   kappa and decides; prediction 1.385 (Chapman-Enskog, hard spheres). [VERIFIED that both
   are printed; JUDGEMENT on which is right until T7 runs]
3. With unequal macroparticle masses no pairwise update can be both exactly conserving
   and give the correct equilibrium (SPEC.md 4.4) [JUDGEMENT]: production runs need
   equal masses; the Nanbu-Yonemura option conserves only in expectation.
4. The relativistic two-temperature relaxation rate falls far below the
   non-relativistic form (0.16 of it at theta_2 = 2.8; `figs/ref_relax.png`), and a code
   that used |v_a - v_b| instead of the Moller speed would be 27 percent too fast there
   and 48 percent too fast in a drifting gas (T4, T11 catch it).
5. The naive gamma_rel - 1 = W_a W_b - u_a.u_b - 1 (and also my first "robust" form)
   loses up to 8 digits for pairs with a large common Lorentz factor; SPEC.md section 3
   gives a form accurate to a few eps, which the kernel should use.

## Requests

To core (branch `core/collisions`):
- Implement SPEC.md; write `tracks/core/interfaces/collisions.md` with the final option
  and history-column names (TESTS.md section 1 lists what the tests need; `an_box.py`
  takes `--col NAME=HEADER` to map names).
- Run T0 with `REFERENCES/test_vectors.json`; add the debug dump of SPEC.md 4.7 for T0b.
- Refuse unequal masses with `coll_weights = equal` (fatal error naming them).
- Use the gamma_rel - 1 form of SPEC.md section 3 (or show equal accuracy on the vectors).
- For T12: a problem-generator option for a static homogeneous metric (constant alpha0,
  psi0, zero shift), with particles and no Z4c evolution.
- Confirm that the per-cell metric at the end of the step (`met1` at the cell centre) is
  available to a kernel running after the particle exchange.

To core (branch `core/rng`):
- Reserve stream 2 sub-streams 0, 1, 2 for the keys K1-K3 of RNG_REQUIREMENTS.md and
  put the table of section 3 there into `coord/INTERFACES/rng.md`; state the tag rules
  (unique for the run, never reused, unchanged by restart and migration).
- Keep `python/nrpic/rng.py` bit-identical for K1-K3 (needed by the replay test T0b).

To kb:
- Fetch and index: the hard-sphere conductivity beyond the first Chapman-Enskog
  approximation (Chapman & Cowling; factor ~1.025); relativistic Chapman-Enskog transport
  coefficients for constant cross-section (Cercignani & Kremer, or an arXiv source);
  Nanbu & Yonemura 1998 (weighted collisions); weighted-collision schemes that claim
  exact conservation for unequal weights (to check SPEC.md 4.4); DSMC cell-size and
  time-step error of transport coefficients (Alexander, Garcia & Alder 1998; Garcia &
  Wagner 2000; Hadjiconstantinou 2000); the collisional Boltzmann treatment of SIDM cited
  by arXiv:2601.17117 as "Gurian:2025zpc" and relativistic lattice Boltzmann ("Ambrus
  2022") as possible cross-validation codes for M5.

To the lead of C-sidm:
- Propose to the orchestrator (outbox) the correction of brief lines 520 and 852
  (2602.17487 is collisionless) and of the charter's row "Collisional relaxation in a
  Minkowski box".
- C-pre-4 (equilibria): sample equal-mass macroparticles for collisional runs (SPEC.md
  4.4) and record the code units needed to convert sigma/m from cm^2/g (SPEC.md 1).
- Card time for T6-T8 is not in this package's allotment.
- Note: the commit e0bbac2 of this package also committed four manifests of other
  helpers' runs (`tracks/C-sidm/runs/C-sidm-20261115-120610-b4592be`, `-120715-38ab057`,
  `-120717-38ab057`, `-120801-38ab057`) by a glob; their owners' later commits update
  them. `.gitignore` ignores `runs/` everywhere, so manifests under `tracks/<ID>/runs/`
  are added with `git add -f` (the harness does the same).
