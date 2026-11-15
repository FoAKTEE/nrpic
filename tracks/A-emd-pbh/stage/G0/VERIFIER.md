# Independent verification of Track A's G0 and G1 material

Verifier of A-emd-pbh (wave 2), 2026-11-15. Given the artefacts, not the conclusions: the
sections 1 to 3 below were written before I opened STATUS.md, HANDOFF.md, the JOURNAL files,
`stage/G0/EVIDENCE.md`, `stage/G0/OPEN.md`, `stage/G1/STATUS.md` or any review by the lead.
Section 4 compares afterwards. Evidence labels: [VERIFIED] recomputed here (run id) or read
at the source (file:line); [BACKGROUND] standard, not checked; [JUDGEMENT] mine.

Runs (all registered with `harness/bin/nrpic-run`, local, 4 cores; outputs under
`scratch/A-emd-pbh/<run id>/`; predictions and outcomes in `JOURNAL.md` of this directory):

| Run | What |
|---|---|
| A-20261115-160935-41f721d | `scripts/verify_claims.py --Nmax 128`: parts V1-V6, first pass (37 s) |
| A-20261115-161239-1c41333 | same, own constraint check to N = 192, the track's constraint test to N = 256 (122 s); the numbers quoted below are from this run unless stated |
| A-20261115-161253-e506d90 | the track's unit tests `expball/tests` (pytest, 32 tests) |

Source figures of arXiv:2609.14218 (`alpha.pdf`, `thre_p0.pdf`) were rendered to PNG inside
the run directories (`src_render/`, never committed) and read by eye; read-offs are marked
"by eye".

## 1. Verdicts

| # | Claim on which the plan rests (where the track states it) | Verdict |
|---|---|---|
| C1a | Flat ball: 2M/R_b = (H R_b)^2; no (anti-)trapped round sphere iff max 2m/R < 1 (DERIVATION.md 4, 8; brief S1) | CONFIRMED |
| C1b | Start a_i/a_H = (q/(R_b H_i))^2; ceilings mu <= 0.031 (q = 3), 0.069 (q = 2) at R_b H_i = 0.9 (SCOPE.md 4, T3) | CONFIRMED |
| C1c | Hence "the ball covers ... not the comparison amplitudes" (SCOPE.md 4), "the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218" (decision 0013) | WRONG for the particle bracket, right for the hoop and fluid amplitudes |
| C2 | deltabar_ent = 12 mu/(5 e_E) = 0.883 mu, delta_c = 12 mu/5, 2M/R_ta = (5/3) deltabar_ent (SCOPE.md 3, 10.1) | CONFIRMED |
| C3 | Hoop line h-hat(0.2, 0) = 0.452, 0.22-0.48 over e = 0.05-0.3 (SCOPE.md 2, 5; T1) | CONFIRMED |
| C4a | Source facts: horizons for mu >= 0.05, none for mu <= 0.045 at e = 0.2; t_H; collapse times scale as the top hat of the r_m shell; mu_fd(250 t_H) = 0.048 (SCOPE.md 2, T2) | CONFIRMED |
| C4b | "If H1 holds, mu = 0.045 forms a horizon near 0.86 t_c(r_m) = 239 t_H" (SCOPE.md 2) | WRONG (contradicted by the published curve); H1 itself not refuted |
| C5 | Ball initial data (A-pre-1, G1 criterion): exact constraints, finite-difference residuals converge at the order of the differences, exact shell times | CONFIRMED (order 2 and 4), with two limits stated below |
| C6 | Dispersion axis s_c in [0.55, 1.5], amplitude independent; lattice N >= 1e5 at deltabar_ent >= 0.04, >= 2e6 at 0.01 (SCOPE.md 5, T4) | CONFIRMED as arithmetic and locators; the N floor is an order-of-magnitude estimate |
| C7 | G2 target: Delta M/M_ADM <~ 1e-3, RMS 2.061e-3, 9.362e-4, 7.347e-4 (SCOPE.md 10.4) | CONFIRMED, with a caveat on what the source paper did not achieve |
| C8 | Compute: measured 5.41 card-hours for jeans/n1e4_v19; model for SR-1/SR-2 and the scan (SCOPE.md 9, 10.7) | measured number CONFIRMED; the model NOT CONFIRMED (no PBH run has finished) |

## 2. Claim by claim

### C1 Ball geometry and the amplitude window

What I did. (a) Derived by hand: inside the flat ball m(R) = (4 pi/3) rho R^3 and
8 pi rho = 3 H^2 give 2m/R = (HR)^2; for round spheres theta_+ theta_- is proportional to
2m/R - 1 (DERIVATION.md 4 gives (4/R^2)(2m/R - 1), which I re-derived from
theta_pm = (2/R)(v pm sqrt(1+2E)) and v^2 = 2m/R + 2E); outside 2M/R falls. Numerically, my
own construction of data set 2t (smooth top-hat core delta_c = 1, R1 = 0.3 R_b, R2 = 0.75 R_b,
H R_b = 0.5, C^4 taper 0.1875 R_b; built from Delta(R) without the track's code) gives
max 2m/R = 0.23612 at R = 8.26, equal to the track's `Ball.summary()` [VERIFIED, run
41f721d]. (b) Own derivation R_b H_i = q r_m (aH)_i = q (a_H/a_i)^(1/2) (aH ~ a^(-1/2) in
Einstein-de Sitter, r_m (aH)_H = 1), inverted numerically: a_i/a_H = (q/(R_b H_i))^2; with the
mean contrast in r_m capped at 0.3 the ceilings are 0.03058 (q = 3) and 0.06881 (q = 2) at
R_b H_i = 0.9, and e_E = 2.718 times less with the central cap [VERIFIED, run 1c41333;
`fig_V1_ball_window.png`].

Trying to break it (C1c). The scoping concludes that the ball cannot hold the comparison
amplitudes; decision 0013 repeats it as the reason for building the threshold line in the
periodic box. With the scoping's own numbers this holds for the hoop amplitude (mu = 0.45 at
e = 0.2 needs a start mean contrast of 1.96 at q = 2) and the fluid amplitudes (~1), but not
for the particle bracket (0.045, 0.05] of arXiv:2609.14218 (MDPBH.tex:1102-1103): at q = 2 the
ceiling exceeds 0.05 for every R_b H_i > 0.75, and mu = 0.05 needs a start mean contrast of
0.218 < 0.3 [VERIFIED, run 1c41333, `cap_needed`]. It fails only with the central cap or q >= 3.
The cap 0.3 itself is a choice [JUDGEMENT of the track]; the ceiling is linear in it.
Consequence [JUDGEMENT]: the periodic box remains the better place for the comparison (it
uses the paper's data unchanged), but the stated reason must be corrected; the H1 test
(mu = 0.045, 0.05, e = 0.2) would fit into a q = 2 ball once non-spherical ball data exist,
which they do not yet.

### C2 Amplitude conventions

What I did. sympy, from ln Psi = (mu/2) exp(-k^2 r^2/6) and delta = -(4/5)(aH)^-2 lap ln Psi
(MDPBH.tex:862 for delta = -div D, :892 for D): deltabar(r) = (12/5) mu exp(-k^2 r^2/6) at
aH = k/sqrt6; r_m = sqrt6/k both from the maximum of r^2 deltabar and from the paper's
condition (MDPBH.tex:709-711); deltabar(r_m) = 0.88291 mu, delta_c = 2.4 mu, ratio e_E.
Turnaround compactness from exact bound shells with simultaneous bang time (my own cycloid
and root finder, not expball): (2m/R_ta)/deltabar_ent = 1.66643 at start contrast 1e-4,
falling linearly in the start contrast (1.6438 at 0.1); the collapse threshold
Delta_i (t_c/t_i)^(2/3) -> 1.68661 against 1.68647 [VERIFIED, run 1c41333,
`fig_V2_conventions.png`]. The relation R_max = 3 r_m/(5 delta_m), b_BH = (5/3) delta_m is
at arXiv:2507.18312 Main.tex:303-316 as quoted [VERIFIED, read].

### C3 Hoop line

What I did. Not from h-hat: the Zel'dovich pancake of the Lagrangian sphere r_m at the
first caustic (eigenvalues of -grad D, MDPBH.tex:907-908, re-derived by hand from the
profile; growth proportional to a), perimeter of the pancake ellipse by direct quadrature of
the arc length, mass of the sphere, h = C/(4 pi M) (arXiv:1609.01588
apj_nonsphericalpbh.tex:600-607), root of h = 1: mu_c(e, 0) = 0.21861, 0.34215, 0.41254,
0.45175, 0.47203, 0.48053 at e = 0.05 ... 0.3, equal to h-hat with the elliptic integral of
modulus sqrt(1 - x^2) to 5e-15; the other convention (parameter) would give 0.4221 at
e = 0.2. The published "Analytic criterion" line of `thre_p0.pdf` sits at ~0.45 at e = 0.2
and ~0.34 at e = 0.1 (by eye), i.e. the modulus convention [VERIFIED, run 1c41333,
`fig_V3_hoop.png`]. The criteria package uses the same convention (`criteria/emd_criteria.py`
`ellipE`, read, not run) and expresses the line in delta_c = (12/5) h-hat, consistent with C2.

### C4 Timing of the particle runs of arXiv:2609.14218 (hypothesis H1)

Confirmed (C4a). Read at the source: horizon for mu >= 0.05, alpha_0 stops falling for
mu <= 0.045 (MDPBH.tex:1102-1103); particle figure at 245 t_H (:1131); the runs do not break
down and continue until stopped (:1141-1142); t_H = 100 sqrt6/k (:716-718) and the start
a_H/a_i = (H_i/(k/sqrt6))^2 = 150 with H_i = 5k (:549) [VERIFIED]. Arithmetic: mu_fd(250 t_H) =
0.04813, t_c(r_m) = 236.1 t_H at mu = 0.05 and 276.6 t_H at 0.045 [VERIFIED, run 1c41333]. My
own read-offs of the steep lapse drops in `alpha.pdf` (by eye): 46, 74, 106, 145, 180 t_H for
mu = 0.15, 0.10, 0.075, 0.06, 0.05, i.e. 1.01, 0.89, 0.82, 0.81, 0.76 of t_c(r_m); they agree
with the track's read-offs (24, 46, 74, 106, 144, 199) except that mu = 0.05 has two stages
(first drop ~180, final collapse ~218) and the track took 199 +- 10. Slope by hand from my
read-offs: -1.24 (first drop of 0.05) to -1.33 (199), the track's -1.31 lies inside.

Wrong (C4b). SCOPE.md section 2 predicts under H1 a horizon for mu = 0.045 near
0.86 t_c(r_m) = 239 t_H. In `alpha.pdf` the mu = 0.045 curve runs to the right edge at
250 t_H; alpha_0 dips sharply at ~205-212 t_H (13.5 to ~9) and stays at 9-9.5 to 250 t_H, with
no collapse near 239 t_H (by eye; `fig_V4_timing.png` places the dip at 0.75 t_c(r_m)). The
paper's own outcome at mu = 0.045 therefore already contradicts the H1 timing with the median
ratio. H1 survives in another form [JUDGEMENT]: the 0.045 dip sits at the same fraction of
t_c(r_m) (0.75) as the first drop of the 0.05 run (0.76), and the 0.05 run collapsed 218/180 =
1.21 times after its first drop; the same factor puts a 0.045 collapse at ~252 t_H, just beyond
the plotted end. The H1 runs to 400 t_H remain the right decision; the predicted time should be
quoted as ~250-280 t_H (ratios 0.9-1.0), not 239.

Qualification. SCOPE.md section 3 names "the known cutoff delta_fd = (t_H/t_end)^(2/3)
(arXiv:1707.03595 L925)". At the source (Spin_PBH.tex:920-927, the definition at :925) delta_fd is the contrast that
reaches unity at t_end, without 1.686 and for delta_{s,H}; taken literally it gives mu = 0.0285
at 250 t_H, against the scoping's top-hat value 0.048 (T2). The text should name the top-hat
version it actually uses [VERIFIED as arithmetic, run 1c41333].

### C5 Expanding-ball initial data (A-pre-1; G1 criterion)

What I did. (i) Rebuilt data set 2t from its definition (Delta(R), my own inversion of
2F1(1/2, 3/2; 5/2; y) = sqrt(1 + Delta), E = -y m/R, v, KL = -dv/dR as a total derivative,
KT = -v/R, conformal factor by quadrature, betar = -v/(psi^2 sqrt(1+2E))) and compared with
the table that AthenaK reads (`scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/*.tab`):
max differences 3e-15 in psi, 4.5e-11 H in KL (my spline derivative), 1.6e-14 H in KT, 8e-15
in betar; alpha = 1 in every row; KL = KT = -0.0445 < 0 at the centre, expansion in the code's
sign (`coord/INTERFACES/spherical_id_format2.md`). (ii) My own finite differences (full box,
second-order centred differences, Christoffel symbols of psi^4 delta_ij written by hand,
r < 1.15 R_b, N = 32 ... 192): Hamiltonian L2/6H^2 from 2.5e-2 to 8.3e-4, orders 1.87, 1.78,
1.93, 1.96, 1.97, 1.98; momentum 9.7e-2 to 4.7e-3, orders 1.38, 1.55, 1.74, 1.85, 1.90, 1.93.
(iii) The track's own test function (`expball.mesh.residuals`) on data set 2t, octant,
all cells, N = 32 ... 256: order 2: H 1.94, 1.98, 2.00; M 1.78, 1.93, 1.98; order 4: H 3.39,
3.75, 3.92; M 2.82, 3.43, 3.79. (iv) The track's 32 unit tests pass (run e506d90). (v) Shell
times by my own cycloid: core tau_ta = 16.89376895004044, tau_c = 44.45420456674754, core-edge
tau_AH = 44.38146574194694, identical to the predictions stored with the data set; first
trapped shell (by minimisation) tau_AH = 44.34927 at R_i = 2.742, m = 0.0805, against the
track's 400-shell grid 44.34942 at R_i = 2.731 [all VERIFIED, run 1c41333;
`fig_V5_constraints.png`, `fig_V5_track_test_rerun.png`, `fig_V5_radial.png`].

Trying to break it. KL -> -KL: residuals flat at 1.09 (H) and 1.89 (M) of 6H^2. KL of a
static gamma_RR (KL = -v' + v E'/(1+2E), the alternative that DERIVATION.md section 2 rejects):
flat at 0.0216 and 0.0399, so the checker sees that mistake and the track's choice is the
right one. K -> -K (the time-reversed, collapsing ball): residuals identical to the true data
to all digits.

Limits. (1) The constraint test cannot tell an expanding from a collapsing ball; the time
orientation rests on the sign convention alone, and only the first evolution step shows how
the code reads the table. (2) Order 4 is reached only at N = 256 (octant): 3.92 (H) and
3.79 (M), the latter 0.21 short of 4; order 2 is within 0.07. (3) Not checked: the particle
samples (`.nrp` files, lattice and stratified) and the mesh file of the data set.

### C6 Dispersion axis and particle number

Recomputed: s_c = sqrt(3/10) = 0.5477 from the virial halt 2K + U = 0 with U = -(3/5) M^2/R
and sigma R conserved (arXiv:2507.18312 Main.tex:542; arXiv:2211.13950
MD_threshold10.tex:330-334), and s_c = 3/2 from R_halt = (4/9) sigma*^2 R*^2/R_ent < 2M
(MD_threshold10.tex:349-358); neither depends on the amplitude. N for b_min = 0.1 b_BH:
lattice (b_min ~ N^(-4/9), Main.tex:523) 7.9e4, 3.7e5, 1.78e6 at deltabar = 0.04, 0.02, 0.01;
random (1.2 N^(-1/3), Main.tex:489) 74 to 209 times more [VERIFIED, run 1c41333,
`fig_V6_dispersion_noise.png`]. Caveat [JUDGEMENT]: the source gives N^(-4/9) without a fitted
coefficient (Main.tex:542: "we multiplied each term ... with a certain coefficient of order
unity"); the scoping uses 1. A coefficient 2 changes the lattice N by 2^(9/4) = 4.8. Both laws are
for Newtonian cold top hats released at turnaround, not for growing-mode lattices deposited on
a mesh; the floor is an order of magnitude, to be replaced by the N-convergence of each bracket
(which the threshold definition already demands).

### C7 Horizon-mass target of the source paper

Read at `refs/arxiv_2611.12831/src/main.tex`: :945 "The fiducial run gives a relative error of
Delta M/M_ADM <~ 1e-3"; :1484 epsilon_M = 2.061e-3, 9.362e-4, 7.347e-4 for A1-A3 [VERIFIED].
The same lines say what the source did not achieve: "Increasing spatial resolution at fixed
particle number, however, does not produce a monotonic reduction in this error" (:945) and "no
monotonic convergence trend of M_irr for the fixed-N SMR sequence" (:1485). The G2 criterion
of the charter's sheet (errors of the horizon-formation time converging in N, dx and R_b) asks
for more than the reference test showed for the horizon mass.

### C8 Compute

The measured cost of `runs/jeans/n1e4_v19`: the 13 chain logs sum to 19475.5 s = 5.41
card-hours (recomputed with a one-line shell sum over `chain/seg*.log`, not registered)
[VERIFIED]. The cost model (SCOPE.md 9) and the SR-1/SR-2 estimates (10.7) are untested: the
directory of the card run A-emd-pbh-20261115-155056-ec1b816 holds only `batch.list` at the time
of writing, so there is no measured PBH-run cost to compare [NOT CONFIRMED].

Not examined at all: the periodic-box set-up (box side 2L, particle loading), the Newtonian
scan design (`newton/`), the gauge choice (`gauge/`), the spin and peak-statistics rows of the
prediction table, and the runs under `runs_ball/` and `periodic_threshold/`.

## 3. The three weakest points of the plan [JUDGEMENT]

1. **The main deliverable now rests on capabilities that do not exist, and G0/G1 tested
   none of them.** Decision 0013 moves the threshold line into the periodic box. That needs a
   problem generator for the long-wavelength data of arXiv:2609.14218 on top of `nrpic_cosmo`,
   a slicing that survives collapse in a periodic box, the horizon finder in a periodic box,
   and the background time from the box-averaged expansion (SCOPE.md 3, 4). Everything verified
   at G0/G1 (C1, C2, C5) concerns the spherical ball, which no longer carries the line, and the
   stated reason for the switch is partly wrong (C1c). G1 validates the verification case, not
   the science path.
2. **The comparison with arXiv:2609.14218 sits on the run-length cutoff.** At e = 0.2 the
   paper's bracket (0.045, 0.05] coincides with mu_fd(250 t_H) = 0.048 (C4a). The published mu =
   0.045 curve is undecided at 250 t_H (dip at ~208 t_H, and the two-stage shape of the 0.05 run
   suggests a collapse near 250 t_H), and the scoping's own timing prediction is already
   contradicted (C4b). A threshold quoted at t_end = 250 t_H near e = 0.2 measures the cutoff,
   not halting physics, unless the runs near the bracket go to 400-1000 t_H, with the cost that
   implies. The lapse-collapse times read from alpha_0 are a slicing-dependent proxy for horizon
   formation.
3. **The spherical G2 test is under-resolved as planned, and its G1 base is blind to two
   things.** The first trapped shell of data set 2t has m = 0.0805 M, i.e. a horizon of areal
   radius 0.161 M at tau = 44.35 (C5, own minimisation), while the planned meshes are dx = M/2
   (SR-1, SR-2), M/4 and M/8 (SCOPE.md 10.7): 0.3 to 1.3 cells across that radius, against the
   twelve cells per horizon radius of the scoping's own cost model (SCOPE.md 8, dx_AH =
   0.06 M_BH). Either several more refinement levels or a data set with a heavier core is needed
   before the horizon-formation time can converge. The constraint test of G1 cannot detect a
   time-reversed ball (C5, limit 1), and the horizon-mass convergence asked at G2 goes beyond
   what the source paper's own Oppenheimer-Snyder test showed (C7).
