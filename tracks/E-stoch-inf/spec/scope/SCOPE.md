# Scope of Track E (S11) at the feasibility gate G0: owner's version 1

Owner E-stoch-inf. Version 0 was written by the E-pre-1 helper (commit 87ba18e); this
version is the lead's rewrite of 2026-11-15 for the G0 package: it fixes the open choices
(section 4), adds the parameter ranges, the verified reference statements, the test plan
by row of brief section 10, what core's implementation already shows, the compute estimate
and the recommendation to the group. Checklist of the gate: `../../stage/G0/CHECKLIST.md`;
artefacts and run ids: `../../stage/G0/EVIDENCE.md`; what the gate lacks:
`../../stage/G0/OPEN.md`. Labels: [VERIFIED] read at the locator or measured by a
registered run, [BACKGROUND], [JUDGEMENT], [TO VERIFY].

Locator keys (sources in `kb-data/raw/arxiv/<id>/<version>/src/`, all ingested by kb,
`kb-data/manifests/inventory.json`, record status ok): P1 = 2512.14649 v2 `PRD_v2.tex`;
P0 = 2401.08530 v2; P2 = 2502.06783 v3 `main_V2PRD.tex`; TH = 2610.32592 v1; BZ =
2606.14853 v2 `Manuscript.tex`; FKTT = 1308.4754 v2 (Fujita, Kawasaki, Tada, Takesako; the
key was "VS" before 2026-11-19, which named the wrong authors); JM = 2206.11234 v2; ST = 2405.10692 v2.

## 1. Problem statement

Science question of S11 (brief 447): once quantum fluctuations enter the full
Einstein-scalar equations as stochastic sources, how far do the statistics of large
perturbations differ from stochastic delta-N, and what do gradients, shear and the
constraints do during ultra-slow roll (USR)?

Feasibility question of this gate (brief 798): can this repository's AthenaK, extended by
core with a minimally coupled scalar field and the Langevin sources of Launay, Rigopoulos
and Shellard (P0, P1), reproduce the slow-roll (SR) and USR test cases of P1, accepted
against the freezing criterion derived from BZ, at a cost per realisation the program can
afford? Code base settled: this repository's AthenaK (decisions 0004, 0010); P1's
GRTeclyn/ISTORIz (P1:480-482) is neither used nor built.

In scope for G0-G2: the reproduction (S11 deliverable 1), stochastic delta-N reference
statistics for the same potentials (E-pre-3), reproducible noise (E-pre-4, brief M11).
Later: compaction-function statistics (deliverable 2, G3), field-to-particle hand-over (3),
eternal inflation (4).

## 2. Parameter ranges

| Quantity | SR (quadratic) | USR (Higgs inflection) | Locator |
|---|---|---|---|
| Potential | m^2 phi^2/2 | Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2)/(3 (3 phi^2 + 2 v^2)^2) | P1:405-409 |
| Printed parameters | eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl | Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl | P1:411-413 |
| Derived | phi0 = -14.0950 Mpl, m = 1.73494e-6 Mpl, eps1(N*) = 1.1107e-2, V(N*) = 2.690e-2 in Mpl = 100 units | dphi/dN(N0) = 0.102682, H0 = 9.5902e-6 Mpl, USR (eps2 > 3) from N* + 2.52 to N* + 6.55, eps1 min 9.7e-13 | two independent integrators: runs E-stoch-inf-20261115-122806-ef0d039 (helper) and E-20261115-135532-3f958a1 (lead) |
| N* - N0, N_f - N* | 5, 8 | 3, 10 | P1:419-420 ("~"); fixed here as integers, which reproduce P1 Fig. 1 |
| Lattice | N = 256, L k_sigma* = 2 pi, k_max = N k_sigma*/4 = 64 dk, a* = 1 | same | P1:509-519 |
| Window | tanh, s = 5, sigma = 1 | same | P1:503-506, 519 |
| Gauge | geodesic slicing alpha = 1, beta = 0; no damping, no AMR; periodic | same | P1:482-483 |
| Courant factor theta | 0.25 (section 4); temporal test at 0.125, 0.0625 | same | not in P1 (SPEC U1); P2 used 0.025 (P2:492); one mode per step needs theta < 0.64 (P1:727) |
| Steps at 256^3 | 1304 | 1630 | N_T = N sigma Delta N/(2 pi theta) (P1:721); `../../codebase/figs/cost.json` |
| Convergence ladder | N = 32, 64, 128 with k_max/dk = 8 | same | P1:747-773 |
| Sensitivity (G2) | s = 2.5, 5, 10; sigma = 0.5, 1, 2; theta; N | same | DESIGN_REVIEW 8.1 L9 [JUDGEMENT] |
| Delta-N reference | band dk-64 dk, end surface N* + 15, sigma <= 0.01, 1e6 realisations | same | `../../langevin/README.md`; runs E-stoch-inf-20261115-130139/-130137-176cdd6 |

## 3. Statements of the key references, verified at the source

| Statement | Locator | Checked by |
|---|---|---|
| S_R = R_k Wddot + [2 Rdot_k + (3 - eps2) H R_k] Wdot; S_Pi = Mpl sqrt(2 eps1) S_R | P1:297-310 | spec helper; lead (read) |
| S_K = -eps1 S_R, S_Kt_ij = a^2 eps1 (delta_ij/3 - k_i k_j/k^2) S_R; constraints carry no source | P1:370-375, 378-392 | spec helper |
| The two cases and their parameters; N* - N0 ~ 5, ~ 3; N_f - N* ~ 8, ~ 10 | P1:405-424 | spec helper; lead (read) |
| Geodesic slicing, AMR and constraint damping off, periodic; GRTeclyn core | P1:480-483 | lead (read) |
| Window with s = 5, sigma = 1; L k_sigma* = 2 pi; k_max = N k_sigma*/4; N = 256, a* = 1, Mpl = 100 | P1:503-519 | spec helper; lead (read) |
| Hamiltonian violation of second order (~1e-10 for noise ~1e-5); a flipped noise sign gives first order | P1:538-541 | spec helper; lead (read) |
| Step count and the bound theta < n sigma/(2 pi) | P1:714-730 | spec helper; lead (read) |
| Without metric perturbations R_k^2 ~ H^4 in SR, stronger in USR; deformed MS equation; eps << 1 is not sufficient | BZ:150-156, 177-212, 264-268 | spec helper; lead (read) |
| Geodesic-gauge initial data (P2:317-327, label eq:eqInitialConditions; not eq. 17, SPEC 5.3 note) and the dictionary delta Pi = d/dt delta phi - phidot Psi_G | P2:262-322 | spec helper (symbolic run); lead (derivation) |
| Courant 0.025; 256^3 "less than a few hours on 64 to 152 processors" | P2:492 | spec helper; lead (read) |
| Draw prefactors dk^(3/2) and (dk/sqrt(2 pi))^(3/2), mutually inconsistent | P2:876-884 | spec helper (run); lead (read) |
| Drift-diffusion moments and the first-passage formalism | FKTT:341-364 | langevin helper |
| Quadratic benchmark m = Mpl, phi_in = phi_UV = sqrt42, phi_end = sqrt2 | JM demonstration.tex 18-55 | langevin helper; lead (own quadrature) |

Errata (details in `../SPEC.md` section 9 and the package READMEs):

| Erratum | Locator | Evidence |
|---|---|---|
| delta Pi of the initial data: the printed term -sqrt(2 eps1) H Mpl Psi_G vanishes in the geodesic gauge; the data need -sqrt(2 eps1) Mpl H Psi_B | P2:320 with 308, 262, 270, 490 | linear Hamiltonian residual 4 eps1^2 H^3 a^2 k^-2 Rdot with the printed form, 0 corrected (run E-stoch-inf-20261115-123146-82d2fd4, rerun identical in E-20261115-135531-0c4e629); lead's re-derivation from P2's dictionary (owner JOURNAL, L-I) |
| Draw normalisation: L^(-3/2) is right; the printed prefactors give (2 pi)^3 and (2 pi)^(3/2) too much power | P2:876-884; TH appendix:487-491 | run E-stoch-inf-20261115-122934-9ac98d8 (rerun identical) |
| Importance-sampling weight sign | JM method.tex 78, 151 | run E-stoch-inf-20261115-125312-dafadc4 |
| v0/4 as the leading pole in general | JM appendix.tex 168-173 | run E-stoch-inf-20261115-125658-e3eaef3 |
| Friedmann denominator lacks 3 Mpl^2; the "very shallow maximum" is an exact stationary inflection point at -sqrt2 v | P1:108, 534 | lead (read); langevin helper |
| USR in the text from N ~ 3.5 to 8, about one e-fold later than P1's Fig. 1 | P1:534 | runs E-stoch-inf-20261115-122806-ef0d039 and E-20261115-135532-3f958a1 |

## 4. Exit criteria and the owner's decisions at G0 [JUDGEMENT, for the group to confirm]

Choices the helpers left to the owner, fixed here:

1. Courant factor theta = 0.25 for G1; test L6 at 0.125 and 0.0625 decides whether a
   smaller one is needed.
2. Backreaction level 0 (Friedmann background in the mode functions) for the first
   reproduction, level 1 (box means) as a variant. Level 2 of P1 is not implemented: a
   stated difference, bounded by P1's own ablation (at most about 1e-4 relative in the
   spectrum, P1:520, 777-790).
3. N* - N0 = 5 (SR) and 3 (USR), N_f - N* = 8 and 10; delta-N end surface at least 3
   e-folds after the last noise.
4. Acceptance thresholds (SPEC 7.2-7.3):
   - A1 background: box means of phi, Pi, K within 1e-4 relative of the Friedmann reference
     (SR), 1e-3 (USR, where delta Pi/Pi_b becomes large, P1:534-536).
   - A2 per mode (same alpha_k, no cosmic variance): |R^NR_k/(W_k R_k alpha_k) - 1| < 0.02
     for every lattice mode with k <= k_max/2 at N_f in SR; the reference uses the lattice's
     discrete wave number. [Amended by the owner on 2026-11-19, wording only: the reference
     mode function R_k is the continuum one of the code's mode equation at k = |n| dk, which
     is what the code injects through the window; the stencil-k^2 reference accumulates the
     sub-horizon dispersion error and fits worse (6.2e-3 against 1.2e-4 at 256^3, ladder
     JOURNAL entry 6). Both pass 0.02. The threshold is unchanged.]
   - A3 freezing: SR, for every mode with N_f - N_k >= 6, the per-mode power ratio between
     N_k + 4 and N_f equals the full-MS ratio within 1 percent (drift of ln Delta below
     2.5e-3 per e-fold, a twentieth of the FLRW lattice's -4 eps1); USR, modes k <= 3 dk
     within 10 percent of the full MS at N_f (the deformed equation is off by 1.4 to 8.4).
   - A4 constraints: H/[H] and M/[M] of second order during the entry (they scale with the
     square of the noise amplitude when it is halved); the sign-flip control is first order
     (P1:541).
   - A5 spatial convergence (N = 32, 64, 128, k_max/dk = 8): order between 4 and 6 before
     the floor.
   - A6 temporal convergence: order 4 +- 0.5 in theta.
   - A7 reproducibility: bit-identical across MeshBlock layouts and restart (NOISE_SPEC
     A11, A12); rank count when the field runs on several ranks.
   - A8 one-point statistics against the lattice sum and the sigma <= 0.01 delta-N
     reference only.
   Results against A1-A7 after wave 2 (SR, scouting runs with core's tested-branch
   executable `core/scalar-2` a58e95b, decision 0013): `../../ladder/README.md` and
   `../../stage/G1/`. A4 in the strict form above FAILS in the paper's set-up
   (k_max = N/4) at every N; A5 passes only with an operational "before the floor" chosen
   after the data were seen. Proposed rewordings are in section 4b; they are not in force.
5. Downgrade (brief 462): if by G1 the SR or USR reproduction fails A3, or one 256^3
   realisation costs more than 5 card-hours (half the allotment, decision 0006), the track
   becomes a supplier of delta-N statistics to Track A.

## 4b. Proposed amendments after wave 2 (not in force; proposed to orch 2026-11-19)

Formulated after the ladder's data were seen (ladder JOURNAL entries 9 and 11, core's
message scalar2-ready); they would change the owner's thresholds, which decision 0013
accepted, so they go to the orchestrator as a proposal (outbox 20261119) and A4/A5 above stay
as written until it rules.

- A4': split H and M_i into the parts odd and even in the noise amplitude s with a mirrored
  pair (s = +-1) and one halving of s. (a) The even part with its box mean removed scales by
  4.00 +- 0.05 when s is halved and agrees between the two finest resolutions within 5
  percent where it lies above the floor (P1's resolution-independent second-order plateau,
  P1:538-541). (b) The odd part is discretisation error: it scales by 2.00 +- 0.05 when s is
  halved and converges at the order of A5; it may exceed the even part once shells with
  fewer than eight cells per wavelength enter (from ln(N/8) e-folds after N* in the
  paper's set-up). (c) The record <|H|/[H]> stays within 10 x 1e-10 (P1:538-539) and
  <|M|/[M]> below 1e-3 ([M] is first order in s, P1:540-541, so <|M|/[M]> is first order).
  (d) The sign-flip control has an odd part at least 1e3 times that of the proper run. The
  record ratios are no order test (they hold the uniform residual H0 of the time
  integration, which does not depend on s).
- A5': "before the floor" = where the finer odd part exceeds three times the floor, the
  floor being the part that does not scale with s and grows with N (N^2.5 measured between
  128 and 256). Factor and floor model were fixed after the data were seen [JUDGEMENT].

## 4c. G2 criteria of the USR case, fixed before the G2 production runs (2026-11-21)

Decision 0023 item 1 asks that the floor and the clause on the maxima are defined here before
any G2 production run. Written by the lead of batch 5 on 2026-11-21 before package `g2prod`
submitted anything. U-A2' and U-A4' were proposed after the scouting data (outbox
20261121T131021Z usr-acceptance-after-data); what is new here is that their definitions are
closed, and that the release runs of `g2prod` are judged by them as written [JUDGEMENT]. The
strict U-A2 and U-A4 of `usr/JOURNAL.md` entries 9.1 and 10 stay FAILED on record.

Common rules. P1's set-up: nmax2 = 4096 (k_max = 64 dk), window s = 5, sigma = 1, Courant 0.25,
deck `g2prod/inputs/usr_prod.athinput`, release card build core-v0.6. "At N_f" means the dump at
t = tlim (the 21st dump, recorded time equal to tlim within 1e-9). Pairs are read only at equal
recorded times (|dt| <= 1e-9). Odd and even parts: O = (X(+s) - X(-s))/2, E = (X(+s) + X(-s))/2
of the same seed and N. **Clause on the maxima:** wherever a clause says "every mode" or "at
every dump", it is the maximum over all of them, with no exclusion of small |alpha_n| and no
dump dropped; a maximum over time is never used where a clause is stated at N_f; pointwise
ratios are reported beside any clause stated on maxima. **Floor:** for a constraint C (H, or
M_i taken together) at one dump, with box means removed, o_s and o_{s/2} the rms of the odd
parts at amplitudes s and s/2: f^2 = max(0, (4 o_{s/2}^2 - o_s^2)/3), the part of C that does
not scale with s. No other floor (out-band, fixed bar, assumed) is used for G2.

| Id | Criterion (G2, USR) | Threshold |
|---|---|---|
| U-A0, U-A1, U-A3 | as pre-registered (`usr/JOURNAL.md` entry 10 table), on every release run | 1e-5 in N; 1e-3; 10 percent |
| U-A2' | D_n = abs(O_n/(s W_n R_n alpha_n L^-3/2) - 1) at N_f for every mode with k <= k_max/2 (68532 modes at 256^3), continuum mode equation (SCOPE 4 A2 wording), on the mirrored pair of each seed | max_n D_n < 0.02; reported: the same to k_max, single-run D_n, even/odd rms (U-A2n, must stay < 0.3) |
| U-A4'(a) | even parts of H and of M with the floor removed, sqrt(e_s^2 - f^2)/sqrt(e_{s/2}^2 - f^2), at every dump where e_{s/2} > 3 f, from the pairs at s = 1 and 1/2 (seed A, 256^3) | 4.00 +- 0.05 |
| U-A4'(b) | the floor itself: with two amplitudes the odd halving is 2 by construction of f, so it is no test; instead f/o_{s/2} is reported per dump, and the clause holds where o_{s/2} > 3 f | reported; (a) judged only there |
| U-A4'(c) | records <abs H'/[H]> (con_signed) and <abs M/[M]> over the whole run, maxima, every release run | below 1e-9 and 1e-1 (U256: 2.9e-12, 2.5e-2; the M record holds a floor over [M], which is proportional to s, so it doubles at s = 1/2: 128^3 group 1 2.47e-2 -> 4.3e-2) [JUDGEMENT: bar set from the scouting values] |
| U-A4'(d) | sign-flip control (noise_pi_sign = -1) against the proper run, odd part of H: ratio of the maxima over the entry (cN <= ln(N/8)); pointwise ratios reported | >= 1e3 (only if the control run exists; queued last in g2prod) |
| U-R | resolution at fixed modes, N = 256 and 320, seed A: (i) max_n D_n (k <= k_max/2) of the odd parts falls from 256 to 320 by a factor 2.0-4.5; (ii) shell power at N_f of the s = +1 runs agrees between N within 1e-3 for k <= 32 dk and 1e-2 to 64 dk; (iii) even/odd rms of the second-order part at N_f agrees between N within 5 percent | as stated |
| U-S | second seed (B) at 256^3: U-A2', U-A3 as above; one-point rms of R^NR at N_f within 5e-3 of the ensemble lattice value 0.89366 (`usr/results/usr_reference.json`) | as stated |
| U-W | window sensitivity (L9): the criterion on the window parameters is the result of package `window` (run E-20261121-154733-0d1fbda): the odd-part shell power at N_f of s = 2.5, 10 and sigma = 0.5, 2 against s = 5, sigma = 1 shifts by less than the NR-vs-reference bound per shell and by at most 1e-3 to k_max/2 and 2e-2 to k_max (measured 1.9e-4 and 9.1e-3). No further window run is part of G2; the late constraint records are NOT required to be window-independent (W6 refuted) | met by the scan [VERIFIED by the window package and the lead's rerun, `stage/REVIEW-wave3.md` Part C] |

"The USR case is reproduced" (G2) = U-A0, U-A1, U-A2', U-A3 on the release build at 256^3 for
seeds A and B, U-A4'(a) at 256^3, U-R and U-W; U-A4'(c) and U-S as stated; U-A4'(d) if its run
exists. Package `g2prod` (`../../g2prod/JOURNAL.md` entry 1) holds the predictions per run.

Gates: G0 (brief 798) = specification, code-base assessment and compute estimate complete,
then the group's decision. G1 = SR spectrum (A2), freezing (A3), constraints converge (A4,
A5), with A1, A6, A7 recommended (`../../stage/G1/STATUS.md`). G2 = USR reproduced (A2, A3,
P-h of SPEC 7.1) and sensitivity (L9). G3 = tail statistics against E-pre-3 (A8).

## 4d. G3: tail statistics of the curvature perturbation in the inflection scenario, fixed before any G3 run (2026-11-25)

Decision 0038 item 2 sets the scope; this section fixes the statistic, its estimator, the seed
count, the reference, and the criteria on constraints, convergence, gauge and level 2 before any
G3 production run. Written by the lead of batch 17 on 2026-11-25 (04:00 PST) before the first G3
submission (the pilot, queue label G3P, is the only card run of this batch). Predictions per part:
`../../g3/JOURNAL.md` entry 2. Anything changed after a G3 run that it judges is recorded as such
and the original wording stays on record (as for 4c).

Common set-up. Deck `g2prod/inputs/usr_prod.athinput` (the G2 USR deck: P1's inflection potential,
window s = 5, sigma = 1, Courant 0.25, geodesic slicing, level 0) at 128^3 with nmax2 = 1024
(k_max = 32 dk = N dk / 4, four cells per shortest injected wavelength, as the window scan),
mode file `usr/inputs/modes_usr_n1024.txt`, to t = tlim (N_f), release card build core-v0.7
(`/data/haiyangw/nrpic/.work/build_gpu_v07/src/athena`). Dumps only at t = 0 and t = tlim
(`scalar_field/dump_dt = tlim`, metric on, constraint fields off except where a part below needs
them), no restart output (a 128^3 run takes minutes). Seeds: `job/rng_seed = 20262000 + i`,
i = 0, 1, ..., in that order, never skipped; a run that fails is rerun with the same seed and the
failure stays on record. Several seeds share one Slurm job (batch launcher), one queue entry each.

### 4d.1 The statistic and its estimator

[Amended 2026-11-25 (batch 19): the two reader tests by 4d.9 A3; the estimator by A5; sign of zeta by A2/A3.]

- Variables, at N_f on every cell of every seed: (i) R^NR(x), the linear extraction of
  `ladder/scripts/ladder_lib.curvature` (the reader of G1 and G2); (ii) zeta(x) = delta N to the
  uniform-field surface phi = phi_e: zeta = -1/2 ln(chi/<chi>) + Delta N_bg(phi(x), dphi/dN(x)) -
  <same>, where Delta N_bg is the e-folds a homogeneous Friedmann-Klein-Gordon universe takes from
  the cell's field and field velocity (from Pi, alpha and K of the cell) to phi_e, phi_e the field
  of the lockstep background at N_e = N* + 15 (the end surface of the one-patch reference). (ii) is
  the variable the one-patch delta-N calculation gives; (i) is the variable of G1 and G2. The zeta
  reader is new: before it judges anything it must give zeta = 0 to 1e-10 on a homogeneous run
  (noise off) and zeta = R^NR to second order in s on a run at s = 1/4 (both on processors, 32^3).
- Standardisation: x = X / sigma_lin with sigma_lin^2 = sum over injected modes of |W_n R_n|^2 L^-3
  from the run's own lockstep record at N_f (not fitted to the data); for zeta the same sigma_lin
  (zeta and R agree at linear order).
- Statistic: the exceedance fractions F_+(nu) = P(x > nu) and F_-(nu) = P(x < -nu) over all cells,
  pooled over seeds, at nu = 3 and 4 (judged), 2, 4.5 and 5 (reported); skewness and excess
  kurtosis of x; the one-point density (figure). Estimator: the mean over seeds of the per-seed
  fractions; its standard error is the seed-to-seed standard deviation over sqrt(S). Cells within a
  box are not treated as independent.
- References: (a) the linear expectation, a Gaussian of variance sigma_lin^2: Q(3) = 1.3499e-3,
  Q(4) = 3.167e-5; (b) the one-patch delta-N calculation of the same scenario, below.

### 4d.2 Number of seeds (power estimate, run E-20261125-115822-29795d6, `g3/power.py`)

[Amended 2026-11-25 (batch 19): S and the reference size set together by 4d.9 A5 and A10.]

Gaussian fields with the linear spectrum of the 128^3 USR box (record of the 128^3 window-scan
run b_p, E-20261120-222424-0eb754b, t = 10.0, nmax2 = 1024), 400 boxes: sigma_lin = 0.4940; the
box-to-box standard deviation of F_+(3) is 4.96e-5 (3.7 per cent of Q(3)), of F_+(4) 5.98e-6
(19 per cent of Q(4)); a box holds about 5.5e5 effectively independent cells for F(3) (of 2.1e6:
the spectrum rises so steeply that the field decorrelates within a few cells). One seed already
measures F(3) to 4 per cent, so the seed count is set by the reach into the tail: S seeds give a
relative standard error 0.19/sqrt(S) at nu = 4. **S = 256**: 1.2 per cent at nu = 4, so a
difference of 3.6 per cent from a reference is seen at three standard errors (the 256^3-band
delta-N tail exceeds the Gaussian by 12 per cent at nu = 4, `langevin/results/ref_inflection.json`;
the 128-band excess is smaller, see 4d.3); nu = 4.5 to about 5 per cent, nu = 5 to about 15 per cent
[JUDGEMENT: the scatter of a Gaussian field stands for that of the lattice field; the pilot checks
it on real output, and S is raised to at most 512 if the measured scatter at nu = 4 is more than
1.4 times the Gaussian one]. Cost: S times the measured cost per seed (pilot; about 0.035
card-hours from the window scan's 128^3 runs).

### 4d.3 The reference: one-patch delta N of the same scenario

[Amended 2026-11-25 (batch 19): reference and variance gate by 4d.9 A1, state at N_f by A4, the result by A2, nu = 4 by A9.]

What exists: `langevin/` (E-pre-3): the phase-space Langevin first-passage solver with the noise
covariance of the linear mode functions (momentum included), the lattice density of states, sigma
= 1, 0.1, 0.01, end surfaces at N_f and N_e = N* + 15, importance sampling; the 256^3 band (|n| <=
64) with 1e6 realisations (`results/ref_inflection.json`, run E-stoch-inf-20261115-130137-176cdd6):
var/var_lattice 0.9905, skewness 0.038, P(dN > 3 sigma_lin) 1.57e-3, P(> 4 sigma_lin) 3.6e-5. What
must be computed: the 128^3 band (|n| <= 32). Pilot reference started in batch 17 (run
E-20261125-115707-b845282, 2e5 realisations, all variants; `ref_spec.py` with NRPIC_REF_NLAT = 32,
outputs `results/ref_inflection_n32.json`). The G3 reference proper: sigma = 0.01 with the lattice
density of states, 4e6 realisations by direct sampling (standard error about 1.4 per cent at nu =
3), and nu = 4, 4.5 by the importance sampler of `sdn/langevin.py`, validated against direct
sampling at nu = 3 (agreement within two standard errors). [TO VERIFY before the comparison: that
the HiggsInflection model of `sdn/models.py` at phi0 = -1.2, N* - N0 = 3 is the deck's inflection
potential and N*, by the background landmarks of U-A0 (start and end of USR, H at N*) within 1e-4
in N, a processor check.] The comparison is made on zeta (variable ii) against the reference at N_e,
and on both variables against the Gaussian.

The G3 result [what the gate reports, not a pass/fail of the code]: r(nu) = F_NR(nu)/F_ref(nu) - 1
with its combined standard error at nu = 3 and 4, for F_+ and F_-; "NR differs from one-patch delta
N" only if |r| exceeds three combined standard errors at a judged nu AND the gauge leg (4d.6) does
not move F by more than its own standard error; otherwise "agrees within" the stated error.

### 4d.4 Constraint scaling with three amplitudes (G3-C; answers the G2 failure of U-A4'(a))

[Amended 2026-11-25 (batch 19): a minimum number of judged dumps by 4d.9 A6.]

Runs: seed i = 0 at s = +-1, +-1/2, +-1/4 (six runs), constraint fields dumped at every
dump_dt = tlim/20 (21 dumps). Per dump and constraint (H, and M_i together), box means removed,
E(s) the even part: D1 = E(1) - 4 E(1/2), D2 = E(1/2) - 4 E(1/4) per cell. Model E(s) = s^2 A + F_s
with a per-run part F_s of equal rms sigma at every s. Model test at each dump (both must hold for
the dump to be judged): rms(D2)/rms(D1) in [0.9, 1.1] and corr(D1, D2) in [-0.30, -0.17] (model: 1
and -4/17). Level: sigma^2 = [rms(D1)^2 + rms(D2)^2]/34. Criterion: sqrt(e_1^2 - sigma^2)/
sqrt(e_{1/2}^2 - sigma^2) and sqrt(e_{1/2}^2 - sigma^2)/sqrt(e_{1/4}^2 - sigma^2) within 4 +- 0.05 at
every judged dump where the smaller of the two even parts exceeds 3 sigma. Range of e-folds: dumps
with cN = N - N* in [2.0, 6.6] (the entry and the USR phase, where G2 showed the even part above the
per-run level); dumps outside are reported, not judged. The criterion fails if any judged factor
lies outside the band, or if the model test fails at more than a third of the dumps in the range.
The two-amplitude estimator of 4c is computed beside it and reported, not judged. D1, D2 and sigma
are computed with the track's own reader (risk R30), not the verifier's.

### 4d.5 Discretisation part of convergence (G3-R): Richardson in the square of the amplitude

[Amended 2026-11-25 (batch 19): a model test by 4d.9 A7.]

The odd part per mode is O(s) = s L + s^3 T + ...; from s = 1 and 1/2 the part linear in s is
L = [8 O(1/2) - O(1)]/3 and the third-order part T = [O(1) - 2 O(1/2)] * 4/3. Runs: seed i = 0 at
s = +-1, +-1/2 on 128^3 (shared with 4d.4) and on 160^3 at the same modes (nmax2 = 1024). Criterion:
D_n^L = |L_n/(W_n R_n alpha_n L^-3/2) - 1|, maximum over modes with k <= k_max/2 at N_f, falls from
128 to 160 by a factor in [2.0, 4.5] (order 3.1 to 6.7 at the ratio 1.25, as U-R (i)); reported: the
same for O(1) alone (the G2 form, which a spacing-independent T caps), and the change of T between
the resolutions (expected below 10 per cent: T is not a discretisation error). A third resolution
is not planned; it is added (192^3) only if the factor misses the band.

### 4d.6 Gauge leg (G3-G): a slicing other than geodesic

[Amended 2026-11-25 (batch 19): WITHDRAWN as a criterion by 4d.9 A8 (decision 0040 item 1); the text below stays on record.]

`<z4c> lapse_kdriver = 2` with `lapse_harmonic = 0` (the driver towards constant mean curvature of
scalar_field_3.md section 5: mean lapse 1, the slicing approaches uniform expansion), the lapse
condition of the scalar-3 release tested there with the stochastic sources. Runs: the first 32
seeds of the baseline (i = 0 ... 31), otherwise identical. Read at t = tlim, where the mean lapse 1
makes the mean proper time equal to the geodesic one; the difference of the mean field between the
slicings is reported. Criterion: for zeta, the per-seed paired differences of F_+(3), F_-(3) and of
the skewness between the slicings are consistent with zero within three standard errors of the
paired mean (zeta to a uniform-field surface does not depend on the slicing once the modes are
outside the Hubble radius); for R^NR the same differences are reported (it may differ at second
order). Also reported: the per-mode odd-part deviation D_n under kdriver against geodesic at N_f
(scalar_field_3.md saw the lowest modes drift to four times the geodesic deviation late; not
explained there).

### 4d.7 Level 2 of the stochastic backreaction (G3-L2): a sensitivity, not the baseline

[Amended 2026-11-25 (batch 19): run as mirrored pairs by 4d.9 A11.]

`scalar_field/noise_level = 2`, `noise_mode_eq = mesh` (core-v0.7; uniform mesh, one rank; defaults
of noise_level2.md for the other level-2 options), the same 32 seeds. Reported: the paired
differences level 2 minus level 0 of F_pm(3), F_pm(4), skewness, kurtosis, with standard errors,
for both variables. Not a pass/fail item. The seven ablation runs of the reproduction made with the
superseded level-2 executable enter no G3 statement until core supplies their provenance (decision
0038 item 3).

### 4d.8 Budget (allotment 60 card-hours, decision 0038 item 4)

[Amended 2026-11-25 (batch 19): order and budget by 4d.9 A12; the definition of 'G3 is met' below by A13.]

Pilot <= 1 (this batch); baseline 256 seeds about 9; three amplitudes 6 runs with 21 dumps about 0.5;
160^3 four runs about 0.4; gauge 32 seeds about 1.2; level 2 32 seeds about 1.5; the G3 total about
14 card-hours at the window scan's cost per seed, leaving room for S up to 512, a 192^3 rung and
reruns. Every number is replaced by the pilot's measured cost before the full set is queued.

"G3 of Track E is met" = the statistic of 4d.1 measured on S seeds with its standard errors; the
comparison of 4d.3 stated with its error; 4d.4 and 4d.5 pass as written; 4d.6 and 4d.7 reported;
the zeta reader passes its two tests; a fresh verifier recomputes the statistic from the dumps.

### 4d.9 Amendments of 2026-11-25 (batch 19, lead of E), before any G3 production run

Ruling: decision 0040 item 1. Source: the independent review `../../g3/scope_review/SCOPE_REVIEW.md`
(B1-B3, S1-S7, N1-N6) and the lead's own checks of its blocking findings, `../../g3/amend/JOURNAL.md`
(B1 confirmed by code that shares nothing with the review's, run E-20261125-151230-a4f4059; B2 by own
arithmetic, E-20261125-151429-83a040c; B3 from the formulas). The text of 4d.1-4d.8 above stays as it was
written; where an amendment and that text differ, the amendment governs. No G3 production run existed
when these were written; the pilot (q0045, scouting) was queued under the text above and is read under it,
with A3 and A8 applied to its reading. Predictions for the amended criteria: `../../g3/JOURNAL.md` entry 4.

A1 (4d.3; review B1) The reference and its variance gate. The lattice-density variant applied the shell
factor of 0.05-wide bins in ln n with the last bin's volume counted to e^3.5 = 33.1 while its shells stop
at 32 (|n| <= 32); its factor was 0.279 instead of 0.934, and the variant's variance 0.97786 of the lattice
sum where 1.00002 is right (lead's run above; |n| <= 64: 0.99058 and 0.99991). `langevin/scripts/
ref_spec.py` now cuts the last bin's upper edge at NLAT (commit d5a5f2f3c). Gate: before any tail
comparison the reference variance equals var_lattice_Ne within three of its standard errors (0.002
relative at 4e6 realisations, about 0.0097 at 2e5). The corrected pilot passes: 0.9993 +- 0.0032 at 2e5,
skewness 0.0234 +- 0.0037 (run E-20261125-151340-743c38c, `langevin/results/ref_inflection_n32_binfix.json`;
the earlier pilot E-20261125-115707-b845282 is superseded for the lattice variant; all other variants are
identical in both files). Standardisation: the reference with sqrt(var_lattice_Ne) = 0.49397 (same file),
the box with the sigma_lin of its own lockstep record (4d.1); their ratio is reported.

A2 (4d.3, the paragraph "The G3 result"; review B2) Variance and tail shape are judged separately. At
fixed thresholds nu sigma_lin, F(nu) responds to the variance with dlnF/dln sigma = 9.85 (nu = 3) and 16.9
(nu = 4), so a 0.4 per cent sigma error, a skewness of 0.009 and the whole delta-N skewness of the band
each move F(3) by amounts the comparison resolves (E-20261125-151429-83a040c). Replaced by:
(V) the variance: sigma^2_NR/var_ref - 1 with its combined standard error.
(T) the tail shape at matched variance: the skewness and the excess kurtosis of zeta compared directly;
F_pm(nu) at thresholds nu sigma_own, each side standardised with its own measured standard deviation, at
nu = 3 and 4 (nu = 4 only under A9); and A(nu) = (F_+ - F_-)/(F_+ + F_-), which a variance error leaves
unchanged at first order.
"NR differs from one-patch delta N in the tail" only if an item of (T) exceeds three combined standard
errors; "in the variance" from (V) alone; otherwise "agrees within" the stated errors. r(nu) at fixed nu
sigma_lin is reported, not judged. Sign: zeta in the delta-N convention of the reference (positive =
more e-folds = behind on the roll); zeta = -R^NR at first order (A3), so F_+ of zeta corresponds to F_- of
R^NR. The clause on the gauge leg is dropped (A8).

A3 (4d.1, the two reader tests; review B3) Test (a) cannot fail (zeta has its box mean subtracted) and test
(b) is wrong in sign: from `ladder/scripts/ladder_lib.py` line 180, R^NR = dchi/(2 chi) + (H/Pi) dphi =
-psi + (H/Pi) dphi, while 4d.1 defines zeta = psi + Delta N_bg with Delta N_bg = -(H/Pi) dphi at first order,
so zeta = -R^NR at first order. Both are withdrawn. Replaced by three tests that can fail at the order
the comparison rests on, on processors (release processor build `.work/build_cpu_v07/src/athena`), with
the 32^3 analogue of the deck (USR, nmax2 = 64, `usr/inputs/modes_usr_n64.txt`), before the reader judges
any G3 run; a reader that fails one judges nothing:
- Z0 (first order): on a mirrored pair at s = +-1/4, with O = [X(+s) - X(-s)]/2 per cell at N_f,
  rms(O_zeta + O_R)/rms(O_R) < 1e-3.
- Z1 (the map): Delta N_bg of the reader against an independent homogeneous integrator (another code path
  and another integration scheme, from the deck's potential) at states (phi_b + d phi, Pi_b + d Pi) of N_f,
  d phi and d Pi at +-eps, +-2 eps with eps of the size of the box's one-point spread: the first and second
  finite-difference coefficients agree within 1 per cent. Where the deck takes a shifted homogeneous
  initial slice, the same on homogeneous runs (noise off).
- Z2 (second order on the lattice): mirrored pairs at s = +-1/4 and +-1/2; the even part
  E = [X(+s) + X(-s)]/2 minus its box mean, regressed on O^2 - <O^2>, gives a_zeta. a_zeta at the two
  amplitudes agree within 2 per cent, and a_zeta agrees within 2 per cent with the quadratic coefficient of
  the independent map along the box's (d phi, d Pi) relation.

A4 (4d.3; review S1) The state at N_f in the reference. `ref_spec.py` records the (phi, varpi) state of
every realisation of the lattice variant at N = N_f (variance, skewness, covariance). The box's
(d phi, d Pi) at N_f, box means removed, is compared with it directly (variance and skewness of each), with
the precision written into g3/JOURNAL.md before the comparison. This separates the NR evolution from the
map Delta N_bg that reader and reference share. The G3 result names the comparison each statement rests on.
Not yet implemented: it goes into the 4e6 run (A10).

A5 (common set-up, 4d.1 estimator, 4d.2; review S2) Baseline as mirrored pairs: seeds i = 0..127, each at
`scalar_field/noise_mode_scale` = +1 and -1 (256 runs, rng_seed 20262000 + i as before); the pilot's
b000-b009 are the + members of pairs 0-9. The pair is the unit: per pair the mean of the two members'
per-run fractions and moments; mean and standard error over the pairs. Reported beside it, per pair, the
even part E (the non-Gaussian part without Gaussian sample variance): a_zeta and a_R from E on O^2 - <O^2>,
and F_+(+) - F_-(-). Baseline dumps at t = 0 and tlim without constraint fields
(`scalar_field/dump_constraints = false`; 4d.1 needs none, the constraint records stay).

A6 (4d.4; review S4) G3-C cannot pass with nothing judged: each factor (1 over 1/2, 1/2 over 1/4) and each
constraint (H; M) is judged at no fewer than four dumps of the range cN in [2.0, 6.6]; with fewer it is
"not testable", which is not a pass. The largest deviation from 4 is reported. The model test is unchanged.

A7 (4d.5; review S5) G3-R gets a model test of the asymptotic regime: the median over modes k <= k_max/2
of D^L_n(128)/D^L_n(160) also lies in [2.0, 4.5], and the sign of L_n/(W_n R_n alpha_n L^-3/2) - 1 is the
same at both resolutions for at least 90 per cent of those modes. G3-R fails if any of the three fails.

A8 (4d.6; review S3; decision 0040 item 1) The gauge leg is withdrawn as a criterion; the 32 kdriver seeds
are not queued. On the geodesic slice of the 128^3 USR box K is uniform (rms dK/|K| at most 4.0e-7 over the
run, 4.9e-13 at N_f), rms dchi/chi stays at 8.2e-7, while the rms of (H/Pi) dphi grows to 0.495 (review run
E-20261125-131805-0806ef8): the curvature perturbation lives in dphi on an unperturbed geometry. A lapse
driven by K has nothing to drive and coincides with the geodesic slice to about one part in a million of
zeta; the leg cannot fail. Limitation, stated in the G3 result and carried as a reservation of G3: "the
slicing is geodesic; a K-driven slicing coincides with it in this model and tests nothing about slicing;
a slicing test needs a lapse condition that depends on the field" (a request to core for later, not for
G3: `outbox/`). The pilot's k000/k001 are read for the record only: rms(alpha - 1) and rms of
H int (alpha - 1) dt at N_f, in units of sigma_lin.

A9 (4d.3, nu = 4; review S6) nu = 4 is judged only if the importance-sampled reference reaches a relative
standard error of at most 2 per cent for F_+(4) and for F_-(4). Target of the sampler (`sdn/langevin.py`
fpt_phase_space, argument bias): a constant shift c of the noise along its dominant direction, one run
against the roll (towards F_+) and one with the opposite sign (F_-), c fixed on a pilot of 1e5 paths so that
the median of the tilted delta N lies within [3.5, 4.5] sigma_lin on its side; validated against direct
sampling at nu = 3 within two standard errors. Otherwise nu = 4 is reported, not judged. (With 4e6 direct
paths the relative standard error at nu = 4 is about 8 per cent, three combined errors 25 per cent, more
than the whole delta-N skewness effect there, 24 per cent: E-20261125-151429-83a040c.)

A10 (4d.2 and 4d.3; review S7; decision 0040) Seeds and reference size together. With N_ref = 4e6 direct
paths the NR error at nu = 3 falls below a third of the reference's at 87 seeds (lead's arithmetic,
E-20261125-151429-83a040c; 78 in the review), so beyond about eighty seeds the nu = 3 comparison is set by
the reference. The 256 runs (128 pairs) stay, for three reasons that do not depend on the reference: the
direct skewness comparison of (T) (threshold 0.0027 at 256 runs against 4e6), the even-part statistics of
A5, and nu = 4 under A9. The reference proper: lattice variant, sigma = 0.01, 4e6 direct paths, with A1's
gate, A4's state, A9's sampler, and sigma = 0.1 at the same size (to bound the coarse-graining dependence of
the skewness below 0.0027, review N3). S beyond 128 pairs only if the nu = 4 reference reaches 1.5 per cent.

A11 (4d.7) Level 2 as 16 mirrored pairs (32 runs; about 1.9 card-hours at 1.7 times a baseline run,
review N6); the paired differences against level 0 use the same pairs.

A12 (4d.8) Order and budget: (1) processors: the 4e6 reference with A1, A4, A9 and sigma = 0.1; the zeta
reader with Z0-Z2. (2) The pilot (re-entered at priority 2: the gate package waits for it). (3) G3-C (six
128^3 runs, 21 dumps with constraint fields) and G3-R (four 160^3 runs) before the baseline, priority 2:
they can invalidate the set. (4) Baseline: the first two jobs (the ten minus members of pairs 0-9 with
pairs 10-12; pairs 13-20) after the pilot; the rest only once the pilot's measured cost per run is written
here. (Changed before the submission, same day: 14 runs a job, the ten minus members of pairs 0-9 with pairs 10-11, then pairs 12-18, so that a job fits the hour at the top of G3P-1, 0.06 card-hours a run.) (5) Level 2. Total about 13 card-hours at the window scan's cost (gauge leg removed, level 2 at 1.9).

A13 Replaces the paragraph '"G3 of Track E is met" = ...' above: the statistic of 4d.1 measured on 128
mirrored pairs with its standard errors; (V) and (T) of A2 and the comparison of A4 stated with their
errors; the reference passes its variance gate (A1); the zeta reader passes Z0-Z2 (A3); 4d.4 with A6 and
4d.5 with A7 pass as written; 4d.7 reported; the slicing limitation of A8 stated; a fresh verifier
recomputes the statistic from the dumps.

A14 (2026-11-25, batch 20, lead of E; written after the smoke tests named here and before the registered runs
read under it; A3 and A9 above stay as written) Two notes from processor work before any G3 production reading.
(a) A9's shift: the constant shift c along the dominant noise direction failed an unregistered smoke test (the
mean path weight of 3200 paths was 0.010 against 1: the shift is spent evenly over the window while the linear
delta-N variance comes mostly from its last e-fold; log-weight variance c^2 W = 39). The sampler uses instead
c(N) = c0 sqrt(p(N)/int p dN), p the share of the linear variance carried by the noise of the step at N (P_R at
N_e of the mode entering at N times the lattice factor), so the linear delta N moves by c0 sigma and the
log-weight variance is c0^2. The rule for c0 (median in [3.5, 4.5]), the validation at nu = 3 and the 2 per cent
bar are A9's. Record: `../../g3/amend/JOURNAL.md` entries 7-8; script `../../langevin/scripts/ref_tilt.py`.
(b) Z2 of A3, part (iii): a_zeta of the box contains the field's own even part as well as the map's, a_zeta =
a_map - a_R at second order (zeta = -(d phi_1 + d phi_2)/v + a_map zeta_1^2), a shift of 2.6 per cent at a_R =
1.84e-4 (`../../zeta/JOURNAL.md` entries 3-4), larger than (iii)'s 2 per cent bar. (iii) is judged as written and
is expected to fail; beside it, pre-registered before the reading as (iii'): |a_zeta - (a_map - a_R)|/a_map below
0.5 per cent with a_R measured on the same pairs. The reader judges G3 runs if Z0, Z1, Z2(i) and (iii') pass;
that (iii) fails as written stays on record and is put to the orchestrator.

## 5. Test plan by row of brief section 10

| Row (owner) | Test | Reference | Status 2026-11-15 |
|---|---|---|---|
| Slow-roll and USR cases (E): power spectrum | L3 linear modes, L7 SR ladder and 256^3; A2 | full-MS mode functions, run E-stoch-inf-20261115-122806-ef0d039 | reference ready; waits for core's initial slice |
| same: freezing | A3 on L7 (SR), L8 (USR) | full vs deformed MS (`../fig/fig_freezing.png`), independently confirmed (run E-20261115-135532-3f958a1) | reference ready |
| same: constraints | L5 single kick with negative control; A4, A5 | P1:538-541, 747-773 | waits for core's constraint diagnostics |
| same: background | L1 homogeneous FLRW; A1 | Friedmann reference (two integrators agree) | core's own test run; E's check pending |
| same: time integration | L6; A6 | D4 of run E-stoch-inf-20261115-123936-b2ec5c7 | waits for a run with kicks |
| same: one-point statistics (G3) | A8 | runs E-stoch-inf-20261115-130137/-130139-176cdd6 | reference ready |
| Reproducible random numbers (C, E) | U1-U9 with validator A0-A15 | `../../noise/ref/` | U1-U8 done on core's executable (section 6); U9 pending |

Test ids L0-L9: `../../codebase/DESIGN_REVIEW.md` 8.1; A1-A8: section 4 above; U, A0-A15:
`../../noise/NOISE_SPEC.md` 9-10.

## 6. What core's implementation already shows (`core/scalar-field` 836ac86)

[Record of 2026-11-15, kept as written. Since then: release core-v0.3 (the field merged,
the window increment formed without cancellation) and core's tested branch `core/scalar-2`
(initial slice at N*, constraint record, NRSFDMP2 dumps), which the slow-roll ladder used;
see section 8 and `../../ladder/README.md`.]

Read in the source (`athenak/src/scalar_field/scalar_field_noise.cpp`) [VERIFIED by
reading]: the kicks of SPEC 2.2 in the sign-safe form, d_t Pi += alpha_b (Pi_b/H) I_R,
d_t Khat += -alpha_b eps1 I_R, d_t At_ij += alpha_b eps1 (delta_ij I_R/3 - T_ij); the
projector from the stencil wave number of the centred first difference (default); window
derivatives equal to SPEC 3 term by term; the mode equation d2R/dtau2 + (3 - eps2) H dR/dtau
+ (k/a)^2 R = 0, which is the e-fold form of SPEC 2.3; eps2 = 6 + 2 V'/(H Pi_b) - 2 eps1 =
-d ln eps1/dN (both checked by hand); mode functions and background advanced with the
driver's own low-storage coefficients in every stage, so each stage evaluates its sources
at its own time (DESIGN_REVIEW request R5 met); amplitudes with the keys of NOISE_SPEC 4;
no FFT. Missing for G1: the initial slice at N* (SPEC 5.3; the problem generator offers
`wave`, `flrw`, `plane`), constraint ratios [H], [M] and R^NR output, a card build, the
interface document; level 2 (not needed for G1).

Core's own runs, read in `scratch/core/`, not yet reported by core [TO VERIFY by core's
report]: five existing set-ups byte-identical after the change (core-20261115-132758-ba37619);
homogeneous slow roll in conformal and geodesic gauge at Courant 0.5, 0.25, 0.125
(core-20261115-133955-836ac86).

The lead's runs with core's processor executable (`wt/core-scalar/.work/exe/athena_cpu_836ac86`,
sha256 65ff2162...00144, read only) [VERIFIED by run]: the noise unit test of
`../../noise/NOISE_SPEC.md` section 9 in a scaled base case (N = 32, nmax2 = 100, 120
cycles; the 64^3 x 300 case costs 95 min per run on the serial processor build, run
E-20261115-135218-bdf4710). Runs E-20261115-135523-a32c3a6 (U1-U8), validations
E-20261115-140502-2957846, diagnostic E-20261115-140553-0b75e1e:
- frozen tanh: every test passes; exact reconstruction from the keys to 4.1e-14 of the rms
  (A1), 1, 8 and 64 MeshBlocks bit-identical (A11), restart bit-identical (A12), N = 16
  against 32 to 2.4e-15 (A13), seeds independent (A15), spectrum, Gaussianity, correlation
  function, band limit (A2-A4, A10). This also confirms the dump convention (increment of
  the step ending at the dump cycle).
- Markov Heaviside: every test passes.
- Markov tanh: every test passes except A1 (1.07e-10 against 1e-11): sqrt(W(t) - W(t - dt))
  for modes long past crossing amplifies a one-ulp difference of W between libm and numpy;
  active modes agree to 4e-14 of their amplitude (`fig_lu_diag.png` of the diagnostic
  run). A numerical-hygiene request to core (cancellation-free increment); the
  Mukhanov-Sasaki model uses frozen amplitudes and closed-form window derivatives and is
  not affected.
Not yet exercised by any run: the Mukhanov-Sasaki model, the kicks, the coupling of the
field to Z4c under noise.

## 7. Risks

`../../RISKS.md` (R1-R14). Deciding for the gate: R1 (G1 waits for the initial slice and
the diagnostics), R2 (a hook defect the generator tests cannot see; L5, L6), R4 (freezing
failing for a reason other than a defect), R9 (cost of tail statistics at G3), R10
(competition with the authors of P1).

## 8. Compute estimate on this machine

Inputs [VERIFIED]: Z4c on one A100 at 2.0e7 zone-cycles/s, 128^3, nghost 4
(`docs/TESTLOG.md:46`); the processor build at 1.35e4-1.5e4 zone-cycles/s per core (runs
E-stoch-inf-20261115-122727-a1c2237, E-20261115-135218-bdf4710); A100 80 GB
(`harness/env/machines/anta.sh:17`). Assumed [JUDGEMENT]: field, Tmunu and kicks add 15
percent; synthesis at 3e12 flop/s on the card.

| Item | Card-hours | Note |
|---|---|---|
| SR 256^3, theta = 0.25, 1304 steps | 0.36-0.41 | 1.0-1.1 s per step, 20 GB |
| USR 256^3, theta = 0.25, 1630 steps | 0.45-0.51 | |
| Both at theta = 0.025 (P2's value) | 8-9 | only if L6 demands it |
| Ladder N = 32-128 and L9 at 128^3 | < 0.3 | |
| L0-L6 | minutes of card time | processor build serial and slow (R12) |
| **Total to G2 at theta = 0.25** | **about 1.5-2** | of 10 GPU-hours (decision 0006) |
| Each further 256^3 realisation (G3) | 0.4-0.5 | 1e3 realisations: 400-500 card-hours |

Checked by hand: 256^3 = 1.68e7 cells at 2e7 zone-cycles/s is 0.84 s per step, 0.97 s with
15 percent, plus 4-14 percent synthesis. 512^3 needs 157-204 GB and does not fit one card.

Measured since (wave 2, supersedes the assumptions above) [VERIFIED by run]: core measured
the field and sources at 128^3 (Z4c 1.98e7, with the field 1.39e7, with the sources 1.20e7
zone-cycles/s; run core-20261115-143907-cea4c86): the overhead is 65 percent, not 15. The SR
case at 256^3 in P1's set-up (548958 modes, 1386 steps to N* + 8.10, theta = 0.25, dumps and
the constraint record every step) ran in 1811 s on one A100: 1.30 s per step, 0.503
card-hours per realisation, peak memory 19.6 GB (ladder run E-20261115-172618-f948386; jobs
B and C 1.13-1.30 s per step). USR is not measured; scaled by the step count of the
verifier's cosmic-time span (1701 against 1368 steps, `../../stage/G0/VERIFIER.md` V7) it
would be about 0.63 card-hours [JUDGEMENT]. Theta = 0.25 is justified by A6 (time error of
R^NR below 3e-4 at theta = 0.25, order 3.93-4.08; runs E-20261119-142317-c851f27,
E-20261119-145230-ff0dff2), so the verifier's case theta = 0.025 (6-15 card-hours per
realisation, above the downgrade threshold) is not needed.

## 9. Recommendation to the group [JUDGEMENT]

**Continue** to G1 and G2 (reproduce the SR and USR cases of P1 in AthenaK) at the scope of
section 4, and decide the scope of G3 (tail statistics, S11 deliverable 2) at G2, once the
cost of one realisation has been measured on a card. Not shrink now, not downgrade.

Reasons:
1. The specification is complete and its numbers are reproduced independently (two
   integrators for the backgrounds and the freezing reference; the delta-Pi erratum
   re-derived from P2's own dictionary; the delta-N benchmark by a second method).
2. The implementation already exists in the code base the group chose: core's
   `core/scalar-field` (836ac86) has the field, the kicks in the specified form, the
   stencil-consistent projector, mode functions integrated in lockstep with the RK stages
   and the noise without a Fourier library; its generator passes the validation written
   before the code existed, bit-identical across MeshBlock layouts and restart (section 6).
3. Cost: about 1.5-2 card-hours to G2 at Courant 0.25 against 10 allotted; one 256^3
   realisation 0.4-0.5 card-hours, ten times below the downgrade threshold. [Updated
   2026-11-19: measured 0.50 card-hours for one SR realisation at 256^3 (run
   E-20261115-172618-f948386), ten times below the threshold; the ladder used 1.42
   card-hours in all.]
4. The downgrade path costs nothing extra: the delta-N solvers and reference statistics
   for both potentials exist now and can serve Track A whatever is decided.

Cost of continuing to G2: core's work package (initial slice at N*, constraint and output
diagnostics, card build, interface document; outbox 2026-11-15T14:10Z), Track E's analysis
of AthenaK output (R^NR, per-mode amplitudes, constraint ratios), about 2 card-hours.

Conditions under which the recommendation turns to shrink or downgrade: the freezing
criterion A3 fails in SR at level 0 and level 1 (downgrade, section 4 item 5); a measured
256^3 realisation above 5 card-hours (downgrade); at G2, 1e3 realisations (400-500
card-hours) beyond any allotment the group will grant (shrink G3 to smaller boxes or to
importance-sampled delta-N with a few NR realisations as a check).

The decision to continue, shrink or downgrade is the group's; this document stops here.

## 10. Stage timeline [JUDGEMENT]

| Gate | Content | Depends on | Indicative (charter 9.2) |
|---|---|---|---|
| G0 | this package; group decision | orch | week 2 (now) |
| G1 | SR case: A1-A7 at 256^3 and the ladder | core: initial slice, diagnostics, card build; E: R^NR analysis | week 8 |
| G2 | USR case; sensitivity L9; first cost measurements of many realisations | G1 | month 4 |
| G3 | tail statistics vs delta-N (A8); compaction function | G2 decision on scope | month 9 |
| G4 | paper | G3 | month 12 |
