# gravothermal: the spherically symmetric baseline of Track C (work package C-pre-3)

Helper package of owner C-sidm. It reproduces the equilibrium sequence and the instability
criteria of relativistic gravothermal evolution used by

- **F21** = arXiv:2108.11967 v2 (Feng, Yu, Zhong), source
  `kb-data/raw/arxiv/2108.11967/v2/src/main.tex` (cited below as `main.tex:<line>`), and
- **G26** = arXiv:2601.17117 v2 (Gu, Jiang, Chen, Li), source
  `kb-data/raw/arxiv/2601.17117/v2/src/SIDM_MS.tex` (`SIDM_MS.tex:<line>`),

compares with the numbers both papers print, and states where the dynamical instability
begins, which fixes the initial models of the full-relativity runs. Everything here is a
semi-analytic reference solution (ordinary differential equations, quadratures, a
one-dimensional eigenvalue problem) and analysis; no simulation code (decision 0010).
Predictions and outcomes: `JOURNAL.md` (P1 to P6).

## Contents

| File | What it is |
|---|---|
| `tmb.py` | Solver: F21's truncated Maxwell-Boltzmann equation of state, TOV sequence (b, w0), all table columns, maxima of E, B, eps, root <gamma> = gamma_cr, Killing-energy moments, finite-element radial pulsation (`fem_lowest`, `pulsation`) |
| `test_tmb.py` | Unit tests (quadrature, limits, Killing-energy form, tolerance, closed form of gamma_cr against the pulsation operator, FEM convergence, gamma = 4/3 Newtonian limit) |
| `paper_tables.py` | Standard-library parser of F21's Tables 1 and 2 (run with `python3 -I`; the source is untrusted data) |
| `run_sequence.py` | Row-by-row comparison with F21, criteria per b, dense sequences, EOS curves, profiles |
| `pulsation_check.py` | Independent check of the FEM: turning-point theorem on Gamma = 2 polytropes |
| `timescales.py` | G26 phases and time scales; F21 threshold models scaled to physical masses; Knudsen numbers |
| `initial_models.py` | Candidate initial models across the onset bracket, in code units |
| `make_figures.py` | All figures (style `python/nrpic/figstyle.py`) |
| `register.py` | Runs a command as a registered run: manifest in `tracks/C-sidm/runs/<run_id>/` |
| `results/` | Copies of the run outputs quoted below (summaries, criteria, time scales, initial models) |
| `figs/` | PNG copies of the figures of run C-sidm-20261115-121859-690ff91 |

## How to rerun

From this directory (`numpy`, `scipy`, `matplotlib` of the user site; the parser needs only
the standard library):

    TEX=/data/haiyangw/nrpic/kb-data/raw/arxiv/2108.11967/v2/src/main.tex
    python3 -E register.py --purpose "tests" -- python3 -E test_tmb.py
    python3 -E register.py --purpose "parse" -- python3 -I paper_tables.py $TEX "{OUT}/f21_tables.json"
    python3 -E register.py --purpose "sequences" -- python3 -E run_sequence.py <parse run dir>/f21_tables.json "{OUT}"
    python3 -E register.py --purpose "polytrope" -- python3 -E pulsation_check.py "{OUT}"
    python3 -E register.py --purpose "time scales" -- python3 -E timescales.py <sequence run dir>/criteria.json "{OUT}"
    python3 -E register.py --purpose "initial models" -- python3 -E initial_models.py <sequence run dir>/criteria.json "{OUT}"
    python3 -E register.py --purpose "figures" -- python3 -E make_figures.py <seq dir> <parse dir>/f21_tables.json "{OUT}" <timescales dir> <polytrope dir>

`register.py` refuses to run while this directory has uncommitted changes, writes
`scratch/C-sidm/<run_id>/` and the manifest. The sequence run takes 4 min on one core,
everything else under 30 s.

Runs of this package (all scouting, processors only, one core, 0 GPU-hours):

| Run id | What |
|---|---|
| C-sidm-20261115-120715-38ab057 | unit tests, all pass |
| C-sidm-20261115-120717-38ab057 | parse of F21 Tables 1 (56 rows) and 2 (14 rows) |
| C-sidm-20261115-120722-38ab057 | sequences, comparison, criteria, EOS, profiles (230 s) |
| C-sidm-20261115-121400-d463e1a | polytrope check, first attempt (node-list defect, see JOURNAL) |
| C-sidm-20261115-121524-5cebcf5 | polytrope check, fixed |
| C-sidm-20261115-121412-d463e1a | time scales and Knudsen numbers |
| C-sidm-20261115-121536-5cebcf5 | initial models (superseded: no core radii) |
| C-sidm-20261115-121748-4e8d6b5 | initial models with core and half-mass radii |
| C-sidm-20261115-121811-38da24f | figures (superseded: y ranges) |
| C-sidm-20261115-121859-690ff91 | figures, final |

## 1. The model and the equations F21 uses [VERIFIED: read in the source]

The collapsed core is a truncated Maxwell-Boltzmann (Michie-King) gas,
f = e^{mu/kT}(e^{-eps/kT} - e^{-eps_c/kT}) for eps <= eps_c (`main.tex:111-116`), with the
Tolman-Klein relations w(r) = alpha(r) - alpha(R), T(r) = T(R)/(1 - b w) (`main.tex:118`),
b = kT(R)/mc^2, w = eps_c/kT. Moments `main.tex:122-139`; TOV `main.tex:143-145`; length
unit zeta `main.tex:147-153`; v = sqrt(3p/rho), gamma = 1 + p/u (`main.tex:172-175`);
energies `main.tex:242-250`; redshift `main.tex:255-257`; Chandrasekhar's pulsation
equation `main.tex:201-206`, the trial-function criterion <gamma> < gamma_cr
`main.tex:208-219` (derivation `main.tex:403-463`); turning points dS/dw(0)|_b = 0,
S = E, B, eps (`main.tex:231-254`).

Derived here (checked by the tests and by the agreement with the tables):

- Hatted units (G = c = 1, lengths in zeta): with h^3 = 8 pi^3 hbar^3 and `main.tex:149`,
  rho^ = 4 sqrt2 pi I_rho, n^ = 4 sqrt2 pi I_n, u^ = 4 sqrt2 pi I_u, p^ = (8/3) sqrt2 pi I_p,
  and dw/dr^ = -((1 - b w)/b)(4 pi p^ r^3 + M^)/(r^ (r^ - 2 M^)).
- Lapse: e^{Phi(r)} = (1 - b w(r)) (1 - 2M/R)^{1/2}, from Tolman's law; consistent with
  the TOV equation since d ln(1 - b w)/dr = Phi'. F21's printed e^{2 Phi} (`main.tex:197`)
  is not correct as printed (the exponent needs a minus sign, a factor 2, and 4 pi G in
  front of p r'^3); F21's own numbers, e.g. Z(0), follow the correct form.
- **The F21 core is an exact Einstein-Vlasov steady state** [VERIFIED by derivation and test
  P3]: with T e^Phi = const and (mu + mc^2) e^Phi = const, f = A (e^{-E/kT_inf} -
  e^{-E_c/kT_inf}) for E < E_c, with E the conserved (Killing) energy and E_c = mc^2 e^{Phi(R)}.
  This is the relativistic King (isothermal) cluster; moments by direct momentum integration
  equal F21's integrals to 1.2e-14. So the same family serves both the collisional (fluid)
  reading of F21 and the collisionless threshold runs of the minimum publishable unit, and
  its particle samples need only f(E).

## 2. Reproduction of F21 (runs C-sidm-20261115-120717/120722-38ab057)

Figures: `figs/fig_sequence_b0.1.png` (and b = 0.2, 0.3, 0.5): curves of this solver through
every Table 1 point; `figs/fig_table_residuals.png`; `figs/fig_eos.png` (F21 Fig. 2);
`figs/fig_profiles_b0.1.png` (F21 Fig. 4); `figs/fig_criteria_vs_b.png`.

Table 1 (56 rows, `main.tex:490-583`), relative difference this solver / paper
(`results/sequence_summary.md`): M^ and E^_rest median 1.5e-6, max 1.1e-4; B^ max 2.4e-4;
eps max 1.3e-4; Z(0) max 2.1e-5; rho^(0), p^(0), v(0)/c max 3.7e-6; <gamma> max 5e-6 and
gamma_cr max 1.6e-5 absolute. The largest deviations sit at the most concentrated models
(b = 0.1, w0 >= 4), as expected from F21's fixed-step RK4. R^: F21 prints the radius
truncated to a grid of step 1e-3 (max difference 9.9e-4), and C = M^/R^(printed).
Three printed typos, each contradicted by the paper's own other columns: `main.tex:516`
(C = 4.0e-4 for M^/R^ = 4.0e-3), `main.tex:491` (C = 1.41053e-2 for M^/R^ = 1.141e-2),
`main.tex:493` (p^(0) = 1.09378e-3, should be about 1.09e-2). The eps_c(0)/mc^2 column
deviates from b w0/(1 - b w0) by up to 1.3e-4 (cause not established, [TO VERIFY]).
Table 2 (14 roots of <gamma> = gamma_cr, b = 0.09 ... 5.0, `main.tex:605-618`): w0 within
1.1e-4 relative, Z(0) within 2.1e-4, <gamma> within 3e-6.

Criteria along the sequences (this solver, exact extrema and roots; `results/criteria.json`):

| b | criterion | w0 | Z(0) | v(0)/c | C = GM/Rc^2 | R/M | eps |
|---|---|---|---|---|---|---|---|
| 0.1 | max eps (F21 turning point) | 3.16524 | 0.5404 | 0.5035 | 0.04892 | 20.44 | 0.035179 |
| 0.1 | omega_0^2 = 0, gamma = 1 + p/u (exact, this package) | 3.58710 | 0.6348 | 0.5342 | 0.04509 | 22.18 | 0.034674 |
| 0.1 | <gamma> = gamma_cr (F21 trial) | 4.05115 | 0.7500 | 0.5662 | 0.03866 | 25.87 | 0.033024 |
| 0.2 | max eps | 1.47995 | 0.5225 | 0.5161 | 0.06478 | 15.44 | 0.035489 |
| 0.2 | omega_0^2 = 0 | 1.63035 | 0.5923 | 0.5434 | 0.06578 | 15.20 | 0.035121 |
| 0.2 | <gamma> = gamma_cr | 1.73634 | 0.6442 | 0.5620 | 0.06589 | 15.18 | 0.034417 |
| 0.3 | max eps | 0.96836 | 0.5176 | 0.5188 | 0.06871 | 14.56 | 0.035539 |
| 0.3 | omega_0^2 = 0 | 1.06297 | 0.5843 | 0.5459 | 0.07057 | 14.17 | 0.035182 |
| 0.3 | <gamma> = gamma_cr | 1.12525 | 0.6304 | 0.5633 | 0.07134 | 14.02 | 0.034554 |
| 0.5 | max eps | 0.57324 | 0.5142 | 0.5207 | 0.07148 | 13.99 | 0.035569 |
| 0.5 | omega_0^2 = 0 | 0.62795 | 0.5790 | 0.5477 | 0.07390 | 13.53 | 0.035220 |
| 0.5 | <gamma> = gamma_cr | 0.66244 | 0.6219 | 0.5643 | 0.07504 | 13.33 | 0.034634 |

Maxima of E^ and B^ (b = 0.1): E^ = 3.47261e-2 at v(0) = 0.2279, Z(0) = 0.089; B^ =
8.48864e-4 at v(0) = 0.3970, Z(0) = 0.300 (F21 grid values 3.47e-2 at 0.225 and 8.49e-4 at
0.395, `main.tex:286`). F21's statements `main.tex:274` and `:280` (eps_max = 0.0352-0.0356 at
Z(0) = 0.548-0.522; <gamma> = gamma_cr = 1.62 at v(0) = 0.566-0.564c, Z(0) = 0.750-0.622)
are reproduced; my exact maxima lie between F21's grid rows (Z(0) = 0.540-0.514).

## 3. Where the dynamical instability begins (beyond F21)

F21's adiabatic-index criterion uses one trial function, xi = r e^Phi (`main.tex:208`), which
gives only an upper bound on the lowest omega^2. Here the radial pulsation equation
(`main.tex:201-206`, Sturm-Liouville form in `tmb.fem_lowest`) is solved exactly by finite
elements (Rayleigh-Ritz on zeta = r^3 eta, eta piecewise linear; eta = 1 is F21's trial).
Checks: the Rayleigh quotient of eta = 1 equals 9 P0 (<gamma> - gamma_cr) to 2e-5, i.e.
F21's closed form `main.tex:216-218` against the un-integrated operator; convergence 2e-5
between N = 800 and 1600; on Gamma = 2, K = 100 polytropes the zero of omega_0^2 coincides
with the maximum of M(rho_c) (M_max = 1.637276 at rho_c = 3.182422e-3) to 3e-8 (run
C-sidm-20261115-121524-5cebcf5, `figs/fig_polytrope_check.png`).

Results (`figs/fig_onset.png`, `figs/fig_criteria_vs_b.png`):

- With F21's gamma = 1 + p/u the exact onset is at **Z(0) = 0.579-0.635** (b = 0.5 ... 0.1),
  between F21's eps maximum (0.514-0.540) and F21's trial root (0.622-0.750). At the trial
  root the exact omega_0^2 is already strongly negative (b = 0.1, w0 = 4.0515: -3.59 against
  -6.7e-4 for the trial, hatted units). The trial function is a poor eigenfunction for these
  centrally concentrated core-halo models; for b = 0.1 it even predicts a return to
  stability at Z(0) > 1.3 that the exact mode does not show. [VERIFIED by runs above]
- With a fixed gamma = 5/3 (G26's EOS, `SIDM_MS.tex:341`) on the same structures the exact
  onset moves to Z(0) = 0.679-0.779; the trial criterion gamma_cr = 5/3 is reached only for
  b >= 0.2 (Z(0) = 0.737-0.777), and never for b = 0.1, where gamma_cr peaks at 1.646.
  [VERIFIED by runs; the physical relevance of this case is a JUDGEMENT, see section 4]
- All criteria cluster at a central redshift Z(0) ~ 0.5-0.75 and central v/c ~ 0.50-0.57
  over a factor of 5 in b, at compactness GM/Rc^2 = 0.04-0.075 (R/M = 13-26).

Which of these is "the" threshold depends on the collision regime [JUDGEMENT]: for a fluid
(short mean free path) it is the exact fluid onset with the correct Gamma_1 of the gas; for
a collisionless cluster (Kn -> infinity) it is the Einstein-Vlasov stability of the same
f(E), which F21 quotes from Shapiro & Teukolsky's N-body runs as eps ~ 0.035 at Z(0) ~ 0.5
(`main.tex:283`; not checked here, it is the subject of the equilibria package of C-pre-4).
Note that gamma = 1 + p/u is F21's definition; the adiabatic index of a Juttner gas,
Gamma_1 = 1 + k/c_v(T), is lower at intermediate temperatures, which would move the fluid
onset to smaller Z(0) [BACKGROUND for the formula, consequence TO VERIFY].

## 4. G26: what it uses, and what a dynamical-time code cannot follow

What G26 computes [VERIFIED: read in the source]: a Misner-Sharp fluid with Eckart heat flux
(Eqs. ms3-ms10, `SIDM_MS.tex:309-348`), ideal-gas EOS with fixed gamma = 5/3
(`SIDM_MS.tex:338-344`), the Balberg-Shapiro-Inagaki conductivity with LMFP/SMFP
interpolation (`SIDM_MS.tex:233`), NFW initial halo (`SIDM_MS.tex:378-386`). It prints no
equilibrium sequence and no criterion of its own: the onset of the dynamical instability is
taken from F21 qualitatively ("velocity dispersion comparable to the speed of light",
`SIDM_MS.tex:175`, `:476`), and the late phase is computed quasi-statically with GR terms
kept (`SIDM_MS.tex:457`). What can be compared is therefore F21's criterion, done above, and
G26's time scales, below. Its fixed gamma = 5/3 EOS never softens toward 4/3, so within G26's
own model the trial criterion for b = 0.1 structures never fires and the exact onset sits
at Z(0) = 0.68-0.78 instead of 0.58-0.64 (section 3) [JUDGEMENT on the consequence].

The phases of G26's fiducial halo (R_s = 2.6 kpc, rho_s = 0.019 Msun/pc^3, sigma/m =
5 cm^2/g, t0 = 0.26 Gyr, `SIDM_MS.tex:384`):

1. core expansion to 51.3 t0, isothermal core at 63.2 t0 (`SIDM_MS.tex:423`);
2. LMFP self-similar gravothermal collapse to 445 t0 (`SIDM_MS.tex:425`);
3. SMFP transition 445.0-445.8 t0, mass outflow, a core with rho > 1e10 rho_s inside
   1e-3 R_s (`SIDM_MS.tex:440`);
4. quasi-static contraction of the SMFP core, t_c from 0.1 t0 to 40 t0
   (`SIDM_MS.tex:474`), m/R from about 1e-6 (`SIDM_MS.tex:455`) to the horizon;
5. dynamical instability and horizon at 580 t0 with m about 3e-8 M, about 200 Msun
   (`SIDM_MS.tex:465`, `:476`).

Time scales (run C-sidm-20261115-121412-d463e1a, `results/timescales.md`,
`figs/fig_timescales.png`):

- Even G26's core at 445.8 t0 (rho >= 1.29e-14 g/cm^3) has a dynamical time
  1/(4 pi G rho)^{1/2} <= 305 yr, so t0 >= 8.5e5 t_dyn, the fastest gravothermal time
  0.1 t0 >= 8.5e4 t_dyn and the remaining 134 t0 to the horizon >= 1.1e8 t_dyn of that core.
- At the onset (F21 models above scaled to the 200 Msun seed of G26), R = 4000-7600 km,
  central t_dyn = 2.2-3.9 ms, light-crossing time R/c = 13-25 ms, and t0/t_dyn,c ~ 2-4e18.
- Check of F21's own estimate (`main.tex:349`, `:355`): for the J1205 benchmark this script
  gives R = 2.33e-3 pc, <rho_seed> = 3.58e25 Msun/kpc^3, t_seed = 68 days (paper 2.3e-3 pc,
  3.5e25, about 69 days).

Conclusion [JUDGEMENT, built on the verified numbers]: no part of phases 1-4 can be followed
by a dynamical-time code: each lasts at least 1e5 dynamical times of the then-current core,
and a single t0 is 2-4e18 central dynamical times of a threshold core of 200 Msun. A dynamical-time
code (NRPIC with or without collisions, time step a fraction of the light-crossing time of
the core) can follow only phase 5, from the onset of the dynamical instability on, whose
time scale is t_dyn,c (F21's t_seed, `main.tex:355`). The full-relativity runs therefore
start from equilibria of the F21 family taken on the threshold: models bracketing
Z(0) = 0.5-0.75 for b = 0.1-0.5 (stable side: eps maximum and below; unstable side: past the
exact fluid onset), which is what `initial_models.py` lists (section 5).

Collision regime at the onset (same run): with G26's sigma/m = 5 cm^2/g and M = 200 Msun the
central Knudsen number is lambda/R ~ 1e-21 (lambda/H ~ 1e-19), and t_coll/t_dyn,c ~ 4e-20;
for M = 1.9e9 Msun, lambda/R ~ 1e-14. The physical core at the onset is therefore deep in the
short-mean-free-path (perfect-fluid, adiabatic on t_dyn) limit; conduction time ~ t_dyn/Kn is
astronomically long. A particle code can reach only Kn >~ 1e-2 [JUDGEMENT]; the minimum
publishable unit's scan in Kn is a bridge between the collisionless limit (Kn = infinity,
Einstein-Vlasov) and the fluid limit (Kn -> 0), and its fluid end must be anchored by the
exact fluid onset computed here, not by the physical Kn.

## 5. Candidate initial models (run C-sidm-20261115-121748-4e8d6b5)

`results/initial_models.md` lists, for b = 0.1, 0.2, 0.3, 0.5 and Z(0) = 0.30 ... 0.80, the
models in code units (G = c = 1, ADM mass M = 1): w0, R/M, r_core/M (areal radius where
rho = rho_c/2), r_half/M, compactness, central lapse alpha_c = 1/(1 + Z(0)), kT_inf/m and
E_c/m of f(E), M0/M = E_rest/E, eps, v(0)/c, and on which side of each criterion the model
lies. Examples:

| b | Z(0) | w0 | R/M | r_core/M | r_half/M | alpha_c | kT_inf/m | E_c/m | side |
|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 0.50 | 2.973024 | 20.016 | 2.075 | 4.044 | 0.66667 | 0.09487 | 0.94872 | stable by every criterion |
| 0.1 | 0.60 | 3.435919 | 21.412 | 1.737 | 3.638 | 0.62500 | 0.09522 | 0.95215 | past eps max, fluid-stable |
| 0.1 | 0.70 | 3.856452 | 24.032 | 1.478 | 3.359 | 0.58824 | 0.09575 | 0.95748 | fluid-unstable, trial-stable |
| 0.5 | 0.50 | 0.560853 | 14.120 | 2.495 | 3.990 | 0.66667 | 0.46324 | 0.92647 | stable by every criterion |
| 0.5 | 0.60 | 0.644973 | 13.422 | 2.181 | 3.575 | 0.62500 | 0.46125 | 0.92249 | fluid-unstable, trial-stable |

The radii are areal (Schwarzschild-like) coordinates; the conformally flat isotropic form of
`nrpic_cf` needs the transformation of `python/nrpic/st_cluster.py` (isotropic_from_areal)
or core's initial-data solver. Cross-section conversion: for a dimensionless model,
Kn_R = lambda_c/R = 1/(s n^(0) M^ R^) with s = (sigma/m) c^4/(G^2 M) the cross-section per
unit mass in units of M^-1; for M = 200 Msun and 5 cm^2/g, s = 2.3e21 (`results/timescales.md`).

## What is not done

- The collisionless (Einstein-Vlasov) stability of the F21 family is not computed here; it
  belongs to the equilibria package (C-pre-4) and to the NRPIC runs.
- Gamma_1 of the Juttner gas instead of F21's gamma = 1 + p/u: not computed (section 3).
- G26's evolution itself is not reproduced (it is a hydrodynamics code; decision 0010 keeps
  such capabilities out of the track directories). Its printed time scales and masses are
  used as given, with locators; its claim that the onset happens when "the velocity
  dispersion becomes comparable to c" is consistent with the v(0)/c = 0.50-0.57 found here.
- The cause of the 1.3e-4 offset of F21's eps_c(0) column is not established.
- Shapiro & Teukolsky (1985), quoted by F21 for the N-body threshold, is not on arXiv and was
  not read.

## Requests

- **To the C-sidm lead**: use section 3 and the models of `results/initial_models.md` to fix
  the initial models of the threshold runs; the F21 family is an exact Einstein-Vlasov steady
  state with f(E), so the equilibria helper (C-pre-4) can sample it directly. Decide which
  onset the collisional runs are compared with (exact fluid onset with gamma = 1 + p/u, or
  with Gamma_1 of a Juttner gas).
- **To core**: none for this package (no AthenaK capability is needed for the baseline). For
  the threshold runs the relevant quantities are R/M = 13-28 and r_core/M = 1.3-3.7 at
  Z(0) = 0.3-0.8 (resolution of the core), and a horizon forms from a centre with
  alpha_c = 0.55-0.77.
- **To kb**: index F21 (2108.11967) Tables 1-2 with the three typos and the e^{2Phi} typo
  noted in section 1-2, and G26 (2601.17117) time scales with the locators above.
