# Review of the G3 scope of Track E (SCOPE section 4d, commit cbe20398), before its production runs

Reviewer: a helper of E who did not write 4d (batch 18, 2026-11-25; decision 0039 item 1). Question: can
4d, as written, be failed by the runs it plans, and would passing it mean what it says? The scope text is
changed by the lead, not here. This file sits in the package directory `g3/scope_review/` (the only path
this package may write); the lead may copy it to `g3/SCOPE_REVIEW.md`.

Evidence: four registered processor runs (no card time). Predictions are in `JOURNAL.md` entries 1, 3 and 5,
written before each run (RB1 after a development run had shown its number; entry 1 says so). Outcomes are in
entries 2, 4 and 5, and every figure was looked at.

| Run | What | Script |
|---|---|---|
| E-20261125-130854-ef74ef8 | expected variance of the lattice-density variant of the one-patch reference, from its own bins | `ref_bins.py` |
| E-20261125-131002-ceefa2f | own reader (own dump and record parsers, own R^NR) on the 128^3 mirrored pair b_p/b_m of the window scan (E-20261120-222424-0eb754b, dump 20): one-point statistics, effective cells by Owen's T and by blocks, box-variance share, second order of R^NR | `box_stats.py` |
| E-20261125-131336-2b903fe | detection thresholds of the 4d.3 comparison from the two runs above and the 128-band reference | `sensitivity.py` |
| E-20261125-131805-0806ef8 | uniformity of K, chi and alpha on the geodesic slice at all 21 dumps of b_p: lever arm of the gauge leg | `kcheck.py` |

## Verdict

**Change these items first, then queue.** Do not queue the full set as written. Items B1-B3 change no card
run and are processor work. They change what the runs are compared with and how. Until they are fixed, a
"NR differs from one-patch delta N" result would most likely come from the reference or from the reader.
S3 decides whether the gauge leg (1.2 card-hours) is worth queuing at all. The pilot (q0045) may run as it
is, and so may the three-amplitude and 160^3 runs (G3-C, G3-R) once S4 and S5 are written in. Queue the
baseline after S1 and S2 are decided, because S2 changes how its seeds are laid out.

## Blocking

### B1. The named reference has a bin defect that by itself produces a "difference" of 7.6 standard errors

4d.3 names "sigma = 0.01 with the lattice density of states" as the G3 reference. That variant multiplies
the noise by the shell-count factor of 0.05-wide bins in ln n (`langevin/scripts/ref_spec.py` lines 64-77).
The last bin is [3.45, 3.50) for |n| <= 32, but the band ends at ln 32 = 3.466. So the bin's continuum
volume is counted to e^3.5 = 33.1 while its shells stop at 32. Its factor is 0.279 where it should be 0.934
(|n| <= 64: 0.166 against 0.992). The top bin holds 3.4 per cent of the 128-band variance (1.1 per cent of
the 256 band). Expected variance of the variant over the lattice sum, computed without Monte Carlo: 0.9778
(|n| <= 32) and 0.9906 (|n| <= 64). Measured: 0.9796 +- 0.0032 and 0.9905 +- 0.0016 (pulls +0.55, -0.05).
With the top bin truncated at ln NLAT the expected ratio is 1.00001 and 0.99991 [VERIFIED, run
E-20261125-130854-ef74ef8, `fig_ref_bins.png`]. The "six standard errors" tension (langevin/JOURNAL.md,
entries 10 and 04:05 PST of 2026-11-25) is this bin, not physics. The deficit moves F_ref(3) by -10.5 per
cent, which is -7.6 combined standard errors with S = 256 and a 4e6-realisation reference [VERIFIED, run
E-20261125-131336-2b903fe]. The rule of 4d.3 would then report "NR differs from one-patch delta N".

Proposed wording (4d.3, after "The G3 reference proper"): "The lattice factor is applied per shell, or the
last bin is truncated at ln NLAT. Before any tail comparison the reference variance must equal the lattice
sum var_lattice_Ne within 0.002 relative (three standard errors at 4e6 realisations). The reference and the
box are standardised with the same sigma_lin, the lattice value." (`ref_spec.py` uses sqrt(var_cont_Ne) =
0.49431 for every variant. The box record gives 0.49395. The 0.07 per cent difference moves F(3) by 0.7 per
cent, half a combined standard error.)

### B2. At nu = 3 the statistic cannot tell a variance error from a tail difference

The thresholds are fixed multiples of sigma_lin, so F(nu) responds to the variance with dlnF/dln sigma =
nu phi/Q: 9.85 at nu = 3 and 16.9 at nu = 4. With S = 256 seeds and 4e6 reference realisations, three
combined standard errors at nu = 3 are 4.15 per cent of F(3). That corresponds to a sigma error of 0.42 per
cent, a skewness difference of 0.0095, or an excess-kurtosis difference of 0.017 [VERIFIED, run
E-20261125-131336-2b903fe]. Three different causes each move F(3) by about 10 per cent: a 1 per cent sigma
error, the whole delta-N skewness of the band (Edgeworth with the reference skewness 0.0231: +10.1 per
cent), and the B1 defect (-10.5 per cent). A significant r(3) is therefore not evidence about the tail.

Proposed wording (replace the "G3 result" paragraph of 4d.3): "Judged separately: (V) the variance,
sigma^2_NR / var_ref - 1 with its combined standard error. (T) the shape of the tail at matched variance:
the skewness and the excess kurtosis of zeta directly, and F_pm at thresholds nu sigma_own, where each side
uses its own measured variance. Also the antisymmetric part A(nu) = (F_+ - F_-)/(F_+ + F_-), which a
variance error leaves unchanged to first order. 'NR differs from one-patch delta N in the tail' only if (T)
exceeds three combined standard errors." The direct skewness comparison has a three-standard-error threshold
of 0.0027 (NR 3.1e-4 at 256 seeds, reference 8.5e-4 at 4e6), 3.5 times finer than what F(3) resolves
[VERIFIED, same run]. Against the reference skewness of 0.023-0.028, that is a 10-12 per cent test of the
non-Gaussianity.

### B3. Neither test of the zeta reader can fail on what the comparison rests on

(a) "zeta = 0 to 1e-10 on a homogeneous run". zeta has its box mean subtracted, so on a homogeneous run it
is zero to round-off whatever the reader computes. This test cannot fail.

(b) "zeta = R^NR to second order in s on a run at s = 1/4". This tests only the first order, and at second
order zeta and R^NR are supposed to differ. The second order is the signal:
- On the existing 128^3 pair the even part of R^NR has the local quadratic coefficient a_R = 2.81e-4. In
  R = O + a(O^2 - <O^2>), the one-patch reference has a = skew/(6 sigma) = 0.0078 (lattice variant) to
  0.0095 (continuum). R^NR therefore carries 3-4 per cent of the delta-N non-Gaussianity [VERIFIED, run
  E-20261125-131002-ceefa2f, `fig_box_stats.png` panel c].
- The chi term of R^NR has rms 8.3e-7 sigma_lin and the anisotropic term 2.3e-7. On the geodesic slice at
  N_f the local scale factor is uniform to about 4e-7, since eps1 ~ 1e-12 after USR (record header). R^NR is
  (H_b/Pi_b) dphi to one part in 1e6 [VERIFIED, same run].
- [JUDGEMENT] So the non-Gaussianity of zeta will come almost entirely from the map Delta N_bg(phi,
  dphi/dN) that the reader evaluates on homogeneous backgrounds. A reader with a wrong quadratic coefficient
  passes (a) and (b), and the comparison then reports "NR differs" at the size of the error.
- Sign: from the definitions, a cell with dphi > 0 lies ahead on the roll (Pi_b = +2.68e-7 at N_f, dump
  means of the same run) and reaches phi_e sooner. So Delta N < 0 while R^NR > 0, the chi terms also enter
  with opposite signs, and zeta = -R^NR at linear order [JUDGEMENT from the formulas in 4d.1; a one-line
  processor check]. Test (b) as written fails at first order. A reader made to pass it would swap F_+ and
  F_- against the reference. The predictions G3-T (g3/JOURNAL.md entry 2: F_+(4)/Q in [0.9, 1.4], F_-(4)/Q
  in [0.6, 1.1] "for both variables") cannot both hold if zeta = -R^NR.

Proposed wording (4d.1, replacing the two reader tests):
- "Z0: zeta = -R^NR at first order. On a mirrored pair at s = 1/4 (32^3, processors), the odd part of zeta
  plus the odd part of R^NR is below 1e-3 of the odd part's rms.
- Z1: the map. Homogeneous runs (noise off) with the initial field shifted by +-eps, +-2eps (and the same
  for Pi). The un-subtracted zeta equals the e-fold difference to phi_e of an independent homogeneous
  integrator, first and second finite-difference coefficients within 1 per cent.
- Z2: the second order on the lattice. On mirrored pairs at s = 1/4 and 1/2 (32^3), the even part of zeta
  regressed on O^2 - <O^2> gives a_zeta. a_zeta agrees between the two amplitudes within 2 per cent and
  agrees within 2 per cent with the quadratic coefficient of the independent map along the box's (dphi,
  dPi) relation."

## Should change

### S1. What "passing" means: the comparison is mostly of the same map applied twice

[JUDGEMENT, from B3's numbers] The box's own non-Gaussianity at N_f (a_R = 2.8e-4, implied skewness 8.3e-4)
is below the 0.0027 three-standard-error skewness threshold of the comparison. The delta-N part comes from
the separate-universe map, which the reader and the reference both apply. So "NR agrees with one-patch delta
N within the stated error" will be true but says little about NR. It mainly checks the variance and the
reader's map, and it cannot see the NR-specific non-Gaussianity (gradients, metric backreaction) at its
present size. Proposed addition to 4d.3: "The box's one-point distribution of (dphi, dPi) at N_f is compared
directly with the reference's state (phi, varpi) at N_f, which ref_spec.py adds to its output: variance and
skewness, with the precision stated in advance. This isolates the NR evolution from the common map. The
result sentence says which of the two comparisons a statement rests on."

### S2. Run the baseline as mirrored pairs

At no extra cost, seed i runs at noise_mode_scale = +1 and -1, as b_p/b_m already did. The even part of a
pair is the non-Gaussian part with no Gaussian sample variance. From one 128^3 pair, a_R comes out with a
residual of a tenth of the even part [VERIFIED, run E-20261125-131002-ceefa2f]. Likewise F_+(X+) - F_-(X-)
vanishes when the even part vanishes, so the Gaussian sample variance cancels from it to first order. With zeta, a_zeta from a few pairs is far more precise than the reference
(S1, B3). Proposed wording (4d common set-up): "Seeds i = 0..127, each at s = +1 and s = -1 (256 runs)."

### S3. The gauge leg has no lever arm and cannot fail

`lapse_kdriver` drives K towards its mean. On the geodesic slice of the 128^3 USR box K is already uniform.
rms dK/|K| is at most 4.0e-7 over the whole run (at cN = 1.5), 7e-12 at the end of USR and 4.9e-13 at N_f.
rms dchi/chi stays at 8.2e-7 from cN = 3.4 on, while the rms of (H/Pi) dphi grows from 1.7e-5 to 0.495
[VERIFIED, run E-20261125-131805-0806ef8, `fig_kcheck.png`]. The whole curvature perturbation lives in dphi on
an unperturbed geometry. A K-driven slicing has nothing to drive and coincides with the geodesic one to about
1e-6 of zeta. The paired differences of 4d.6 will be zero within their errors. For the same reason the clause
"AND the gauge leg does not move F" in 4d.3 is met automatically. [JUDGEMENT for the kdriver runs themselves:
scalar_field_3.md section 5 measured a lapse perturbation of 3e-6 in the quadratic case. The pilot pair
k000/k001 will show it for this case.] Proposed wording (4d.6): "First the pilot pair k000/k001 is read. Report rms(alpha - 1) and
rms of H int (alpha - 1) dt at N_f in units of sigma_lin. If this is below 1e-3, G3-G is recorded as 'no
lever arm in this model' and the 32 kdriver seeds are not queued. A slicing test then needs a lapse that
depends on the field (a request to core), or the scope states that the slicing question is empty for this
model at N_f." Also define "its own standard error" in 4d.3 (paired, over 32 seeds).

### S4. G3-C can pass with nothing judged

The judged set is the dumps with cN in [2.0, 6.6] where the smaller even part exceeds 3 sigma. With
dump_dt = tlim/20 those are dumps 4 to 13 (cN about 2.07 to 6.52; tlim is N* + 10 e-folds, H about 0.95-1
in code units). At 128^3 the quarter amplitude may pass the 3-sigma bar at few or none of them: in G2 at
256^3 the 4c floor judged H at only 3 dumps from the quarter pair (g2prod/JOURNAL.md entry 4.1). With none
judged, the factor criterion holds vacuously. Proposed wording: "each factor (1 over 1/2, 1/2 over 1/4) and
each constraint is judged at no fewer than four dumps of the range, otherwise 'not testable', which is not
a pass. The largest deviation from 4 is reported." The band 4 +- 0.05 is ten times wider than the
three-amplitude reading at 256^3 (4 +- 0.0045 for H, 4 +- 0.0012 for M; g2prod/JOURNAL.md entry 4.2). It
can still fail, but only on a gross departure. The model test (ratio in [0.9, 1.1], correlation in [-0.30,
-0.17]) can fail and is the real test.

### S5. G3-R hangs on one mode

The maximum of D^L over modes can sit on a single mode. In G2, U-R (i) gave 2.10 because the maximum sat on
the s^2 common mode (g2prod/JOURNAL.md entry 2.3), which Richardson in s now removes. Proposed addition: "a
model test of the asymptotic regime: the median over modes k <= k_max/2 of D^L_n(128)/D^L_n(160) also lies
in [2.0, 4.5], and the sign of L_n/(W_n R_n alpha_n L^-3/2) - 1 is the same at both resolutions for at least
90 per cent of those modes." The criterion as written can fail and has its number. This only makes it
robust.

### S6. nu = 4 cannot fail on the physics unless the reference reaches a few per cent

With a 4e6 direct reference (relative standard error 8.9 per cent at nu = 4), three combined standard
errors are 27 per cent of F(4). That is more than the whole delta-N skewness effect there (24 per cent)
[VERIFIED, run E-20261125-131336-2b903fe]. Proposed wording (4d.3): "The importance-sampled reference at nu
= 4 reaches a relative standard error of at most 2 per cent, fixed before the comparison and validated as
stated; otherwise nu = 4 is reported, not judged."

### S7. 256 seeds are more than the comparison can use

The power estimate holds up under an independent estimator. Owen's T with the record's correlation gives a
per-box s.d. of F_+(3) of 5.42e-5 (4.0 per cent of Q(3); n_eff 4.6e5). The power run gave 4.96e-5 and 5.5e5,
9 per cent lower in s.d., which is 2.6 times the sampling error of its 400 boxes. A block jackknife on the
real box gives 5.40e-5. At nu = 4: 6.20e-6 (19.6 per cent). rho(r) = 0.68 and 0.26 at one and two cells,
then near zero: the cells are nearly independent beyond two cells [VERIFIED, run E-20261125-131002-ceefa2f].
The scatter of the box variance is 0.39 per cent per box and makes up 23 per cent of Var F(3) (2.8 per cent
at nu = 4). My own prediction that it would dominate was refuted (JOURNAL entry 2, BS3).

However, the "3.6 per cent at three standard errors" of 4d.2 ignores the reference's error. The NR error
falls below a third of the reference's at 78 seeds (nu = 3) and at 44 seeds (nu = 4, 4e6 direct). So 256
seeds are not too few. They are more than the comparison can use unless the reference improves (S6). The
seeds are cheap (about 9 card-hours), so the proposal is about order, not about cutting: queue 128 mirrored
pairs (S2). Raise S beyond that only if the nu = 4 reference reaches about 1.5 per cent.

## Notes

- N1, statement (4), "R^NR Gaussian to the precision of one box": confirmed, and more strongly. An
  independent reader reproduces sd/sigma_lin 1.001616, skewness 0.001384, F_+(3)/Q 1.0481, F_-(3)/Q 1.0336,
  F_+(4)/Q 1.099 and F_-(4)/Q 1.220 to every digit read_seed.py quoted. The pair gives mean skewness 8.4e-4
  and a_R = 2.8e-4 (3-4 per cent of delta N) [VERIFIED, run E-20261125-131002-ceefa2f]. With 256 seeds the
  skewness of R^NR (about 8e-4) will be measured at about 2.7 standard errors (3.1e-4), so "Gaussian" should
  read "non-Gaussian at 3-4 per cent of the delta-N level". The G3-T band for the R^NR skewness, [-0.01,
  0.05], cannot discriminate. Suggest [0, 0.002].
- N2, box mean and box-scale modes: the box mean of R^NR is zero by construction (no k = 0 mode). The
  effective number of modes of the variance is 1.32e5, against about 1.37e5 lattice vectors in the band: the
  per-mode power is nearly flat, so no few box-scale modes dominate. The lowest shells carry P_R ~ 1e-5 of a
  band variance of 0.244. Subtracting the box mean of zeta shifts it by about a sigma^2 x 0.0039 ~ 1e-5
  sigma, which is negligible [VERIFIED for R^NR, same run; JUDGEMENT for zeta].
- N3, the reference against what the box measures. Time of the uniform-field surface: the 128-band
  reference gives the same variance and skewness at N_f and N_e (s0.01: 1.0009 and 1.0010; 0.0288 and
  0.0282; ref_inflection_n32.json, run E-20261125-115707-b845282), so the surface time does not matter for
  this band. Coarse-graining scale: the variance needs sigma = 0.01 (sigma = 1 gives 1.379 times linear,
  because gradients at crossing are missing). The skewness at sigma = 1, 0.1, 0.01 is 0.0225 +- 0.0056,
  0.0116 +- 0.0047, 0.0282 +- 0.0044 (128 band) and 0.0436, 0.0429, 0.0381 +- 0.002-0.003 (256 band, 1e6),
  i.e. weakly dependent on the coarse-graining at the present precision. Suggest the 4e6 reference also runs
  sigma = 0.1, to bound that dependence below the 0.0027 threshold. Linear against nonlinear: comparing zeta
  (not R^NR) is right, with the sign of B3.
- N4, the linear-limit variant s0.01_lin of the 128 band gives 0.9844 of the continuum variance from 5e4
  realisations. That is about 2.5 standard errors low by my estimate sqrt(2/5e4) = 0.0063 [TO VERIFY in the
  4e6 run; the file carries no standard error for the rescaled variance].
- N5, items of section 4d that cannot fail as written: the zeta reader tests (a) and (b) (B3); G3-G (S3);
  the judged nu = 4 comparison with a direct reference (S6); G3-C when nothing is judged (S4); G3-L2 by
  design (a report, which is fine as labelled; the G3 statement should then say "at level 0"). Items that
  can fail and have their numbers: G3-C model test and factors, G3-R, the pilot's G3P-1 to G3P-3.
- N6, budget and order (4d.8): about 14 of 60 card-hours, checked against the window scan's cost (0.3836
  card-hours for 16 runs of E-20261120-222424-0eb754b, about 0.035 per 128^3 USR run with 21 dumps; the G3
  runs dump twice and should cost less). Level 2: 32 x 0.035 x 1.7 is about 1.9, not 1.5. Proposed order:
  (1) processor work: B1 fix plus the 4e6 reference with the nu = 4 importance sampler (S6) and the (phi,
  varpi) output (S1); the zeta reader with Z0-Z2 (B3). (2) Pilot q0045, now waiting at priority 5 although
  the gate package waits for it (the rules give 2). Read its cost and the kdriver lever arm (S3). (3) G3-C
  (6 runs) and G3-R (4 runs), about 0.9 card-hours: they can invalidate the set, so they go before the
  baseline. (4) Baseline as 128 mirrored pairs. (5) Level 2, 32 seeds (or 16 pairs). (6) The gauge leg only
  if S3 finds a lever arm.

## Requests

- To the lead of E: the wording changes above (B1-B3, S1-S7). Fix `lattice_factor_fn` in
  `langevin/scripts/ref_spec.py` (per-shell factor or truncated top bin) before the 4e6 reference. Add the
  (phi, varpi) state at N_f to its output. Raise q0045 to priority 2 if the gate waits for it.
- To core (only if S3 confirms no lever arm and the group wants a slicing test): a lapse condition that
  depends on the field, for example a driver towards uniform phi. Not needed for the rest of G3.
