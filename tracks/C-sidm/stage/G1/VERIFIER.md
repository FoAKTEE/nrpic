# VERIFIER: fresh-context verification of the G1 material of C-sidm (criterion C17)

Verifier: package `tracks/C-sidm/verify_g1/` (wave 3; resumed in batch 2b). Own code only (no
module of the track imported or copied; python/nrpic readers of the formats used). Every
computation is a registered run; predictions and outcomes in `verify_g1/JOURNAL.md`.

Order of work (decision 0016 item 4): the blind verdicts `verify_g1/VERDICTS_BLIND.md` were
written from the test definitions, the raw run outputs, the model files and the papers, and
committed and pushed (commit 00adbb95) before any claim was read. Only then were the claims
below read: `stage/G1/CHECKLIST.md`, `stage/G1/EVIDENCE.md`, `heat/README.md`,
`box_tests/README.md`, `models/README.md`, `stage/REVIEW-wave2.md` sections 1-3 and 6.
Exposures before that point (recorded in the journal): one row of core's own T12 claim in the
interface text (entry 7); the names and `role` labels of the track's model files (entries 9,
12), read while checking against them as the task asked.

Runs of the verifier: C-20261120-222423-519f12b (V1a), C-20261120-223130-6742500 (V1b),
C-20261120-223133-2f98a0e (V1c), C-20261121-074926-5d9ae56 (V2), C-20261121-075256-2084cb5
(V3), C-20261121-080313-84094f1 (V4), C-20261121-080720-dbcd7ff (V4b), C-20261121-081036-0d6117b
(V5), C-20261121-081415-b8c9d29 (V5b), C-20261121-081715-2ad1421 (claim checks of this file).
Failed or superseded runs on record: C-20261120-222754-14bd23d (V1b first evaluation, same
numbers), C-20261121-080152-b8d0acd (V4, failed at its figure), C-20261121-080633-8ee41f7 (V4b,
sample check invalid: my sign error).

## 1. Claims against my values

Agree = same number within the stated errors or to the printed digits; differ = a different
number (cause given); not checked = no computation of mine.

| Claim (file:line) | My value | Verdict | Comment |
|---|---|---|---|
| T1 per step <= 2.8e-19 of sum M W, 1e-7 of the bound; sum M W bit-identical start to end (box_tests/README.md:76; EVIDENCE.md:14) | per-step defects <= 1.1e-7 of the bound; snapshot sum M W unchanged (exactly rounded) in all 16 runs | agree | V2 |
| T1 over 1e4 steps: 1.56e7 collisions, sum M W bit-identical at 11 snapshots (box_tests/README.md:77; REVIEW-wave2.md:44-46) | drift 0.0 at all 11 snapshots, 1.559e7 / 1.560e7 collisions | agree | V5 |
| T2: ratio 0.99991-1.00010, z_b -2.2..2.9, z_a -2.1..1.6 (box_tests/README.md:78; EVIDENCE.md:15; REVIEW-wave2.md:37-42) | 0.999906-1.000096 against my own Moller quadrature; z (step-to-step se) -2.20..+2.92; z_a -2.10..+1.58 | agree | V2. With a batch-mean error two configurations reach z = 4.21, -4.55; the tested pairs follow the sample's own pair mean (\|z\| <= 2.26): the 1e-4 sample effect of TESTS 2a |
| R3: counts identical to the release in all 3200 steps (box_tests/README.md:142; REVIEW-wave2.md:223-226) | n_tested and n_coll identical in all 200 steps of all 16 cases; sum_P to 8.9e-16 | agree | V2 (final momenta between the executables not compared) |
| T3: KS p 0.084-0.99; <u^2/W>/3 = theta_eq within 0.01 se; populations ~1 se (box_tests/README.md:79; REVIEW-wave2.md:50-52) | KS p 0.084, 0.77, 0.99, 0.92; \|z\| <= 0.007; populations \|z\| <= 0.78 | agree | V5 |
| T4: slope/exact 0.9924, 0.9792, 0.9959, 1.0088 (box_tests/README.md:80; EVIDENCE.md:16) | 0.9963, 0.9826, 1.0003, 1.0088 against my own exact rate (quadratic fit over 16 snapshots, t = 0 ... 0.15 tau_rel) | agree within 1 se; differ in the window | the lead's recheck (REVIEW-wave2.md:68-71) found exactly my numbers with 16 snapshots; the README values use one snapshot fewer. Both pass. My tau_rel equals the generator's to 0.1 percent |
| T4 refutes \|v_a - v_b\|: 1.27 at theta_2 = 1 (TESTS.md T4) | 1.265; 1.0007 at 1e-3 | agree | V5 |
| T5 PASS 4/4 (box_tests/README.md:81; CHECKLIST.md:33) | - | not checked | needs an entropy estimator with a bias study |
| T9: same theta z in [-1.2, 0.6]; KS p >= 0.089; mean energy drift +2.4 se, +0.18(7) percent of the thermal energy (box_tests/README.md:82, 104-105; REVIEW-wave2.md:53-54) | class difference z in [-1.16, 0.56]; KS p >= 0.089 against each class's own theta, >= 0.084 against the theta of the final energy, but p = 1.7e-4 (light class, seed 3) against the theta of the initial energy; drift +5.3(2.2)e-5 of the total energy, z = 2.42 (= 0.18 percent of the thermal energy) | agree, with a reservation | the KS clause passes only if the reference temperature is the class's own or that of the final energy: the nanbu energy drift of seed 3 (+1.48e-4) shifts theta by exactly the offset seen (V5b). T9 should name its reference temperature |
| T9 refusal with coll_weights = equal names the masses (box_tests/README.md:82) | message "unequal rest masses (smallest and largest ...)" | agree | V5 |
| T10 release: 1/8/64 MeshBlocks and restarts from 0, 37, 74 bit-identical; seed 8 changes every particle (box_tests/README.md:83; REVIEW-wave2.md:47-49) | final snapshots byte-identical (run C-20261115-165902-f9b1c8f, checked with the claim run); seed 8 differs | agree | claim check C-20261121-081715-2ad1421 |
| "seed 8 differs in every particle (385554 collisions)" (REVIEW-wave2.md:49) | 385554 is the collision count of the seed-7 runs (mb1, mb8, mb64 alike); seed 8 has 385838 | differ (wording) | the parenthesis attaches the count to the wrong run |
| R4: MeshBlocks and restarts bit-identical; 385554 collisions as the release (box_tests/README.md:144; REVIEW-wave2.md:227-229; EVIDENCE.md:65) | snapshots byte-identical; restart histories identical record by record; 385554 collisions in all three MeshBlock variants | agree | V5 and claim check. The MeshBlock variants' histories differ in the last bits of the sums (sum_P, sum_MW, sum_W to <= 1.8e-13), not in counts: summation order, history only |
| T10 "byte-identical records" (EVIDENCE.md:19) | particle records of the snapshots byte-identical; the coll.hst records of different MeshBlock divisions are not byte-identical (sums) | agree if "records" means the snapshot records | wording |
| R5 T12: rate per coordinate time and volume / flat twin = alpha0 psi0^6 = 1.41725 exactly; analytic 0.99997-1.00009 (\|z\| <= 2.4); T1 within 3.6e-7 of the bound; cell = particle (box_tests/README.md:145; REVIEW-wave2.md:230-237; EVIDENCE.md:66) | ratio 1.417249 (identical counts in all 200 steps of 4 pairs); my expectation gives 1.0000896, 0.9999717, 1.0000718, 1.0000525; per-step defects <= 3.6e-7 of the bound; cell = particle in counts, momenta within 1.3e-14 | agree | V3; also pair counting sum_W = my own count to 4e-13 |
| "T12 position bookkeeping ... not investigated by either of us" (REVIEW-wave2.md:252-253) | psi0^2 (x_curved - 10) = x_flat - 10 within 4.0e-13 after the periodic wrap, end momenta u_i/psi0^2 = flat u_i within 2.5e-13 | now checked | V3 |
| T6(b): literal chi_fit/chi(kappa_1, 0.015) = 0.994, 1.027; f = 1.029, 1.063 against the nonlinear reference (heat/README.md:105, 170; EVIDENCE.md:84; CHECKLIST.md:33) | linear form with chi_1 at the final particle-weighted temperature 0.013359: 1.051, 1.086; converted to chi_1 at 0.015: 0.9940, 1.0271; nonlinear reference f = 1.027, 1.062 | agree | the literal statistic depends on the reference temperature by 5.7 percent; 0.015 is the mean of the reservoir temperatures, the gas ends at 0.01336. Both pass [0.95, 1.10]. TESTS T6(b) should name the temperature [JUDGEMENT] |
| T7 theta = 0.003: f = 1.0232(39), 1.0174(47), 1.041(11) at k lambda 0.1, 0.2, 0.4; extrapolated 1.019 +- 0.004 (heat/README.md:107, 172; CHECKLIST.md:33; EVIDENCE.md:86) | 1.0233(39), 1.0172(49), 1.041(12); 1.0194 +- 0.0038 (same nonlinear correction); 1.0090 +- 0.0038 by the test's estimator on the entropy amplitude without it | agree | V1b; the agreement is to <= 2e-4 although my entropy combination (A_n - (c_v/c_p) A_p) and my reference were written independently |
| T7 number mode alone 1.05, 1.11, 1.45; sound bias +5, +11, +43 percent (heat/README.md:107, 133-134) | 1.04, 1.13, 1.79 with the T7 estimator on the number mode | differ (size), agree (finding) | the bias depends on the fit window against the sound period; both show that the number mode is unusable at k lambda 0.4 |
| T7 theta = 0.003, 1.0250 +- 0.0025 N-weighted with card seeds (heat/README.md:110; CHECKLIST.md:33) | - | not checked | card seeds not in my item list (one card run was reserved for another helper) |
| T7 theta 0.1, 1: CE order 4 of V1a 1.0988 +- 0.0015, 0.9933 +- 0.0010 (heat/README.md:112-113, 173) | 1.0988 +- 0.0015, 0.9933 +- 0.0010 (my ce_kappa.json order 4 / (75 sqrt(pi)/64)) | agree | the quotation of my V1a is exact; the measured 1.0957, 0.9914 were not checked |
| CE value at 0.003: 1.0296; measured value 0.5-1.0 percent below, zero-cell-size 1.2-2.9 percent below [TO VERIFY] (heat/README.md:151-153; CHECKLIST.md:33) | my V1a 1.0296(10); my corrected T7 1.019(4), 1.1 percent below | agree | the open small discrepancy is seen by both; cause open |
| Finding 1: b = 25 sqrt(pi)/32 right, Balberg 0.72 excluded (heat/README.md:125-129) | kappa/kappa_1 = 1.01-1.02 by two estimators; Koda & Shapiro b read at arXiv:1101.3097 sidm1.tex 401-415 | agree | |
| T6(a), T6(c), T7 collisionless, T8 (card and processors), T8 part 2 (heat/README.md:103-106, 108-109, 114-116) | - | not checked | not in my item list; T8 rests on card runs |
| F21 tables reproduced; eps maximum Z(0) = 0.5404, exact onset 0.6348 (CHECKLIST.md:36; models/README.md:85-87; REVIEW-wave2.md:97-102) | F21 Table 1 b = 0.1 rows to <= 1.3e-4 (R to their 1e-3 grid); eps maximum Z(0) = 0.540413 (w0 3.165241); exact onset with 1 + p/u 0.634817 (w0 3.587103); F21's trial-function onset 0.75001 reproduced | agree | V4, own solver (finite elements, J = 100/200/400) |
| King y_max = 0.334032 against the printed 0.334 (CHECKLIST.md:36) | 0.334032 (E_b,max 0.0355886); zero 0.784518 (paper 0.784) | agree | V4 |
| Juttner Gamma_1 anchor Z(0) = 0.5331 at the energy-matched temperature; 0.4125 at the Tolman temperature; 0.5404 with the Juttner 1 + p/u; anchor 0.0074 below the eps maximum (CHECKLIST.md:12; models/README.md:85-93; REVIEW-wave2.md:97-102, 116-122) | 0.533057 (exact; trial 0.5947); 0.412527 (exact; trial 0.4357); 0.540380; difference 0.0074 | agree | V4, V4b. My blind verdict used the Tolman reading first and then judged the energy-matched one the physical choice, as the lead decided (REVIEW-wave2.md:116-120) |
| Juttner onset at theta = p/n 0.5317; J_E onsets 0.504, 0.498, 0.494 at b = 0.2, 0.3, 0.5 (models/README.md:88-90) | - | not checked | |
| King family: Juttner fluid onset y0 = 0.32143 against the E_b maximum 0.33403 (CHECKLIST.md:12) | 0.321433 (exact, energy-matched T; trial 0.34033) | agree | V4b. With the Tolman reading it would be 0.0392 |
| Model files: Z(0), eps, R/M, M0/M agree between two solvers to 5e-11; E_b maximum Z(0) = 0.54041288 (models/README.md:69-73) | my independent solver at the files' y0: E_b, C, Z(0), M, R/M, M0/M, n_c, rho_c, p_c to <= 6e-10 (18 King and b = 0.1 files); eps maximum 0.54041285 | agree | V4b. The k = 0.5 polytrope files agree to 2e-5, limited by my quadrature |
| Models table (w0, Z(0), E_b, R/M of 13 models) (models/README.md:48-60) | w0 of the three named b = 0.1 models 3.130774, 3.165241, 3.587103; the rest via the files to 6e-10 | agree | |
| Particle files: count inside the core radius, sum m W/psi - M (models/README.md:69-77; REVIEW-wave2.md:92-96) | radial distribution of 3 threshold samples (1e5) equals my enclosed rest mass to D = 1e-5 = 1/N; sum of particle masses = my M0/M to 6e-13 | agree (radial distribution) | sum m W/psi and E/E0 not checked |
| "J_pu onset coincides with the eps maximum to 3e-5 in Z(0); not explained" (REVIEW-wave2.md:108-109) | 0.540380 against 0.540413: the same coincidence, found blind | agree | unexplained for me too |
| First mass maximum of the King sequence y0 = 0.0982 (REVIEW-wave2.md:149-150) | maximum of M(y0) at fixed amplitude 0.098197; the rest mass N peaks at 0.1050 | agree (number) | the two maxima do not coincide, so the family is not a one-parameter barotropic sequence: supports the lead's caution that the turning-point reading is unproven |
| R6 King defect, cost, T0b, T10b, T11, D1/D2 (box_tests/README.md:75, 84-87, 140-146) | - | not checked | not in my item list |
| AthenaK read test, growth pipeline, card runs (models/README.md:79-115; REVIEW-wave2.md section 3) | - | not checked | not in my item list |

## 2. Claims I found wrong or unsupported

1. REVIEW-wave2.md:49: "(385554 collisions)" is attached to seed 8; that run has 385838
   collisions; 385554 belongs to the seed-7 runs (wording).
2. box_tests/README.md:82 (and the T9 row of CHECKLIST C6): "KS p >= 0.089" passes T9's
   "both Maxwell-Juttner" only with the reference temperature taken from each class (or from
   the final energy). Against Maxwell-Juttner at the temperature of the initial energy the light
   class of seed 3 has p = 1.7e-4. The cause is the nanbu energy drift (energy conserved in
   expectation only), not the shape. Unsupported as written: the reference temperature should
   be named in the claim and in TESTS.md T9.
3. heat/README.md:107, 133-134: the sizes of the number-mode bias (+5, +11, +43 percent) are
   specific to the track's fit; with the T7 estimator I get +4, +13, +79 percent. The finding
   (the number mode is biased by sound) stands; the numbers should carry their fit window.
4. Not a claim of the track but of the baseline paper, relevant to how it is quoted: F21's
   adiabatic-index onset (Z(0) = 0.750, arXiv:2108.11967 main.tex:274) rests on the trial
   function xi = r e^Phi, and F21's remark that the result is insensitive to xi (main.tex:220)
   does not hold for these centrally condensed models: the exact fundamental mode with the same
   gamma goes unstable at Z(0) = 0.6348 (the trial-function quotient is still +0.73 there), and
   the trial quotient even turns positive again above Z(0) ~ 1.3 where the exact mode is
   strongly unstable (verify_g1/figs/v4_ev.png). The track already uses the exact onset; any
   text that cites 0.750 as F21's onset should say it is a trial-function value.
5. Definitions the tests leave open (not errors of the runs): T6(b) does not name the temperature
   of chi(kappa_1) (0.015 or the final 0.01336: 5.7 percent in the literal statistic); T9 does
   not name the reference temperature of its KS clause; "Gamma_1 of the local temperature" has
   two readings for a truncated distribution (Tolman 0.4125 against energy-matched 0.5331 in
   Z(0)), which the lead has settled for the energy-matched one.

No number of the track that I recomputed is wrong beyond these points.

## 3. What I could not check, and why

- T5 (entropy): needs an entropy estimator with its own bias study; not attempted in the time.
- T7 with the card seeds (N-weighted 1.0250), T7 at theta 0.1 and 1 (measured values), T7 at
  eps = 0.05, T8 (card), T6(a), T6(c), the T7 collisionless check: not in my item list, or on
  card runs; run C-20261119-150335-73fd40f was reserved for another helper.
- T0b replay, T10b, T11, D1/D2, R6 (King defect), cost figures: not in my item list.
- The MPI variant of T10: the executables of these runs have no MPI.
- Juttner onset at theta = p/n and at b = 0.2, 0.3, 0.5; the gr-qc/0601112 shell models (another
  ansatz with L0 > 0); sum m W/psi - M and E/E0 of the particle files; the AthenaK read test;
  the growth pipeline and all card cluster runs (G2 material).
- The C16 note, C2 pipeline items beyond the box and heat analyses, and the claims of
  REVIEW-wave2.md sections 4, 5, 7, 8 (not in the reading list of this package).

Remarks added after the blind verdicts (the verdicts themselves are unchanged):
- My V1 remark (iii) (corrected T7 value 1.1 percent below the relativistic Chapman-Enskog value)
  is the track's own open item (heat/README.md finding 8: cell-size bias of +0.7 to +1.9 percent
  at dx = 0.245 lambda); with that bias the zero-cell-size value moves further below, so the
  discrepancy is not explained by the cell size [TO VERIFY at G2, as the track says].
- My V4 verdict judged the energy-matched temperature the physical reading after I had seen the
  `role` label of the model file that names it, but before I read the lead's decision and its
  reasons (REVIEW-wave2.md:116-120); the two agree. My Tolman-temperature value (0.4125) was
  computed before I saw that label.
