# RUNS: parameters of the secondary-infall runs in AthenaK (D-pre-3)

Status: proposal of the secondary_infall helper to the D-bh-dress lead, 2026-11-15. No
AthenaK run has been made by this package; 0 card-hours used. Every number below comes
from a registered run of this package (run id given) or from the scoping run
D-bh-dress-20261115-120304-795eee9; `JOURNAL.md` holds the predictions and outcomes.
Units G = c = 1, M = initial mass of the hole, eps = H_i M, t_i = 2/(3 eps).

## 1. What the references establish

| Result | Value | Source |
|---|---|---|
| Turnaround mass, unperturbed Hubble flow + seed at t_i | M_ta/M = 1.525, 2.630, 4.875 at a/a_i = 2, 4, 8 (closed form = shells to 1e-15); -> 1 + 0.5648 a/a_i only beyond a/a_i ~ 120 | analysis D-bh-dress-20261115-125613-248fdaf; scoping run |
| Hole mass, cold radial dust absorbed at 2M | M_bh/M = 1.193, 1.828, 3.219 at a/a_i = 2, 4, 8 (closed form to 4e-15); doubles at a/a_i = 4.52; asymptote M + 0.356 M a/a_i | same |
| Dress (dust that passed the centre once), centre passing | 0.189, 0.820, 2.193 M at a/a_i = 2, 4, 8; the same for eps = 0.01, 0.03, 0.1 to 1.5 %; reaches 0.25, 0.5, 1, 2 M at a/a_i = 2.22, 3.03, 4.54, 7.44 | same |
| Self-similar limit (seed negligible) | rho ~ r^(-9/4) below lambda = r/r_ta ~ 1e-4 (slope of m: 0.741 on [1e-4, 1e-3], 0.705 on [3e-3, 3e-2]); outermost caustic lambda_1 = 0.355; rho/rho_frozen -> 3.0; dress = 0.625 M_ta = 0.353 M a/a_i | test 2 D-bh-dress-20261115-123813-97afeea |
| Approach to it | shells reach the self-similar profile on lambda in [0.01, 0.3] by a/a_i ~ 30 (eps 0.1 run to 100); at a/a_i <= 8 only the outer decade, r in [10 M, 0.3 r_ta], has slope -2.2 to -2.3 | analysis 125613, `figs/selfsim_check.png` |
| Infall stream onto an absorbing hole | rho = Mdot/(4 pi r^2 (2 M_bh/r)^(1/2)) below ~0.2 r_ta; fitted slope -1.42 on [3M, 0.1 r_ta] | analysis 125613, `figs/profiles_eps*.png` |
| Warm dust and capture at L < 4 M_bh | eps = 0.01, a/a_i = 4: sigma_i = 0.02, 0.05: all collapsed dust captured; 0.1: 97 %; 0.2: 74 % (and M_ta falls to 1.47 M) | analysis 125613, `figs/angular_momentum.png` |
| Growth exponent d ln M_dress / d ln a | > 3/2 for a/a_i < 4.5, 1.3 at 8, 1 by ~30: neither 1805.09034's a^(3/2) (main.tex:216-218) nor the self-similar a^1 is what a run ending at a/a_i <= 8 sees | `figs/growth.png` |

Two consequences for the design [JUDGEMENT]:
1. Cold dust onto a hole in full relativity has no dress: every particle with L < 4 M_bh
   is captured (1305.2619 `SFWpaper.tex:120`, via `../scope/REFERENCES.md`), and cold
   radial infall has L = 0. The full-relativity counterpart of the Newtonian dress is the
   accretion of the same shells, and its observable is the hole's growth law and the
   r^(-3/2) infall stream, not an r^(-9/4) spike. A surviving dress needs L > 4 M_bh,
   i.e. tangential speeds near 0.1-0.2 c at r_i ~ 20-30 M, which also change the infall.
2. The Newtonian set-up maps onto a Lemaitre-Tolman-Bondi solution with a central mass:
   E(r) = -M/r (the scoping run's energy identity, checked to 1.5e-10) and
   M(r) = M + (4 pi/3) rho_i r^3, with R_t^2 = 2 M(r)/R + 2 E(r) in the dust's proper
   time and areal radius [BACKGROUND: the LTB equation; the mapping is my derivation,
   to be checked]. Without shell crossing (the absorbing case never crosses), the closed
   forms of `common.kepler_radial` are then exact in proper time and areal radius, with
   M(r) the Misner-Sharp mass, which is smaller than the rest mass of a shell by the
   factor (1 + 2E)^(1/2) ~ 1 - M/r_i (the binding energy, a few per cent). The first full-relativity run therefore
   has an exact reference.

## 2. The parameters

Newtonian scaling: lengths ~ eps^(-2/3), times ~ eps^(-1); masses at fixed a/a_i do not
depend on eps. Relativity enters through r_ta/M (compactness of the dress region) and
through H_i R_ball (the dust region against the Hubble radius). From
`run_plan_D-bh-dress-20261115-125613-248fdaf.txt` (cost: the scoping model, AMR rate of
the production run jeans/n1e4_v19, 1e6 particles, one global step at dx_min, outer
boundary at max(128 M, 1.25 R_ball, 0.71 T)):

| eps | a/a_i | T/M | M/M_ta | r_ta/M | r_sp/M (99 %) | R_ball,i/M | R_ball(T)/M | card-h dx_min = M/16, dx_ball = 2M / 1M | card-h M/32, 1M |
|---|---|---|---|---|---|---|---|---|---|
| 0.003 | 2 | 406 | 0.656 | 74.6 | 30.0 | 58.7 | 117 | 6.5 / 31 | 63 |
| 0.01 | 2 | 122 | 0.656 | 33.4 | 13.5 | 26.3 | 52.6 | 0.82 / 1.5 | 3.1 |
| 0.01 | 4 | 467 | 0.380 | 83.9 | 34.4 | 38.3 | 153 | 12.5 / 76 | 153 |
| 0.03 | 2 | 41 | 0.656 | 16.1 | 6.5 | 12.6 | 25.3 | 0.27 / 0.27 | 0.59 |
| **0.03** | **4** | **156** | **0.380** | **40.3** | **16.5** | **18.4** | **73.7** | **1.3 / 3.6** | **7.5** |
| 0.03 | 8 | 481 | 0.205 | 99.8 | 43.2 | 24.6 | 197 | 23 / 162 | 325 |
| 0.1 | 4 | 47 | 0.380 | 18.1 | 7.4 | 8.3 | 33.0 | 0.31 / 0.35 | 0.76 |
| 0.1 | 8 | 144 | 0.205 | 44.7 | 19.4 | 11.0 | 88.2 | 1.5 / 5.2 | 10.7 |

r_ta and r_sp (radius holding 99 % of the dust that passed the centre) are those of the
eps = 0.01 shell runs scaled by (eps/0.01)^(-2/3); the eps = 0.03 runs give r_sp = 6.4 and
16.1 M at a/a_i = 2, 4 directly.

- Hole mass against the mass inside turnaround: M/M_ta = 0.656, 0.380, 0.205 at a/a_i =
  2, 4, 8, for every eps. For the dust to dominate (M/M_ta < 0.5) a/a_i > 2.9 is needed (M_ta = 2.07 M at
  a/a_i = 3, shell run absorb_e0.03).
- Radii the mesh must cover: from the horizon (dx_min = M/16 to M/32, as in the
  scoping's puncture anchors) to R_ball(T) = 1.2 r_i(M_ta(T) - M) a_end, where
  r_i(mu) = (2 mu/eps^2)^(1/3): by Birkhoff's theorem dust outside the last shell that
  turns around before T does not act on the inside, so the ball need not be larger. The
  dress region is r < r_sp ~ 0.4 r_ta. The outer boundary follows the scoping's causal rule.
- Duration for a given dress (Newtonian, centre passing): T = k/eps with k = 1.53, 2.84,
  5.77, 12.86 for 0.25, 0.5, 1, 2 M. For eps = 0.03: 51, 95, 192, 429 M; for eps = 0.01:
  153, 284, 577, 1286 M. In full relativity the same mass is accreted instead.
- Affordability (allotment 30 card-hours to the next gate, decision 0006): eps = 0.03 to
  a/a_i = 4 costs 1.3-3.6 card-h (7.5 at M/32); eps = 0.01 to a/a_i = 4 costs 12.5-76;
  anything to a/a_i = 8 except eps = 0.1 exceeds or exhausts the allotment. The ball
  region dominates the cost (dx_ball = 2M is five times cheaper than 1M).
- Softening (Newtonian mode): the mesh softens the dust's own gravity as well as the
  seed's; at eps = 0.1 a softening of 5M lowered M_ta at a/a_i = 100 five-fold (run
  D-bh-dress-20261115-123522-cff68f1), while 0.5M at eps = 0.03 keeps M_ta within
  1.8e-3 of the closed form. Rule [JUDGEMENT]: cell size near the centre <= 0.1 r_i of the
  lightest shell whose dress matters, i.e. <= 0.5 M at eps = 0.03 (r_i(0.05 M) = 4.8 M).

## 3. First Newtonian-mode run (AthenaK, `core/newton`, pusher = newton)

Outcome (wave 2, README "Wave 2", JOURNAL from "Wave 2"): run on the release processor
executable with the hole as a 19952-particle clump at a cell centre (no fixed point mass yet),
eps = 0.03, dust edge 18.35 M, 5e5 particles, nx = 64 and 128 to a/a_i = 4 and nx = 128 in a
+-176 M box to a/a_i = 8. M_ta and the dress agree with the shell reference matched to the
mesh softening to 0.1-0.5 %; the profile within the bin scatter outside the outermost
caustic. The prediction below (dress 0.796 M, M_ta 2.593 M at a/a_i = 4) holds within 0.2 %.
The clump must not sit at a mesh vertex (unstable). The parameters of this section (2e6
particles, 384^3 cells, a card) were not used: 5e5 particles and one core per run sufficed.

Purpose: the Newtonian reference of the full-relativity run below, same particles, gravity
the only difference (interface `tracks/core/interfaces/newtonian_mode.md` on `core/newton`);
checks the mode against this package's shells, independently.

- eps = 0.03: t_i = 22.22 M, to t = 177.8 M (a/a_i = 4), T = 155.6 M.
- Seed: mass M = 1 fixed at the origin (request 1 below; otherwise one heavy particle).
- Dust: uniform ball 3 M <= r <= R_ball,i = 18.4 M (rest mass 2.81 M; the vacuum core of
  radius R_w = 3 M matches the full-relativity data, where it contains the horizon, and
  removes 0.012 M of dust), velocities v = eps r radial, cold. N = 2e6 equal-mass
  particles (1.41e-6 M each); the dress at a/a_i = 4 then holds ~5.6e5 particles.
- Domain: isolated, `mg_bc = multipole`, half-width >= 92 M (1.25 R_ball(T)); uniform
  mesh 384^3 (dx = 0.48 M) if the multigrid fits on one card, else 256^3 (dx = 0.72 M)
  together with a shell reference at s = 0.75 M (request 4).
- Outputs: particle snapshots at a/a_i = 1.5, 2, 3, 4; radial profiles; per particle a
  flag or counter of passages through the centre (request 2).
- Predictions for this set-up (shell run pass_e0.03_s0.5_rw3,
  D-bh-dress-20261115-130000-d087954, s = 0.5 M, vacuum core 3 M): M_ta = 1.505, 2.045,
  2.593 M and dress = 0.173, 0.472, 0.796 M at a/a_i = 2, 3, 4. Without the vacuum core
  (pass_e0.03_s0.5, D-bh-dress-20261115-123520-cff68f1): M_ta = 1.524, 2.627 M, dress =
  0.187, 0.818 M; r_ta = 16.0, 40.3 M; 99 % of the passed dust inside 6.4, 16.1 M; and
  the density rho/rho_b(t) below (rho_b = 1.34e-5 and 1.68e-6 M^-2 at a/a_i = 2, 4; the
  profile of the vacuum-core set-up was not tabulated, its inner bins at a/a_i = 2 are
  expected lower):

  | r/M | 1 | 2 | 4 | 8 | 16 | 32 |
  |---|---|---|---|---|---|---|
  | a/a_i = 2 | 123 | 43 | 14 | 1.8 | 1.09 | 1.01 |
  | a/a_i = 4 | 1060 | 557 | 142 | 48 | 4.9 | 1.43 |

  (`profiles_eps0.03.json` of analysis 125613; logarithmic bins of 0.18 dex; values
  inside ~2 cells depend on the softening.) The inner profile is not r^(-9/4) at these
  times: slope -2.66 on [3, 10] M at a/a_i = 2 and -1.85 at 4. The dust that was already
  bound to the seed at t_i dominates there.
- Refuted if the dress mass at a/a_i = 4 differs from 0.796 M by more than 5 % or M_ta
  from 2.593 M by more than 2 %, or the profile at r >= 4 cells differs from the shell
  reference of the same set-up and softening by more than 30 % per bin.
- Cost: not estimated here (Newtonian-mode throughput on a card not yet measured by core);
  [JUDGEMENT] well under one card-hour for ~5e3 steps.
- Second Newtonian-mode run (after this one agrees): eps = 0.03 to a/a_i = 30-100 on a
  refined mesh, against the self-similar solution (`figs/selfsim_check.png`): only the
  Newtonian mode can reach the regime where the r^(-9/4) dress and the a^1 growth hold.

## 4. First full-relativity run (puncture + LTB dust)

Purpose: the hole's growth by cold collisionless accretion in an expanding medium, against
an exact (LTB) reference; the G2 criterion "mass growth agrees with the integrated
particle flux through the horizon"; the infall profile in the strong field.

- eps = 0.03, from t_i = 22.22 M to a/a_i = 4 (T = 155.6 M of dust proper time), cost
  1.3 card-h (dx_min = M/16, dx_ball = 2 M), 3.6 (dx_ball = 1 M), 7.5 (M/32): two
  resolutions fit in the allotment with a third at M/32 for convergence.
- Initial data: a puncture of horizon mass M; no dust inside the areal radius R_w = 3 M
  (vacuum around the horizon; the construction is the einstein_straus helper's with an
  over-massive hole); outside, the LTB slice E = -M/r, uniform rest-mass density
  3 eps^2/(8 pi) at t_i, dust at rest with respect to the slice normal (u_i = 0) and the
  expansion in K_ij (format-2 table, `tracks/core/interfaces/spherical_id_format2.md` on
  `core/id-extrinsic`); ball edge at R_ball,i = 18.4 M, vacuum (Schwarzschild) outside.
  Same particle set as the Newtonian-mode run (2e6).
- Predictions for this set-up (absorbing shell run absorb_e0.03_rw3,
  D-bh-dress-20261115-125957-d087954, vacuum core 3 M, capture at 2M): hole mass 1.060,
  1.183, 1.484, 1.811 M at a/a_i = 1.5, 2, 3, 4 (dust proper time t = 40.8, 62.9, 115.5,
  177.8 M); M_ta = 1.507, 2.049, 2.595 M at a/a_i = 2, 3, 4; one stream everywhere (no
  crossing). Without the vacuum core (absorb_e0.03, D-bh-dress-20261115-124552-5d687b5):
  hole 1.198, 1.833 M at a/a_i = 2, 4, and the density rho/rho_b(t):

  | r/M | 4 | 8 | 16 | 32 |
  |---|---|---|---|---|
  | a/a_i = 2 | 3.6 | 1.7 | 1.11 | 1.01 |
  | a/a_i = 4 | 16.2 | 6.6 | 2.8 | 1.43 |

  following Mdot/(4 pi r^2 (2 M_bh/r)^(1/2)) below ~0.2 r_ta. These are Newtonian
  numbers. By the LTB mapping of section 1 the growth is exact in dust proper time and
  Misner-Sharp mass up to the rest-to-Misner-Sharp factor; a shell enters the horizon at
  R = 2 M_bh, a few M of proper time before the fixed r = 2M where the proxy absorbs it.
  The code's coordinate time differs from the dust's proper time under the
  moving-puncture gauge, so compare per shell (by particle label), not per coordinate
  time (request 5).
- Refuted if the horizon mass, as a function of the label of the last particle shell
  inside it, differs from M(r) of that shell by more than the noise floor of D-pre-4 plus
  the particle-shot noise of a shell; or if the mass growth and the integrated flux of
  particle energy through the horizon differ by more than that.
- What it does not give: a dress (section 1, consequence 1). The dress in full relativity
  needs either eps <= 0.003 (r_ta = 75 M at a/a_i = 2, 6.5-31 card-h) with tangential
  velocities, or a Newtonian-mode dress (run 3) imported as initial data for a
  full-relativity continuation (D's "initial data for dressed black holes" to F). That
  choice is the lead's.

## 5. Requests to other owners

1. core (Newtonian mode): a fixed point mass at the origin, potential -M/(r^2 + s^2)^(1/2)
   added to the mesh potential at the particles (or a pinned heavy particle), so the seed
   neither random-walks nor is smeared by CIC deposition.
2. core (both modes): per-particle count of passages through pericentre (or the sign
   changes of x . v), so the dress (dust that passed the centre) is measured directly.
3. core (Newtonian mode): the card throughput of the mode at 256^3 and 384^3 with 2e6
   particles, to cost run 3; and a statement whether the multigrid octets on refined
   meshes are verified (needed for the second Newtonian-mode run).
4. this package (follow-up, cheap): a shell reference at the softening of the actual
   Newtonian-mode mesh once it is fixed (`shells.py` configuration with that s).
5. core (full relativity): per-particle proper time and the particle flux of energy
   through the apparent horizon, to compare with the LTB reference per shell.
6. D-bh-dress lead / einstein_straus helper: the puncture + LTB initial data of section 4
   (an over-massive central hole: the removed dust mass inside R_w is << M); and the
   check of the LTB mapping of section 1, consequence 2.
7. D-bh-dress lead: the scoping JOURNAL says M_ta = 1.63 M at a/a_i = 4; its own table and
   this package give 2.63 M (`../scope/JOURNAL.md`, outcome item 5).
8. kb: Bertschinger 1985 (ApJS 58, 39) is not on arXiv; a locator for its lambda_1 and
   density normalisation would let test 2 be compared with printed numbers (my
   recollection of lambda_1 = 0.364 against 0.355 here is [BACKGROUND], not checked).
