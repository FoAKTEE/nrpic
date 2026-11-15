# PLAN: three black holes in vacuum, a binary passing a heavier hole (F-pre-3, F-pre-4)

Helper package of F-hills, 2026-11-15. Units G = c = 1; lengths and times in units of
the bare mass M = 1 of the large black hole. Labels: [VERIFIED] measured in a registered
run of this package or read in a source at the locator given; [BACKGROUND] standard
result not checked in a source here; [JUDGEMENT] my reading or choice; [TO VERIFY].
Run ids are `F-hills-20261115-<time>-<commit>`; manifests under `tracks/F-hills/runs/`,
outputs under `scratch/F-hills/<run_id>/`, predictions and outcomes in `JOURNAL.md`.
Nothing here ran the code of `core/multi-puncture`; the runs that need it are named in
section 7 for the lead.

## 0. Summary

1. Capability: core's branch `core/multi-puncture` gives `nrpic_cf` Bowen-York punctures
   with momentum and spin, closed-form corrections of the conformal factor, and
   `puncture_setup` (trackers, refined regions, horizon finders). It builds and has run
   three black holes for 16 M (`core-20261115-120834-d08c476`). Everything a passage
   needs exists except the items of section 6 marked missing.
2. First configuration (section 3): M = 1, an equal-mass binary m1 = m2 = 0.05
   (q = M/m_b = 10), a_b = 3 (30 r_gb), coplanar prograde, Newtonian pericentre
   r_p = 8 (D = r_p/r_t = 1.24), binary phase 130 deg, start at r0 = 4 r_t = 25.85.
   Newtonian outcome: m1 ejected with E1 = +1.75, m2 captured with E2 = -1.84 (units
   (m1 m2/a_b) q^(1/3) = 1.80e-3 M) on an orbit between 5.6 and 9.3 M. The fiducial of
   the novelty helper (r_p = 6, D = 0.93) is rejected: a member passes inside 4 M in
   87 percent of the phases.
3. Mesh and cost (section 4): domain +-204.8, 11 levels, members at m/8 (cells
   0.00625), heavy hole at M/10; 1800 MeshBlocks at the start, at most 2332 along the
   passage (measured trees, core's count reproduced exactly); 39 card-hours for one
   passage of 240 M. m/16 needs 2934 to 4544 MeshBlocks (not one card), m/32 9472 (not
   at all). A q = 4 variant at the same D costs 15 card-hours. The F-hills allotment is
   40 card-hours (decision 0006).
4. Junk and constraints (section 5): the member data carry P/m = 0.28; the closed-form
   correction lowers the Hamiltonian residual about 23 times in RMS but does not change
   the junk; expected junk below 1e-4 M per member (core's scaling 1.3e-2 (P/m)^4 m
   gives 4e-6 M), at wavelength 0.84 M, unresolved in the wave zone; the passage burst
   is about 1.1e-4 M at wavelength 48 M. Uncorrected data would shift each member's
   mass by 2.5e-3 M = 1.4 energy units: the correction is required.
5. Diagnostics (section 6): trajectories, horizons and r psi4 modes exist; missing are
   the radiated-energy integration, a gauge calibration of tracker speeds (needed for
   the binding energies), a pairwise common-horizon trigger, ADM surface integrals and
   a position-dependent shift damping.

## 1. What exists in this repository's AthenaK

| Item | Where | State |
|---|---|---|
| N punctures with P and S, closed-form u with background factor | `core/multi-puncture`: `athenak/src/pgen/nrpic/nrpic_bowen_york.hpp`, hooks in `nrpic_cf.cpp` | built; interface `tracks/core/interfaces/multi_puncture.md` (PROPOSED) |
| Trackers, refined regions, finders per puncture | same branch, `nrpic_puncture_setup.hpp` | finder tolerance scaled with mass after core's test 3; three horizons found at the first search (`core-20261115-131206-372e977`) |
| Stock generators | `pgen/tests/z4c_boosted_puncture.cpp` (one boosted hole), `pgen/z4c/two_punctures/` (wrapper of the outside TwoPunctures library: not usable, decision 0010) | on `main` |
| Tracker | `z4c/compact_object_tracker.cpp`: integrates minus the shift (`tracker_mode = ode`), file `<base>.co_<n>.txt` (iter, time, x, y, z, vx, vy, vz; line 87) | exists |
| Horizon finder | `z4c/fastflow.cpp`: `horizon_summary_<n>.txt` (mass, Sx, Sy, Sz, S, area, hrms, hmean, radii; lines 260-261) | exists |
| Waves | `z4c/z4c_wave_extr.cpp`: r psi4 modes l = 2..8 on spheres about the origin (`spherical_grid.cpp` lines 75-77; factor r in `z4c_calculate_weyl_scalars.cpp` lines 409-410), files `waveforms/rpsi4_{real,imag}_RRRR.txt` | exists; energy, momentum, angular momentum not computed |
| Constraint norms | `outputs/history.cpp` lines 176-250: squared norms summed with sqrt(gamma) dV where chi >= excise_chi, and the volume | exists |
| Time step | `z4c/z4c_newdt.cpp` lines 45-58, `mesh/mesh.cpp` 595-666: one global step, cfl times the finest cell; no subcycling | sets the cost |
| Shift damping | `z4c/z4c_calcrhs.cpp` line 716: one constant eta | position-dependent eta missing |
| CCE dumps | `z4c/cce/` | processing needs an outside CCE code: not usable (decision 0010) |

## 2. What the three-black-hole papers used

- 0710.0879 (`first.tex`): three equal-mass holes (m about M/3), 11 levels, finest
  h = M/80, outer boundary 640 M (lines 143-146); convergence with M/80, M/96, M/115.2,
  fourth order (lines 186-189); waves extracted about the origin, unchanged for
  r > 50 +- 20 M (lines 132-135); radiated energy (6.06 +- 0.02)e-3 M for 3BH1 (line 291).
  [VERIFIED] In units of each hole's mass the finest cell was about m/27.
- 0711.1165 (`second.tex`): the same grid for all three-hole runs (lines 441-442);
  the approximate conformal factor that `corr = approx` implements (lines 222-290,
  core's locators). [VERIFIED]
- 1004.1353 (`Punc_N.tex`): the approximate data have a finite error that does not
  converge with resolution, and solving the Hamiltonian constraint can change the
  evolution "dramatically" (lines 185-194); for 3BH102 the merger order changed and no
  adjustment of masses or momenta of the approximate data reproduced the solved tracks
  (lines 1238-1276); the junk of approximate data does not converge and its difference
  between resolutions is ten times that of solved data (lines 1253-1261); gauge
  eta = 2/M, Courant 1/4 for runs longer than 200 M (lines 995-1000). [VERIFIED]
- 2505.03934 (`apssamp.tex`): binary-single scattering of equal masses with BAM;
  multigrid-solved data with residual tolerance 1e-10 needed (line 208); "a key
  limiting factor ... are large separations" (line 212); psi4 frame issues for several
  holes (line 216); 11 levels, finest 0.0078-0.0234 for holes of mass 0.5, domains
  2688-4608 M (lines 250-288); eta = 1/(2 M_total) (line 196); junk visible in the ADM
  integrals (line 631). [VERIFIED]
Lesson for us [JUDGEMENT]: the published three-hole runs resolved each hole with 20 to
60 cells per mass; our m/8 is a scouting resolution, and a converged Hills result will
need either more card time than one A100 allows for q = 10 (section 4) or smaller q.

## 3. The first configuration

Scale estimate (brief line 275), re-derived by the novelty helper (runs
`F-hills-20261115-045435-f62d553`, `-045438-f62d553`): r_t = a_b q^(1/3)
(0911.1136 `prp.tex` line 88), separation before a plunge needs a_b/m_b > 4 q^(2/3) =
18.6 at q = 10, Peters time 6328 M for a_b = 30 m_b. [VERIFIED there]

Choice of pericentre (T2, runs `F-hills-20261115-130342-0471114`,
`-130755-982aba0`; newton3 driver; figures `figures/fig_newton_phase.png`,
`fig_newton_choice.png`): 360 binary phases, coplanar prograde, starts at 4 r_t and
10 r_t. [VERIFIED]

| a_b | r_p | D | disrupted (4 r_t / 10 r_t) | a member inside 4 M | clean window |
|---|---|---|---|---|---|
| 3 | 6 | 0.93 | 0.928 / 0.911 | 0.867 / 0.778 | 4 deg |
| 4 | 8 | 0.93 | 0.928 / 0.911 | 0.533 / 0.406 | 30 deg |
| 3 | 8 | 1.24 | 0.878 / 0.839 | 0.050 / 0.050 | 45 deg (115-160) |

"Clean": single ejection from both starts, both members beyond 4.5 M. Prograde
disruption extends to D = 2.1 (0911.1136 `prp.tex` lines 846-847). 4 M is the
marginally bound radius of Schwarzschild in areal radius [BACKGROUND]; the Newtonian
distance is a proxy only.

First configuration [JUDGEMENT], numbers from run `F-hills-20261115-132430-7d0c6dd`:

| Quantity | Value |
|---|---|
| masses (bare) | M = 1, m1 = m2 = 0.05, q = 10; no spins |
| binary | a_b = 3 (30 m_b), circular, prograde in the orbital plane; period 103 M |
| orbit | parabolic, r_p = 8, r_t = 6.463, D = 1.238; pericentre speed 0.52 |
| start | binary centre at r0 = 4 r_t = 25.85 from M, 79.5 M before the Newtonian pericentre; tidal-to-binding ratio 2 (r_t/r0)^3 = 0.031 |
| phase | 130 deg (middle of the clean window) |
| start state | newton3 `trajectory` from 10 r_t, read when the centre passes 4 r_t: binary separation 3.036, eccentricity 0.029 |
| positions | M (0.8959, 2.1729, 0); m1 (-7.6709, -20.9806, 0); m2 (-10.2465, -22.4765, 0) |
| momenta | M (-0.022037, -0.014755, 0); m1 (0.008611, 0.011325, 0); m2 (0.013426, 0.003430, 0); P/m = 0.027, 0.285, 0.277 |
| Newtonian outcome | m1 ejected, E1 = +1.75 units (3.15e-3 M), v_inf = 0.36; m2 captured, E2 = -1.84 units (-3.31e-3 M), a = 7.5, closest 5.6 M |
| background factors | Lambda = 1.002 (M), 1.029 (m1), 1.027 (m2) |

Input file: `inputs/hills_q10_m8.athinput` (written by `scripts/plan_numbers.py`, not
run). Caveats [JUDGEMENT]: (i) the momenta are Newtonian; at r0 the relativistic
corrections are of order M/r0 = 0.04, so the NR orbit is not exactly parabolic and its
pericentre is not exactly 8; the comparison models (newton3, geodesic_binary) must be
started from the NR state, not from these numbers (section 6); (ii) relativistically the
captured member, Newtonian a = 7.5 and closest approach 5.6 M, is near or inside the
separatrix of Schwarzschild and probably plunges within one or two returns, which is
part of the physics this run measures [TO VERIFY with geodesic_binary].

Variant q = 4 (runs `F-hills-20261115-131832-907e5fe`, `-131933-907e5fe`):
m1 = m2 = 0.125, a_b = 5 (20 m_b), r_p = 9.82, D = 1.238, phase 127 deg, r0 = 31.75,
81 percent disrupted, clean window 36 deg; m1 ejected with E1 = +1.53, m2 captured with
E2 = -1.63 units (4.96e-3 M); input `inputs/hills_q4_m8.athinput`. [VERIFIED]

## 4. Mesh and cost of one passage

Method (T3, T3b; runs `F-hills-20261115-131109-634fb86`, `-131348-634fb86`): the trees
that `puncture_setup` builds were made with the processor executable of `main`
(`athena -m`, no evolution), with the refined regions written exactly as
`nrpic_puncture_setup.hpp` (lines 115-141 on the branch) writes them; this reproduces
core's 1100 MeshBlocks of `by_triple` exactly. The wave zone follows the corner rule of
the radius criterion (`z4c_amr.cpp` lines 348-366). Positions along the passage are the
Newtonian ones every 10 M. Cost = sum of MeshBlocks times cycles (dt = 0.25 h_min, one
global step) over the vacuum rate 2201 MeshBlock-cycles/s (2022-2310, novelty run
`-045438-f62d553`; core's three-hole run 2140). [VERIFIED for the counts at t = 0 and
along the Newtonian track; the AMR evolution adds blocks: +11 percent in core's 16 M
three-hole run]

| Layout | MeshBlocks start / max / mean | card-hours (240 M) | one card? |
|---|---|---|---|
| q = 10, +-204.8, 11 levels, m/8, radii 1.8 m | 1800 / 2332 / 2006 | 38.9 (37.0-42.3) | yes, limit 2400-2700 |
| same, radii 1.2 m | 1744 / 2290 / 1909 | 36.9 | yes |
| same at m/16, radii 1.2 | 2654 / 2934 / 2574 | 99 | no |
| same at m/16, radii 1.8 | 3690 / 4544 / 4019 | 156 | no |
| +-409.6, m/32, radii 1.8 | 9472 at the start | - | no |
| q = 4, +-256, 10 levels, m/8 (270 M) | 1716 / 2080 / 1744 | 15.2 (14.5-16.5) | yes |
| q = 4 at m/16, radii 1.2 | 2416 / 2654 / 2348 | 41 | marginal |

Recommended layout for q = 10 [JUDGEMENT]: domain +-204.8 with 64^3 root cells (6.4);
11 levels; members at level 10 (cells 0.00625 = m/8) within 1.8 m; heavy hole at level
6 (0.1 = M/10) within 1.8 M (`puncture_setup` rule); wave zone cells 1.6 within 48 and
3.2 within 100 (no extra MeshBlocks at the start: inside the 2:1 padding of the
punctures); spheres at 40, 48 (cells 1.6) and 70, 90 (cells 3.2), all outside the
binary's start radius 22-25; `max_nmb_per_rank = 2700` (core measured 63.1 GB at the
limit 2400 with three finders: 26 MB per slot, so 2700 slots need about 71 GB of the
80 GB; to be checked in run R1). The outer boundary at 204.8 M is reached by light from
the centre at t = 205 and returns to the 48 M sphere at t = 360: after the 250 M run.
Wavelengths: passage burst pi/Omega_p = 48 M (30 cells of 1.6), ringdown of the heavy
hole 16.8 M (10 cells), ringdown of a member 0.84 M (not resolved outside the members'
own levels). [numbers: run `-132430-7d0c6dd`; quasinormal frequency 0.3737/m BACKGROUND]

Correction for the track: the novelty helper's model (23.6 / 60.9 / 149 card-hours at
m/8 / m/16 / m/32 with 1313 / 1693 / 2073 MeshBlocks, a JUDGEMENT taken from core's
"190 leaves per level and hole") is 1.5 to 2.4 times low in MeshBlocks, and m/32 does
not fit one card. [VERIFIED by the trees above] Resolution studies of q = 10 beyond m/8
are not possible on this machine without MPI across the two cards (the build has no
MPI, `scripts/README.md` line 4).

## 5. Junk radiation and constraint violation of superposed Bowen-York data

Expected sizes:
- Hamiltonian constraint at t = 0. Without correction the residual is algebraic,
  H = -psi^-12 Abar_ij Abar^ij, proportional to P^2 (core test 1a). With `approx` and
  the background factor the closed form drops 9.8 times for core's three holes, 2.65
  times in the code's norm at m/8 (truncation at the light punctures) [VERIFIED by core,
  journal-mp "Outcome of test 3 at t = 0"]. For one puncture with P/m = 0.3 the history
  gives <H^2> = 5.5e-12 (approx) against 2.9e-9 (none), RMS ratio 23 (T4, run
  `F-hills-20261115-131605-634fb86`, from core's card runs). By t = 8 every run sits at
  <H^2>^(1/2) about 2e-5, the level of the evolved puncture at m/16, also for the exact
  boosted slice. [VERIFIED] Expected for the first configuration [JUDGEMENT]: the
  members dominate (P/m = 0.28), RMS ratio none/approx near 20 in the closed form and 2
  to 3 in the code's norm at m/8; after the gauge transient the norm is set by the
  evolution, not by the data.
- Mass error. An uncorrected member has ADM mass lower by (5/8) P^2/m = 2.5e-3 M
  (0711.1165 `second.tex` 285-287 via core), that is 1.4 energy units, the size of the
  Hills energies themselves; core measured the uncorrected single puncture settling
  0.6 percent lighter (journal-mp, outcome of 1b). With `approx` the residual is fourth
  order [VERIFIED by core]; I expect a mass error near 1e-4 M per member, 0.06 units
  [JUDGEMENT]. Run with `approx` only.
- Junk. Core's estimate from test 1b, E about 1.3e-2 (P/m)^4 m "good to a factor two at
  best", gives 4e-6 M per member and 6e-9 M for the heavy hole; my analysis of the same
  runs with another background model gives up to 2e-3 m (1e-4 M per member): the
  spheres at 10-14 m are in the near zone and the two estimates differ by ten (T4 and
  the journal's reading of core's entry). The correction does not change the junk (A
  and B within 12 percent): its source is conformal flatness [JUDGEMENT]. The member
  junk rings at the member quasinormal frequency (wavelength 0.84 M): it cannot
  propagate on the wave-zone cells and is damped at the refinement boundaries; what
  reaches the spheres is the heavy hole's (negligible) and the binary's own
  conformal-flatness junk (not estimated) [JUDGEMENT]. Passage burst for comparison:
  quadrupole energy of a parabolic flyby 1.1e-4 M (q = 10) and 3.7e-4 M (q = 4)
  [BACKGROUND formula, TO VERIFY its locator], arriving at a sphere of radius R at about
  79.5 + R (q = 10).

How to measure (runs of section 7):
1. R0, t = 0 on processors: `<H^2>` and the residual field for `corr = approx`, `none`
   and the plain sum (`corr_background=false`), against the closed form with core's
   `tracks/core/analysis/mp/triple_static.py`.
2. R2, one puncture with P/m = 0.28 and spheres at 40, 60, 80 m: a clean junk energy per
   unit mass (the near-zone problem of T4 removed), with and without correction.
3. In the passage: (a) energy through R = 40 and 48 for t < 79.5 + R - 20, before the
   burst can arrive; (b) the member horizon masses in the first 2 M (ringing) and their
   settled values against m Lambda and the boosted-hole value sqrt(M_ADM^2 - P^2)
   (core's test 1b: 1.0107 against 1.0112); (c) the history norms.
Decision rule for solving the constraints [JUDGEMENT]: keep `approx` data for the first
passage if (i) each settled member horizon mass is within 0.5 percent of the closed-form
expectation (0.0520 for the members, 1.002 for the heavy hole), and (ii) the energy
through R = 48 before the burst is below a tenth of the expected burst. Otherwise, and
in any case before G3, request the elliptic solve on the mesh (decision 0010 item 4;
`coord/notes/design_wave2_initial_data.md`): 1004.1353 lines 1238-1276 show that for
three holes approximate data can change the outcome itself.

## 6. Diagnostics of F-pre-4

| Diagnostic | Exists | Missing / to do | Plan |
|---|---|---|---|
| Puncture trajectories | trackers, `co_<n>.txt` | nothing in the code; a track-side reader and figure | coordinate tracks of the three holes; binary separation; centre of mass of the binary |
| Gauge of the tracker speed | - | calibration: core's test 1b shows the tracker speed is 0.48 (t = 10-20) to 0.62 (t = 30-40) of P/M_ADM, the same for all momenta and for the exact boosted slice, with eta m = 2 (journal-mp, outcome of 1b). Our members have eta m = 0.1 | R4: the single-puncture input of R2 with `z4c/shift_eta=0.1`, to get the speed ratio f(t) for the members |
| Binding energy of each member to M | - | track-side analysis | (a) E_i = mu_i (|v_i - v_M|^2/2 - (M + m_i)/|x_i - x_M|) from trackers with v corrected by f(t) and masses from the horizons, plotted against time and compared with newton3 started from the NR state at t = 60; (b) gauge-free checks: the ejected member's late-time speed relative to M, the captured member's radial period and turning points against Schwarzschild geodesics (geodesic_binary), and the energy balance E_rad + horizon masses |
| Wave extraction | r psi4, l = 2..8, spheres about the origin | radiated energy, momentum, angular momentum (track side: `scripts/junk_energy.py` has the energy integral); extrapolation in R; the heavy hole moves 5.5 M off the centre in 248 M on the Newtonian track (mode mixing, 2505.03934 line 216); the ejected member is 69 M from the origin 168 M after the pericentre, so it crosses the 40 and 48 spheres about 100 M after the pericentre, after the burst has passed them (Newtonian track, run `-130755-982aba0`) | energy and recoil from R = 40, 48, 70, 90 in the window before the member crosses; compare with the flyby estimate |
| Horizon mass and spin | finder per puncture from `puncture_setup` (flow constant m^2, tolerance scaled with m) | the common-horizon trigger `PuncAreClose` uses the largest distance between ALL punctures (`fastflow.cpp` lines 1529-1612): a merger of m2 with M while m1 is far away is never searched as a common horizon | the heavy hole's finder follows it (it becomes the merged horizon); request a pairwise trigger from core for later runs |
| ADM mass, momentum, angular momentum | none found in `athenak/src/z4c` or `outputs` | surface integrals | request (low priority); junk and energy balance can be read without them |
| Constraint norms | history | - | as in section 5 |
| Shift damping | constant eta | position-dependent eta for q >= 10 [TO VERIFY by kb: literature on unequal-mass gauge] | first look at R1's member tracks with eta = 2 (eta m = 0.1) |

## 7. Runs named for the lead (not run by me; they need `core/multi-puncture`)

Executables (core's worktree, read only): processors
`/data/haiyangw/nrpic/wt/core-mp/.work/build_cpu/src/athena`, card
`/data/haiyangw/nrpic/wt/core-mp/.work/build_gpu_final/src/athena`.

| Run | What | Command (rundir under `scratch/F-hills/<run_id>/`) | Cost | Predictions |
|---|---|---|---|---|
| R0 | t = 0 constraint check, three variants | `athena -i tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput -d <rundir> time/nlim=0` and the same with `problem/comp0_corr=none problem/comp1_corr=none problem/comp2_corr=none`, and with `problem/corr_background=false` | processors, minutes; about 70 GB memory each (core: 108 GB at 4096 slots) | 1800 MeshBlocks; <H^2> none / approx between 3 and 30 in the code's norm; three horizons at the first search when run with `time/nlim=1` |
| R2 | junk of one puncture, P/m = 0.28 | `inputs/junk_single_P028.athinput`; variant `problem/comp0_corr=none` | about 1 card-hour each [JUDGEMENT: about 1200 MeshBlocks, 7000 cycles] | radiated energy the same at R = 40, 60, 80 within 20 percent; 1e-5 to 1e-3 of m; none and approx within 20 percent |
| R4 | gauge calibration for the members | `inputs/junk_single_P028.athinput` with `z4c/shift_eta=0.1` | about 1 card-hour | tracker speed ratio f(t) differs from the eta m = 2 curve; its value at t = 60 decides how the binding energies are read |
| R1 | first 60 M of the q = 10 passage | `ATHENA_EXE=<card exe> scripts/submit_chain.sh <rundir> tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput time/tlim=60` | 9.5 card-hours | MeshBlocks 1800 at the start and below 2700 to t = 60; rate 2000-2300 MeshBlock-cycles/s; three horizons from the first search, members 0.0515-0.0525, heavy 1.002 +- 0.005; trackers start at zero speed; the heavy hole's (eta M = 2) reaches about half of P/M by t = 20 as in core's test 1b, the members' (eta m = 0.1) is not predicted; binary separation 3.0 +- 0.3 to t = 40; no non-finite values |
| R3 | rest of the q = 10 passage | the same chain continued with `time/tlim=250` | 29 card-hours | separation of the binary near t = 80 (pericentre plus the gauge lag); m1 leaves, m2 bound or plunging; burst at R = 48 near t = 130 |
| R3' | alternative: the q = 4 passage | `inputs/hills_q4_m8.athinput` | 15 card-hours | as R1 + R3 for q = 4; burst near t = 150 at R = 48 |

Order and budget [JUDGEMENT]: R0 (free), R2 and R4 (2 card-hours), then R1 (9.5). With
the 40 card-hours of decision 0006 the lead can then either complete q = 10 (R3, 29;
total 40.5, the whole allotment, no resolution check) or run the q = 4 passage (R3',
15; total 27) and keep 13 for a second phase or resolution check at q = 4. The G1
criterion of the track sheet ("constraint residuals and junk radiation of the
three-puncture data are quantified; one complete vacuum passage is done") is met by
R0 + R2 + (R1 + R3 or R3'). A q = 10 scan line at G3 needs a larger allotment (to be
asked of the user, decision 0006) or MPI across the two cards.

## 8. Requests to other owners

- core: (1) a pairwise common-horizon trigger in `fastflow` (merger of two of three
  punctures); (2) optional position-dependent shift damping eta(x), if R1 shows the
  members' gauge misbehaving with eta m = 0.1; (3) optional ADM surface integrals;
  (4) note for the interface (section 4 "Block count"): the measured trees of
  three-scale configurations are 1.5-2.4 times the "190 leaves per level and hole"
  estimate (runs `-131109-634fb86`, `-131348-634fb86`); (5) confirm the card memory at
  `max_nmb_per_rank = 2700` with three finders.
- kb: the locator of the quadrupole energy of a parabolic flyby (formula used here as
  BACKGROUND); literature on gauge choices for punctures of mass ratio 10-20 (variable
  eta); published junk energies of boosted Bowen-York punctures against P/m.
- newton3 (sibling): the functions used (`HillsSetup`, `initial_state`, `scatter`,
  `trajectory`) should stay stable; a driver function "state at radius r0 after
  integrating from 10 r_t" would replace my `state_at_radius`.
- geodesic_binary (sibling): run the two chosen configurations (q = 10, a_b = 3,
  r_p = 8, phase 130; q = 4, a_b = 5, r_p = 9.82, phase 127) in the geodesic-plus-
  Newtonian model: does m2 plunge, and does the separation survive the relativistic
  pericentre?
- F-hills lead: the budget choice of section 7; replace the novelty cost numbers by
  section 4 in the G0 package; the first configuration is r_p = 8, not 6.

## 9. Risks and open items

- Gauge lag of the trackers (eta m = 0.1 for the members) may distort the coordinate
  trajectories for tens of M; calibration R4. [JUDGEMENT]
- The AMR evolution may hold more MeshBlocks than the t = 0 trees (+11 percent in core's
  run): 2332 x 1.11 = 2590, inside 2700, outside 2400.
- m/8 is a scouting resolution: core saw the member horizon masses scatter by 1 percent
  in the first 2.5 M and the constraint norm rise 600 times at m/8 (test 3). No
  convergence test of q = 10 fits one card.
- The Newtonian start state is not a relativistic parabola; outcome comparisons must
  start the models from the NR state.
- The binary's own conformal-flatness junk has not been estimated.
