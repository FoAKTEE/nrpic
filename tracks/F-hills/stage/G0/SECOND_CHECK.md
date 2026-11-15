# Second check of two results of G0 (F-hills, wave 2)

Helper of F-hills, 2026-11-15. This is an independent check from the artefacts: the lead's
scripts, summaries and figures, the drivers' code, and the paper sources. Their conclusions
were not taken over. Predictions and outcomes are in `JOURNAL.md` (entries 1-4). Code and
figures are in `second_check/`. Every number below carries a run id (outputs under
`/data/haiyangw/nrpic/scratch/F-hills/<run id>/`, manifests under `tracks/F-hills/runs/`) or
a source locator. Labels: [VERIFIED] (run or source at the locator), [JUDGEMENT] (my reading),
[TO VERIFY].

## Summary

1. **Novelty verdict: holds.** I repeated the search on 2026-11-15 between 17:57 and 18:06 UTC
   with my own queries: 31 INSPIRE queries, complete forward-citation lists of 10 papers, and
   6 web searches. I found no full-NR calculation of a binary tidally separated by a heavier
   black hole on a near-parabolic orbit, and no full-GR calculation of a matter binary passing
   a black hole. The search turned up 13 papers that NOVELTY.md does not list; none of them
   changes the verdict. The wording that NOVELTY.md allows ("may be said") stands as written.
   [JUDGEMENT on searches; locators below]
2. **Baseline disagreement at q = 10: neither driver has a defect.** Its qualitative core is
   physical, relativistic capture. Its size at r_p >~ 9 M is set by two properties of the
   geodesic (HRNA) model at the NR release radius. Details:
   - Driver check. My hole-fixed Newton reproduces the lead's V7 numbers to all digits, and
     my full Newton agrees with newton3 within 0.011. My HRNA agrees with V7 within 0.04 and
     with `geodesic_binary/hrna.py` phase by phase (SC1, SC2).
   - Physical capture. Every HRNA capture is a member whose test-particle (E, L) lies inside
     the Schwarzschild capture region. In the Newtonian model, the member left bound at
     r_p = 7-10 M has L = 2.2-3.2 M < sqrt(12) M, an orbit that Schwarzschild does not allow
     (SC4).
   - Model properties at 4 r_t = 25.85 M. (i) 2404's initial binary is Newtonian-circular in
     coordinate time, so under HRNA it starts too wide. (ii) HRNA's pair force gives a moving
     binary a spurious sideways self-acceleration. I found (ii) in this check; it is present
     in hrna.py as well (SC0d).
   - Effect of removing them. With both removed (my diagnostic variant), the HRNA separated
     fraction at r_p = 13/15/17 M drops from 0.94/0.89/0.82 to 0.48/0.23/0.06. The captured
     fraction at r_p = 11-13 M drops from 0.79-0.33 to about 0.1. At r_p = 7-8 M, captures
     stay at 0.82-0.88.
   - Release radius. No HRNA variant is converged in release radius at q = 10 (SC3, SC6).
     The quantitative HRNA numbers in `stage/G1/STATUS.md` (94 percent capture, separation
     at 13 M) should therefore not be used as predictions.
3. **For the passage P1.** Read in GR, the NR start state `hills_q10_m8.athinput` does not
   correspond to "r_p = 8 M". Its CM has E = 0.99925 and L = 4.19 M (test mass, hole frame),
   which puts the GR turning point at r_S = 5.8 M (isotropic 4.7 M). With the total mass, the
   CM lies inside the capture region (SC7). P1 is a capture-boundary encounter in GR, not the
   intended Hills passage at 8 M. Request R1 below.

## Part 1: novelty (F-pre-5)

What was searched (my own queries; generic; INSPIRE only through
`python3 -I harness/bin/nrpic-fetch-arxiv --inspire-query`; records in
`kb-data/meta/inspire/query/`; listed with `second_check/inspire_list.py`, run with
`python3 -I`; the query log with times is `scratch/F-hills/tmp/sc_inspire_*.txt.log`):

- **Forward citations, complete lists** (`refersto:recid:<n>`, 17:57:49-17:58:27 UTC):
  - 2406.11985 (9 citing records)
  - 2505.03934 (8)
  - 2404.16270 (4)
  - 2402.02178 (16)
  - 2308.07365 (11)
  - 2605.20320 (8)
  - 2604.27429 (2)
  - 2605.22525 (1)
  - 1303.1540 (20)
  - 2610.09336 (0)

  The INSPIRE form `refersto:arxiv:<id>` is not understood: it returned 25270 unrelated
  hits (17:57:14). Record ids are needed; NOVELTY.md used them too.
- **Title, abstract and full-text queries** (17:58:41-18:00:08 UTC), among them:
  - binary + SMBH + numerical relativity
  - three-body + black hole + NR or full GR
  - triple, or hierarchical, + black hole + NR
  - full text "Hills mechanism" + "puncture", and "Hills mechanism" + "numerical relativity"
  - full text "binary-single" + "numerical relativity" (85 hits, 25 most recent read)
  - full text "three-body" + "Bowen-York"
  - full text "tidal separation" + BSSN/Z4c/moving puncture
  - "Einstein-Vlasov" after 2024
  - boson star + binary + black hole + tidal
  - hypervelocity + relativistic
  - IMBH + binary black hole + encounter
  - three abstract-field queries

  The two title queries that serve as sanity checks returned the known papers.
- **Web** (general engine, 18:00-18:06 UTC; candidates only, each checked by its INSPIRE
  abstract):
  - NR simulation of a binary tidally separated by a heavier black hole (extended mode)
  - three/triple black holes, full NR, unequal mass, disrupted binary
  - GR simulation of star or cluster binaries passing a black hole in a dynamical spacetime
  - boson-star or neutron-star binary disrupted by a third black hole
  - Hills mechanism in numerical relativity
  - particle-in-cell NR of collisionless clumps passing a black hole

Papers found that NOVELTY.md does not list (abstracts read in `kb-data/meta/inspire/<id>.json`),
none a full-NR Hills calculation [VERIFIED: abstracts]:

| Paper | What it is |
|---|---|
| 2511.00307 | NR, hyperbolic encounters of two equal-mass black holes (two bodies) |
| 2604.06312 | Fully nonlinear black hole-boson star binaries (two bodies) |
| 2601.14979 | Geodesics around a tidally deformed black hole ("relativistic restricted three-body problem"; no NR) |
| 2609.03007 | EMRIs in an external tidal field (no NR) |
| 2609.27492 | Binary-star collisions near hypermassive black holes with the EIH equations (1PN) |
| 2409.09597 | Three-body scattering of binary stars near an SMBH (Newtonian) |
| 1805.09593 | Black-hole mergers induced by tidal encounters (Newtonian) |
| 2205.04985 | Black-hole triplets with PN up to 2.5 order |
| 2602.06961, 2610.20594 | N-body 2PN Hamiltonian; Peters-based estimates for triples (BAM group, no NR) |
| 2609.14755 | Spherical Einstein-Vlasov environment of a black hole (no binary) |
| gr-qc/9904011 | Duez et al.: a collisionless cluster around a black hole driven unstable by a distant companion's tidal field. Perturbative and quasi-static, fixed background. The closest precedent for object (b)'s physics (collisionless matter in a relativistic tidal field), not a passage. Worth citing. |

Spot check of locators in NOVELTY.md [VERIFIED]:
- 2406.11985 `massratio_table.tex` l. 9-30: binary separation d = 1.979 and 0.990 M; third
  hole m3^H = 0.80 and 0.90 at D = 12.93 and 11.96 M.
- 2406.11985 `TBH3.tex` l. 708-712: "could be continued for at least until 128:1:1".
- 2505.03934 `apssamp.tex` l. 88, 110, 498: equal masses only.

All three are as NOVELTY.md states.

Verdict [JUDGEMENT]: the verdict of NOVELTY.md holds as of 2026-11-15 18:06 UTC, with its
stated limits: ADS and non-arXiv journals were not searched, and work in progress cannot be
seen. The likely competitors remain the RIT group (2406.11985 l. 708-712) and the BAM group
(2505.03934 and its PN follow-ups). Repeat the two citation queries (recid 2799952 and
2919080) before any submission.

## Part 2: Newtonian against geodesic baseline at q = 10, r_p = 7-13 M

Set-up as in the lead's V7 (`checks/lead_checks.py`):
- masses M = 1, m1 = m2 = 0.05, a0 = 3, r_t = 6.463 M
- prograde, coplanar, release at 4 r_t, stop at 30 r_t
- 180 release phases
- r_p = 7-13 M, extended to 15 and 17 M

My integrators (`second_check/models.py`, written from the sources without importing the
track's drivers):
- Newton with the hole fixed.
- Full Newtonian three-body problem.
- HRNA of 2404.16270, Eq. CoordtEqs (`article.tex` l. 245-267). The geodesic part was derived
  separately from the Schwarzschild radial and azimuthal equations; the initial data follow
  `appendix.tex` l. 143-179.
- Diagnostic variants: the Gamma-corrected binary (internal angular velocity divided by the
  CM's Gamma), and `hrna_sym`. In hrna_sym one factor (1/Gamma^2) g^ij, the geometric mean of
  the two members' factors with g^ij at the CM, multiplies both pair forces, so that the pair
  forces cancel. hrna_sym is my construction, not a model of the literature.

Model labels used below:
- NF4: Newton, hole fixed, release at 4 r_t.
- NT4: full Newtonian three-body, 4 r_t.
- H4: HRNA with 2404's data, 4 r_t.
- HG4: HRNA with the Gamma-corrected binary, 4 r_t.
- H20: HRNA with 2404's data, 20 r_t.
- S4raw: hrna_sym with 2404's data, 4 r_t.
- S4: hrna_sym with the Gamma-corrected binary, 4 r_t.
- S20: as S4, released at 20 r_t.

**SC0, the integrators** [VERIFIED, F-20261115-175549-456bf4a, `figures/fig_sc0_selftest.png`]:
- Pair force off: E and L of the 2404 parabola conserved to 7e-12 and 1.3e-10, r_p = 8 M to
  7e-11.
- Kepler orbit: 5e-12.
- Full three-body problem: energy conserved to 3e-9, momentum to 1e-16.

**SC1, phase-averaged against the lead** [VERIFIED, scan F-20261115-175614-5cc133d, figures
F-20261115-181106-52c4613, `figures/fig_sc1_vs_lead.png`]. Separated fractions at
r_p = 7, 8, 9, 10, 11, 12, 13 M:

| Model | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|
| Newton, hole fixed (mine = lead) | 0.911 | 0.889 | 0.844 | 0.789 | 0.678 | 0.467 | 0.000 |
| Full Newton (mine) | 0.911 | 0.889 | 0.833 | 0.756 | 0.700 | 0.589 | 0.233 |
| Full Newton (newton3) | 0.900 | 0.878 | 0.833 | 0.756 | 0.700 | 0.589 | 0.222 |
| HRNA (mine) | 0.99 | 0.99 | 0.98 | 0.96 | 0.96 | 0.94 | 0.94 |
| HRNA (lead) | 0.99 | 1.00 | 1.00 | 0.98 | 0.97 | 0.98 | 0.98 |

Captured fraction (a member crosses 2.5 M inwards):

| Model | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|
| HRNA (mine) | 0.96 | 0.93 | 0.88 | 0.84 | 0.79 | 0.71 | 0.33 |
| HRNA (lead) | 0.96 | 0.94 | 0.89 | 0.86 | 0.78 | 0.69 | 0.30 |

My HRNA runs that ended in a point-mass near-collision of the members (2-6 of 180 per r_p,
all of them bound) count as not separated.

**SC2, phase by phase against `geodesic_binary/hrna.py`** [VERIFIED, F-20261115-180835-66e13b2,
`figures/fig_sc2_phase_by_phase.png`]:
- Law newton: 360 of 360 outcome codes are equal.
- Law hrna: 178 of 178 are equal at 8 M and 162 of 174 at 13 M. The 12 differences are late
  plunges of a bound member after hrna.py's bound-CM stop (energies equal to 3 digits), and
  phases next to outcome boundaries.

**No defect in either driver.**

**SC4, is the capture physical?** [VERIFIED, `figures/fig_sc4_capture_plane.png`]
- All 658 HRNA captures at r_p = 7-10 M are members whose test-particle (E, L) lies inside
  the Schwarzschild capture region (E^2 above the barrier of their L, or L < sqrt(12) M). So
  are 488 of the 490 captures of S4.
- Under Newton (NF4), applying the same criterion to the members' final (E, L) flags a
  member in 0.91, 0.91, 0.91, 0.84, 0.76, 0.58, 0.19 of the phases at r_p = 7..13 M.
- The flagged Newtonian members are the bound ones, at L = 2.2-3.2 M and E = 0.91-0.97 (the
  V6a member with pericentre 5.9 M is one of them).

[JUDGEMENT] The disagreement "a member plunges in GR, none in Newton" is physical:
Newtonian gravity has no capture, and the member that the Hills mechanism leaves bound at
these pericentres has too little angular momentum to survive in Schwarzschild. The role
swap in V6a (Newton binds m2, HRNA plunges m1) is a different binary phase at pericentre;
SC3 gives its cause.

**SC3, the initial binary under HRNA** [VERIFIED, F-20261115-175636-5432651 (NR state) and
the scan; `figures/fig_sc5_nrstate.png` right, `fig_sc3_sc6_models.png`]
- The cause. At 4 r_t the CM has Gamma = 1/(1 - 2M/r0) = 1.084. 2404's binary is
  Newtonian-circular in coordinate time while the pair force is divided by Gamma^2.
- What it does to the NR start state. Under HRNA the binary separation grows from a0 to
  1.8 a0 before pericentre. Newton gives 1.07 a0, and the Gamma-corrected binary 1.2 a0
  (spatial-metric anisotropy and tides remain).
- In the scan. Removing the effect changes the separation edge most:

  | Separated fraction at r_p = | 12 M | 13 M | 15 M | 17 M |
  |---|---|---|---|---|
  | H4 (2404 data) | 0.94 | 0.94 | 0.89 | 0.82 |
  | HG4 (Gamma-corrected) | 0.76 | 0.63 | 0.46 | 0.33 |
  | S4 (Gamma-corrected, symmetric factor) | 0.54 | 0.48 | 0.23 | 0.06 |

  Full Newton gives 0.59, 0.23, 0, 0 at the same pericentres.
- Captures fall with it. S4 captures 0.88, 0.82, 0.52, 0.50, 0.10, 0.10, 0.12 of the phases
  at r_p = 7..13 M; H4 captures 0.96-0.33.
- The bigger effect at 4 r_t. The symmetric factor alone (S4raw against H4) changes little
  there; the initial binary is the larger effect.

**SC0d and SC6, a spurious self-force in HRNA** [VERIFIED, F-20261115-175620-df20ffe,
`figures/fig_sc0d_flat_binary.png`, `fig_sc3_sc6_models.png` right]
- The mechanism. In Eq. CoordtEqs each member's pair force carries its own 1/Gamma_i^2, so
  the pair forces do not cancel for a moving binary. Their sum is F (v2^2 - v1^2) in flat
  space.
- In flat space. A circular binary moving at V = 0.28 with M = 0 accelerates sideways at
  1.065e-4 under HRNA. My integrator and hrna.py agree to 4 digits; Newton and hrna_sym give
  exactly 0.
- Size. My estimate (m1 m2/m_b)(omega/a0)|V| is 1.42e-4. Relative to the hole's pull at
  r = k r_t this is about 0.35 k^(3/2) m_b/a0 [JUDGEMENT, from that estimate]:
  - about 1e-4 for 2404's binaries at 50 r_t;
  - about 0.1 for F's binary at 4 r_t;
  - about 1 for F's binary at 20 r_t.
- At q = 10. It raises the CM's angular momentum by 0.12 M between 4 r_t and 2 r_t
  (predicted 0.127). Released at 20 r_t, the CM never comes closer than 30-44 M for nominal
  r_p = 7-17 M, so nothing separates (H20).
- Consequence [JUDGEMENT]. HRNA cannot be released farther out at q = 10. The effect is a
  candidate for the r0 dependence that 2404 (`appendix.tex` l. 217-222) and the helper's C2
  (`geodesic_binary/JOURNAL.md` l. 400-415) left open [TO VERIFY at 2404's parameters].

**Release-radius test of my variant: failed.** S4 and S20 differ by up to 0.35 in the
separated fraction and 0.38 in the captured fraction (r_p = 8 M: 0.91/0.56 and 0.82/0.44).
S20 has 25-60 percent of runs ending in member near-collisions, 90 percent of them after the
CM pericentre. So the S numbers are indicative, not a reference. [VERIFIED runs; the cause
of S20's eccentric survivors is open]

**SC5 and SC7, the NR start state of P1** [VERIFIED, F-20261115-175636-5432651,
F-20261115-175637-a592d7a, `second_check/nr_invariants_F-20261115-175637-a592d7a.json`]
- The models from the coordinate state:
  - Newton (fixed and full) ejects m1 and binds m2, with pericentre 5.9 and 5.6 M.
  - HRNA plunges m1 at t = 96.9 M (V6a reproduced).
  - With the Gamma-corrected velocities, under HRNA and hrna_sym alike, the two point masses
    collide at t = 84.5 M before pericentre. In NR the members would merge.
- GR invariants. I read P_i = m u_i in isotropic Schwarzschild coordinates of the heavy hole
  [JUDGEMENT: approximate for Bowen-York data at q = 10]:

  | Reading | CM E | CM L | GR turning point |
  |---|---|---|---|
  | Test mass, hole frame | 0.99925 | 4.19 M | r_S = 5.77 M (isotropic 4.72 M) |
  | Test mass, hole at rest | 0.993 | 3.81 M | captured |
  | Total mass M + m_b | 0.9951 | 4.19 M (3.81 in units of M + m_b) | captured |

  The baselines' "r_p = 8 M" means L = 4.0 M (Newton, hole fixed), 4.20 M (Newton, mass
  M + m_b) and 4.62 M (2404 parabola, E = 1). Capture at E = 1 sets in below 4 M.
- [JUDGEMENT] The NR data, built from Newtonian momenta at 25.85 M, are sub-parabolic and
  deeper in GR than any of the three baselines' encounters. The lead's expectation for P1
  (one member merges with the heavy hole) is probably right, but for this reason and not
  because HRNA captures in 94 percent of phases. A whole-binary plunge is possible.

## Which tests would tell

1. Driver defect: done, and negative (SC1, SC2, SC0). It would be repeated after any change
   to the drivers.
2. Physical capture against model artefact, per encounter: the test-particle capture
   criterion on the members' (E, L) after separation (SC4). It holds for every HRNA capture.
3. Size of the GR effect at q = 10. This needs a relativistic reference whose binary is
   consistent at the release radius and that converges in release radius. HRNA fails at
   q = 10 (spurious self-force), and so does my symmetric variant. Candidates, not run:
   - [JUDGEMENT] 1PN EIH three-body equations with the hole free (2404 `appendix.tex`
     l. 117-125). They conserve momentum and include finite q, but are poor at r ~ 8 M.
   - The NR passage itself.
   - A cheaper discriminating test: the same scans with a0 scaled at fixed D = r_p/r_t.
     HRNA - Newton must vanish like M/r_p if the difference is relativistic. The artefacts
     scale with m_b/a0 and with Gamma at release instead.
4. For P1: compare the CM track of the first 40 M of a low-resolution NR run with the
   geodesic of the SC7 invariants (turning point r_S = 5.8 M) and with the 2404 parabola
   (8 M). This tells within an hour of processor time which encounter the data describe.

## Open, not done

- 1PN (EIH) reference; the fixed-D scaling test; the cause of S20's eccentric survivors;
  the self-force at 2404's own parameters (whether it explains their r0 stall).
- Retrograde encounters and q = 4 were not rechecked.
- The SC7 reading of the puncture momenta is approximate (bare against horizon masses,
  conformal against areal coordinates, Galilean hole frame).

## Requests (to the F-hills lead, to forward)

- R1 (F lead, before P1 is submitted): either rebuild the momenta of
  `hills_q10_m8.athinput` from the GR parabola (E = 1, L for the intended areal r_p,
  converted to the puncture's isotropic coordinates), or state P1's purpose as a
  capture-boundary encounter. The SC7 numbers are in
  `second_check/nr_invariants_F-20261115-175637-a592d7a.json`.
- R2 (F lead): drop or qualify the HRNA percentages (94 percent capture, separation at 13 M)
  in `stage/G1/STATUS.md` and STATUS.md. At q = 10 and 4 r_t they depend on the
  initial-binary convention (SC3), and the model has a self-force of 10 percent of the
  hole's pull (SC6).
- R3 (geodesic_binary helper): add the flat-space moving-binary test (SC0d) to
  `geodesic_binary/tests`, and test the self-force against 2404's r0 dependence (C2).
- R4 (core, optional): none needed from this package. The NR passage is the decisive test.
