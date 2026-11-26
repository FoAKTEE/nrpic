# JOURNAL of package g3 (Track E, gate G3): tail statistics of the curvature perturbation in the inflection scenario

Scope: `../spec/scope/SCOPE.md` section 4d (written in batch 17 before any G3 run; decision 0038 item 2).

## entry-1 (2026-11-25 03:59 PST, lead of E, batch 17): the power estimate, predictions before its run

`power.py` draws Gaussian random fields with the linear spectrum of the 128^3 USR box at N_f (the
lockstep record `usr.sf.00020.modes` of the 128^3 window-scan run b_p, E-20261120-222424-0eb754b,
nmax2 = 1024, t = tlim) and measures the box-to-box scatter of the exceedance fractions F_pm(nu),
the skewness and the kurtosis; 400 boxes, 2 cores. The difference Delta used in (a) is the 256-band
value of `../langevin/results/ref_inflection.json` (P(dN > 3 sigma_lin) = 1.57e-3 against the Gaussian
1.35e-3, Delta = 2.2e-4) until the 128-band reference (run E-20261125-115707-b845282) has run.
Predictions:
- W1: the field variance equals the linear lattice variance (var_ratio mean 1 within 0.01) and the
  mean F_+(3) is the Gaussian 1.35e-3 within three standard errors of the mean (a test of the
  synthesis and the normalisation; refuted otherwise: the script is wrong and no seed count is
  taken from it).
- W2: the effective number of independent cells for F(3) lies between 1e3 and 1e5 (the band ends at
  |n| = 32, so a box holds of order 32^3 = 3e4 independent regions; clustering of exceedances lowers it).
- W3: seeds for (a) between 5 and 300; for (b) on F(4) at least 10 times more than for F(3).

Outcome (run E-20261125-115822-29795d6, 400 boxes, 2 cores; `power.json`, `fig_power.png` looked at):
- W1 HOLDS: var_ratio 1.0001 +- 0.0002; mean F_+(3) 1.3501e-3 +- 2.5e-6 against Q(3) = 1.3499e-3;
  F_+(4) 3.167e-5 +- 3e-7 against 3.167e-5. sigma_lin = 0.4940 (record t = 10.0016 of the window
  deck, nmax2 = 1024).
- W2 REFUTED: 5.5e5 effectively independent cells for F(3), five times above the band's top. The
  spectrum rises so steeply toward k_max (P_R from 1e-5 to 0.53 across the band, ref run
  E-20261125-115707-b845282) that the field decorrelates within a few cells; my count of 32^3
  regions treated the band as flat.
- W3 REFUTED for (a): 0.46 seeds (not 5-300) detect the 256-band delta-N excess at nu = 3 at three
  standard errors; for (b) F(4) needs 26 times the seeds of F(3) (3.6 against 0.13): holds.
Consequence for the scope: statistics at nu = 3 are not seed-limited; the seed count is set by the
reach into the tail (nu = 4 to 5). SCOPE 4d.2 fixes S = 256 from these numbers.

## entry-2 (2026-11-25 04:06 PST, lead of E, batch 17): predictions for G3 (SCOPE 4d), written before any G3 run

Pilot (queue label G3P, one batch job on .work/build_gpu_v07, list `inputs/pilot.list`): ten baseline
seeds i = 0..9 (rng_seed 20262000-20262009, s = +1, geodesic, level 0), seeds i = 0, 1 under
lapse_kdriver = 2, seeds i = 0, 1 at level 2; 128^3, nmax2 = 1024, dumps at t = 0 and tlim.
- G3P-1 (cost): 0.02-0.06 card-hours per baseline seed, wall including the two dumps; level 2 at most
  1.7 times a baseline seed; kdriver within 1.2 times. Refuted outside: the budget of 4d.8 is redone.
- G3P-2 (health): every run reaches tlim with finite fields; records <abs H'/[H]> and <abs M/[M]>
  below 1e-9 and 1e-1 as in 4c U-A4'(c) (the M bar at 128^3: the G2 group-1 value 2.47e-2).
- G3P-3 (estimator on real output): per seed, sigma of R^NR at N_f within 3 per cent of sigma_lin of
  its record; the seed-to-seed standard deviation of F_+(3) of R^NR within a factor 1.4 of the
  Gaussian 4.96e-5 (power run); mean F_+(3)/Q(3) of R^NR over ten seeds in [0.9, 1.3].
G3 proper (each judged when its runs exist; refutations stay on record):
- G3-T: skewness of R^NR over 256 seeds in [-0.01, 0.05]; F_+(4)/Q(4) in [0.9, 1.4] and F_-(4)/Q(4)
  in [0.6, 1.1] for both variables. For zeta against the one-patch reference: |r(3)| and |r(4)| below
  three combined standard errors [JUDGEMENT: at N_f the band is far outside the Hubble radius and
  the separate-universe picture holds]. Refuted if |r| exceeds three combined errors at nu = 3 or 4:
  then NR differs from one-patch delta N, the result S11 asks for, and it is reported only together
  with 4d.6 and 4d.7.
- G3-C: the model test holds at every dump with cN in [2.0, 6.6] and every judged factor lies within
  4 +- 0.05 at 128^3 (G2 at 256^3: within 4 +- 0.005 with the three-amplitude level).
- G3-R: the Richardson factor of D^L from 128 to 160 in [2.0, 4.5]; T changes by less than 10 per cent.
- G3-G: zeta tail statistics agree between geodesic and kdriver slicing within three paired standard
  errors; R^NR one-point sigma differs by less than 1 per cent.
- G3-L2: level 2 moves F_pm(3) of zeta by less than 10 per cent and the skewness by less than 0.02.

## entry-3 (2026-11-25 04:10 PST, lead of E, batch 17): the per-seed reader on existing USR output, predictions

`read_seed.py` (variable (i), R^NR, as dumppass forms it; sigma_lin from the run's own record with the
function of power.py) on two existing USR runs at their last dump, before the pilot exists: the
128^3 window-scan run b_p (E-20261120-222424-0eb754b, scouting build, t = 10.0) and the 256^3
release run seed A, s = +1 (E-20261121-211214-0377aab, core-v0.6, t = tlim). A test of the
estimator on real output, not a G3 result (no seed of the G3 list).
- RS1: sigma(R^NR)/sigma_lin within [0.97, 1.03] for both (U-S found the 256^3 rms 0.894 against
  the lattice ensemble 0.89366).
- RS2: F_+(3)/Q(3) in [0.9, 1.3], F_-(3)/Q(3) in [0.7, 1.1], skewness in [-0.01, 0.05], for both.
- RS3: the one-point density follows the Gaussian of the linear variance down to 1e-5 within a
  factor 1.5 (figure). Refuted outside any band: then either the reader or the linear picture of
  the box at N_f is wrong, and G3P-3 is reconsidered before the pilot is read.

Outcome (run E-20261125-120930-980b18e, 2 cores; `W128bp.json`, `U256A.json`, `fig_seeds.png` looked at):

| | W128bp (128^3, t = 10.00) | U256A (256^3, t = tlim) |
|---|---|---|
| sigma_lin (own record) | 0.49395 | 0.89365 |
| sigma(R^NR)/sigma_lin | 1.0016 | 1.0010 |
| skewness, excess kurtosis | 0.0014, 0.011 | 0.0024, 0.0011 |
| F_+(3)/Q(3), F_-(3)/Q(3) | 1.048, 1.034 | 1.017, 1.016 |
| F_+(4)/Q(4), F_-(4)/Q(4) | 1.10, 1.22 | 1.10, 1.09 |
| extreme x | -4.95, +4.68 | -4.99, +5.11 |

- RS1 HOLDS (both within 0.2 per cent; U256A agrees with U-S's 0.894).
- RS2 HOLDS (both tails at nu = 3 within the bands; skewness 0.001-0.002). At 128 one box measures
  F(3) to 3.7 per cent (power run), so 1.048 and 1.034 are about one standard error high.
- RS3 HOLDS where the bins hold at least about 20 cells (density >= 1e-4); between 1e-4 and 1e-5 a bin
  holds a few cells and the points scatter by up to a factor 3 about the Gaussian (Poisson), so the
  band of RS3 is not testable there from one box.
Reading [JUDGEMENT]: the linear extraction R^NR is Gaussian to the precision of one box; its skewness
(0.001-0.002) is an order of magnitude below the one-patch delta-N skewness of the same band (0.023
at 128, 0.038 at 256). The non-Gaussianity that G3 compares lives in the nonlinear variable zeta
(SCOPE 4d.1 (ii)); R^NR serves as the Gaussian control and the check of sigma_lin. This is the
reason zeta and its tests come before the full set.

## entry-4 (2026-11-25 07:40 PST, lead of E, batch 19): predictions for the amended criteria (SCOPE 4d.9), before any G3 production run

The scope review (`scope_review/SCOPE_REVIEW.md`) and the lead's checks (`amend/JOURNAL.md` entries 1-4)
changed 4d by the dated amendments A1-A13 of SCOPE 4d.9. Entry 2's G3-T and G3-G are superseded as stated
here; G3P-1..3, G3-C (as amended by A6), G3-R and G3-L2 of entry 2 stand. Refutations stay on record.
- Z0 (32^3, s = +-1/4): rms(O_zeta + O_R)/rms(O_R) about 1e-4, below the 1e-3 bar (the difference is third
  order in s plus the chi and anisotropic terms of R^NR, about 1e-6 of sigma). Refuted above 1e-3.
- Z1: first and second finite-difference coefficients of the reader's Delta N_bg within 0.1 per cent of
  the independent integrator (bar 1 per cent). Refuted above 1 per cent.
- Z2 (32^3): a_zeta > 0 (delta-N skewness positive in this scenario), a_zeta sigma_lin in [0.002, 0.008]
  (a local quadratic model gives skewness = 6 a sigma, and the reference skewness lies at 0.02-0.04);
  a_zeta at s = 1/4 and 1/2 agree within 2 per cent. Refuted outside any band.
- V (128 pairs): |sigma^2_zeta/var_ref - 1| below three combined standard errors and below 0.01 (the
  window-scan box gave sd(R^NR)/sigma_lin = 1.0016 on one box, E-20261125-120930-980b18e).
- T (128 pairs, zeta against the corrected reference): skewness of zeta in [0.015, 0.032] and within three
  combined standard errors of the reference's 0.0234 +- 0.0037 (2e5 pilot; the 4e6 value replaces it);
  A(3) of zeta in [0.05, 0.16] (pilot reference 0.108); F_+(4)/Q(4) of zeta in [1.1, 1.8], F_-(4)/Q(4) in
  [0.5, 1.0]. For R^NR: skewness in [0, 0.002] (review N1: 8.4e-4 on one pair), F_pm(4)/Q(4) in [0.85, 1.2]
  both. "NR differs in the tail" is not expected [JUDGEMENT: at N_f the band is far outside the Hubble
  radius; the box's own non-Gaussianity, a_R = 2.8e-4, is below the comparison's reach (review S1)].
- A4: variance of the box's d phi at N_f within 1 per cent of the reference's phi variance at N_f; both
  skewnesses below 0.005 in magnitude [JUDGEMENT: the non-Gaussianity enters through the map].
- G3-C with A6 (six 128^3 runs): M judged at four or more dumps for both factors; H for 1 over 1/2 at four
  or more; H for 1/2 over 1/4 may come out "not testable" [JUDGEMENT, about even odds: at 256^3 G2 judged H
  at three dumps from the quarter pair]. Every judged factor within 4 +- 0.05; the model test holds at two
  thirds of the dumps of the range or more.
- G3-R with A7: Richardson factor of the maximum and median of D^L from 128 to 160 in [2.3, 4.0] (order four
  to six at the ratio 1.25); the sign agrees at 128 and 160 for more than 90 per cent of the modes.
- A8 (pilot k000/k001, read for the record): rms(alpha - 1) at N_f below 1e-5 and rms of H int (alpha - 1)
  dt below 1e-3 sigma_lin.
- A9: a tilted run of 4e6 paths per side reaches a relative standard error at or below 2 per cent at nu = 4
  [JUDGEMENT; refuted if above 3 per cent with the shift that centres the tilted median in [3.5, 4.5]].

## entry-5 (2026-11-25 18:21 PST, lead of E, batch 23): the pilot has ended; predictions for its reading, written before any read

The pilot (queue q0050, run E-20261126-002413-65295f3, job 5340, 17:46:42-18:07:51 PST) is closed by `nrpic-run
finish` with status "failed (exit 1)": the ten baseline members b000-b009 ended with rc = 0; the four others
stopped at start-up, before any step, because `athenak/src/parameter_input.cpp` line 400 only replaces lines the
deck already has: `Parameter 'lapse_kdriver' in block 'z4c' on command line not found` (k000, k001) and
`Parameter 'noise_mode_eq' in block 'scalar_field' on command line not found` (l000, l001). The deck
`g2prod/inputs/usr_prod.athinput` has neither line. A defect of my list, not of the code; no card time was spent
on them (1-2 s each). The other waiting lists (base00, base01, g3c, g3r) use only lines the deck has (checked
with awk over every override of every list, this session).
Predictions for the reading (only b000-b009 exist; `read_pilot.py`, `compare_readers.py`, `../zeta/z1_variational.py`):
- G3P-1 (cost) for the baseline as written in entry 2: 0.02-0.06 card-hours a run. kdriver and level 2: not
  measurable (failed); recorded as such, not as a pass.
- G3P-2 and G3P-3 as written in entry 2 (H' as column 25 <|H-<H>|/[H]>, M as column 7 <|M|/[M]> of
  `usr.sf.con.hst`, maximum over all records).
- P5-1 (map applies): v = Pi/H_cell > 0 in every cell of every member.
- P5-2 (readers per cell, b000 at N_f): the lead's map (zeta_reader.py's V, dV, map_rk4, verbatim through ast)
  and the verifier's (zv_lib long-double RK4 in N, h = 2e-3, phi_e from the lockstep record) give per-cell zeta
  (box means removed) with max |difference| below 1e-8 and rms below 2e-9 (basis: 2.2e-9 in N along the relation
  for |zeta| <= 3, E-20261125-173501-2644c27). Refuted above 1e-6 at the maximum: then the 128 band carries
  states where the two maps differ and the reader is not cleared for G3 at 128.
- P5-3 (steps): the lead's map at 1000 steps against 4000 on 20000 random cells per member: max |dN| below 1e-9.
- P5-4 (box relation at 128, single members): correlation of (Pi - <Pi>) with (phi - <phi>) above 0.999 and the
  slope within 10 per cent of the 32^3 value 0.0132235 [JUDGEMENT: the high-k end of the 128 band left the
  horizon later]. Refuted below 0.99.
- P5-5 (zeta, ten single members; a preview of (T), not its judgement, which needs the pairs): sd(zeta)/sigma_lin
  in [0.98, 1.02]; mean skewness of zeta in [0.015, 0.032]; skew(zeta) + skew(R^NR) per member (the part free of
  Gaussian sample scatter) in [0.017, 0.023] (6 a_zeta sigma_lin with a_zeta = 6.76e-3 of the 32^3 pairs and
  sigma_lin = 0.494); mean A(3) of zeta with its own sd in [0.05, 0.16]; mean F_+(4)/Q(4) in [1.1, 1.8],
  F_-(4)/Q(4) in [0.5, 1.0]. For R^NR: mean skewness in [-0.002, 0.004] (per-member sample scatter about
  sqrt(6/5.5e5) = 0.0033, entry 1's effective cell count).

## entry-6 (2026-11-25 18:27 PST, lead of E, batch 23): predictions for the next card entries, written before they are queued

To be queued only if the pilot's reading (entry 5) holds. Lists (every override checked against its deck with
`check_lists.py`): `inputs/base02.list` .. `base06.list` (mirrored pairs 19-29, 30-40, 41-51, 52-62, 63-73; 22 runs a
job; queue labels G3B02..G3B06, preregistered to entry 4 like G3B00/G3B01) and `inputs/l2_00.list` (level 2, mirrored
pairs 0-4 at noise_level = 2, mesh mode by default, the same seeds and modes as baseline pairs 0-4; with k000, k001 of
the pilot on `inputs/usr_prod_kd.athinput`, the production deck with the line lapse_kdriver = 0.0 added; label G3L00).
- C6-1 (cost, baseline): 0.033-0.038 card-hours a run (pilot 0.0351, 125-128 s), a job of 22 in 45-50 minutes.
  Refuted if a job reaches its 55-minute limit.
- C6-2 (cost, level 2 at 128^3): wall per run 1.1-1.7 times the baseline run (core's interface: 1.14-1.16 at 64^3,
  1.63 at 256^3; coord/INTERFACES/noise_level2.md); kdriver within 1.2 times (G3P-1). Refuted outside.
- C6-3 (health): G3P-2 of entry 2 for every member of every job.
- C6-4 (level 2, preview on five pairs; G3-L2 of entry 2 is judged on all 16): per pair, level 2 changes F_pm(3) of
  zeta by less than 10 per cent and the skewness by less than 0.02 against the level-0 pair of the same seed.
- A8 (entry 4) for k000/k001: rms(alpha - 1) at N_f below 1e-5 and rms of H int (alpha - 1) dt below 1e-3 sigma_lin.
