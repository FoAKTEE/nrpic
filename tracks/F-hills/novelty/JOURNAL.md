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
