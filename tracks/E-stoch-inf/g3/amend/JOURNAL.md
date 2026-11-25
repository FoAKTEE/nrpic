# JOURNAL of package g3/amend (Track E, gate G3): the lead's checks of the scope review and the amendments of SCOPE 4d

Batch 19 (2026-11-25), lead of E. Ruling: coord/DECISIONS/0040 item 1. Review: `../scope_review/SCOPE_REVIEW.md`.

## entry-1 (2026-11-25 07:25 PST): B1, the top bin of the lattice factor; predictions before `bins_lead.py`

What I have already seen: the review's numbers (factor 0.279 against 0.934 for |n| <= 32, 0.166 against
0.992 for 64; expected variant/lattice 0.9778 and 0.9906; top-bin share 3.4 and 1.1 per cent). My script
`bins_lead.py` uses none of the review's code and none of ref_spec's binning code (own vector count, own
bins written from the rule, own integrals); its weight (b) takes P_R(N_e) from the reference's linear module.
Predictions:
- LB1 (weight P_R(N_e)): variant/lattice as ref_spec bins it 0.978 +- 0.002 (32) and 0.991 +- 0.002 (64);
  with the top bin cut at NLAT 1.000 +- 0.001 at both; top-bin factor as is 0.28 +- 0.02 (32), 0.17 +- 0.02
  (64); top-bin share of the band 0.034 +- 0.005 (32), 0.011 +- 0.003 (64). Refuted if the as-is ratio at
  32 lies outside [0.970, 0.985] or a fixed ratio outside [0.998, 1.002]: then B1 is not confirmed as
  stated and the reference is not changed on its strength.
- LB2 (weight P = 1, pure lattice geometry, no reference code): the top bin spans only ln 32 - 3.45 =
  0.016 of 3.47 in ln n, so the as-is deficit is small, 0.996-0.998 at 32; fixed within 0.003 of 1 (the
  sparse low shells make the per-bin factor a coarse stand-in for the lattice sum). Refuted outside.

## entry-2 (2026-11-25, written before the rerun of the pilot reference): the corrected reference, its variance gate

Change to `../../langevin/scripts/ref_spec.py` (lattice_factor_fn): the upper edge of the last bin is cut at
NLAT (the review's second option), and for the lattice variant the tails are also standardised with
sigma = sqrt(var_lattice_Ne) (B1, last sentence). The output of the corrected pilot goes to
`results/ref_inflection_n32_binfix.json` (`NRPIC_REF_SUFFIX=_binfix`); the old file stays.
Pilot rerun: 2e5 realisations, NLAT = 32, as E-20261125-115707-b845282 otherwise.
Predictions:
- RF1 (the variance gate of the amended 4d.3 at the pilot's size): var(s0.01_lattice)/var_lattice_Ne =
  1.000 within three of its standard errors (about 0.0032 each at 2e5; the old run gave 0.9796 +- 0.0032).
  Refuted if outside 1 +- 3 se: then the variant has a second defect and no tail comparison uses it.
- RF2 (only the lattice variant changes): every other variant gives the same moments as the old file to
  all printed digits (same seeds from crc32 of the variant name). Refuted otherwise (then the run is not
  deterministic and the pilot comparisons need their own seeds on record).
- RF3: skewness of s0.01_lattice at N_e within two standard errors of the old value (0.0288 class; the top
  bin carries 3.4 per cent of the variance and is near Gaussian at crossing, so the shape moves little).

## entry-3 (2026-11-25 07:40 PST): B2 and B3 from the formulas; predictions before `b2_lead.py`

B2, own arithmetic (`b2_lead.py`, Edgeworth to first order, inputs named in its header). Seen beforehand:
the review's 9.85, 16.9, 4.15 per cent, 0.42 per cent, 0.0095, 0.017, +10.1 per cent, 78 seeds.
- LB3: dlnF/dln sigma 9.85 +- 0.05 (nu = 3), 16.9 +- 0.1 (nu = 4); three combined standard errors at nu = 3
  (S = 256, 4e6) 4.1 +- 0.2 per cent of F; the sigma error seen 0.42 +- 0.03 per cent; skewness seen 0.0095
  +- 0.001; the reference skewness 0.0231 moves F(3) by 10 +- 0.5 per cent; NR error at a third of the
  reference's at 70-90 seeds. Refuted outside: then B2's numbers are not confirmed and 4d.3 keeps r(nu).
B3, from the code (no run): `ladder/scripts/ladder_lib.py` line 180 forms R^NR = dchi/(2 chi) + (H/Pi) dphi
(+ anisotropic part). With gamma_ij = gammatilde_ij / chi the local ln a = -(1/2) ln chi, so dchi/(2 chi)
= -psi, and R^NR = -psi + (H/Pi) dphi. SCOPE 4d.1 defines zeta = -(1/2) ln(chi/<chi>) + Delta N_bg = psi +
Delta N_bg with Delta N_bg = -(H/Pi) dphi at first order (a cell ahead on the roll reaches phi_e sooner).
So zeta = -R^NR at first order [VERIFIED from the formulas; the processor test Z0 checks it on output].
Test (a) of 4d.1 subtracts the box mean of zeta, so it is zero whatever the reader computes: it cannot
fail [VERIFIED from the definition]. Test (b) asks zeta = +R^NR: it fails at first order.

## entry-4 (2026-11-25): outcomes of entries 1-3

LB1 HOLDS (run E-20261125-151230-a4f4059, `bins_lead.json`, `fig_bins_lead.png` looked at): with P_R(N_e)
the variant over the lattice sum is 0.97786 (|n| <= 32) and 0.99058 (64) as ref_spec binned it, 1.00002 and
0.99991 with the top bin cut at NLAT; top-bin factor 0.2789 against 0.9338 (32) and 0.1656 against 0.9922
(64); top-bin share of the band 0.0338 and 0.0113. Every number agrees with the review's (0.9778, 0.9906,
1.00001, 0.99991; 0.279/0.934, 0.166/0.992; 3.4 and 1.1 per cent) to the digits it quoted, from code that
shares nothing with ref_bins.py. B1 is CONFIRMED.
LB2 REFUTED in part: with P = 1 the as-is ratio is 0.99998 (32) and 1.00062 (64), not 0.996-0.998; the
fixed ratio 1.00271 and 1.00226 lies within 0.003 of 1 as predicted. The sparse low shells make the per-bin
factor overcount a flat spectrum by about 0.27 per cent, and at 32 that excess cancels the top-bin deficit
by chance. I had treated the low-shell part as noise around 1. It does not matter for the reference: P_R
rises by four decades across the band, so the low shells carry no weight (LB1).
LB3 HOLDS (run E-20261125-151429-83a040c, `b2_lead.json`): dlnF/dln sigma 9.849 (nu = 3), 16.90 (nu = 4);
at S = 256 and 4e6 reference realisations three combined standard errors are 3.94 per cent of F(3), which a
sigma error of 0.40 per cent, a skewness of 0.0090 or an excess kurtosis of 0.016 produces; the reference
skewness 0.0231 moves F(3) by 10.1 per cent; the NR error falls to a third of the reference's at 87 seeds
(nu = 3) and 50 (nu = 4). With my reference F(3) of 1.5e-3 instead of the review's value the thresholds are a
few per cent lower than its 4.15 per cent, 0.42 per cent, 0.0095 and 78 seeds; B2 is CONFIRMED.
B3 CONFIRMED from the formulas (entry 3).
RF1 HOLDS (run E-20261125-151340-743c38c, `results/ref_inflection_n32_binfix.json`, `fig/ref_inflection_
n32_binfix_pdf.png` looked at): var(s0.01_lattice)/var_lattice_Ne = 0.9993 +- 0.0032 (old 0.9796 +- 0.0032);
the gate flag in the file is true. RF2 HOLDS: every other variant has the same variance, skewness and
kurtosis as in ref_inflection_n32.json to all digits. RF3 HOLDS: skewness 0.0234 +- 0.0037 (old 0.0231 +-
0.0038), excess kurtosis 0.0106 (old 0.0131). Tails of the corrected variant at 2e5 (sigma of the lattice):
F_+(3) 1.585e-3, F_-(3) 1.275e-3, F_+(4) 7e-5, F_-(4) 4e-5 (14 and 8 realisations at nu = 4: no tail
statement at this size). The corrected 128-band reference is the one G3 uses; the 4e6 run follows (SCOPE
4d.9 A1, A9, A10).

## entry-5 (2026-11-25 07:35 PST): A4, the state at N_f in the reference; predictions before the smoke run and the 4e6 run

Change: `sdn/langevin.py` fpt_phase_space takes record_N (a step lands on it; state_at_record returned);
`ref_spec.py` records (phi, varpi) at N_f for the lattice variant (columns 2-3 of the samples; `state_Nf`
in the output) and takes NRPIC_REF_VARIANTS to run a subset. Background at N_f from the corrected pilot:
dphi/dN = 1.420e-6, eps2 = -0.0276 (`results/ref_inflection_n32_binfix.json`).
Smoke run (2e4 paths, s0.01_lattice only, suffix _smoke):
- SM1: it completes; the first-passage moments of s0.01_lattice equal those of a 2e4 run without record_N
  in distribution (variance/var_lattice within 3 standard errors of 1, about 0.03).
- SM2: var(phi at N_f)/(dphi/dN)^2/var_lattice_Ne in [0.95, 1.05] (on the attractor a field displacement is a
  shift in time, delta N = -delta phi/(dphi/dN)); |corr(phi, varpi)| above 0.9 [JUDGEMENT].
The 4e6 run (s0.01_lattice and s0.1, suffix _4e6): RF1's gate within 0.002; skewness of s0.01_lattice
within two of the pilot's standard errors of 0.0234 (0.0234 +- 0.0074); SM2 within [0.99, 1.01];
skewness of phi at N_f below 0.005 in magnitude (A4 prediction of g3 entry 4).
Smoke run E-20261125-152419-40200ec FAILED (exit 1) after the Monte Carlo: the figure of ref_spec.py
assumed every variant present (KeyError 's1' with NRPIC_REF_VARIANTS). The moments printed before the
failure: s0.01_lattice variance/var_lattice 0.9932 +- 0.0105 at 2e4 (SM1 holds). Fixed (the figure draws the
variants that ran); rerun with the same predictions.
Smoke rerun E-20261125-152619-d917a14 (2e4, s0.01_lattice): completes; SM1 HOLDS (variance/var_lattice 0.9932
+- 0.0105, gate true); SM2 HOLDS (var(phi at N_f)/(dphi/dN)^2/var_lattice 0.9932, the same number as the
first-passage variance; corr(phi, varpi) 0.999997). varpi in the solver is dphi/dt (cosmic time): its mean
1.265e-11 = (dphi/dN) H at N_f. Observation [TO VERIFY at 4e6]: the skewness of phi at N_f is 0.023 (+- about
0.02 at 2e4), the size of the first-passage skewness, not below 0.005 as the A4 prediction of g3 entry 4 and
entry 5 above expect. If the 4e6 run confirms it, the one-patch non-Gaussianity is already in the field at
N_f, the map Delta N_bg is nearly linear there, and the review's reading (S1, B3 bullet 3: "the
non-Gaussianity of zeta will come almost entirely from the map") does not hold for the reference; the box's
d phi skewness at N_f (about 8e-4 from a_R, review run E-20261125-131002-ceefa2f) would then differ from the
one-patch field's by a factor of about 30, which A4's comparison would show directly.

## entry-6 (2026-11-25 07:55 PST): outcome of the 4e6 reference (entry 5)

Run E-20261125-152832-c301e92 (4e6 paths each, s0.01_lattice and s0.1, 4 cores, 18 minutes;
`langevin/results/ref_inflection_n32_4e6.json`, `langevin/fig/ref_inflection_n32_4e6_pdf.png` looked at).
- Gate HOLDS: var/var_lattice_Ne = 0.99865 +- 0.00058 (within 0.002 and within three standard errors).
- Skewness of s0.01_lattice at N_e 0.0199 +- 0.0012, excess kurtosis 0.0022 +- 0.0021: within two of the
  pilot's standard errors of 0.0234 (HOLDS). At N_f: 0.0203 +- 0.0012.
- SM2 HOLDS: var(phi at N_f)/(dphi/dN)^2/var_lattice = 0.99849; corr(phi, varpi) 0.999997.
- The A4 prediction HOLDS and my smoke-run observation is REFUTED: the skewness of phi at N_f is
  0.0007 +- 0.0012 (and of varpi 0.011). The 0.023 of the 2e4 smoke run was noise, as its own error bar
  (+- 0.02) said; I should not have written it up as a possible contradiction of the review. The one-patch
  field at N_f is Gaussian to 0.0012 while the first-passage delta N is skewed by 0.020: the non-Gaussianity
  comes from the map (phi, varpi) -> N, as the review's B3 bullet 3 and S1 say. A4's direct comparison
  therefore tests the NR evolution at a precision of about 0.0012 in skewness (the box's own R_lin
  coefficient gives about 8e-4 at 128^3, review run E-20261125-131002-ceefa2f), and the zeta comparison tests
  NR plus the map. R35 is withdrawn.
- Tails (lattice variant, standardised with the lattice sigma, 4e6): F_+(3) = 1.5015e-3, F_-(3) = 1.2105e-3,
  F_+(4) = 4.05e-5 (162 paths), F_-(4) = 2.325e-5 (93 paths); A(3) = 0.107. The relative standard error at
  nu = 4 from direct sampling is 8-10 per cent: A9's sampler is still needed for nu = 4.
- sigma = 0.1 (continuum density of states): skewness 0.0210 +- 0.0010, 0.0011 +- 0.0016 above the lattice
  variant at sigma = 0.01: no coarse-graining dependence seen, but the bound at three standard errors (0.0047)
  is not below 0.0027 as A10 wanted; a lattice variant at sigma = 0.1 of the same size would be the clean test.

## entry-7 (2026-11-25 08:05 PST, lead of E, batch 20): A9's tilted reference and the lattice variant at sigma = 0.1; predictions before the runs

Defect found and fixed before any registered run: `sdn/langevin.py` normalised the bias direction e = L^-1 u
by its norm also where the noise vanishes (lattice factor 0 at the band edge), e = 0/0, so every biased path
turned NaN (smoke test in scratch/E-stoch-inf/tmp/smoke_tilt, not registered). The shift is now skipped where
L = 0. Unbiased runs (bias None) do not pass through that line: the 4e6 direct run is unaffected.

`langevin/scripts/ref_tilt.py` (new): the s0.01_lattice system of `ref_spec.py` with a constant shift c of the
noise along its dominant direction, the rule for c fixed in the script's docstring before the run (pilots of
1e5 paths at |c| = 1..3.5, median of the tilted x interpolated to 4, a confirmation pilot within [3.5, 4.5]),
then 4e6 paths per side. Validation at nu = 3 against the direct 4e6 samples (E-20261125-152832-c301e92).
- TL1: the chosen |c| lies in [1.5, 3.0] on both sides [JUDGEMENT: a shift of 4 sigma spread over a window of
  ln 32 = 3.5 e-folds needs c of about 4/sqrt(3.5) = 2.1; a response that is not flat across the window moves it].
- TL2 (A9, g3/JOURNAL.md entry 4): relative standard error of F_+(4) and F_-(4) at or below 2 per cent (refuted
  above 3 per cent). [For a Gaussian with the optimal shift the error would be 0.1 per cent; a constant c is not
  the optimal profile, so I expect 0.2-1 per cent.]
- TL3: validation at nu = 3: tilted F_pm(3) within two combined standard errors of the direct 4e6 values
  (direct F_+(3) = 1.5015e-3, F_-(3) = 1.2105e-3 at latsig; combined error about 1.4 per cent).
- TL4: mean path weight within three of its standard errors of 1.
- TL5: F_+(4)/Q(4) in [1.15, 1.40] and F_-(4)/Q(4) in [0.6, 0.85] (direct 4e6: 4.05e-5 and 2.325e-5 against
  Q(4) = 3.167e-5, i.e. 1.28 and 0.73 with 8 and 10 per cent errors).

Lattice variant at sigma = 0.1 (`ref_spec.py` variant s0.1_lattice, new; the variance gate now loops over the
lattice variants that ran), 4e6 paths, 128 band (A10's coarse-graining bound, review N3):
- TS1: variance gate passes (var/var_lattice_Ne - 1 within three standard errors, about 0.002 relative).
- TS2: skewness of delta N at N_e within 0.0027 of the s0.01_lattice value 0.0199 +- 0.0012 (the continuum pair
  s0.1 - s0.01 differed by 0.0011 +- 0.0016). Refuted if the difference exceeds 0.0027 by more than two combined
  errors: then the coarse-graining dependence is not bounded below the T threshold and sigma must be stated.
- TS3: state at N_f: var_phi within 0.5 per cent of s0.01_lattice's 4.913e-13 and skew_phi below 0.004 in magnitude.

## entry-8 (2026-11-25 08:14 PST): the constant shift of A9 fails its smoke test; a shift profile instead, before any registered run

Unregistered smoke tests (scratch/E-stoch-inf/tmp/smoke_tilt, logs log2 and log3; their outputs deleted from
`results/` and `fig/`): with the constant shift of A9 as written, the pilot needed c = 3.3 for a tilted median
of 4 sigma, and the mean path weight of 3200 paths was 0.010 (expected 1): the shift is spent evenly over the
window while the linear delta-N variance comes mostly from its last e-fold, so the log-weights have variance
c^2 W = 39 and the estimator is useless at any affordable size. TL1 of entry 7 is moot.
Change (`ref_tilt.py`, before the registered run): c(N) = c0 sqrt(p(N)/int p dN), p(N) = P_R(sigma aH(N)) at N_e
times the lattice factor, i.e. the shift follows each step's share of the linear variance; then the linear
delta N moves by c0 sigma and the log-weight variance is c0^2 (16 at c0 = 4). Smoke pilot with 1600 paths per
point: median of the tilted x = 3.03, 3.57, 4.00, 4.57 at c0 = 3, 3.5, 4, 4.5 (side +). [This informs TL1'.]
This departs from the wording of A9 ("a constant shift c"); the rest of A9 (median in [3.5, 4.5], validation at
nu = 3 within two standard errors, 2 per cent bar) stands. Proposed as a dated note to A9 in SCOPE 4d.9.
- TL1': c0 within [3.5, 4.5] on both sides.
- TL2-TL5 of entry 7 stand unchanged (TL4: mean weight within three standard errors of 1).

## entry-9 (2026-11-25 08:32 PST): outcome of TS1-TS3 (lattice variant at sigma = 0.1, run E-20261125-160722-a6d1f26)

4e6 paths, 128 band, 2 cores, 17 min (`results/ref_inflection_n32_s01lat.json`, `fig/ref_inflection_n32_s01lat_pdf.png`
looked at: the density follows the Gaussian of the linear variance to 3e-5; in the right panel the skewness square
sits at the edge of the axis because only one variant ran, a cosmetic defect).
- TS1 FAILED: var/var_lattice_Ne = 1.00245 +- 0.00050, 4.9 standard errors above 1 (s0.01_lattice: 0.99865 +- 0.00058).
  The sigma = 0.1 variant is 0.38 per cent above the sigma = 0.01 one. No cause named [JUDGEMENT, untested: modes
  joined 2.3 e-folds after crossing instead of 4.6 carry a gradient correction of order (sigma)^2 = 1e-2 of their
  power at their entry; a test would vary sigma at 0.05 and 0.2]. The G3 reference stays sigma = 0.01 (A10).
- TS2 HOLDS as worded: skewness 0.01824 +- 0.00136 against 0.01989 +- 0.00117, difference -0.0017 +- 0.0018, inside
  0.0027. But the bound A10 wanted is NOT reached: at two standard errors the difference may be 0.0053, twice the
  threshold of (T). Bounding the coarse-graining dependence of the skewness below 0.0027 needs about 4 times the
  paths of both variants (or the paired-noise design: same noise for both sigma).
- TS3 HOLDS: var_phi at N_f 4.932e-13 (+0.39 per cent of sigma = 0.01's 4.913e-13); skew_phi 0.0024 +- 0.0013.
  Exceedance at latsig: F_+(3) 1.4515e-3, F_-(3) 1.2698e-3, F_+(4) 3.93e-5, F_-(4) 2.35e-5.
