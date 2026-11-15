# D-pre-2: the dark-matter spike in the probe limit (Schwarzschild and Kerr)

Work package of D-bh-dress (helpers of wave 1 and wave 2). References: Sadeghian, Ferrer &
Will 2013, arXiv:1305.2619 ("SFW", `kb-data/raw/arxiv/1305.2619/v1/src/SFWpaper.tex`);
the Kerr sequel Ferrer, da Rosa & Will 2017, arXiv:1707.06302 ("FdRW",
`kb-data/raw/arxiv/1707.06302/v2/src/kerrdm.tex`, the reference for the Kerr spike as the
lead corrected the brief). Predictions and outcomes, including the failed ones:
`JOURNAL.md`. Units G = c = m_BH = 1 (written Gm); Schwarzschild: R_S = 2 Gm, horizon
2 Gm; Kerr a = 0.8: r_+ = 1.6 Gm, ten horizon radii = 16 Gm.

## Contents

| File | What it is |
|---|---|
| `spike_lib.py` | Semi-analytic reference (decision 0010: reference solution, no time evolution): Schwarzschild orbits (turning points, radial action, coordinate-time radial period, capture angular momentum L_c(E), E_min(r)), Hernquist DF and the inverse of its radial action (table), adiabatically grown DF f(E, L), densities for constant f and for a Hernquist cusp: relativistic with the canonical or the SFW-printed radial action, Newtonian with the Gondolo-Silk (GS) capture ansatz. |
| `paper_curves.py` | Digitizer of the printed curves (SFW Figs. 1, 3 from their PDF vector paths; FdRW fig_rho_a, fig_rho_hern from their PGF). Standard library only, run with `python3 -I`; output to scratch, never committed. |
| `spike_reference.py` | P1: the reference against the printed numbers and curves; `figs/ref_constf.png`, `figs/ref_hernquist.png`. |
| `sample_spike.py` | P2 initial data: species 0 drawn from the final DF (stationary), species 1 loss-cone boundary probes; `.nrp` files for AthenaK. |
| `spike_geodesic.athinput` | AthenaK input: `nrpic_geodesic`, analytic Cartesian Kerr-Schild metric, a = 0, midpoint pusher. |
| `drive_runs.py` | Runs the CPU executable on several particle files in parallel. |
| `analyze_spike.py` | P2 analysis: binned density against the reference, invariants, horizon crossings against exact geodesics; `figs/stationarity_profile.png`, `figs/stationarity_time.png`, `figs/invariants_losscone.png`, `figs/losscone_dt0.05.png`, `figs/losscone_dt0.025.png`. |
| `compare_dt.py` | P2e: crossing-time offsets for two time steps; `figs/crossing_dt.png`. |
| `particle_budget.py` | P3: particle number to resolve the profile inside 20 Gm; `figs/particle_budget.png`. |
| `register_run.py` | Writes `tracks/D-bh-dress/runs/<run_id>/manifest.json` around a command. |
| `kerr_lib.py` | Wave 2. Kerr reference by FdRW's method (decision 0010: quadratures, no time evolution): capture boundary C_crit(E, Lz; r) = min over r_+ < r' <= r of C_V = P/Delta (FdRW's two criteria in closed form), turning points, canonical radial action and polar action, E_min(r, theta), the currents J_t, J_phi, rest-frame density rho and coordinate number density n at (r, theta) for constant f or the Hernquist-grown f (action matching, L = |Lz| + I_theta/2pi); planar-orbit densities (FdRW appendix B). |
| `kerr_curves.py` | Digitizer of FdRW fig_rho_a, fig_rho_theta, fig_rho_hern, fig_angle_hern, figequator1, figemin (PGF text, standard library, `python3 -I`; output to scratch only). |
| `kerr_reference.py` | K1: Kerr reference against FdRW's numbers and curves; `figs/kerr_ref_constf.png`, `figs/kerr_ref_hernquist.png`, `figs/kerr_ref_checks.png`. |
| `sample_kerr.py` | K2 initial data: particles drawn by rejection from the Hernquist-grown Kerr DF (E <= E_cut) on the Kerr-Schild slice (Jacobian of p(BL) -> p(KS) included; `--slice bl` leaves it out). |
| `kerr_geodesic.athinput` | AthenaK input: `nrpic_geodesic`, analytic Cartesian Kerr-Schild metric, a = 0.8 along +z, midpoint pusher, dt = 0.05 M. |
| `kerr_expected.py` | K2 reference: n(r, theta) and <Lz> on a (ln r, cos theta) grid for the binned counts. |
| `analyze_kerr.py` | K2 analysis: counts in (ln r, |cos theta|) bins against the reference, ranges, equator/pole contrast, <Lz>, trends, invariants E, Lz, Q; `figs/kerr_main_profile.png`, `figs/kerr_main_time.png`, `figs/kerr_main_invariants.png`. |
| `compare_slice.py` | K2 control: KS-slice against BL-slice sampling; `figs/slice_control.png`. |
| `kerr_budget.py` | K3: particle number to resolve the Kerr spike inside 10 r_+ = 16 Gm (counting and deposit criteria); `figs/kerr_budget.png`. |

## How to rerun (from this directory; the run ids are in `../runs/`)

```
python3 register_run.py --purpose P1 -- python3 spike_reference.py --out {OUT}            # 2 min
python3 register_run.py --purpose IC -- python3 sample_spike.py --out {OUT} --n0 48000 --n1 2400 --nfiles 12 --ecut 0.99 --seed 20261115
python3 register_run.py --cores 12 --purpose A -- python3 drive_runs.py --ic <IC> --out {OUT} \
    --files spike_0.nrp ... spike_11.nrp -- time/tlim=20000 particles/snap_dt=250 particles/dt=0.05   # 19 min
python3 register_run.py --purpose B -- python3 drive_runs.py --ic <IC> --out {OUT} --files spike_lc.nrp \
    -- time/tlim=1500 particles/snap_dt=2 particles/dt=0.05     # and dt=0.025 for B2
python3 analyze_spike.py --ic <IC> --runs <A>/spike_* --out <dir>    # or --runs <B>/spike_lc
python3 compare_dt.py --a <analysis of B> --b <analysis of B2> --out <dir>
python3 particle_budget.py --out <dir>
```
Executable of wave 1: `/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena` (main,
read-only); no source was changed and no card-hour was used.

Wave 2 (Kerr; `PY=../../../.venv/bin/python`, the worktree's venv from `harness/bin/nrpic-env
create --no-kokkos`; each command was wrapped in `python3 register_run.py --purpose ... --`):
```
$PY kerr_reference.py --out {OUT} --np 8 --nr 44                                   # 105 s
$PY sample_kerr.py --out {OUT} --n 48000 --nfiles 12 --a 0.8 --ecut 0.99 --slice ks --seed 20261116
$PY kerr_expected.py --out {OUT} --np 4                                             # 207 s
python3 drive_runs.py --ic <IC> --out {OUT} --exe /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena \
    --athinput kerr_geodesic.athinput --files kerr_0.nrp ... kerr_11.nrp \
    -- time/tlim=20000 particles/snap_dt=100 particles/dt=0.05                       # 21 min, 12 cores
$PY analyze_kerr.py --ic <IC> --ref <expected> --runs <run>/kerr_* --out {OUT} --tag kerr_main
$PY kerr_budget.py --out {OUT} --np 4                                               # 288 s
```
Executable of wave 2: `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (release
core-v0.3, read-only). No source changed, no card-hour used.

## Results

Numbers with their run ids; the full record with predictions is in `JOURNAL.md`.

**1. The relativistic spike reproduced by SFW's own method** (run
D-bh-dress-20261115-123029-4df1e76; `figs/ref_constf.png`, `figs/ref_hernquist.png`).
- [VERIFIED] Constant f (SFW Fig. 1): relativistic density vanishes at 4 Gm = 2 R_S, GS at
  8 Gm; our peaks 0.8699e8 GeV/cm^3 at 7.58 Gm (relativistic) and 0.3359e8 at 16.0 Gm (GS)
  equal the digitized figure to 0.02 %; whole curves to 0.26 % (2.2 % only at the GS edge);
  FdRW's Schwarzschild curve to 0.4 %. Enhancement at the peak: 2.59. SFW's text value
  "about 15 %" for GS with 8 -> 4 Gm is 9.2 % from their own figure.
- [VERIFIED] Hernquist cusp (M = 1e12 M_sun, a = 20 kpc), m = 4e6 M_sun, canonical radial
  action: FdRW's Schwarzschild curve (arXiv:1707.06302, fig_rho_hern) to 1.0 % (median
  0.07 %); peak 2.44e18 GeV/cm^3 at 7.75 Gm; inner cut-off 4 Gm; spike meets the Hernquist
  profile at 12.42 pc (FdRW: 12.4 pc). Enhancement over the Newtonian GS spike at the
  peak: 3.39 (canonical), 3.57 (SFW action); the two agree to 0.9 % beyond 100 R_S.
- [VERIFIED to 0.04 dex] SFW Fig. 3 is reproduced with m = 1.0e6 M_sun (not the 4e6 M_sun
  of their Sec. V) for 0.45 < log10(r/R_S) < 4, relativistic and non-relativistic curves;
  [JUDGEMENT] beyond 1e4 R_S their curves bend to slope -1.9 where ours keep -7/3.
- [VERIFIED] SFW eq. (3.19)/(4.13) omits the factor 1/(1-2Gm/r) of the canonical radial
  action (FdRW footnote, kerrdm.tex line 919). The printed form raises the inner spike by
  +6.9 % (6 Gm), +5.2 % (peak), +1.9 % (95 Gm), +0.3 % (1e3 Gm). The probe test below uses
  the canonical action.

**2. AthenaK check in the probe limit** (CPU executable of main, analytic Kerr-Schild
metric a = 0, midpoint pusher, dt = 0.05 M; no card-hours).
- Stationarity (run A D-bh-dress-20261115-123755-25227d4, analysis -125739-a18d74d):
  48000 particles drawn from the final DF (E <= 0.99, apocentres <= 92 Gm) for 20000 M
  (9 radial periods of the widest orbits): chi^2/dof of the binned profile 1.48 at t = 0
  and 0.44-1.69 (median 0.98, dof 23) over 81 snapshots; counts in 4-6 / 6-10 / 10-20 /
  20-50 Gm within 3 sigma at every snapshot, late-half means 0.976 +- 0.070,
  0.994 +- 0.022, 0.999 +- 0.011, 0.998 +- 0.006 of the reference. Invariants: |dE/E| median
  8.5e-9, max 1.3e-6 (at r_p = 4.2 Gm); |dL/L| max 1.9e-10.
- Loss cone: the final DF has an empty loss cone; none of the 48000 particles reached
  r < 2. Boundary probes (runs B -123801-25227d4 and B2 -123936-72cd01e): all 1200
  particles with L^2 = L_c^2(1-|q|), |q| = 1e-4 ... 0.1, crossed r = 2, none of the 1200
  with L^2 = L_c^2(1+|q|) did. Crossing times agree with exact geodesics to -0.024 M
  (median; at most -0.75 M at |q| = 1e-4) and converge at second order in dt (ratio
  3.997 for dt 0.05 -> 0.025); the offset grows as 1/|q| (whirl near the unstable orbit).
- [VERIFIED in the source] the analytic-metric mode has no excision: `NrpicExcise` acts
  only for metric = mesh (athenak/src/particles/nrpic.cpp:627); particles inside the
  horizon fall to r ~ 0.004, are flagged when their push turns non-finite, and stay in the
  arrays. "Removal" was therefore measured as "r < 2 in a snapshot" (no particle came back
  out). See Requests.

**3. Particle number inside ten horizon radii (r < 20 Gm)** (run
D-bh-dress-20261115-123848-72cd01e, `figs/particle_budget.png`): equal-mass particles from
the DF truncated at E_cut need N = 3.0e4 (1 - E_cut = 1e-2), 2.8e5 (1e-3), 1.5e6 (1e-4),
7.4e6 (1e-5), 3.5e7 (1e-6) in total for 100 particles in each of 8 log bins in 5-20 Gm
(10 % counting noise; x4 for 5 %); asymptotically x4.6 per decade of the largest
apocentre (N(<r) ~ r^(2/3) of a r^-7/3 spike). For a self-gravitating run the deposited
density is the stricter requirement: about 6e7 particles inside 20 Gm for 5 % noise on
0.25 Gm cells [JUDGEMENT, extrapolated from docs/results_cluster_test.md 2(d)], i.e.
lighter particles near the hole (mass refinement) or a capped deposit level are needed.

**4. What a self-gravitating run can add** [JUDGEMENT]. The probe test fixes the metric,
so it tests only the pusher and the initial-data machinery. A self-gravitating NRPIC run
(puncture plus particles, Z4c) adds: (i) the dress's own gravity, negligible for a
Sgr A*-like spike (dress mass inside 100 Gm far below m) but not for primordial-black-hole
dresses whose mass can approach the hole's, which moves L_c, E_min and the inner edge;
(ii) the growth of the hole by the particle flux through the horizon, the G2 criterion of
the track (horizon mass against integrated flux); (iii) growth that is not adiabatic
(hole forming or growing on the orbital time), which the action-matching method cannot
treat; (iv) numerical relaxation: the deposit noise scatters particles into the loss cone,
and since the probe run keeps the loss cone empty to the particle, the horizon flux of a
self-gravitating run started from this DF measures that relaxation directly; (v) an
expanding background (S4). It cannot be checked against SFW beyond the probe limit.

## Results of wave 2: the Kerr spike (a = 0.5, 0.8)

**5. FdRW reproduced by their method** (runs D-bh-dress-20261115-171134-38634d6 and the
rerun D-bh-dress-20261115-171615-8adbbdd that compares at our nodes; JOURNAL K1;
`figs/kerr_ref_constf.png`, `figs/kerr_ref_hernquist.png`, `figs/kerr_ref_checks.png`).
- [VERIFIED] a = 0 through the Kerr code equals the wave-1 Schwarzschild references to
  8.9e-4 (constant f) and 3.8e-4 (Hernquist) on 4.07-40 Gm.
- [VERIFIED] Constant f (f0 = 5.13e8 GeV/cm^3, FdRW line 763), equator: a = 0.5 and 0.8
  within 0.88 % and 0.95 % of fig_rho_a (median 0.12-0.15 %); peaks 0.9271e8 GeV/cm^3 at
  7.31 Gm and 1.0604e8 at 6.61 Gm (FdRW 0.9256e8 at 7.25, 1.0585e8 at 6.53); a = 0.8 on the
  axis within 0.78 % of fig_rho_theta. Peak ratio a = 0.8 over a = 0: 1.219 (FdRW text
  line 213: "20 %").
- [VERIFIED] Inner edge at the equator = r_mb+ = 2 - a + 2 sqrt(1 - a) (FdRW eq. mborbit):
  2.9143 / 2.9142 (a = 0.5), 2.0952 / 2.0944 (a = 0.8); off the plane (a = 0.8): 2.241 Gm
  at theta = pi/3, 3.640 Gm on the axis. Counter-rotating orbits enter at
  r_mb- = 2 + a + 2 sqrt(1 + a) (kinks of the planar curves).
- [VERIFIED] E_min(10 Gm, equator) against figemin to 5.9e-5 for 0.1 <= a <= 0.99;
  C_crit = 10.32 (Gm)^2 for a = 0.75, E = 0.97, Lz = 2 (caption: 10.3); on the axis the
  general routine equals FdRW's closed form eq. (825) to 4e-5.
- [VERIFIED] Planar orbits: FdRW's figequator1 is 0.2500-0.2505 times their eq. (584) as
  printed (prefactor 8 f/sqrt(r)) at a = 0, 0.5, 0.8; shapes then agree within 3.3 %.
  Eq. (lmax) has a sign typo (a^2 - x(x-2) must read a^2 + x(x-2) = Delta(x), as in eq.
  lmaxe1); with it the viterate caption's Lz^max = 4.829 fits a ~ 0.72 (spin not stated).
- [TO VERIFY] Hernquist DF (m = 4e6 Msun, M = 1e12 Msun, r_s = 20 kpc): a = 0 within 1.4 %,
  a = 0.8 on the axis within 1.5 %, but for Lz != 0 at a != 0 ours is below FdRW: -0.5 % at
  20 Gm, -1 % at 12 Gm, -4.0 % at the a = 0.8 peak (3.922e18 GeV/cm^3 at 5.06 Gm against
  4.083e18 at 5.07), -6 to -18 % at the steep inner edge (2.4-3 Gm); a = 0.5 peak -0.9 %;
  a = 0.8, pi/3 peak -2.3 %. Our actions equal independent quadratures to 1e-10, the
  quadrature is converged to 1e-4, and constant f (same domain) agrees to 1 %; the
  difference is in the action matching for Lz != 0 and has no identified cause. FdRW's own
  text ratio a = 0.8/0.5 "approximately 35 %" lies between ours (1.406) and their figure
  (1.451); "around 70 %" over Schwarzschild is their figure (1.674; ours 1.609).
- [TO VERIFY] FdRW's constant-f theta = pi/3 curve (fig_rho_theta) rises 1-1.5 Gm further
  out than ours and lies 1-2.7 % above ours at 8-17 Gm, while the peak values agree to
  0.2 %; no single polar angle of ours reproduces it; their Hernquist pi/3 curve does not
  show the shift. [JUDGEMENT] a problem of that one curve.

**6. AthenaK stationarity in the fixed Kerr metric** (release processor executable,
analytic Cartesian Kerr-Schild a = 0.8, midpoint pusher, dt = 0.05 M; IC
D-bh-dress-20261115-172335-9e5ccf9, run D-bh-dress-20261115-172611-1e40191: 12 processes,
1278 s, 4.3 core-hours, no card-hour; reference grid -172646-ed6a510; analysis
-174954-786ddcc; JOURNAL K2).
- Initial data: 48000 particles from the Hernquist-grown Kerr DF with E <= 0.99 (pericentres
  >= 2.28 Gm, apocentres <= 95 Gm, 17.7 % inside 16 Gm), sampled on the Kerr-Schild slice:
  the phase-space density f is per d^3x d^3p_i of the slice whose time is used, so a sample
  drawn on t_BL = const and put at t_KS = 0 needs the factor 1 + (2r/Delta) v^r_BL
  (wave 1 drew on the Schwarzschild-time slice without it; see the control below).
- [VERIFIED] chi^2 of the binned counts (18 log bins in r x 3 bands of |cos theta|, 47 bins
  with > 20 expected) 51.4 at t = 0, median 43.8, range 20-75 over 201 snapshots to
  20000 M; counts in 0-4, 4-6, 6-10, 10-16, 16-40 Gm within -2.6 ... +2.1 sigma at every
  snapshot; late/early-half ratios 0.998, 1.003, 0.999, 1.000, 1.000; trends per 1e4 M
  (-0.7 +- 0.9), (0.3 +- 0.5), (-0.04 +- 0.19), (-0.01 +- 0.13), (0.01 +- 0.04) per cent;
  time averages -1.1, -0.9, -1.0, -0.1, +0.6 sigma from the reference (error of a time
  average over independent orbit draws). The depletion of the polar band inside ~6 Gm and
  the equator/pole contrast (late-half 1.130, reference 1.127) stay as in the reference.
- [VERIFIED] Net prograde rotation: mean Lz = 2.27, 1.80, 1.07, 0.645, 0.352 Gm in the five
  ranges (reference 2.267, 1.800, 1.069, 0.645, 0.352), constant in time (late-half means
  2.267, 1.810, 1.054, 0.655, 0.370; single snapshots up to 4.3 standard errors off in the
  inner two ranges, no trend).
- Invariants: max over snapshots |dE/E| median 1.2e-8, max 7.9e-6 (r_p = 2.31 Gm),
  |dLz| max 1.7e-9, |dQ|/max(Q, 1) max 9.5e-6. No particle came within r_+ (smallest
  r 2.288 Gm); 14 went below their predicted pericentre by up to 3.1e-3 Gm (energy error
  near the capture boundary; the 1e-3 threshold predicted was too tight).
- Control of the slice (runs -173649-d343137, -174807-ba95d18, -175504-5b843b8, analyses
  -175512-5b843b8, -175842-16be482, comparison -175852-16be482, `figs/slice_control.png`):
  the same DF sampled on the BL slice without the Jacobian (the wave-1 scheme) evolves like
  the exact KS-slice sample within the noise over 3000 M (largest running-mean excursions
  1.3-2.0 sigma in both); the differential offsets (BL minus KS: -3, +1.4, -0.8, +0.1 % in
  0-4, 4-6, 6-10, 10-16 Gm) persist rather than decay and are within the noise of the
  ~3000 non-shared particles. So wave 1's Schwarzschild test is not affected at its
  precision [JUDGEMENT on the second-order origin; JOURNAL K2 control].

**7. Particle number inside ten horizon radii, Kerr a = 0.8 (r < 16 Gm)** (run
D-bh-dress-20261115-173114-af8bfcc, `figs/kerr_budget.png`; JOURNAL K3). Equal masses,
DF truncated at E <= E_cut:
- Counting, 8 log bins in 4-16 Gm (2.5-10 r_+) x 3 bands of |cos theta|, set by the polar
  band at 4-4.8 Gm: N_total = 1.35e5 (10 %) / 5.4e5 (5 %) for 1 - E_cut = 1e-2 (largest
  apocentre ~110 Gm); 1.25e6 / 5.0e6 (1e-3), 6.8e6 / 2.7e7 (1e-4), 3.3e7 / 1.3e8 (1e-5),
  1.5e8 / 6.1e8 (1e-6): about 1e5 particles inside 16 Gm, and x4.7 per further decade of
  the largest apocentre.
- **Self-gravitating run (deposit noise, the stricter requirement):** 5 % noise in every
  cell between 4 and 16 Gm needs about 30 particles per cell (noise 0.26 at 1.1 particles
  per occupied cell with two filter passes, N^-1/2: docs/results_cluster_test.md (d)),
  i.e. **8.6e7 particles inside 16 Gm at dx = 0.25 Gm (6.9e8 at dx = 0.125 Gm)**, or
  N_total = 4.8e8 (3.8e9) when the DF is truncated at E <= 0.99, 4.1e9 (3.3e10) at
  E <= 0.999 [JUDGEMENT: the noise law is extrapolated from the cluster test and assumes
  equal masses; lighter particles near the hole (mass refinement) or a capped deposit
  level change the totals, not the number needed inside 16 Gm].

## Not done

- The cause of the 4 % Hernquist difference to FdRW at a = 0.8 (item 5) is not found.
- The AthenaK check used a = 0.8 only (not 0.5), dt = 0.05 M only (no dt-halving run), and
  no loss-cone probes in Kerr (the analytic-metric excision request of wave 1 is still
  open; the stationary DF has an empty loss cone, so the check did not need it).
- No self-gravitating run (outside this package).

## Requests

- **core**: excision for the analytic metric sources. Apply `alpha_exc` (lapse of the
  analytic metric at the particle) also for metric = kerr_schild, kerr_schild_sph,
  boyer_lindquist and lattice, and let `NrpicExcise` remove flagged particles (PGID < -1)
  for every metric source, counted in n_excised / m_excised of the history. Today a particle
  whose push turns non-finite is flagged but kept and pushed again every cycle
  (athenak/src/particles/nrpic.cpp:462-533, 627). Acceptance test supplied here:
  `spike_lc.nrp` of IC run D-bh-dress-20261115-123734-25227d4 with
  `particles/alpha_exc=0.62`: n_excised must reach 1200, each removal after the predicted
  horizon crossing (`tcross` in `ic_meta.npz`) by the infall time from r = 2 to the
  excision lapse, none of the 1200 bound probes removed; run A's files: no removal.
- **core** (for the self-gravitating dress, later): particle mass refinement near the
  hole, or an adaptive deposit level cap inside ~20 Gm (result 3).
- **kb**: annotate arXiv:1305.2619 with (a) the missing 1/(1-2Gm/r) in eqs. (3.19)/(4.13)
  (FdRW kerrdm.tex line 919), (b) Fig. 3 drawn for m = 1e6 M_sun (this package, P1),
  (c) "about 15 %" (SFWpaper.tex line 443) is 9.2 % from Fig. 1; and arXiv:1707.06302 with
  the +35 % / +20 % of the text against +45 % / +14 % of fig_rho_hern / fig_rho_a.
- **lead (D-bh-dress)**: the track sheet's D-pre-2 says "integrate geodesics ... to obtain
  the adiabatically grown density profile"; the profile comes from action matching, the
  geodesic integration (in AthenaK) is the stationarity and loss-cone check. Wording for an
  outbox note if wanted. The dev figures committed by mistake in e25f22a were overwritten
  by the registered ones.
- **core**: the release processor executable ran the Kerr stationarity test without
  problems (1.3e6 particle updates per second per core); nothing new needed for the probe
  limit. For a self-gravitating spike: the particle numbers of item 7 (8.6e7 inside 16 Gm
  at dx = 0.25 Gm for 5 %) call for particle mass refinement near the hole or a capped
  deposit level inside ~16 Gm (repeats the wave-1 request with Kerr numbers).
- **orch (harness)**: `harness/bin/nrpic-run submit --package tracks/D-bh-dress/spike`
  refused every run of this package because another helper left an untracked file at the
  worktree root (`es.horizon_summary_0.txt`); all runs of wave 2 were registered by hand
  with `register_run.py`. A shared-worktree package mode that ignores untracked files
  outside `tracks/<ID>/` (or lists them in the manifest) would let helpers use nrpic-run.
- **kb**: annotate arXiv:1707.06302 with (a) eq. (lmax) sign typo (a^2 + x(x-2)), (b)
  figequator1 drawn with 1/4 of the prefactor of eq. (584), (c) fig_rho_theta's pi/3 curve
  not reproducible inside 8 Gm, (d) the Hernquist Kerr curves 4 % above an independent
  recomputation at the a = 0.8 peak (cause open), (e) text "approximately 35 %" against
  45 % in fig_rho_hern.
- **lead (D-bh-dress)**: wave 1's Schwarzschild stationarity sample (sample_spike.py) was
  drawn uniformly in Schwarzschild time and put on the Kerr-Schild slice without the
  Jacobian 1 + (2/(r-2)) v^r; the control of item 6 says whether that matters at the
  precision of the wave-1 test. The Kerr baseline of D-pre-2 is now in place for G1 with
  the open Hernquist difference stated.
