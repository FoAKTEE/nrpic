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

## entry-7 (2026-11-25 18:49 PST, lead of E, batch 23): the first reading runs were stopped; what changes, before the rerun

Both runs of entry 5 were stopped by `nrpic-run stop` after 24 minutes with no member finished (E-20261126-022447-40a80b4,
E-20261126-022448-9510ee9, status stopped, no output): on this machine (load 85-100) the lead's map at 4000 steps on a
full 128^3 dump takes far more than R41's 11 core-minutes (at least 24, likely about 40: the 32^3 timing did not carry
over; the arrays no longer fit in cache). R41 is restated. Changes, nothing else: the pilot reading runs the map at 1000
steps for every cell, with the 4000-step map on 20000 random cells per member as the check of P5-3 (the same comparison
entry 5 predicted, the other way round); the cell-by-cell comparison of P5-2 runs on 100000 random cells of b000 plus
every cell with |R^NR| > 2.5 sigma_lin (about 25000), the cells that decide F(3) and F(4). Predictions of entry 5 stand
as written; P5-2 is judged on those cells.

## entry-8 (2026-11-25 19:09 PST, lead of E, batch 23): zeta of the pilot is not read this session

The rerun at 1000 steps (E-20261126-024953-ed2d15f) was stopped after 18 minutes with no member finished: the map is
memory-bound on 2.1e6 cells (about 220 array passes a step), so on this machine a member takes of order 1.5 hours at 1000
steps and some 6 at 4000. P5-3 and P5-5 (zeta) are not judged this session; P5-1 and P5-4 and the R^NR part (G3P-2,
G3P-3) are read now with `read_pilot.py --msteps 0` (no map). The zeta of G3 needs a cheaper evaluation of the same map
before the baseline can be read (R41: a table of the map along the box relation with its second-order correction
across it, checked against map_rk4 on sampled cells, is the candidate); written into the handoff. The pilot holds or not
on G3P-1..3 as entry 2 defined it (R^NR is the variable of G3P-3).

## entry-9 (2026-11-25 19:11 PST, lead of E, batch 23): outcomes of entries 5 and 7 (pilot without zeta; readers cell by cell)

Runs: pilot reading E-20261126-030904-76e7c72 (`read_pilot.py --msteps 0`, ten members; `pilot.json`, `fig_pilot.png`
looked at); readers cell by cell E-20261126-024954-1c0a893 (`compare.json`, `fig_compare.png` looked at).
- G3P-1 HOLDS for the baseline: 125-128 s a run, mean 0.0351 card-hours (batch status of job 5340). Level 2 and kdriver:
  NOT MEASURED (their members stopped at start-up; entry 5).
- G3P-2 HOLDS (ten members): all reach t = 10.4375 = tlim with finite records; max over records <|H-<H>|/[H]> = 7.15e-12
  (bar 1e-9), max <|M|/[M]> = 0.0323 (bar 1e-1; G2 group 1 had 2.47e-2).
- G3P-3: sigma(R^NR)/sigma_lin = 1.0002-1.0029 per member (bar 3 per cent): holds. Mean F_+(3)/Q(3) of R^NR over ten
  members 1.0075 (band [0.9, 1.3]): holds; F_-(3)/Q(3) 0.994. Seed-to-seed sd of F_+(3) = 6.96e-5 against the Gaussian
  4.96e-5: ratio 1.403, the bar was "within a factor 1.4": FAILED as written by 0.3 per cent of the bar. With ten members
  the sd itself is uncertain by about 24 per cent (1/sqrt(18)); F_-(3) gives 0.84 of the Gaussian value. Recorded as a
  failed clause, not a defect found [JUDGEMENT].
- P5-1 HOLDS: no cell with v <= 0 in any member. P5-4 HOLDS: corr(d phi, d Pi) = 0.9999971 (bar 0.999), slope 0.0132252
  against 0.0132235 at 32^3 (+0.013 per cent). rms dK/|K| at N_f = 5.0e-13.
- P5-2 HOLDS: lead's map (4000 steps) and verifier's (long double, h = 2e-3) on 124402 cells of b000 (100000 random,
  25668 with |R^NR| > 2.5 sigma_lin): max |difference| 4.26e-9 (bar 1e-8), rms 9.1e-10 (bar 2e-9); no cell changes side
  at 3 or 4 sigma_lin; the two parsers read identical fields. The verifier's map took 967 s for 1.2e5 cells.
- R^NR one-point, ten members: mean skewness 0.0006 (band [-0.002, 0.004]: holds), member scatter 0.0041 (entry 1's
  sqrt(6/N_eff) = 0.0033); excess kurtosis -0.003; F_pm(4)/Q(4) 0.968, 0.976.
- P5-3 and P5-5 (zeta): NOT JUDGED (entry 8).
Reading: the pilot holds for the baseline on G3P-1..3 with one clause failed narrowly as written; the box is healthy and
R^NR is Gaussian to one-box precision, as at 128^3 before (entry 3). The two zeta readers agree per cell at 1e-8 of
sigma on the G3 box. What is not yet possible is reading zeta on 2.1e6 cells a member at acceptable cost (R41).

## entry-10 (2026-11-26 03:50 PST, lead of E, batch 27): readings of G3C and G3R, and the table map; predictions before any read

G3C (q0051, run E-20261126-030044-6933f21, job 5348) and G3R (q0052, run E-20261126-041110-0a78c93, job 5353) have
ended (batch status rc = 0 for all six and all four members); `nrpic-run finish` closes them before any read. Nothing
of them has been read yet. Readers written this session, before any read: `read_g3c.py` (4d.4 with A6, own code on
card_lib.read_fields; D1, D2, sigma per cell as 4d.4 says; M = (Mx, My, Mz) together, box mean removed per component;
cN from the efolds column of c_p1's con.hst at the dump's cycle; the 4c estimator of judge_g2.floor_halving beside it
for both amplitude pairs) and `read_g3r.py` (4d.5 with A7; per-mode coefficients of card_lib.Extractor, reference
card_lib.ShellReference on modes_usr_n1024.txt with alpha_n of rng_seed 20262000; modes |n| <= 16; for A7's "sign"
of the complex ratio L_n/cref_n - 1 the sign of its real part, fixed here; the imaginary part is reported).
Predictions are those of entry 2 (G3-C, G3-R) and entry 4 (G3-C with A6, G3-R with A7), unchanged. Restated for the
record: G3-C every judged factor within 4 +- 0.05, M judged at >= 4 dumps for both factors, H for 1 over 1/2 at >= 4,
H for 1/2 over 1/4 possibly "not testable" (even odds), model test holding at >= 2/3 of the dumps in the range;
G3-R factor of max and median of D^L in [2.3, 4.0] (bar [2.0, 4.5]), sign agreement > 90 per cent, T changes < 10
per cent. One addition before the read [JUDGEMENT]: at 128^3 the M factor at the late dumps (cN near 6.5) is where
G2 missed at 256^3 (3.9245); the three-amplitude level is expected to bring it inside the band here too.

Table map for zeta (R41; `zeta_table.py`, written this session, nothing run yet). Per member, from the member's own
dump at N_f: v = Pi/(-K/3); the box relation v = v0 + b (phi - <phi>) by least squares; u = phi - <phi>, w = v - v0 -
b u. Table of the lead's map_rk4 (4000 steps, verbatim through ast as read_pilot.py does) on 4097 uniform nodes in u
over the box range (2 per cent margin) times 7 Chebyshev nodes in w over the box range (5 per cent margin); per cell
a not-a-knot cubic spline in u at each w node and the Lagrange polynomial through the 7 w nodes. Cost: 28679 map
evaluations instead of 2.1e6.
- TB-1 (bar, validation on b000 of the pilot at N_f, the 124402 cells of compare_readers.py: 100000 random with
  seed 11 plus every cell with |R^NR| > 2.5 sigma_lin): zeta of the table against zeta of map_rk4 at 4000 steps on
  every one of these cells: max |difference| <= 1e-10, rms <= 2e-11 (two orders under the readers' agreement,
  4.26e-9, entry 9). Refuted above 1e-9 at the maximum: then the table is not used and the baseline waits.
- TB-2: table against the verifier's map (zv_lib, long double, h = 2e-3) on the 25668 tail cells of b000: max
  |difference| (means removed) below 1e-8 and rms below 2e-9, the P5-2 bar. Refuted above 1e-6.
- TB-3 (cost): table plus evaluation under 3 core-minutes a member at 128^3 on this machine (load about 50).
  Refuted above 10.
Then the pilot's zeta with the table, ten members, P5-3 (1000 against 4000 steps on 20000 random cells per member,
max |dN| below 1e-9) and P5-5 (as written in entry 5) judged as written; per member a spot check of the table
against map_rk4 at 4000 steps on 4000 cells (2000 random, 2000 of the largest |R^NR|) with TB-1's bar.

## entry-11 (2026-11-26 04:00 PST, lead of E, batch 27): TB-1 refuted; a diagnostic, prediction before it runs

Outcome of entry 10 (run E-20261126-115112-43da266, `validate.json`): TB-1 REFUTED as written: table against map_rk4 at
4000 steps on 124402 cells of b000, max |difference| 5.41e-9, rms 1.23e-9 (bar 1e-10 / 2e-11, refuted above 1e-9).
TB-2 HOLDS: table against the verifier's long-double map on the 25668 tail cells (means removed), max 3.87e-9, rms
9.8e-10 (bar 1e-8 / 2e-9). TB-3 HOLDS: 22 s for table and evaluation on the whole box (bar 180 s), against 82 s for
the full map on 124402 cells. By entry 10's rule the table is not used for G3 readings as it stands. Three
differences on the same cells (lead full map L, table T, verifier V; rms 0.91e-9 L-V from entry 9, 0.98e-9 T-V,
1.23e-9 T-L) are consistent with independent noise of about 0.8e-9 in L, 0.9e-9 in T and 0.4e-9 in V; T and L share
the same 4000-step map at the nodes, so a smooth step error would cancel between them [JUDGEMENT: the 4000-step map
is not smooth in (phi, v) at 1e-9, or the table does not resolve it].
Diagnostic (`diag_table.py`, 20000 cells of b000: the 2.5-sigma tail cells first, filled with random cells): (a) map_rk4
at 4000 steps, (b) at 16000 steps, (c) the table on 4000-step nodes, (d) the table on 16000-step nodes, (e) the
verifier's map. Prediction: if the 1e-9 part is the fixed-step error of map_rk4 (not smooth across cells), then
rms(b - e) and rms(d - e) fall below 1e-10 and rms(d - b) below 1e-10 while rms(c - a) stays near 1e-9; refuted if
rms(d - b) stays above 3e-10 (then the table's interpolation is the cause and the table needs more nodes). Either
way the outcome is a reason, not a new bar: TB-1 stays refuted as written; a table on 16000-step nodes would be
judged against a bar written here before its run: max |d - b| <= 1e-9 and max |d - e| <= 4.3e-9 (the cleared
readers' agreement of entry 9).
The pilot reading with a table on 16000-step nodes (`read_pilot.py --map table --msteps 16000`; P5-3 stays 1000
against 4000 steps of the full map on 20000 random cells per member, as written) is started beside the diagnostic to
save time; its zeta numbers are judged against P5-5 only if the diagnostic meets the table16000 bar above, otherwise
they are recorded as not judged.

## entry-12 (2026-11-26 04:04 PST, lead of E, batch 27): outcome of entry 11; the rule for the table, before its reading

Diagnostic E-20261126-115925-a2c6da5 (`diag.json`, `fig_diag.png` looked at; 20000 tail cells of b000), rms / max
with means removed: rk4(4000) - verifier 0.99e-9 / 4.25e-9; rk4(16000) - verifier 3.55e-9 / 9.74e-9; table4000 -
rk4(4000) 1.29e-9 / 5.42e-9; table16000 - rk4(16000) 4.86e-9 / 1.82e-8; table4000 - verifier 0.99e-9 / 3.87e-9;
table16000 - verifier 3.36e-9 / 9.24e-9. Both alternatives of entry 11 are REFUTED: the step error is not the cause
(16000 steps are four times further from the long-double map than 4000, not 256 times closer), and the table16000
bar fails (max |d - b| 1.8e-8 > 1e-9). The prediction's "interpolation" flag is set by its rule but the reading is
another one: the difference between rk4(16000) and rk4(4000) sits on discrete levels (fig_diag left panel), the mark
of round-off in the double-precision fixed-step map (p += h accumulated m times misses phi_e by whole ulps, scaled
by dN/dphi at the end), which grows with the number of steps. This run could have refuted that cause (16000 steps
closer to the verifier) and did not. So map_rk4 at 4000 steps carries round-off noise of about 1e-9 per cell; a
table built on it inherits noise of the same size; TB-1's bar (1e-10 against map_rk4) lay below the noise of its
own reference: TB-1 stays FAILED as written. The pilot reading started with 16000-step nodes (E-20261126-115929-84cd060)
fails the table16000 bar and its zeta numbers are NOT judged (its P5-3 part, full map 1000 against 4000 steps, is
independent of the table and is judged).
Rule from here (written before the reading below): the G3 reader of zeta is the table on 4000-step nodes (the
lead's cleared map, unchanged) when (i) on b000 it agrees with the verifier's long-double map within the readers'
agreement of entry 9 (max 4.3e-9) [post hoc for b000: measured as 3.87e-9 in E-20261126-115112-43da266 and
E-20261126-115925-a2c6da5 before this rule], and (ii) on every member its spot check against map_rk4(4000) (4000
cells: 2000 random, the 2000 largest |R^NR|) stays below 1e-8, twice the largest difference seen between two cleared
maps. The noise (1e-9 = 2e-9 sigma_lin) moves a cell across nu = 3 with probability about 4e-12 per cell; no
statistic of 4d.1 resolves it [JUDGEMENT]. Pilot reading on these terms: `read_pilot.py --map table --msteps 4000`,
P5-3 and P5-5 judged as written in entry 5; prediction (ii) per member max below 6e-9.

## entry-13 (2026-11-26 04:08 PST, lead of E, batch 27): outcomes of entries 10-12 (G3-C, G3-R, table, pilot zeta)

Runs (all registered, figures looked at): G3C and G3R closed by `nrpic-run finish` (E-20261126-030044-6933f21, 52.4 GB,
and E-20261126-041110-0a78c93, 13.2 GB, status completed; card time 15.8 and 21 minutes); G3-C reading
E-20261126-115943-32970f2 (`g3c.json`, `fig_g3c.png`); G3-R reading E-20261126-120438-9d48377 (`g3r.json`,
`fig_g3r.png`); pilot zeta with the 4000-node table E-20261126-120434-5dda273 (`pilot.json`, `fig_pilot.png`); the
16000-node reading E-20261126-115929-84cd060 is on record, its zeta not judged (entry 12).
- G3-C (4d.4 with A6) PASSES as written. Ten dumps in cN [2.0, 6.6]; the model test holds at all ten for H and for M
  (rms D2/rms D1 0.999-1.003, corr -0.234 to -0.245; model -4/17 = -0.235). Judged factors: H 1 over 1/2 at 8 dumps,
  max |f - 4| 8.4e-4; H 1/2 over 1/4 at 5 dumps, 1.3e-4; M 1 over 1/2 at 8 dumps, 6.8e-4; M 1/2 over 1/4 at 6
  dumps, 1.2e-4 (band 0.05). Entry 4's prediction holds, including the even-odds clause: H 1/2 over 1/4 was testable
  (5 dumps). Entry 10's addition holds in this sense: the 4c two-amplitude estimator (reported, not judged) leaves
  the band at the late dumps (M: 3.80 at cN 4.54, 3.55 at 5.04; H: 3.85 at 4.05, 5.19 at 5.04, 5.27 at 5.53, all with
  the 1/2-over-1/4 pair, whose floor estimate is poor), the three-amplitude level brings every judged factor to
  4 within 1e-3: the G2 failure of U-A4'(a) is a failure of the floor estimator, now shown on a run designed for it.
  Outside the range (reported): beyond cN 7 the even parts fall below 3 sigma and nothing is judged.
- G3-R (4d.5 with A7) PASSES as written: 8538 modes |n| <= 16 at N_f; max D^L 1.146e-4 (128) and 3.68e-5 (160),
  factor 3.12; median of the per-mode ratio 2.63; Re(L/cref - 1) has the same sign at both resolutions for 100 per
  cent of the modes (imaginary part 99.6). Entry 4's [2.3, 4.0] holds for both. Reported: O(1) alone, factor of max
  3.41 but median ratio 1.54 and sign agreement 0.74 (T caps it: |T/cref| = 1.28e-5 on every mode at both
  resolutions, `fig_g3r.png` right); T changes by 5.6e-4 between resolutions (prediction below 0.1 holds). At the
  lowest modes D^L falls from 1.4e-6 to 0.6e-6, a factor near 1.25^4 = 2.44.
- Table rule of entry 12: (i) b000 against the verifier 3.87e-9 <= 4.3e-9 [post hoc, measured before the rule];
  (ii) spot check against map_rk4(4000) on 4000 cells per member: max 4.45e-9 to 5.91e-9, all below 1e-8; the
  prediction "below 6e-9" holds, narrowly (b002 5.907e-9). The `spot_holds` field of the member json files uses
  TB-1's 1e-10 bar and reads false; the rule's bar is 1e-8. Table and evaluation 16-23 s a member (TB-3).
- P5-3 FAILED as written: 1000 against 4000 steps, max |dN| 3.2e-9 to 4.1e-9 per member against 1e-9. Reading: the
  round-off of entry 12 (about 1e-9 at 4000 steps, quantized levels); 4e-9 is 8e-9 sigma_lin [JUDGEMENT: below
  every statistic of 4d.1].
- P5-5 (preview, ten single members; zeta from the 4000-node table) HOLDS on every clause: sd(zeta)/sigma_lin
  1.0003-1.0030 (mean 1.0016; band [0.98, 1.02]); mean skewness of zeta 0.0200 (sd 0.0040; band [0.015, 0.032]);
  skew(zeta) + skew(R^NR) per member 0.0204-0.0208 (sd 1.2e-4; band [0.017, 0.023]; 6 a_zeta sigma_lin = 0.0200);
  mean A(3) of zeta 0.082 (sd 0.028; band [0.05, 0.16]); mean F_+(4)/Q(4) 1.195 (band [1.1, 1.8]) and F_-(4)/Q(4)
  0.751 (band [0.5, 1.0]); F_+(3)/Q 1.071, F_-(3)/Q 0.909; excess kurtosis -0.003; corr(zeta, R^NR) -0.999988.
  For orientation only (not the (T) comparison, which needs the 128 pairs): the 4e6 reference skewness is 0.0199
  +- 0.0012 (E-20261125-152832-c301e92); ten members give 0.0200 +- 0.0013.
Consequence: the zeta of a 128^3 member costs about 20 s of table plus the reading (about 1.5 min a member in all on
one core of the loaded machine), against 1.5 core-hours before (R41): 256 members take about 6 core-hours. R41 closes.

## entry-14 (2026-11-27 15:27 PST, lead of E, batch 34): two jobs were preempted; what is re-queued, predictions before it is queued

State found at the start of batch 34 (from the batch status files and Slurm logs, before any read of the dumps): G3B00-G3B05
(q0053, q0054, q0061-q0064) ended with every member rc = 0 (14, 14, 22, 22, 22, 22 runs). G3B06 (q0065, job 5419) was CANCELLED
DUE TO PREEMPTION at 2026-11-26 18:04:09 PST after 17 of its 22 members (p063-p071, m063-m070 rc = 0; m071 cut at cycle 220;
pairs 72-73 not started). G3L00 (q0066, job 5420) was CANCELLED DUE TO PREEMPTION at 18:07:39 PST while its first member lp000
was at cycle 820 of about 850 (no member finished; k000/k001 and the other level-2 members not started). The queue lists both
entries as "done"; the dispatcher does not resubmit a preempted batch job. Complete now: pairs 0-70 (142 runs) and p071.
Seen before this entry was written (so not a prediction): lp000's log gives 131.5 s at cycle 820 against 0.149 s a cycle of the
baseline member p070 (32.7 s at cycle 220): a level-2 step costs about 1.08 times a baseline step at 128^3, below C6-2's band.
Re-queued at priority 2 (the G3 package waits for them), lists written by `inputs/gen_lists.py` from the lines of base06 and
l2_00 with seed and sign changed only, every override checked with `check_lists.py`, release card build core-v0.7 as the common
set-up of SCOPE 4d fixes (core-v0.8 changes restart outputs, the finder and figure files only, none of which these runs use;
keeping one build for the whole set is the scope's rule [JUDGEMENT]): G3B07 (m071 and pairs 72-81, 21 runs), G3B08-G3B11 (pairs
82-92, 93-103, 104-114, 115-125, 22 runs each), G3L00 again (l2_00.list unchanged: level-2 pairs 0-4 with k000, k001), G3L01
(level-2 pairs 5-10), G3L02 (level-2 pairs 11-15 with the baseline pairs 126-127). The incomplete m071 of job 5419 is not read.
Predictions (entry 6 restated, unchanged): C6-1 a baseline run 0.033-0.038 card-hours, a job of 22 in 45-50 minutes, refuted if a
job reaches its 55-minute limit; C6-2 a level-2 run 1.1-1.7 times a baseline run (the partial lp000 above points below the band;
the band is not moved); C6-3 G3P-2 for every member; C6-4 and A8 as written in entries 2, 4, 6. A job preempted again keeps its
finished members; the rest are listed anew with the same seeds (SCOPE 4d: never skipped) and the preemption stays on record.
