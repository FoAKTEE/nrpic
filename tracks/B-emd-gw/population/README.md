# population (helper package of B-emd-gw, wave 3a, 2026-11-19)

Design of Track B's G3 science run, the stochastic GW background of a population of halos
in a small periodic box, with a Newtonian-mode scouting run of the same box at 64 cells on
processors. The deliverable is `DESIGN.md`; predictions P1-P10, I1 and their outcomes are
in `JOURNAL.md`. Units as in `DESIGN.md` (G = c = 1, H = 1 and a = 1 at the start,
lengths in initial Hubble radii, conformal time t, a = (1 + t/2)^2).

## Contents

| Path | What |
|---|---|
| `DESIGN.md` | the design: spectrum and scales from the references (locators), the box (L = 8) and the amplitude scan, halo counts, signal estimates and the Newtonian measurements, cost of the full-GR run at 128 and 256 cells, run list, what the code lacks |
| `JOURNAL.md` | predictions written before each run, outcomes after it, failed ones included |
| `scripts/make_ic.py` | initial data: Gaussian random field with the early-matter-era spectrum P(k) ~ A_s k cut at k_c (cosmo/ic/random_field.py), Newtonian particles (make_field.newtonian_particles), the relativistic data (`--gr`, make_field.build) or the dictionary without constraint solve (`--gr-nosolve`, timing only) |
| `scripts/run_newton.sh` | one Newtonian case: make_ic.py, then the release core-v0.3 processor build |
| `scripts/run_gr_ic.sh` | relativistic initial data for several box sizes |
| `scripts/design.py` | semi-analytic design (scales against L, BBKS and Press-Schechter counts, baseline GW energy per maximum, quasi-static TT floor, card cost) |
| `scripts/analyze.py` | friends-of-friends halos; GW energy of the box from the TT stress of the snapshots (radiated with junk and near field removed, switch-off measure of 2212.00425, near field); quadrupole formula per halo during formation; `--lscale` for the same run as a box lambda L |
| `scripts/compare.py` | checks of P3-P7 and P9 from the analysis outputs |
| `inputs/pop_newton.athinput` | Newtonian mode, periodic, expanding, L = 4, 64^3 |
| `inputs/pop_gr.athinput` | full relativity (nrpic_cosmo, production configuration), for the pending timing runs |
| `results/` | design.json, analysis_{n32,fid,amp2,nc4,fidL8,fidL2}.json, compare.json |
| `figs/` | design_scales, pop_halos_*, pop_density_*, pop_gw_*, pop_compare (PNG; PDF beside the scratch copies); all looked at |

## Rerun

From the worktree root (`/data/haiyangw/nrpic/wt/B-emd-gw`), each command registered (add
`--background` for long runs and `harness/bin/nrpic-run finish <run_id>` afterwards):

```
P=tracks/B-emd-gw/population
harness/bin/nrpic-run submit --kind scouting --gate G3 --package $P --cores 1 --purpose "..." \
    -- python3 $P/scripts/design.py
harness/bin/nrpic-run submit --kind scouting --gate G3 --package $P --cores 1 --background --purpose "..." \
    -- bash $P/scripts/run_newton.sh fid64 "--n 64 --L 4 --nc 3.2 --sigma1 0.0562 --seed 1 --ppc 1" \
    particles/dt=0.03125 particles/newton_cfl=0.25 particles/newton_mg_tol=1e-6
# 32 cells: add mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 particles/dt=0.0625
harness/bin/nrpic-run submit ... -- python3 $P/scripts/analyze.py --case fid:<scratch>/fid64 \
    --case seed2:<scratch>/seed2 --case n32:<scratch>/n32 --gw fid --ng 64 --nhalo-q 10 \
    --design $P/results/design.json --tag _fid           # --lscale 2 --tag _fidL8 for L = 8
harness/bin/nrpic-run submit ... -- python3 $P/scripts/compare.py
harness/bin/nrpic-run submit ... -- bash $P/scripts/run_gr_ic.sh 64 "4 8 16" "--nc 3.2 --sigma1 0.0562 --seed 1 --ppc 1"
```

## Runs (manifests in `../runs/<run id>/`, outputs in `scratch/B-emd-gw/<run id>/`)

| Run | What | Status |
|---|---|---|
| B-20261119-143348-728c0e5 | Newtonian fiducial, step 1/64, solve to rounding | stopped after 32 cycles (6 s per cycle; JOURNAL entry 2) |
| B-20261119-143828-0ef9b5b | Newtonian fiducial (seed 1, 64^3, L = 4, nc = 3.2, sigma1 = 0.0562) to a = 100 | completed |
| B-20261119-143832-85cbe25 | Newtonian, seed 2 | completed |
| B-20261119-145324-525e4fd | Newtonian, 32 cells | completed |
| B-20261119-145328-4b3663f | Newtonian, sigma1 doubled | stopped by me at a = 57 (a = 50 needed) |
| B-20261119-145715-b18561e | Newtonian, nc = 4 | completed |
| B-20261119-143836-644f0a9 | design | failed (rfft layout), fixed |
| B-20261119-144134-092e73f | design | completed; `results/design.json` |
| B-20261119-160611-3ef806d | design, rerun for the figure axes | see `JOURNAL.md` |
| B-20261119-153509-02a921f | analysis A-n32 | completed (per-halo quadrupole of that version is an artefact, JOURNAL entry 3) |
| B-20261119-153724-a6f1ab5 | analysis A-fid with the old per-halo code | stopped by me, superseded |
| B-20261119-154315-c55b30f | analysis A-fid (fid, seed2, n32; GW of fid) | completed |
| B-20261119-154447-99fa502 | analysis A-amp2 | completed |
| B-20261119-155537-d49f8f1 | analysis A-nc4 | completed |
| B-20261119-155621-68170ca | compare (P3-P7, P9) | completed |
| B-20261119-155808-0942d44 | analysis A-fid-L8 (lscale 2) | completed (figure range cut; rerun B-20261119-160632-e1a1d05) |
| B-20261119-155838-4f1954f | analysis A-fid-L2 (lscale 1/2) | completed |
| B-20261119-154528-9306cb1 | relativistic initial data at 64^3, L = 4, 8, 16 | stopped by me in L = 16 (NaN); L = 4 converged, L = 8 not to tolerance |

## Results (details and labels in DESIGN.md and JOURNAL.md)

- Box with 16.5 expected maxima (BBKS) forms 25 halos by a = 30 and holds 18 to 28 to
  a = 100 (64 cells, L = 4); seed 2 agrees; 32 cells find every halo above their mass limit.
- The Newtonian evolution depends on sigma1 a only (P4) and the radiated GW energy of the
  box follows sigma1^(7/2) at equal stage including the post-collapse emission (P9).
- At L = 4 the radiated energy is 2 to 12 times the wave-1 baseline up to a = 30 and 200 to
  800 times later; the quasi-static near field (1.2e-8 a in linear theory, as the first
  source measured) dominates the TT energy until a ~ 50 to 100.
- Recommended G3 configuration: L = 8, nc = 3.2, 256^3, one particle per cell, to a = 143,
  amplitudes sigma1 = 0.014, 0.028, 0.056; 2.9 card-h per full-GR run (extrapolated rate),
  about 14 card-h for the run list.
- The initial-data tool converges at L = 4, not to tolerance at L = 8 with the top
  amplitude within its 18 outer iterations, and fails (NaN) at L = 16.

## Requests

To core (through the B-emd-gw lead's outbox):
1. In-situ output of the low-wave-number Fourier modes of gamma_ij and K_ij (|k| <= k_max,
   double precision, every n cycles) for the periodic cosmology runs: a 256^3 run cannot keep
   the cadence of the GW analysis with full mesh dumps (2.7 GB each; `DESIGN.md` 7, 9).
2. Initial data for near-horizon, large-amplitude fields: `cosmo/ic` make_field.build fails
   at L = 16 (|psi_N| ~ 0.35, NaN) and needs more than its 18 outer iterations at L = 8;
   the in-code solver (core/id-solver, id-solver-2) for this case, or an `outer` option.
3. Second-order TT part in the initial conformal metric (h_ij = (20/3)[d_i Phi d_j
   Phi]^TT/k^2; `scripts/design.py` `quasi_static_tt` is a reference outside the source
   tree), or the option to add a given TT tensor in `nrpic_cosmo` id = file (needed only
   for a < 10, `DESIGN.md` 5(d)).
4. Release of periodic refinement and the periodic horizon finder (core/cosmo-amr), the
   threaded processor build (core/build-openmp) and several cards (core/mpi).

To the B-emd-gw lead:
5. Card timing of the full-GR box at 128^3 and 256^3 (one batch job, about 0.3 card-h,
   `inputs/pop_gr.athinput` with initial data from `scripts/make_ic.py --gr` at 128 cells
   and `--gr-nosolve` at 256): not submitted here, the owner had two card jobs queued.
6. Pre-register the run list of `DESIGN.md` section 8 for G3, after G2.
7. An `--outer` option in `scripts/make_ic.py` passed to make_field.build, then the L = 8
   data at sigma1 = 0.014, 0.028, 0.056 (not run here).
