# D-pre-2: the dark-matter spike in the probe limit

Work package of D-bh-dress (helper). Reference: Sadeghian, Ferrer & Will 2013,
arXiv:1305.2619 ("SFW", source `kb-data/raw/arxiv/1305.2619/v1/src/SFWpaper.tex`); Kerr
sequel Ferrer, da Rosa & Will 2017, arXiv:1707.06302 ("FdRW", `.../1707.06302/v2/src/`).
Predictions and outcomes, including the failed ones: `JOURNAL.md`. Units G = c = m_BH = 1
(written Gm), R_S = 2 Gm, horizon radius 2 Gm.

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
Executable: `/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena` (main, read-only); no
source was changed and no card-hour was used.

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

**Not done.** The Kerr case: FdRW give equatorial curves for a = 0.5 and 0.8 (digitized
targets, `paper_curves.json` of the P1 run: constant f peaks 0.926e8 at 7.25 Gm and
1.058e8 at 6.53 Gm; Hernquist peaks 2.81e18 at 7.11 Gm and 4.08e18 at 5.07 Gm; their
text says +35 % (Hernquist) and about +20 % (constant f) from a = 0.5 to 0.8, the
digitized curves give +45 % and +14 %). It needs the three-dimensional (E, C, L_z)
integral with the Kerr capture boundary and a Kerr sampler; not started. No
self-gravitating run was made (outside this package).

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
