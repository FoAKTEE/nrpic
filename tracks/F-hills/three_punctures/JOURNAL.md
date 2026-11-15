# JOURNAL of the F-hills package three_punctures (F-pre-3 and F-pre-4: plan)

Helper of F-hills, one work package. Entries are appended; nothing is rewritten.
Units G = c = 1, lengths and times in units of the bare mass M of the large black hole
unless said otherwise. Labels: [VERIFIED] read in a source at the locator given or
measured in a registered run; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 2026-11-15 what I read, before any test

- Rules, charter to "Owners", decisions 0005, 0006, 0010; brief lines 30-68, 267-278,
  466-492, 548-552, 804-822, 834-860.
- Source on `main`: `athenak/src/pgen/nrpic/nrpic_cf.cpp` (punctures at rest, K_ij = 0),
  `pgen/tests/z4c_boosted_puncture.cpp`, `pgen/z4c/two_punctures/` (wrapper of the
  outside TwoPunctures library, not usable: decision 0010), `z4c/compact_object_tracker.cpp`
  (tracker output columns iter, time, x, y, z, vx, vy, vz, line 87),
  `z4c/fastflow.cpp` (summary columns mass, Sx, Sy, Sz, S, area, hrms, hmean, radii,
  lines 260-261; common-horizon trigger `PuncAreClose` = largest distance between ALL
  `npunct` punctures below `merger_distance` times their summed mass, lines 1529-1612),
  `z4c/z4c_wave_extr.cpp` (r psi4 modes l = 2..8 on spheres about the origin; the
  sphere centre is the origin, `geodesic-grid/spherical_grid.cpp` lines 75-77; the
  factor r is applied in `z4c_calculate_weyl_scalars.cpp` lines 409-410),
  `z4c/z4c_amr.cpp` (tracker and radius criteria), `outputs/history.cpp` lines 176-250
  (constraint norms, masked by chi >= excise_chi), `z4c/z4c_newdt.cpp` lines 45-58 and
  `mesh/mesh.cpp` lines 595-666 (one global time step set by the finest cell: no
  subcycling in time), `z4c/z4c_calcrhs.cpp` line 716 (constant shift damping eta).
- Branch `core/multi-puncture` (git show, not built or run by me): interface
  `tracks/core/interfaces/multi_puncture.md`, journal `tracks/core/JOURNAL-mp.md`
  (tests R, 1a, 1b, 2, 3; the three-black-hole scouting run
  `core-20261115-120834-d08c476`).
- Measured cost of the two-black-hole runs: `notes/results_brief_selfgravity.md` part D;
  chain logs of `runs/jeans/n1e4_v20` (15 segments of 1500 s, 7.3e6 to 8.1e6
  zone-cycles per second); the novelty helper's cost runs
  (`tracks/F-hills/novelty/JOURNAL.md`, runs `F-hills-20261115-045435-f62d553`,
  `-045438-f62d553`), which re-derived the scale estimate of brief line 275 and built a
  block-count model that is a JUDGEMENT (not measured).
- Sources fetched with the helper (read only): 0710.0879v2 `first.tex`, 1004.1353v2
  `Punc_N.tex`; read from kb-data: 0711.1165v2 `second.tex`, 0911.1136v1 `prp.tex`,
  2505.03934v2 `apssamp.tex`.
- The newton3 driver `tracks/F-hills/newton3/hills3/threebody.py` (sibling helper,
  work in progress): `initial_state` places an unperturbed binary at distance r0 on the
  incoming parabola; `trajectory` integrates with SciPy DOP853.

## 2026-11-15 predictions, written before the three analysis runs

Fiducial configuration (the novelty helper's, so that the track uses one): M = 1,
m1 = m2 = 0.05 (q = M/m_b = 10), circular binary a_b = 3 (30 r_gb), coplanar prograde,
parabolic centre-of-mass orbit with Newtonian pericentre r_p = 6 (D = r_p/r_t = 0.93,
r_t = a_b q^(1/3) = 6.46), start r0 = 4 r_t = 25.8.

**T2. Newtonian outcome and start state (newton3 driver, analysis on processors).**
 (a) Coplanar prograde at D = 0.93: the binary is disrupted for more than half of the
     binary phases; 0911.1136 `prp.tex` lines 846-847 give disruption up to D = 2.1
     prograde, so D = 0.93 is well inside [JUDGEMENT on the fraction]. Refuted if fewer
     than half of 360 phases end disrupted.
 (b) For a sizeable fraction of phases (at least a tenth) one member comes closer to M
     than 4 M (the marginally bound radius of Schwarzschild in areal radius; Newtonian
     distance used as a proxy), because a_b/2 = 1.5 is a quarter of r_p. This would make
     the fiducial a poor first run [JUDGEMENT]. Refuted if every phase keeps both members
     beyond 4.5 M.
 (c) The start from an unperturbed circular binary at r0 = 4 r_t against the state
     reached by integrating from 10 r_t (0911.1136 `prp.tex` line 599): at 4 r_t the
     binary separation differs from a_b by less than 5 percent and its eccentricity is
     below 0.05; the outcome class is the same for at least 80 percent of phases when the
     effective phase is held fixed. Refuted otherwise; then the initial data must be taken
     from the integrated state, not from `initial_state` at r0.
 (d) Barycentric momenta of the start state: |P| of each light member 0.012 to 0.020
     (binary centre-of-mass speed sqrt(2 * 1.1/25.8) M/(M+m_b) = 0.27 plus the internal
     speed 0.09), heavy hole |P| = 0.027 to 0.030. Refuted outside these ranges (that
     would be an error in my reading of the driver's frame).

**T3. MeshBlock count at t = 0 (main processor executable with `-m`, no evolution).**
 (a) Emulating what `puncture_setup` writes (cubes of half-width `puncture_radius` m at
     level `puncture_level - round(log2(m/m_min))`, from the source of
     `nrpic_puncture_setup.hpp` lines 115-141 on `core/multi-puncture`) for core's
     `by_triple.athinput` reproduces core's 1100 MeshBlocks at the start exactly.
     Refuted by any difference; that would mean my emulation is wrong and the counts
     below are not those of the real set-up.
 (b) The fiducial start state with light holes at m/8 (domain +-409.6, root cells 12.8,
     finest level 11), heavy hole at M/10 (level 7), and a wave zone of cells 1.6 within
     about 77 of the origin: 1500 to 2600 MeshBlocks. Refuted outside 1200 to 3000.
 (c) Each halving of the finest cells (m/16, m/32) adds 300 to 450 MeshBlocks (two light
     holes, about 190 leaves per level each when off the block corners, core interface
     note section 4; at t = 0 the punctures may sit nearer the 2x2x2 state, so fewer).

**T4. Junk radiation and constraint violation of Bowen-York data (analysis of core's
card runs 1b, read only: `scratch/core/core-20261115-121046-0c197fb` (A, m = 1,
P = 0.3, closed-form correction), `-121049-` (B, same, no correction), `-121047-` (C,
stock boosted Schwarzschild slice, velocity 0.2844), `-121050-` (E, P = 0.043,
S = 0.3), extraction at r = 10 and 14).**
 (a) Radiated energy of the first pulse (t < 30 at r = 14), from the l = 2..8 modes of
     r psi4 integrated twice in time: B (no correction) larger than A by more than a
     factor 2; C, the exact boosted slice, smaller than A by more than a factor 3
     (its pulse is gauge and near-zone content, no junk of conformal flatness).
     Refuted if B <= A or C >= A.
 (b) A: energy of the first pulse between 1e-6 and 1e-3 of m [JUDGEMENT; no source].
 (c) Hamiltonian-constraint norm (history) at t = 0: B larger than A by a factor near
     1/0.040 = 25 in the closed form of core's test 1a(iv) on the cells it uses, but less
     in the code's norm because truncation error at the puncture adds to both (core saw
     this in test 3). Refuted if B <= A at t = 0.
 What I take from T4 for the plan: the junk energy per unit mass of a light member with
 P/m = 0.3 and of the heavy hole, scaled to the fiducial masses, against the
 quadrupole energy of the passage.

Amendment to T2 (d), written before the run, after redoing the arithmetic: the member
momenta depend on the binary phase. Centre-of-mass speed 0.292 M/(M+m_b) = 0.266 and
internal speed 0.091 per member give |P| between 0.0087 and 0.0179 for a member and
0.0266 for the heavy hole. The range 0.012 to 0.020 above is wrong at its lower end; the
test is now: members inside [0.0087, 0.0179], heavy hole 0.0266 +- 0.0005.

## 2026-11-15 outcome of T2, run `F-hills-20261115-130342-0471114` (newton3 driver, 145 s)

Figure `figures/fig_newton_phase.png` (looked at; the E1 panel of the third column is
dominated by two near-collision spikes of 8e5, axis clipped in the rerun). 360 phases per
configuration, coplanar prograde, start 4 r_t and 10 r_t, end at 30 r_t outbound.
 - (a) held: fiducial (a_b = 3, r_p = 6, D = 0.93) disrupted in 0.928 (start 4 r_t) and
   0.911 (10 r_t) of the phases; every disruption is a single ejection (m1 or m2; no
   "both bound", no "both free").
 - (b) held, more strongly than predicted: in the fiducial one member passes closer than
   4 M to M (Newtonian distance) in 0.867 (4 r_t) and 0.778 (10 r_t) of the phases; the
   window of clean single ejections with both members beyond 4.5 M and the same outcome
   from both starts is 4 phases wide. The novelty helper's fiducial (a_b = 30 r_gb,
   r_p = 6 r_g) is therefore a plunge-dominated encounter, not a clean first run.
   The Newtonian problem is scale free at fixed D: a_b = 4, r_p = 8 gives the same
   outcomes and energies with distances times 4/3, still 0.533 of phases below 4 M.
   a_b = 3, r_p = 8 (D = 1.24): disrupted 0.878 / 0.839, below 4 M only 0.050 (near the
   two narrow near-collision windows), clean window 45 phases (115 to 160 deg), 128
   clean phases in all. Two phases end "unsettled" with a near collision of the members
   (point masses; energy error 0.24 there; elsewhere below 3e-3).
 - (c) held at the margin: the outcome class agrees between the two starts for 0.839
   (D = 0.93) and 0.806 (D = 1.24) of the phases (threshold 0.80; the differences sit at
   the boundaries between classes); median |dE| difference 0.05 to 0.07 units. Binary
   at 4 r_t when integrated from 10 r_t: separation within 2.6 percent of a_b,
   eccentricity at most 0.044 (36 phases).
 - (d) checked on the smoke test of the driver (fiducial, phase 0, 8 phases, not
   registered) and in this run: heavy |P| = 0.0265 at r0 = 25.85 (fiducial) and 0.0230
   at r0 = 34.5 (wide); member |P| 0.0092 and 0.0176 (fiducial, phase 0), 0.0117 and
   0.0126 (wide, 106 deg): inside the amended range.
 Choice [JUDGEMENT]: the first configuration is a_b = 3 M (30 r_gb), r_p = 8 M
 (D = 1.24), coplanar prograde, phase 130 deg (inside the 45-degree clean window; m1
 ejected with E1 = +1.78 / +1.75 units and m2 captured with E2 = -1.84 / -1.85 from the
 4 r_t / 10 r_t starts; closest approach of the captured member 5.5 / 5.6 M). The run
 picked "wide" at 106 deg automatically (its rule looked only at fid and wide); a rerun
 with the choice fixed writes the start state and the Newtonian track for the mesh test.

Prediction for the rerun (same code, `--choose far 130`): scan numbers identical to the
first run (deterministic); the chosen state has |P_heavy| = 0.0266 (r0 = 4 r_t = 25.85),
member momenta inside [0.0087, 0.0179], total momentum zero to 1e-15.

## 2026-11-15 outcome of the T2 rerun, run `F-hills-20261115-130755-982aba0` (128 s)

Prediction held: scan numbers identical to the first run; chosen state (a_b = 3,
r_p = 8, phase 130 deg, start 10 r_t read at 4 r_t = 25.85, t = -79.5 before the
unperturbed pericentre): |P| = 0.02652 (M), 0.01423 (m1), 0.01386 (m2), total momentum
1e-17; binary separation 3.036, eccentricity 0.029 there. Figure
`figures/fig_newton_choice.png` looked at: m2 is captured on an orbit between 5.6 and
9.3 M from M (Newtonian; period about 100 M), m1 leaves along +y; the heavy hole recoils
along -y; the members come within 2.2 M of each other near the pericentre.

Prediction for T3 part C, added before the mesh run: along the Newtonian passage the
count changes by less than a factor 1.5 between its smallest and largest value; the
largest count comes after the separation (the members' regions split at the coarser
levels), not at the pericentre.

## 2026-11-15 outcome of T3, run `F-hills-20261115-131109-634fb86` (7 s, processors)

Figure `figures/fig_mesh_count.png` looked at.
 - (a) held: the emulation of `puncture_setup` gives 1100 MeshBlocks for core's
   by_triple, the number core reports at the start of `core-20261115-120834-d08c476`.
   [VERIFIED] So the counts below are those the real set-up would build at t = 0.
 - (b) held for the punctures alone, FAILED with the wave zone as I wrote it: start
   state at m/8 (domain +-409.6, 12 levels, heavy at M/10 within 1.8 M, light holes
   within 1.8 m): 1954 MeshBlocks; with the wave zone as two cubes (cells 1.6 within
   +-64, 3.2 within +-128) 2836, above the predicted 1500-2600 and above the card limit.
   The cubes are rounded outward to whole blocks and padded by the 2:1 rule at the
   coarse levels (448, 448, 490 blocks on levels 1-3 against 154 each without them).
   The evolution refines the wave zone by spheres (`z4c_amr` radius criterion: a block
   is refined when one of its corners lies inside the radius, `z4c_amr.cpp` lines
   348-366), not by cubes; the count must be redone with that rule.
 - (c) FAILED: halving the finest cells adds 2058 (m/16: 4012) and then 5460 (m/32:
   9472) MeshBlocks, not 300-450. With the radii fixed in units of the masses, each
   halving multiplies the finest-level blocks by up to 8 (m/32: 1440 on level 13), and
   the heavy hole, whose level follows the lightest (`level = L_f - round(log2 20)`),
   gets cells of M/20 and M/40 within 1.8 M (508 and 1944 blocks on its finest level).
   My prediction counted levels, not volumes.
 - Track prediction (C) held: along the Newtonian passage 2598 to 3298 (m/8, cube wave
   zone) and 4222 to 5104 (m/16): ratio 1.27 and 1.21; the largest counts come 50 to
   160 M after the pericentre (the members apart), the smallest at the pericentre.

Predictions for T3b (written before it runs): wave zone emulated with the corner rule
of the radius criterion (cells 1.6 within 48, cells 3.2 within 100 of the origin);
domains +-409.6 (root cells 12.8) and +-204.8 (root cells 6.4, one level fewer for the
same finest cells); puncture radii 1.8 (as core) and 1.2 (in units of each mass).
 - The spherical wave zone adds at most 300 MeshBlocks at m/8 (cubes added 882).
 - The smaller domain saves 100 to 200 MeshBlocks at the same finest cells.
 - m/8, +-204.8, radii 1.8, with the wave zone: 1800 to 2300 at the start and below
   2600 along the passage. Refuted above 2600 at the start.
 - m/16, +-204.8: radii 1.8 3500 to 4500; radii 1.2 2500 to 3200.

## 2026-11-15 outcome of T3b, run `F-hills-20261115-131348-634fb86` (8 s, processors)

Figure `figures/fig_mesh_count_b.png` looked at.
 - Spherical wave zone, at most 300 more MeshBlocks: held, and stronger: it adds none.
   The corner rule turns "cells 1.6 within 48" into the cube +-51.2 and "cells 3.2 within
   100" into the cube +-102.4, and both lie inside the 2:1 padding that the three
   punctures' nesting already puts at those levels (count identical with and without, all
   six cases). Extraction spheres up to R = 48 (cells 1.6) and R = 100 (cells 3.2) cost
   nothing extra at the start.
 - Smaller domain saves 100-200: held at m/8 (1954 -> 1800); at m/16 it saves 322.
 - m/8, +-204.8, radii 1.8: 1800 at the start (held), largest along the passage 2332,
   mean 2006 (held, below 2600 and below the card limit 2400).
 - m/16: radii 1.8 3690 (held), radii 1.2 2654 (held); along the passage the m/16 runs
   reach 4544 and 2934: neither fits one card (block limit about 2400, core's test 3).
 Cost of one passage (240 M from 4 r_t to 160 M after the pericentre; dt = 0.25 h; vacuum
 rate 2201 MeshBlock-cycles/s, range 2022-2310, novelty run -045438-f62d553):
 m/8 radii 1.8: 38.9 card-hours (37.0-42.3); radii 1.2: 36.9; m/16 radii 1.2: 99
 (not on one card); m/16 radii 1.8: 156; m/32 (9472 MeshBlocks at the start on +-409.6)
 cannot run on one card at all.
 Against the novelty helper's model (23.6 / 60.9 / 149 card-hours at m/8 / m/16 / m/32,
 with 1313 / 1693 / 2073 MeshBlocks taken as a JUDGEMENT from core's interface note):
 the measured tree has 1.5 (m/8) to 2.4 (m/16) times more MeshBlocks, and the m/32 case
 does not fit a card. The F-hills allotment (40 card-hours, decision 0006) buys one
 passage at m/8 and nothing else.

## 2026-11-15 outcome of T4, run `F-hills-20261115-131605-634fb86` (2 s, processors)

Figure `figures/fig_junk.png` looked at. Core's single-hole card runs of test 1b, read
only; the extraction spheres (r = 10, 14) are close to a hole that starts at x = -4 and
moves toward +x, so what they record is not clean radiation.
 - (a) "B larger than A by more than a factor 2": FAILED. The r psi4 signals of A
   (closed-form correction) and B (none) are nearly the same: energy in the window
   [r - 6, r + 14] after removing a quadratic background 1.85e-3 (A) and 1.68e-3 (B) of m
   at r = 14, 7.8e-4 and 7.0e-4 at r = 10. "C smaller than A by more than a factor 3":
   held, C (the exact boosted slice) gives 5.7e-6 (r = 14) and 9.1e-5 (r = 10).
   Reading [JUDGEMENT]: the junk of a Bowen-York puncture with P/m = 0.3 comes from
   conformal flatness (the data are not a boosted Schwarzschild slice), which the
   regular correction of the Hamiltonian constraint does not touch; the correction
   changes the mass of the data, not their shape. The signal of A and B at r = 14
   oscillates with a period of about 18 M from t = 10 to the end (t = 40) without
   decaying much (peaks 4.7e-3 and 3.9e-3 at t = 17 and 36), close to the l = 2
   quasinormal period 16.8 M of a unit-mass Schwarzschild hole [BACKGROUND], with the
   hole approaching the sphere: near-zone ringing, not an outgoing pulse.
 - (b) "A between 1e-6 and 1e-3 of m": held at r = 10 (7.8e-4), not at r = 14 (1.8e-3).
   The energy grows with the extraction radius, which a radiated energy does not do: the
   number is near-zone contaminated and serves only as an upper bound, about 2e-3 m.
   A clean junk energy needs spheres at 50 M or more around a hole at the origin
   (requested from core below; not run by me).
 - (c) held once the units are read right: the history holds the squared norm <H^2>.
   At t = 0 <H^2> = 5.52e-12 (A), 2.93e-9 (B), 3.2e-13 (C, truncation only), so the RMS
   ratio B/A is 23 (closed form of core's test 1a(iv): 1/0.040 = 25). By t = 8 all four
   runs sit at the same <H^2>^(1/2) of about 2e-5, set by the evolution near the
   puncture (finest cells m/16): as in core's test 3, the initial violation is not
   visible in the evolved norm at this resolution after the gauge transient.
 - E (P = 0.043, S = 0.3): pulse energy 1.7e-4 (r = 14), 6.3e-5 (r = 10) of m; the spin
   part of Bowen-York data rings as well.
