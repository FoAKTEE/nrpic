# Lead review of the wave-1 helper packages of B-emd-gw

Lead of owner B-emd-gw, 2026-11-15. Checked from the artefacts, not from the helpers'
conclusions: every package rerun from a clean `git archive` export, results compared
leaf by leaf, AthenaK cases re-executed, key derivations redone with code the helpers did
not write, figures opened with Read, locators spot-checked at the source. This is the
owner's check; the independent verifier of the gate (a fresh agent, charter 9.2 and
CLAUDE.md "Models and roles") is still owed (OPEN.md).

Runs of this review:
- L1 `B-emd-gw-20261115-131016-03b1119`: `analysis/lead_recheck.sh` on commit 03b1119,
  174 s on processors; comparison `scratch/B-emd-gw/B-emd-gw-20261115-131016-03b1119/compare.json`.
- L2 `B-emd-gw-20261115-131027-03b1119`: `analysis/lead_checks.py`, independent
  derivations a-f; `lead_checks.{json,png}` in its scratch directory.
- A first launch of L1, `B-emd-gw-20261115-130926-a1c2237`, was stopped after 19 s
  (misregistered by a path error of the lead's helper; on record, not cited).
Predictions and outcomes: `tracks/B-emd-gw/JOURNAL.md`, entry 2026-11-15T13:05Z.

Summary of L1: all 16 steps return 0; every numerical result of the five packages is
reproduced bit for bit (gw_diag 14 of 14 tests with real files, `test_zeldovich.py` 13 of
13); the only differences are figure paths and wall times. AthenaK re-executions
(lw_x_prod N16, N32; lw3d_check_diag; gauge_nl_conformal N64) are byte-identical in
every output except 36 bytes of uninitialised padding in the restart files.

## scope (`tracks/B-emd-gw/scope/`)

Confirmed:
- `check_item3.json`, `crossed_waves_tt.json`, `regime_estimates.json` reproduced bit for
  bit (L1).
- Item 3 amendments (a)-(b) and check 1E, by an independent derivation (L2 b, c): with a
  transverse metric Y(t) the Einstein equations admit X = Y(1 + D f) only with D = const
  (relabelling of x) or D ~ 1/t; the plane-symmetric traceless divergence-free tensor is
  A^i_j = c Y^-3 diag(1, -1/2, -1/2) and its overlap with K is -c d/dt of the integral of
  X/Y. Amendment (a) by hand: a 90-degree rotation about x maps h_+ to -h_+ and h_x to
  -h_x, so E(2) (or the lattice's 90-degree rotation) removes both.
- Crossed-wave coefficient (L2 d): real-space projection of the source of arXiv:1604.06065
  (`compendium_arxiv.tex` lines 294-298, metric line 142, read by the lead) gives
  h_+ = -(5/6) phi_x phi_y cos(K.x) at K = (k, k, 0), i.e. Fourier coefficient
  (5/12)|phi_x phi_y| = 1.3858e-5 at delta = 0.01, L = 4: scope's number.
- Throughput numbers in the two cosmology logs (5.770e6 zone-cycles/s, 1404 cycles,
  63.78 s at 64^3; 4.467e6, 1301.8 s at 128^3) read by the lead.
- Locators read by the lead: 2403.15126 `pII_GW_Vir_C2_Arx.tex:1074` (Omega_GW ~ sigma^(7/2));
  2605.04487 `main_v3.tex:2395-2405` (0.4-0.5 c at sigma = 0.1); 2111.09163
  `prd_v1.tex:258-262` (rho_K); 1604.06065 `compendium_arxiv.tex:142, 294-298`.
- Junk-TT decay as 1/a: consistent with the matter-era homogeneous solution
  3 j_1(k tau)/(k tau), envelope ~ tau^-2 ~ 1/a [lead's hand argument].

Not confirmed: the noise criterion (eps >= 0.03 at a = 40, >= 0.3 at a = 100) is a
JUDGEMENT bound; the virial-frequency estimate of check 3B was rerun, not rederived;
thin periodic boxes with particles are untested; the five unread references.

Wrong or defective: the "(5/12) phi_x phi_y" was stated without its Fourier
normalization (a reader would take it as the real amplitude, off by 2): FIXED by a lead
note in `SCOPE.md` section 3. Nothing else found wrong.

## periodic_z4c (`tracks/B-emd-gw/periodic_z4c/`)

Confirmed:
- All six JSON and four Markdown tables regenerate bit for bit from the run outputs (L1);
  four AthenaK runs re-executed byte for byte (L1), so the tables rest on reproducible runs.
- The polarization-tensor bug of `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines
  107-112 (read by the lead): |e.k| = 0.77 for k = (1,1,1) and O(1) for 400 random
  directions; flipping a_xy and a_yz gives < 1e-15 with trace 0 and e:e = 2 (L2 a,
  `lead_checks.png` panel a).
- Second-order closed-box backreaction (L2 f): <K_ij K^ij> = pi^2 A^2, so
  alpha - 1 = -1.64e-10 (conformal time) and -9.87e-10 (1+log) at t = 10, A = 1e-6,
  as measured.
- Figures opened: lw_x_convergence, lw3d_check, awa_history, gauge_nl_gradient.

Not confirmed: the Fourier-symbol prediction `analysis/predict_lw.py` and the gauge-wave
coordinate transformation `analysis/refsol.py` item 2 were rerun, not rederived; the
rounding explanation of the A = 0.01, N = 200 floor and the gauge-shock reading are
JUDGEMENT; the Apples-with-Apples standard asks for 1000 crossings (200 run).

Wrong or defective: 34 manifests of this and the gw_diag package were labelled
"production" with no pre-registration and no G0 pass: FIXED (relabelled scouting with a
`kind_correction` field; `make_cases.py` writes scouting). Runs were registered from a
dirty worktree (`worktree_dirty: true`); inputs carry checksums and L1 reproduces them,
so accepted. Overlapping x tick labels in `figs/lw_x_convergence.png` (cosmetic, not fixed).

## gw_diag (`tracks/B-emd-gw/gw_diag/`)

Confirmed:
- 14 of 14 tests pass in the clean export with real files (L1); `results_tt.json`,
  `results_weyl.json`, `results_athenak.json` reproduced bit for bit.
- Energy normalization by hand: with K_ij = -(1/2) d_tau h_ij,
  rho_K = (M_pl^2/2) K^TT K^TT = <d_tau h d_tau h>/(64 pi G), half of Isaacson, as the
  README states and as `prd_v1.tex:260` and its footnote define.
- Psi_4 amplitude on the AthenaK dump: (2 pi)^2 A = 39.5 A (`figs/athenak_psi4.png`).
- Figures opened: athenak_tt, athenak_psi4, cosmo_tt, weyl_convergence, tt_gauge_scalar.

Not confirmed: the cause of the weyl-output lag (source reading of `z4c_tasks.cpp` and
`driver.cpp` line 600) was not re-read by the lead; the lag itself is reproduced only by
the helper's script. The frozen TT part of the cosmology dumps as the induced tensor
mode is JUDGEMENT.

Wrong or defective: (1) the scripts imported `python/nrpic` through this worktree's
absolute path: FIXED (relative). (2) New caveat, not in the package: in
`figs/cosmo_tt.png` the rise of rms h^TT after a ~ 600 coincides with (rms non-TT part)^2
reaching the TT level (4e-5 squared = 1.6e-9 at a = 1000), the size of the second-order
gauge piece of the flat projection in the code's zero-shift gauge; the late rise is not
yet a GW signal [JUDGEMENT, TO VERIFY].

## baseline (`tracks/B-emd-gw/baseline/`)

Confirmed:
- `baseline_results.json` reproduced (374 numbers identical; paths and wall times differ).
- Zel'dovich-ellipsoid formulas by hand and by quadrature (L2 e): Q''' coefficient 80/27,
  sum_i (3 lambda_i^2 - sum lambda^2)^2 = 6 S, P = (8/45) M S t^(-2/3) (G = c = t_k = 1,
  R_L = 3/2, M = 3/4), E = (8/15) M c^2 S [(t2)^(1/3) - (t1)^(1/3)], to 2e-16.
- Self-similarity exponent by dimensions: E ~ G M^2 R^4/(c^5 t_turn^5) with R ~ t_turn^(2/3)
  gives t_turn^(-7/3) ~ (2 alpha)^(7/2).
- Locator read by the lead: 2605.04487 `main_v3.tex:2276-2278` (22.536 and 29.097).
- Figures opened: t2_za_scaling, t4_t5_axes_quadrupole_power.

Not confirmed: that 2605.04487's code is model B (JUDGEMENT); the factor 144-392 of T7b
(cause unknown); the slip at 2403.15126 lines 959-961 (not re-read).

Wrong or defective: nothing found beyond the failed predictions the helper recorded.
Note for the plan: R1 (quadrupole history) is largely provided on `core/newton` (tip
ce329f5, interface note section 3: columns 19-43 of `<basename>.newton.hst`), not yet on
main; per-species selection and centroid-relative physical coordinates remain to ask.

## verify_cosmo (`tracks/B-emd-gw/verify_cosmo/`)

Confirmed:
- Zel'dovich reference by hand and symbolically (L2 f): s = a and a^(-3/2) solve
  d/dtau (a ds/dtau) = (3/2) s with a = (1 + tau/2)^2; s0 = v0 makes a pure growing mode
  and the first crossing a = 1 + 1/d.
- `flrw_recheck.json`, `pancake.json`, `pancake_profiles.json` reproduced bit for bit
  from the run outputs; `test_zeldovich.py` passes.
- No file under `cosmo/` names 2003.08014 (grep by the lead); `cosmo/PLAN.md` line 166
  says one particle per cell suffices with the cubic cloud before collapse.
- Card use 0.284 + 0.197 = 0.481 card-hours (manifests -115217-69ab1db, -115902-a3207d7).
- Independent support from another code path: the Newtonian mode on `core/newton` finds
  the same first-order lattice error with one particle per cell (interface note 5.6).
- Figures opened: pancake_errors, pancake_ppc, pancake_grdiff.

Not confirmed: the AthenaK pancake runs themselves were not re-executed (0.48 card-hours;
only their analysis); TESTLOG numbers marked "(log)" were not recomputed; the
2003.08014 coordinate change is JUDGEMENT; the early velocity oscillation (a < 5) is
unidentified.

Wrong or defective: the analysis manifest -123852-ea4475c gives wall_time_s 300 against
51 s between its start and finish stamps (minor; left as is, noted here).
