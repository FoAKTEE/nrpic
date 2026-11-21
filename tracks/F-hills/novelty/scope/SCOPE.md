# Scope of Track F (S12, Hills mechanism) for gate G0

Helper draft for the F-hills lead, 2026-11-15. Sources: brief lines 267-278 (section 3.11),
466-492 (S12), 548-552 (M12), 804-822 (track sheet), 834-860 (section 10); decisions
0005, 0006, 0010; `NOVELTY.md`; runs `F-hills-20261115-045435-f62d553` (scale, "run A"),
`F-hills-20261115-045438-f62d553` (cost, "run B"), `F-hills-20261115-045918-e7d0a66` (cost of
object b, "run C"), whose numbers are in `../results/` and figures in `../figures/`. Labels:
[VERIFIED] (source or run with locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Units
G = c = 1; M is the mass of the large black hole, r_g = M; m_b is the total binary mass,
r_gb = m_b, q = M/m_b; a_b the binary separation; r_t = a_b q^(1/3) the tidal radius
[VERIFIED: 0911.1136 `prp.tex` l. 88; 2404.16270 `article.tex` l. 165-176]; D = r_p/r_t.

## 1. Problem statement

A bound binary on a near-parabolic orbit passes a heavier black hole at a pericentre r_p
of a few r_g, comparable to its tidal radius. Computed in full NR with this repository's
AthenaK (decision 0010): whether the binary is separated, the energy given to the ejected
and to the captured member, the orbit of the captured member, the gravitational-wave
burst, and, for matter members, their stripping and heating. Compared with the
Newtonian three-body reference (F-pre-1) and the "exact Schwarzschild plus Newtonian
self-gravity" model (F-pre-2, arXiv:2404.16270), both as reference solutions of ordinary
differential equations outside the source tree.

Novelty (`NOVELTY.md`): no full-NR Hills encounter with q > 1 and no full-GR matter binary
passing a black hole found on 2026-11-15; closest are 2406.11985 (binary on a bound orbit
about a 4 or 9 times heavier hole, outside r_t) and 2505.03934 (equal-mass
binary-single scattering). The RIT group states the intention to go to 128:1:1
(2406.11985 `TBH3.tex` l. 708-712): the window may be short. [JUDGEMENT]

## 2. Objects (decision 0005, provisional)

| | object | members | needs from core | status of the needs |
|---|---|---|---|---|
| (a) | binary black hole passing a heavier hole, vacuum | two light punctures, one heavy | Bowen-York punctures with momentum and spin, N trackers and finders, approximate correction | built on `core/multi-puncture` (interface `tracks/core/interfaces/multi_puncture.md`), tests 1-3 run, not merged to main [VERIFIED: git log core/multi-puncture] |
| (b) | binary of collisionless clumps passing a heavy puncture | two equilibrium clusters | moving clump initial data with momentum (curvature of a moving clump), the puncture of (a) | design `coord/notes/design_wave2_initial_data.md` sections 3 and item 4 of its list; extrinsic-curvature tables on `core/id-extrinsic` (spherical only) |
| (c) | dressed binary | black holes with dark-matter spikes | Track D's dressed initial data | not started |

Recommendation [JUDGEMENT, for the G0 decision on 0005]: keep (a) as the verification
baseline but do not let it gate (b). Run C finds object (b) about ten times cheaper per
passage than (a) at the coarsest useful resolution (section 7), because the clumps need
no puncture resolution, and (b) is the regime only NRPIC reaches. Order: (a) one
passage (G1), (b) one passage, then the scan lines.

Constraint on (b) found here: the clumps must fit inside the Roche lobe of the binary,
R_c < 0.38 a_b for equal members [BACKGROUND: Eggleton 1983 fit; TO VERIFY]. With
a_b = 30 r_gb and member mass m_b/2 this means compactness m/R_c > 0.044: the clumps are
mildly relativistic clusters (like the least compact stable models of the cluster
sequence, `notes/results_brief_selfgravity.md` part B). A larger a_b relaxes this (0.022
at 60 r_gb) and moves r_t out (12.9 r_g at q = 10), at the price of a longer passage.

## 3. Parameter ranges

| parameter | range | first values | reason |
|---|---|---|---|
| q = M/m_b | 4 to 10 (30 stretch) | 10 (target of the brief), 4 (cheap first line) | brief l. 487, 806; cost (section 7) |
| member mass ratio | 1 | 1 | as 0911.1136 and 2404.16270 scans |
| a_b / r_gb | above the plunge bound r_mb q^(2/3): 10.1 (q = 4), 18.6 (q = 10), 38.6 (q = 30) for a = 0 | 30 at q = 10 (r_t = 6.46 r_g); 20 at q = 4 (r_t = 7.94 r_g) | run A |
| r_p / r_g | r_mb < r_p < 2.1 r_t (Newtonian disruption limit, 1804.02911 `mnras.tex` l. 361) | q = 10, a_b = 30: 4.5, 5, 6, 7, 8.5, 10, 13 (D = 0.70 to 2.0); q = 4, a_b = 20: 4.5, 6, 8, 10, 13, 16 | run A, fig_pdis_q10 |
| binary orientation | coplanar prograde, coplanar retrograde; later inclined 90 degrees | prograde and retrograde | retrograde is more stable [VERIFIED: 0911.1136 l. 740-742]; relativistic effects larger for retrograde [VERIFIED: 2404.16270 l. 475] |
| binary phase at pericentre | one value per run; four values at two r_p for a first probability | one | outcome depends strongly on phase [VERIFIED: 2404.16270 l. 180-182] |
| binary eccentricity | 0 | 0 | |
| spin of the heavy hole | 0; then 0.6 pro/retro (deliverable 5) | 0 | r_mb = 2.66 and 5.13 M at a = 0.6 (run A) |
| start distance r0 | 4 r_t (tidal force 1/64 of the binary's binding at start) | 4 r_t = 26 r_g (q = 10) | trade-off with cost; 0911.1136 uses 10 r_t (l. 599), unaffordable |
| outer boundary | at least r0 + passage light-crossing; wave extraction at 50 to 100 r_g | domain +-200 to +-400 r_g | [JUDGEMENT] |

Definition of r_p in NR [JUDGEMENT]: the pericentre is a parameter of the initial data
(energy E = 1 and angular momentum L of the centre-of-mass geodesic in Schwarzschild,
L^2 = 2 r_p^2/(r_p - 2M)), not a measured coordinate distance; the minimum coordinate
separation of the trackers is reported as a gauge-dependent diagnostic. The momenta of
the Bowen-York punctures are set from these E and L in the frame of zero total momentum,
as core did for its scouting input `by_triple.athinput` (header l. 1-8, Newtonian there).

## 4. The scale estimate of brief line 275, re-derived and checked (run A)

- r_t/r_g = (a_b/r_gb) q^(-2/3): follows from the definition (difference 4e-15). [VERIFIED]
- Plunge bound: a parabolic Schwarzschild orbit with pericentre below r_mb plunges;
  numerical root of V = 1, V' = 0 gives r_mb = 4.000000 M (L = 4); separation before the
  plunge needs r_t > r_mb, i.e. a_b/r_gb > 4 q^(2/3) = 18.57, 86.18, 400.0 for q = 10,
  100, 1000: the brief's 19, 86, 400 are right. [VERIFIED; figures fig_scale_plane,
  fig_rmb_check] With spin the bound becomes r_mb(a) q^(2/3) with
  r_mb = 2 -+ a + 2 sqrt(1 -+ a) (numerical roots agree to 5e-15): at q = 10, a = 0.9,
  8.0 (prograde) to 26.3 (retrograde).
- The bound is an order-of-magnitude criterion: r_t carries no exact prefactor
  (2404.16270 l. 180), disruption extends to D = 2.1 in the Newtonian restricted problem
  (1804.02911 l. 361), and the members themselves pass at r_p +- a_b/2. [JUDGEMENT]
- Correction: "full NR can reach q = 10-30 and a_b = 20-60 r_gb: the separation happens at
  a few r_g" holds only above the plunge bound; at q = 30 separation needs a_b >= 38.6,
  at q = 20 a_b >= 29.5 (lower right corner of the shaded box in fig_scale_plane). The
  published NR configurations 2406.11985 (a_b = 9.9 r_gb at q = 4 and 9) and core's
  scouting input (a_b = 10 r_gb, q = 10, Newtonian r_p = 3 r_g) lie below the bound.
- Peters time (5/64)(a_b/r_gb)^4 m_b = 6328 GM/c^3 for a_b = 30, q = 10 (closed form and
  quadrature equal): "about 6x10^3" right. [VERIFIED]
- "A few hundred GM/c^3 of one passage": the Schwarzschild parabolic coordinate time in
  and out from r0 = 3, 4, 5 r_t to r_p = 6 r_g is 163, 223, 285 GM/c^3 for q = 10,
  a_b = 30 (40 to 50 percent longer than Newtonian). Right for starts within 5 r_t. The
  binary period is 103 GM/c^3: the binary turns about twice during the passage, and
  Peters/passage = 28, so it survives until the encounter. [VERIFIED]
- Speeds: v_b = (a_b/r_gb)^(-1/2) = 0.18 c and v_ej ~ v_b q^(1/6) = 0.27 c at q = 10,
  a_b = 30 [BACKGROUND scaling, 0911.1136 prp.tex:106-110 (corrected 2026-11-21, lead, after
  coord/BRIEF_ERRATA.md row 2.81); prefactor taken as 1; kb's reading of Hills' numbers gives
  1.10-1.35, i.e. 0.30-0.36 c (run kb-20261119-153659-4688c5b) TO VERIFY]: the ejected member is relativistic;
  the energy split is not a small correction to the Newtonian one. [JUDGEMENT]
- The restricted three-body approximation behind the Newtonian scalings needs
  (M/m)^(1/3) >> 1 [VERIFIED: 0911.1136 l. 138-139]; at q = 10 it is 2.15. The Newtonian
  reference of F-pre-1 must therefore be the full three-body problem at the actual q, with
  the restricted results (0911.1136, 1804.02911) as its q -> infinity check. [JUDGEMENT]
  The same holds for HRNA, whose validity needs the binary small against the curvature
  radius (2404.16270 l. 272): at q = 10 the binary (3 r_g) is half the pericentre
  distance, so HRNA is a frame of comparison, not a truth.

## 5. Exit criteria

G0 (this package plus the lead): `NOVELTY.md` with verdict and limits; this scope with
parameters, tests and compute; decision 0005 confirmed or changed; compute request
(section 7) put to the orchestrator.

G1 (track sheet l. 818, made concrete) [JUDGEMENT on the numbers]:
1. F-pre-1: the Newtonian three-body reference reproduces the disruption probability fit
   of 1804.02911 (l. 371-375) within the binomial error of its sample at D = 0.25, 0.5, 1,
   1.5, 2 in the large-q limit (q >= 10^6), and the energy scale (G m1 m2/a)(M/m)^(1/3)
   (0911.1136 l. 106, 353) to a few percent in its slope with q.
2. F-pre-2: HRNA reproduces the separation fraction and ejection-speed curves of
   2404.16270 for its parameters (m_b = 1e-6 M, a_0 = 1.013 r_g, l. 317-318).
3. Three-puncture data at t = 0: Hamiltonian residual against the closed form (core test
   3 did this for its scouting input: factor 2.65 below the uncorrected data in the code's
   norm [VERIFIED: core/multi-puncture JOURNAL-mp.md l. 308-330]); junk energy through a
   sphere at 50 r_g quantified for the fiducial input.
4. One complete vacuum passage at q = 4 or 10 (cells m/8 at least): all three horizons
   found in every search, trackers followed until the members are back at r0, outcome
   (separated or not) stated with the constraint norm and the energy budget.

G2: at D >= 2 (r_p >= 13 r_g for q = 10, a_b = 30) the NR binary survives as both
references predict, and its change of internal energy agrees with HRNA within the
difference between two resolutions; convergence at three resolutions for one r_p; for
(b), the numerical relaxation time of an isolated clump at least ten times the passage
time (223 GM/c^3 at q = 10), measured on the clump alone.

G3: three resolutions on the two scan lines of section 3 (one for (a), one for (b)),
with the separation boundary in r_p, the energy split and the waveform.

## 6. Test plan, mapped to the rows of brief section 10 held by Track F (l. 857-859)

| row of section 10 | reference | test | figure | where |
|---|---|---|---|---|
| Hills scattering in the restricted three-body problem | 0911.1136, 1804.02911 | P_dis(D) against the fit (l. 373-374) at large q; energy scaling with q; then the same at q = 4, 10 with the full three-body integrator (the actual reference for NR) | P_dis(D) with the fit; energy versus D | F-pre-1, ODE reference outside the source tree |
| Geodesic binary passing a Schwarzschild black hole | 2404.16270 | separation fraction and v_inf of their scans; then HRNA run at the exact (E, L, a_b, phase) of every NR run | their two curves overlaid; per-run trajectories NR against HRNA | F-pre-2, ODE reference |
| Three-puncture vacuum evolution | 0710.0879, 1004.1353 (and 2406.11985) | (i) t = 0 residual against the closed form (core's test 3); (ii) a published configuration re-run: 2406.11985 `3BH1q1` (equal masses, inner merger at 945.66 m, 6.51 orbits, `merger_times_massratio_table.tex`) and, if affordable, `3BH1q8` (1461.25 m) with their tabulated positions and momenta (`massratio_table.tex` l. 9-30); tolerance 10 percent in merger time because the initial data differ (their hybrid TwoPunctures against our approximate correction) [JUDGEMENT]; (iii) one Hills passage | H-norm history; tracker paths; inner separation versus time against their figure | NR runs on the cards, input written by F, code by core |
| (added) two-body limit | the binary alone | the fiducial binary without the heavy hole for the same time: eccentricity and separation drift that the heavy hole's effect must exceed | separation versus time | NR |
| (added) single-member limit | Schwarzschild geodesic | one light puncture on the fiducial parabolic orbit: deflection angle and pericentre time against the geodesic (checks the E, L mapping and the gauge reading of r_p) | trajectory against geodesic | NR |
| (added) clump in isolation (object b) | equilibrium model | relaxation time of one clump on the passage mesh (G2) | central density and Lagrangian radii versus time | NR with particles |

Estimated card-hours of the added NR tests at q = 10, m/8: two-body limit and
single-member limit about 16 each (about 900 MeshBlocks), 3BH1q1 about 15 at m/16 of
its members [JUDGEMENT: cost model of run B with R = 2201, N_MB = 1000, T = 945.66 x 2/3
= 630 M, h = (1/3)/16].

## 7. Compute estimate (runs B and C)

Measured [VERIFIED, run B]: the two-black-hole run of part D (`jeans/n1e4_v19`, cells
M/64, 8 levels, 790 to 1945 MeshBlocks of 16^3) used 5.41 card-hours of compute for 100 M
(13 chained segments, 5.89 h wall including queue), peak card memory 79155 MiB. Vacuum
puncture runs of this repository and core's three-black-hole run reach 2022 to 2310
MeshBlock-cycles per second on one A100; n1e4_v19 reached 1440 to 1950 with black holes
and particles, 830 to 1150 after the merger. AthenaK takes one global time step
(dt = cfl x smallest cell; `athenak/src/mesh/mesh.cpp` l. 595-666, `z4c/z4c_newdt.cpp`
l. 45-58), so cost = N_MB x T/(cfl h_min)/R. The model reproduces core's measured
three-black-hole run (0.155 against 0.159 card-hours). Card memory limits a run to about
2400 MeshBlocks (26 MB per slot, core JOURNAL-mp l. 331-333).

| case (T from r0 = 4 r_t, in and out) | cells at light members | MeshBlocks [JUDGEMENT] | card-hours |
|---|---|---|---|
| (a) q = 10, a_b = 30, r_p = 6 r_g, T = 223 | m/8 | 1313 | 23.6 |
| same | m/16 | 1693 | 60.9 |
| same | m/32 | 2073 | 149 |
| (a) q = 4, a_b = 20, r_p = 6 r_g, T = 280 | m/8, m/16, m/32 | 1313 to 2073 | 11.9, 30.6, 74.9 |
| (b) q = 10, clumps R_c = 1 M, 2e5 particles | R_c/16, R_c/32 (heavy hole M/16) | 1000 | 1.84, 3.67 |
| (b) same, 2e6 particles | R_c/16 | 1000 | 2.20 |

If (b) needs the cells of the verified cluster runs (M/2 to M/4 of the cluster mass,
part B l. 78), i.e. M/40 to M/80 here, a passage costs 4 to 9 card-hours. [JUDGEMENT]

Programme totals (q = 10, m/8 unless stated): G1, one vacuum passage, 24; G2, one r_p at
m/8, m/16, m/32, 234; one scan line of 6 r_p x 2 orientations x 1 phase, 283; with 4
phases, 1133 card-hours. The allotment of F to its next gate is 40 GPU-hours (decision
0006). So: G1 fits (one passage of (a), one of (b), the t = 0 checks); G2 and G3 do not,
by a factor of 6 to 30. Raising an allotment is asked of the user (decision 0006).

Ways to cut the cost, to be proposed to core [JUDGEMENT]: (1) larger MeshBlocks: the
smoke benchmark of the stock one-puncture problem on a uniform 256^3 mesh with 128^3
MeshBlocks, four ghost cells and RK4 gives 1.9e7 zone-cycles per second
(`runs/smoke/perf/ng4_256_mb128_rk4`; 2.5e7 to 5e7 with RK3 or two ghost cells) against
8 to 9e6 on the refined 16^3 meshes with RK4 and four ghost cells (run B); 32^3 blocks
near the punctures may recover part of that factor of two; needs a benchmark on the
three-puncture mesh. (2) Subtracting the truncation error of the known
heavy-hole background (East and Pretorius, arXiv:1303.1540 abstract) to coarsen the mesh
around the heavy hole. (3) q = 4 for the first scan line (half the cost). (4) r0 = 3 r_t
(27 percent shorter).

## 8. Risks

| risk | effect | handling |
|---|---|---|
| R1 compute | scan lines need 300 to 1100 card-hours against 40 | ask for the allotment at G0; object (b) first; q = 4; section 7 cuts |
| R2 resolution of the light holes | m/8 is coarse: core's test 3 saw horizon masses scatter by one percent in the first 2.5 M at m/8 [VERIFIED: JOURNAL-mp l. 507-511]; outcomes near the separation boundary may change with resolution | three resolutions on one r_p (G2); report the boundary as an interval |
| R3 chaos | strong binary-single encounters change outcome under small numerical changes [VERIFIED: 2505.03934 `apssamp.tex` l. 407, 502] | compare distributions over phase, not single outcomes, near the boundary; this multiplies the cost |
| R4 initial data | superposed Bowen-York data violate the Hamiltonian constraint (core: approximate correction lowers the residual 2.65 times in the code's norm); the binary starts out of tidal equilibrium at r0 = 4 r_t; eccentricity from the superposition | quantify at G1 (junk energy, eccentricity of the two-body limit run); constraint solve on the mesh is core's wave-2 item (decision 0010 item 4) |
| R5 heavy-hole gauge | core's test 3: the heavy hole's tracker hardly moved over 1.6 of its masses, candidate cause the shift damping eta = 2 in code units, i.e. 20 in units of the heavy mass [VERIFIED: JOURNAL-mp l. 515-524, cause not tested] | request to core: eta scaled with the local mass, or a tracker test of the heavy hole's recoil |
| R6 gauge-dependent observables | r_p, energies and the capture orbit read from coordinate trajectories | define r_p by the initial data; energies of members from asymptotic speeds and horizon masses after separation; waveform at large radius |
| R7 the comparison frame | at q = 10 neither the restricted Newtonian results nor HRNA are valid (section 4) | full three-body Newtonian and HRNA at the actual q, used as frames, not as truths |
| R8 competition | RIT plans 128:1:1 (2406.11985 l. 708-712); BAM group scatters N black holes (2505.03934) | repeat the citation queries of `search/SEARCH_LOG.md` before each gate |
| R9 clumps (b) | clumps must be mildly relativistic (m/R_c > 0.044 at a_b = 30); numerical relaxation and particle noise during the 223 GM/c^3 passage; tidal compression could trigger collapse | G2 relaxation test; clump compactness chosen with Track C's stability sequence; larger a_b as fallback |
| R10 horizon finders | heavy horizon missed in core's first test 3 (tolerance, fixed); the light horizons at m/8 found in all searches [VERIFIED: JOURNAL-mp l. 437-512] | keep finder checks in every G1 run |

## 9. Not done in this package

No NR run was made; the cost numbers are a model calibrated on measured runs, with the
MeshBlock counts of the Hills meshes as JUDGEMENT. The Roche-lobe factor 0.38 is from
memory (Eggleton 1983) and must be checked. The disruption window uses the restricted
Newtonian fit, which is not valid at q = 10 (section 4); F-pre-1 will replace it.
