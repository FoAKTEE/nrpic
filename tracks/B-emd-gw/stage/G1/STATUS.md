# G1 status of B-emd-gw (pre-core baseline)

State 2026-11-15, after wave 1 and the lead's review. Verdict: **G1 not met**; one sheet
criterion met in a flat box, one met in its semi-analytic part, one superseded. For each
criterion: (E) verified from existing evidence of `cosmo/` (charter, "What differs from
the brief", item 2), (W) added by this wave, (M) missing. Run ids are under
`tracks/B-emd-gw/runs/`; every number below was reproduced bit for bit by the lead's
clean-export re-check B-emd-gw-20261115-131016-03b1119.

## Track-sheet criteria (`coord/CHARTER.md` line 121)

### 1. "The two diagnostics agree on analytic linear waves": MET in a flat periodic box; open for oblique and expanding cases

- (E) none: `cosmo/` has no GW diagnostic.
- (W) Fourier TT projection (h^TT, d_tau h^TT, rho_K, spectra, helicity) and Weyl E, B,
  Psi_4 (`gw_diag/gwdiag/`), 14 tests passing. On analytic fields: 48 random waves to
  2.6e-12; Psi_4 = hddot_+ - i hddot_x with error proportional to A, reverse direction at
  rounding; E, B at FD orders 2, 4, 6 (runs -115206-2e6c497, -115637-175cbca). On
  AthenaK output (z4c_linear_wave along x, 32^3, two periods, run -113218-0ea0f74,
  analysis -120128-7dfaa38): TT amplitude within 3e-7, phase within 1.2e-6 rad, rho
  within 6e-7; Psi_4 from the same dump equals the analytic hddot_+
  (`gw_diag/figs/athenak_psi4.png`). The wave itself propagates with errors matching the
  Fourier symbol of the scheme to 1 % up to 64 cells (periodic_z4c, `tables/lw_x.md`).
- (M) An oblique wave (k = (1,1,1)): the generator's data are not transverse
  (`athenak/src/pgen/tests/z4c_linear_wave.cpp` lines 107-112; confirmed by the lead,
  run -131027-03b1119 check a); waits for core's sign fix. The two diagnostics on a wave
  in an expanding box (1/a decay reference ready in scope run -113632-2960145). AthenaK's
  own weyl output lags by waveform_dt - dt (measured, run -120128-7dfaa38): gwdiag's
  fixed-direction Psi_4 replaces it.

### 2. "The Newtonian baseline reproduces the scaling of the literature": MET for the semi-analytic baseline; NOT MET for the N-body baseline

- (E) `cosmo/newton/pm.py` exists (Newtonian particle mesh, predates decision 0010); no GW
  quantity.
- (W) Zel'dovich ellipsoid and homogeneous-ellipsoid ODE (`baseline/`, run
  -115752-840e994): the ZA spectrum formula of both papers reproduced exactly (also
  rederived by the lead, run -131027-03b1119 check e); slopes 3.5 (energy and peak) and 1.5
  (peak frequency) within 0.034 for delta_L <= 1e-2 (2403.15126 lines 1031, 1074); the
  single-patch Newtonian problem is exactly self-similar, E = F M c^2 (2 alpha)^(7/2) to
  3e-13, the origin of the sigma^(7/2) law; crossing times of 2605.04487 (22.536, 29.097)
  reproduced to 1.0 % and 0.09 % by the literal model B; redshift scalings exact, 21.027
  against 21.03. Plane-wave pancake with `pm.py` against the exact Zel'dovich solution
  (runs -115239-69ab1db, -122451-01801f6): 1e-3 in position to a = 15 at 64 cells, first
  order in the cell size with one particle per cell, set by the lattice sampling (two
  per cell: 4.1e-4 at 32 cells).
- (M) The N-body pancake or ellipsoid with the quadrupole formula in AthenaK's Newtonian
  mode (decision 0010): the mode and its quadrupole history exist on `core/newton` (tip
  ce329f5, not on main); tests N1-N3 of `baseline/BASELINE.md` are specified, not run.
  The Omega prefactor of 2403.15126 line 1501 is missed by a factor 144-392 (cause open).

### 3. "Background error and constraint convergence with the stand-in matter": SUPERSEDED (reword proposed)

- (E) The particle FLRW background is measured directly: lapse = scale factor to 1.9e-7
  at a = 4 (`runs/cosmo/flrw_n32_cpu_sd`) and 7.0e-8 at a = 36 (`dtexp_test/lim`),
  recomputed in run -115414-7ffbde1; fourth-order mesh convergence and Hamiltonian
  constraint 1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32 cells over a thousandfold expansion
  (`cosmo/analysis/daverio_a.json`).
- (W) The re-check above; `verify_cosmo/VERIFY.md` sections 1 and 4.
- (M) The stand-in fluid was never run and is not needed; outbox
  `20261115T1340Z__to-orch__track-b-criteria-under-0010.md` asks to strike it. Not shown:
  particle-number convergence of the background (every homogeneous run has one particle
  per cell on a lattice), a homogeneous run in the full production configuration.

## Gate-level G1 items (charter 9.2)

| Item | State | Evidence |
|---|---|---|
| Baseline results obtainable without the NRPIC coupling | (W) vacuum Z4c in periodic boxes (linear wave, gauge wave, lapse and shift record), semi-analytic GW baseline | periodic_z4c, baseline |
| Analysis pipeline validated on them | (W) gw_diag on analytic fields and on AthenaK vacuum output; scouting on existing full-GR cosmology dumps (runs -120846-d1509b5, -121143-0eace55) with a new caveat: the late TT rise there may be a second-order gauge piece (`stage/G0/REVIEW.md`) | gw_diag |
| Interface proposals submitted | (W) outbox of this session: GW output, generator fix, weyl timing, initial data with a TT part, thin boxes, lattice jitter, Newtonian mode for B | `tracks/B-emd-gw/outbox/20261115T1340Z__*` |
| Baseline data and figures | (W) figures of all five packages, looked at | `stage/G0/EVIDENCE.md` |

## Beyond G1, already in hand (counts toward G2)

- (E) Growth of linear perturbations: growing-mode amplitude within 1e-5 of linear theory
  over a thousandfold expansion (`daverio_b.json`); growth rate f(a) not extracted;
  particle-number convergence only in the old configuration.
- (W) First full-GR kinetic run through shell crossing: the plane-wave pancake at L = 1
  and 4, 32-96 cells, one and two particles per cell, to a = 42 with every particle kept
  (runs -115217-69ab1db, -115902-a3207d7; 0.48 card-hours); GR departure from Zel'dovich
  converged and scaling with (H/k)^2; constraints in the void need two particles per cell
  and direction.
- (M) The multi-code row (shearing dust of arXiv:2003.08014) is specified, not run.

## What closes G1 (next)

1. Core's sign fix of `z4c_linear_wave.cpp`, then the oblique 3D convergence on a card
   (spec `periodic_z4c/inputs/lw_3d.athinput`) with both diagnostics.
2. Both diagnostics on a TT wave in an expanding box (1/a reference of scope check 3A).
3. Newtonian mode on main: plane-wave pancake (`verify_cosmo/inputs/pancake.athinput`)
   and ellipsoid tests N1-N3 against `baseline/` with its quadrupole history.
4. Orchestrator's answer on the criteria rewording.
