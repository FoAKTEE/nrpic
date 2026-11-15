# JOURNAL of the F-hills novelty package (F-pre-5 and G0 scoping)

Helper of F-hills, one work package. Entries are appended; nothing is rewritten.

## 2026-11-15 start: predictions before the search and the checks

P1 (novelty search). Expectation, written before any query: the literature has full-NR
evolutions of three black holes (the papers the brief names, arXiv:0710.0879,
0711.1165, 1004.1353, and their followers) but none in the Hills geometry (a bound
binary on a near-parabolic orbit about a heavier black hole, tidally separated), and no
full-NR evolution of a binary of matter clumps passing a black hole. Refuted by any
paper that evolves the Einstein equations (not a fixed background, not a post-Newtonian
or geodesic-plus-Newtonian model) for a bound pair whose centre of mass passes a third,
heavier black hole closely enough that the pair is separated or strongly perturbed.
A near miss that does not refute P1: three equal-mass black holes, or hierarchical
triples whose outer orbit is bound and wide, evolved in NR.

P2 (scale estimate of brief lines 275). Written before the script runs: the closed forms
r_t/r_g = (a_b/r_gb) q^(-2/3), the plunge bound a_b/r_gb > 4 q^(2/3) and the Peters time
(5/64)(a_b/r_gb)^4 G m_b/c^3 follow from r_t = a_b (M/m_b)^(1/3), the marginally bound
radius 4GM/c^2 of Schwarzschild and the Peters (1964) circular-orbit merger time; the
script reproduces the brief's 19, 86, 400 (to the brief's rounding) and 6x10^3 GM/c^3.
Refuted if any closed form differs by more than a rounding (5 percent) from the script,
or if the prefactor of the tidal radius used by the Newtonian references (arXiv:0911.1136)
differs from 1 so that the bound moves by more than 20 percent. Separately, the claim
"few hundred GM/c^3 of one passage" is checked against the Newtonian parabolic time from
a start distance that keeps the binary outside its tidal radius; refuted if the passage
from a sensible start (at least 3 r_t) is longer than 10^3 GM/c^3 for q = 10, a_b = 30.

P3 (compute estimate). Written before the logs are parsed: the M/64 two-black-hole run
`jeans/n1e4_v19` used one card for about six hours for 100 M (13 segments of 25 min in
its chain log). Refuted if the chain log gives more than 8 or fewer than 4 card-hours.

## 2026-11-15 predictions for the two analysis runs (written before they ran)

Run A, `scripts/scale_estimate.py` (re-derivation of brief line 275):
- A1. Plunge bound 4 q^(2/3): 18.57, 86.18, 400.0 for q = 10, 100, 1000 (the brief's 19, 86,
  400 are these rounded). Refuted by any difference beyond rounding.
- A2. Numerical root of V = 1, V' = 0 (Schwarzschild, E = 1) gives r_mb = 4.0000, L = 4.0000;
  the Kerr equatorial roots agree with 2 -+ a + 2 sqrt(1 -+ a) to 1e-8 for 0 <= a <= 0.99.
  Refuted by a difference above 1e-6.
- A3. Peters time for a_b = 30 r_gb, q = 10: 6328 GM/c^3 closed form, the quadrature equal to
  1e-8; the brief's "about 6x10^3" holds.
- A4. The Schwarzschild parabolic coordinate time tends to the Newtonian one for r_p >> M
  (ratio within 2 percent at r_p = 1000 M); for the fiducial q = 10, a_b = 30 r_gb,
  r_p = 6 r_g, from r0 = 4 r_t (26 r_g) the in-and-out time is 150 to 300 GM/c^3, i.e.
  "a few hundred" holds only for starts within about 5 r_t. Refuted if the time from
  r0 = 4 r_t exceeds 400 GM/c^3.
- A5. The 8:1:1 and 18:1:1 configurations of 2406.11985 sit at D/r_t of 4 to 6 (outside the
  Newtonian disruption range D < 2.1 of 1804.02911): they are not Hills encounters.
  (By hand before the script: 4.1 and 5.8.) Refuted if D/r_t < 2.1 for either.

Run B, `scripts/compute_estimate.py` (cost):
- B1 (= P3). n1e4_v19 used 4 to 8 card-hours for 100 M.
- B2. Vacuum MeshBlock-cycle rate of the four vacuum puncture runs and core's three-BH run
  lies within 1800 to 2400 per second (16^3 blocks, one A100). Refuted if any is outside
  1500 to 2600.
- B3. The cost model N_MB * T / (cfl h_min) / R reproduces core's measured 0.159 card-hours
  of test 3 to 10 percent when fed its own block count and rate (consistency, not a
  prediction of physics).
- B4. One vacuum passage at q = 10, a_b = 30 r_gb, r_p = 6 r_g, from r0 = 4 r_t, cells m/8 at
  the light holes: 15 to 40 card-hours; at m/32 above 100 card-hours. Refuted if m/8 is
  below 5 or above 80 card-hours.

## 2026-11-15 outcomes of runs A and B

Run A, final `F-hills-20261115-045435-f62d553` (results copied to
`results/scale_F-hills-20261115-045435-f62d553.json`; figures `figures/fig_scale_plane.png`,
`fig_rmb_check.png`, `fig_pdis_q10.png`, all looked at). Earlier attempts on record: `-045124-ae6bca8`
FAILED at import (`python3 -I` hides the user site-packages that hold numpy; the analysis
scripts read only repository files, so they run without -I; the INSPIRE scripts that read
downloads keep -I); `-045332-ae6bca8` and `-045407-bf52f4e` superseded (same numbers, legends
redrawn).
- A1 held: 18.566, 86.177, 400.000 for q = 10, 100, 1000; the brief's 19, 86, 400 are these
  rounded. [VERIFIED]
- A2 held: Schwarzschild root r_mb = 4.000000000000001, L = 4.0; Kerr roots against the
  closed form, largest difference 1.8e-15 (prograde) and 5.3e-15 (retrograde) over
  0 <= a <= 0.99. The isotropic radius of r_mb is 2.914 M. [VERIFIED]
- A3 held: 6328.125 GM/c^3 closed form and quadrature. [VERIFIED]
- A4 held: Schwarzschild over Newton 1.0156, 1.0038, 1.00075 at r_p = 50, 200, 1000 M. For
  q = 10, a_b = 30 r_gb (r_t = 6.46 r_g), r_p = 6 r_g: in-and-out coordinate time 163, 223,
  285 GM/c^3 from r0 = 3, 4, 5 r_t (Newtonian in-time 54, 80, 107: the relativistic passage
  is 40 to 50 percent longer). The binary period is 103 GM/c^3, so the binary turns about
  twice during the passage. "A few hundred GM/c^3" holds for starts within 5 r_t.
- A5 held: 2406.11985 8:1:1 at D/r_t = 4.12, 18:1:1 at 5.81 (q = 4.00 and 9.00,
  a_b = 9.90 r_gb). New observation (not predicted): their a_b of 9.9 r_gb lies BELOW the
  Schwarzschild plunge bound for both (10.1 at q = 4, 17.3 at q = 9): such binaries could
  not be separated by any parabolic passage before plunging. The same holds for core's
  scouting input `by_triple.athinput` (q = 10, a_b = 10 r_gb, bound 18.6; Newtonian
  r_p = 3 r_g < 4 r_g): it tests the machinery, not a Hills encounter.
- Correction to the brief (not predicted): the box "q = 10-30, a_b = 20-60 r_gb" of line 275
  is not all above the plunge bound: at q = 30 separation needs a_b >= 38.6 r_gb, at q = 20
  29.5 r_gb (fig_scale_plane, left: lower right corner of the shaded box under the dashed
  line). [VERIFIED by the closed form; the bound itself assumes r_t = a_b q^(1/3) with
  prefactor 1, which is an order-of-magnitude criterion (2404.16270 article.tex l. 180)]

Run B, final `F-hills-20261115-045438-f62d553` (results `results/cost_...json`, figure
`figures/fig_cost.png`, looked at); `-045410-bf52f4e` superseded (same numbers).
- B1 held: n1e4_v19 used 5.41 card-hours of compute (13 segments, 19475 s), 5.89 h from the
  first submission to the end including queue gaps, for 100 M; peak card memory 79155 MiB.
- B2 held: vacuum rates 2022 to 2310 MeshBlock-cycles per second (median 2201); core's
  three-BH run 2140. n1e4_v19 ran at 1440 to 1950 while the two black holes inspiralled
  with particles, and dropped to 830 to 1150 after the merger with 790 MeshBlocks (cause not
  isolated; candidate: the common-horizon finder, which runs only then).
- B3 held: model 0.1546 card-hours against 0.1588 measured (3 percent).
- B4 held: q = 10, a_b = 30, r_p = 6 r_g, r0 = 4 r_t: 23.6 card-hours at m/8 (25.7 at the
  slowest vacuum rate), 60.9 at m/16, 149 at m/32 (2073 MeshBlocks, under the card limit
  of about 2400). q = 4, a_b = 20 r_gb, r_p = 6 r_g: 11.9, 30.6, 74.9. The block model
  (+380 MeshBlocks per level, +150 for the larger domain) is a JUDGEMENT taken from core's
  interface note (190 leaves per level and hole), not measured for these configurations.
