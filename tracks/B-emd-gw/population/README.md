# population (helper package of B-emd-gw, wave 3a, 2026-11-19)

Design of Track B's G3 science run, the stochastic GW background of a population of halos
in a small periodic box, with a Newtonian-mode scouting run of the same box at 64 cells on
processors. The deliverable is `DESIGN.md`; predictions and outcomes are in `JOURNAL.md`.
Labels and units as in `DESIGN.md` (G = c = 1, H = 1 and a = 1 at the start, lengths in
initial Hubble radii, conformal time t, a = (1 + t/2)^2).

## Contents

| Path | What |
|---|---|
| `DESIGN.md` | the design: spectrum and scales from the references (locators), box size as the knob of the relativistic content, halo counts, signal estimates, cost of the full-GR run at 128 and 256 cells, what the code lacks, draft run list |
| `JOURNAL.md` | predictions written before each run, outcomes after it |
| `scripts/make_ic.py` | initial data: Gaussian random field with the early-matter-era spectrum P(k) ~ A_s k cut at k_c (cosmo/ic/random_field.py), Newtonian particles (make_field.newtonian_particles), optionally the relativistic data (make_field.build, `--gr`) or the dictionary without the constraint solve (`--gr-nosolve`, timing only) |
| `scripts/run_newton.sh` | one case: make_ic.py, then the Newtonian mode of the release core-v0.3 processor build |
| `scripts/design.py` | semi-analytic design (scales against L, BBKS and Press-Schechter counts, baseline GW energy per maximum, quasi-static TT floor, card cost) |
| `scripts/analyze.py` | friends-of-friends halos, the GW energy of the box from the TT stress of the snapshots (radiated, switch-off and near-field measures), quadrupole formula per halo, figures |
| `inputs/pop_newton.athinput` | Newtonian mode, periodic, expanding, L = 4, 64^3 |
| `inputs/pop_gr.athinput` | full relativity (nrpic_cosmo, production configuration), for the timing runs of the design |
| `results/design.json`, `figs/design_scales.png` | output of the design run |
| `results/analysis*.json`, `figs/pop_*.png` | output of the analysis runs |

## Rerun

From the worktree root (`/data/haiyangw/nrpic/wt/B-emd-gw`), each command registered:

```
# design (one core, about a minute)
harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/B-emd-gw/population \
    --cores 1 --purpose "..." -- python3 tracks/B-emd-gw/population/scripts/design.py
# one Newtonian case (one core; about an hour at 64^3 on the loaded machine)
harness/bin/nrpic-run submit --kind scouting --gate G3 --package tracks/B-emd-gw/population \
    --cores 1 --background --purpose "..." -- bash tracks/B-emd-gw/population/scripts/run_newton.sh \
    fid64 "--n 64 --L 4 --nc 3.2 --sigma1 0.0562 --seed 1 --ppc 1" \
    particles/dt=0.03125 particles/newton_cfl=0.25 particles/newton_mg_tol=1e-6
harness/bin/nrpic-run finish <run_id>
# analysis of finished cases (NAME:DIR pairs; --gw names the case for the GW analysis)
harness/bin/nrpic-run submit ... -- python3 tracks/B-emd-gw/population/scripts/analyze.py \
    --case fid:scratch-path/fid64 --case seed2:scratch-path/seed2 --gw fid --ng 64 \
    --design tracks/B-emd-gw/population/results/design.json
```

32-cell cases need `mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16
meshblock/nx3=16` and the step 1/16 on the command line.

## Runs

| Run | What | Status |
|---|---|---|
| B-20261119-143348-728c0e5 | fiducial, step 1/64, solve to rounding | stopped after 32 cycles (6 s per cycle; JOURNAL entry 2) |
| B-20261119-143836-644f0a9 | design | failed (rfft layout), fixed |
| B-20261119-144134-092e73f | design | completed; `results/design.json` |
| B-20261119-143828-0ef9b5b | Newtonian fiducial (seed 1, 64^3, nc = 3.2, sigma1 = 0.0562) to a = 100 | see JOURNAL |
| B-20261119-143832-85cbe25 | Newtonian, seed 2 | see JOURNAL |

## Results

See `DESIGN.md` sections 1 to 6 and the outcomes in `JOURNAL.md`.

## Requests

To core (through the B-emd-gw lead's outbox):
1. In-situ output of the low-wave-number Fourier modes of gamma_ij and K_ij (|k| <= k_max,
   double precision, every n cycles) for the periodic cosmology runs: a 256^3 science run
   cannot keep the dump cadence of the GW analysis with full mesh dumps (2.7 GB each in
   double precision; `DESIGN.md` sections 7 and 9). Risk 7 of `../scope/SCOPE.md`.
2. Initial data with the second-order TT part of the conformal metric (h_ij =
   (20/3)[d_i Phi d_j Phi]^TT/k^2 for the matter era, `scripts/design.py`
   `quasi_static_tt` is a reference implementation outside the source tree), or the
   option to add a given TT tensor to the conformal metric of `nrpic_cosmo` id = file: the
   junk of conformally flat data is as large as the radiated signal at L = 4 (`DESIGN.md`
   5(d)).
3. Release of the periodic refinement and the periodic horizon finder (core/cosmo-amr) and
   the threaded processor build (core/build-openmp); the halo population needs them at
   L >= 8 and for the Newtonian references at 128^3 and above.

To the B-emd-gw lead:
4. Card timing of the full-GR box at 128^3 and 256^3 (one batch job, about 0.3 card-h,
   section 10 of `DESIGN.md`): not submitted here because the owner already had two card
   jobs queued.
5. Pre-register the run list of `DESIGN.md` section 8 for G3, after G2.
