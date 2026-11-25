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
