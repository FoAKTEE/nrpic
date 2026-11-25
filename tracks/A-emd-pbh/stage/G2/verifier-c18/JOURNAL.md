# JOURNAL of verifier-c18 (fresh verifier of item C18 of gate G2, Track A; batch 18)

Helper of A-emd-pbh, 2026-11-25. Decision 0016 item 4, decision 0039 item 2(b). Processors
only, no card run. Claims are taken from the result tables of `threshold_ball/README.md` and
`conv_ball/README.md`; criteria from `scope/SCOPE.md` sections 3 and 7; predictions of the
packages as written before their runs (`conv_ball/JOURNAL.md` entry 3, committed before job 1;
`threshold_ball/JOURNAL.md` entry 1, committed 12:41:43 PST 2026-11-21 as c48bd33b, and entry 11's
statement of T4 written before its analysis). Not read before VERIFIER-C18.md is written: the
outcome entries of both journals, `stage/REVIEW-wave3.md`, `stage/G2/CHECKLIST.md`.

Readers and reference are the verifier's own (`scripts/vread.py` from docs/FORMATS.md and
coord/INTERFACES/diagnostics.md; `scripts/vref.py`: LTB dust from the format-2 table, written
from coord/INTERFACES/spherical_id_format2.md and the dust equations; `scripts/vmeasure.py`).
Nothing of conv_ball, threshold_ball, runs_ball, expball or python/nrpic is imported.

## Entry 1, 2026-11-25 13:02Z: predictions for the tests of the readers and the reference (before running them)

V0a (reference on an analytic field). A synthetic format-2 table of closed FLRW dust in
stereographic coordinates (psi^2 = 1/(1 + rbar^2/(4a^2)), KL = KT = -H, alpha = 1) at
eta0 = 1.2, a_m = 10, 4001 rows to rbar = 2a: vref.LTB returns m = a_m sin^3(chi)/2, the
turnaround tau_ta = (a_m/2)(pi - eta0 + sin eta0) and tau_AH from (1 - cos eta_AH)/2 = sin^2 chi
with relative errors below 1e-6 for chi in [0.1, 1.4] (second-order differences on rows of
about 5e-3 a; truncation about 1e-6 at worst). Refuted by an error above 1e-5 anywhere there.
V0b (exact areal radius). vref.LTB.areal_radius at tau_AH returns 2m to 1e-9 relative, and at
tau_ta returns 2A = a_m sin chi to 1e-9. Refuted by more.
V0c (trajectory reader). Synthetic traj/trajmet files (5 particles, 11 times, linear in t),
with a "restart" that repeats the last three times with changed values: Tracks keeps the
repeated (later) values, interpolates linear data exactly (1e-14), and the areal radius of
gamma_ij = A n_i n_j + B (delta_ij - n_i n_j) equals r sqrt(B) to 1e-14. Refuted otherwise.
V0d (summary reader and the BH rule). Synthetic summaries with known outcomes: (i) found from
search 10 to the end (40 searches every 0.25, mass 0.3): BH, persistent from t(10); (ii) the
same with the last search failed: not BH; (iii) found only in the last 3 searches spaced 0.25
(span 0.5 < 5 x 0.3): not BH; (iv) duplicated times with the later copy failed: the later copy
wins. Refuted by any other answer.
V0e (line measures). A tab line of Schwarzschild in isotropic coordinates (psi = 1 + M/(2r),
K = 0, M = 1, points 0.05 apart on [-16, 16]): line Misner-Sharp mass 1 to 1e-3 for r > 1 (the
derivative is second order on 0.05), MOTS at |x| = 0.5 with m = 1 to 2e-3; the constraint ratio
of a line with H = 0.3 x 16 pi E is 0.3 to 1e-12 in every weighting. Refuted otherwise.
V0f (the real tables). For the table of conv_ball's data set 3 my reference gives the exact
events the packages quote (conv_ball/JOURNAL.md entry 3, DESIGN.md 1: core turnaround 3.3716,
tau_AH of the core edge 9.5511, m 0.686563) to 1e-3 relative or better, and for the eight
threshold tables the tau_AH column of threshold_ball/DESIGN.md section 1 (15.386 ... 114.574)
to 1e-3 relative. This is the first independent check of the exact column; refuted by a
difference above 1e-3 relative in any member.

### Entry 1 outcome (registered run A-20261125-130535-b79555d; fig_v0a.png, fig_v0e.png looked at)

Before the registered run, an unregistered smoke run of the same script (scratch/A-emd-pbh/tmp/
vc18_smoke, a debugging run, stated here because its result changed the code) gave V0a FAILED:
relative errors 3.9e-6 in m and 1.5e-5 in tau_ta, tau_AH at chi = 0.1, above the 1e-5 bound. The
cause is the cancellation in 1 - (dR/dl)^2 at small radii (relative error amplified by 1/chi^2)
with a second-order derivative of the table; the core-edge "exact" values also came out 1e-3 off
because the last row inside the break is up to one row (1e-3) inside the edge. Changes (commit
before the registered run): fourth-order central differences of R inside each piece, quadratic
extrapolation of the last three rows of a piece up to its break. Registered outcome:
- V0a PASS: max relative error 4.8e-12 (m), 1.9e-11 (tau_ta), 1.8e-11 (tau_AH) for chi in [0.1, 1.4].
- V0b PASS: R(tau_AH) = 2m to 3e-13, R(tau_ta) = a_m sin chi to 2.4e-12.
- V0c PASS: trajectory reader keeps the later of repeated records, interpolation and areal radius
  exact to 4e-16.
- V0d PASS: the BH rule gives (i) BH from t(10), (ii)-(iv) not BH; the duplicated-time summary
  keeps the later (failed) copies.
- V0e PREDICTION FAILED in one part: the line Misner-Sharp mass of Schwarzschild is 1 to 2.0e-4 for
  r > 1 (pass) and the constraint ratio is 0.3 to 5e-15 in all three weightings (pass), but the
  line MOTS sits at |x| = 0.5031, not within 2e-3 of 0.5 (error 3.1e-3); its mass is 1.0006 (within
  the 2e-3 predicted). Cause: second-order differences on 0.05 spacing where psi is steep; the
  mass, which is what is used, is within bound. The line MOTS mass is used below only as a
  secondary check with an uncertainty of order 1e-3 at that resolution.
- V0f PASS for all eleven tables (relative differences to the quoted values at most 2.6e-6 after the
  fix): data set 3 (and its 1.25, 1.35 balls) core turnaround 3.371611, core-edge tau_AH 9.551093,
  m 0.686562 (quoted 3.3716, 9.5511, 0.686563); threshold tables tau_AH(edge) 15.386139, 23.404718,
  35.159637, 40.053600, 43.656126, 46.415299, 54.979747, 114.574469 for delta_c = 1.0 ... 0.2
  (DESIGN: 15.386, 23.405, 35.160, 40.054, 43.656, 46.415, 54.980, 114.574), m_edge 0.54925 ...
  0.32955 as quoted. Core homogeneity: tau_ta equal at rbar = 1, 2 and the edge to 1e-6; the first
  trapped row beyond rbar = 0.3 is the last row inside the core edge in every table (the core edge
  is the first trapped sphere, as threshold_ball/DESIGN.md section 1 states). [VERIFIED] The exact
  columns of both packages are reproduced by an independent reference.

## Entry 2, 2026-11-25 13:15Z: predictions for the recomputation of conv_ball (before running vconv.py)

Claims (conv_ball/README.md table and findings; final analysis A-20261121-120257-a2eb839): first
detection t, ddet, dtrap, mass median per member; mesh orders ddet 1.5, 2.0, dtrap 2.1, 1.5; mass
7.4e-3 -> 2.1e-3 -> 2.1e-4; fixed N = 4969736 mass 2-5e-4 on all meshes; at B the time errors do
not depend on N, the mass does (-2.1e-3 vs -3.0e-4).
- P1 first detection times: identical to the printed digits of the table (same files, my reader).
  Refuted by any difference.
- P2 ddet: my two interpolations agree with each other within 0.005 M and with the table within
  0.01 M for A, B, C, A-N8, A-N64, B-N8, B-R1.25, B-R1.35, A-R1.25, A-R1.35 (the definition is the
  same; band means and record interpolation may differ). The mesh orders then reproduce within
  +-0.3 (1.5, 2.0). Refuted by a larger difference.
- P3 dtrap: within max(0.005 M, 20 per cent) of the table values for the mesh triple. Refuted
  otherwise.
- P4 mass median: within 1e-3 (absolute, relative mass error) of the table for every member, with
  |dm(A)| > |dm(B)| > |dm(C)| reproduced; the C value below 1e-3 in magnitude. My exact horizon mass
  interpolates the trapped label between tracked bands, which the package may not; where the bands
  are far apart (gap > 0.1 in rbar) I expect differences up to 1e-3. Refuted by a larger difference
  or a changed ordering.
- P5 particle leg at B: |ddet(B) - ddet(B-N8)| < 0.01 M and the masses differ by more than 1e-3
  (-2.1e-3 vs -3.0e-4 claimed). Refuted otherwise.
