# Independent check of the zeta reader of G3 (decision 0041 item 1)

Helper of E-stoch-inf, batch 21, 2026-11-25. I did not write `zeta/zeta_reader.py` and read it,
and the lead's journal entries on Z0-Z2, only after my own numbers were registered and journaled
(`JOURNAL.md` entry 3, commit 662f5740e). Processors only; no card time.

**Verdict: the reader may judge G3 runs as it is.** Its per-cell zeta agrees with an independent
reader on the box's states (Z0 to 5 digits, the quadratic coefficient to 5.6-6.7 digits, rms of
the first-order zeta to 9.6 digits), and the failure of Z1 along the momentum alone is a wrong
expected value: the reader's coefficient there is right to 3.4e-5, the test's reference integrator
is off by 12.4 per cent because it sits on its own round-off floor. Even if the reader were off by
the whole 14.2 per cent in that coefficient, F(3) and F(4) of a G3 box would move by less than
1e-6 of themselves. Two changes to the *tests* (not the reader) are recommended (README,
Requests 1-2). At G3 amplitudes (|zeta| up to 3 e-folds) the lead's map, run verbatim, agrees with
mine within 2.2e-9 in N (section 5).

Runs: E-20261125-170519-fa5ad33 (closed forms), E-20261125-172002-6890cad (the pairs),
E-20261125-173127-4dcc4ee (comparison with the lead), E-20261125-173501-2644c27 (the two maps at
G3 amplitudes). Data: the 32^3 mirrored pairs of
E-20261125-153148-cfad424 at s = +-1/4, +-1/2, dumps at N_f = N* + 10.

## 1. My reader and its closed-form tests

Own code (`scripts/zv_lib.py`): parser of the NRSFDMP2 dumps from the format in
`athenak/src/scalar_field/scalar_field_diag.cpp`; the deck's potential from
`scalar_field.hpp` lines 56-95 (only L = V'/V enters the map); homogeneous FKG in e-folds,
state (phi, y = dphi/dN), y' = -3y + 4 pi y^3 - (3/(8 pi)) L (1 - 4 pi y^2/3); classical RK4 with
a fixed step in N in long double (eps 1.1e-19); the end surface by a last RK4 step of
Newton-solved length; first and second variational equations for the exact derivatives of N at
the end surface; a cell's y = -3 Pi/K. zeta = -1/2 ln(chi/<chi>) + Delta N - <Delta N> with the
full nonlinear map per cell, phi_e from the lockstep state of the dump at N_f integrated to
N* + 15 (SCOPE 4d.1).

| Test (run E-20261125-170519-fa5ad33) | Result | Bar |
|---|---|---|
| exponential potential, y0/y_a - 1 in [-0.5, 0.5]: N against the closed form | 8.2e-16 | 1e-11 |
| same: N_y, N_yy against 40-digit references | 1.1e-14, 3.4e-12 relative | 1e-8 |
| same: N_phi = -1/y_a; N_phiphi, N_phiy (shift symmetry: 0) | 2.2e-16; below 8.2e-13 | |
| Hamilton-Jacobi attractor: N, first and second derivative along the attractor | 1.0e-14 (N = 27.6), 6e-19, 3e-17 | 1e-10, 1e-7 |

[VERIFIED] (`fig/fig_closed_form.png`: fourth order in the step).

## 2. The pairs: zeta against R^NR, the quadratic coefficient, the map

Set-up checks: alpha - 1 at most 3.0e-13, rms dK/K 1.8e-14, so y = Pi/H_b to 1e-14; the lockstep H
equals the Friedmann H of (phi_b, Pi_b) to 1e-16. Run E-20261125-172002-6890cad.

**Linear relation [VERIFIED].** zeta = -R^NR at first order: the slope of O_zeta on O_R is
-1.0000301 (s = 1/4) and -1.0000302 (s = 1/2); Z0 = rms(O_zeta + O_R)/rms(O_R) = 3.01e-5 and
3.03e-5 (bar 1e-3). The 3.0e-5 is of the size of the difference between R^NR's coefficient H/<Pi>
and the map's slope along the box relation (2.9e-5 with Pi_b, 3.7e-5 with the box mean of Pi).

**Quadratic coefficient [VERIFIED].** a_zeta = 6.762717e-3 (s = 1/4) and 6.762708e-3 (s = 1/2):
Z2(i) agrees to 1.4e-6 (bar 2 per cent). a_R = 1.8385e-4. With a_map along the box relation
6.962410e-3 at the box's (lockstep) state: Z2(iii) a_zeta/a_map - 1 = -2.87 per cent (fails the 2
per cent bar as written, as A14(b) foresaw); Z2(iii') = -0.228 per cent (bar 0.5 per cent). The
remainder of (iii') is the momentum's own second-order part: the regression of N_Pi E_Pi on
O_zeta^2 is -1.674e-5 (-0.240 per cent of a_map), and a_map + a(N_phi E_phi) + a(N_Pi E_Pi) =
0.0069624 - 0.0001830 - 0.0000167 reproduces a_zeta to 1e-7 (`fig/fig_z0_z2.png`).

**The map at N_f [VERIFIED]**, exact (variational; changing the step 1e-3 -> 5e-4 moves the
first derivatives by 2.4e-15 and the second by 6.3e-13), at the lockstep state phi_b =
-0.0558140583, Pi_b = 2.69501e-7, H = 0.951814:

| Direction | N' | N'' | a = N''/(2 N'^2) |
|---|---|---|---|
| field alone (per unit phi) | -3.515664e6 | 1.721056e11 | 6.96226e-3 |
| momentum alone (per unit Pi) | -1.225513e6 | 2.098822e10 | 6.98730e-3 |
| box relation dPi = r dphi, r = 0.0132235 (per unit phi) | -3.531870e6 | 1.736997e11 | 6.96241e-3 |
| cross term N_phiPi | | 6.013639e10 | |

N_Pi is within 0.9 per cent of the decaying-mode estimate -1/(3 Pi_b) = -1.236855e6. The end
surface does not matter: phi_e from my own 15-e-fold background from the deck's slice instead of
the lockstep state moves phi_e by 9.2e-9 (0.03 e-folds) but N_PiPi by 1.0e-5 and a_map by 1.7e-10
relative (on the attractor every cell reaches phi_e with the same velocity).

## 3. The momentum direction (task item 3)

**Not a property of the map [VERIFIED].** Along Pi at fixed phi, N minus its linear and quadratic
Taylor terms is cubic in dPi from 1 per cent to 100 per cent of Pi_b, both signs
(`fig/fig_momentum_map.png`, left); Pi_b + dPi stays positive (|dPi|/Pi_b about 2e-4 in the box).
The map is analytic along the momentum, the end surface is reached in the same way (on the
attractor) whatever the perturbation.

**Not a defect of the reader [VERIFIED].** At the lead's own Z1 state, eps and five-point stencils
(run E-20261125-173127-4dcc4ee), the exact second coefficient along Pi alone is 1.33413e-9 (in N
per eps^2): the lead's reader gives 1.33418e-9 (+3.4e-5), the lead's reference (scipy DOP853 in
cosmic time, event at phi_e, float64) 1.16849e-9 (-12.4 per cent). Hence Z1's 0.142 is the
reference's error: **a wrong expected value of the test.**

**Why the reference fails there [VERIFIED].** The second-order change of N along Pi alone is
N_PiPi eps^2/2 = 4.2e-11 at the s = 1/4 spread (6.7e-10 at the lead's eps, four times larger). An
integration of the absolute field in N accumulates rounding of phi (ulp 7e-18 in float64) at every
step, and N responds to phi with |N_phi| = 3.5e6: measured floor of N (rms about a cubic, 41
states) 4.4e-10 to 5.1e-10 in float64 and 2.3e-13 to 3.3e-13 in long double, for both directions
and two steps (`fig/fig_momentum_map.png`, right). Along the field and the box relation the second
change is 2.0e-6, far above either floor; along the momentum it is at or below the float64 floor,
so a float64 integrator in N or t cannot give that coefficient at this eps
(`fig/fig_fd_scan.png`: my own float64 differences are off by a factor 10 at one spread, long
double by 1.2 per cent, and converge to the variational value at larger eps). [JUDGEMENT, from
reading its code, not tested:] the lead's reader escapes the floor because it integrates in phi,
with the same phi-grid for all five stencil states along Pi, so no rounding of phi enters N there.

**How far the box lies from its relation [VERIFIED].** The odd parts satisfy dPi = r dphi with
r = 0.0132235 (both amplitudes), correlation 1 - 6e-12; the residual (O_Pi - r O_phi) has rms
3.5e-6 of rms(O_Pi) (`fig/fig_relation.png`). The full members lie off the linear relation by
8.2e-5 (s = 1/4) and 1.6e-4 (s = 1/2) of rms(dPi), growing with s: the second-order part of Pi
(the curvature of the trajectory), not scatter. The component across the relation contributes
1.6e-8 of rms(zeta) at first order.

**One-point error of a reader with that discrepancy [VERIFIED for the 32^3 pairs; JUDGEMENT for
the scaling to G3].** Changing N_PiPi by 14.2 per cent in the map changes zeta by at most 6.0e-9
sigma in any cell (s = 1/4; 1.2e-8 at s = 1/2); no cell crosses nu = 3 or 4. The change grows like
sigma (it is quadratic in dPi), so in the G3 box (sigma_lin = 0.494, SCOPE 4d.2) the bound on
the relative change of F(3) and F(4) is 5.8e-7 and 7.5e-7 (4.1e-6 and 5.3e-6 for a coefficient
off by 100 per cent), against the 1.2 per cent statistical error planned at nu = 4. The bound
assumes the 128^3 band keeps the relation's slope (the high-k modes may be less frozen;
[TO VERIFY] on the first G3 dumps, but a tenfold larger slope would still leave the bound below
1e-4).

## 4. Comparison with the lead's reader (task item 4)

| Quantity | Lead (E-20261125-161456-8d3f43c) | Mine | Digits |
|---|---|---|---|
| Z0, s = 1/4 | 3.0100897e-5 | 3.0101140e-5 | 5.1 |
| Z0, s = 1/2 | 3.0260024e-5 | 3.0260286e-5 | 5.1 |
| rms O_zeta, s = 1/4 | 0.0168400271 | 0.0168400272 | 9.6 |
| a_zeta, s = 1/4 | 6.762735e-3 | 6.762717e-3 | 5.6 |
| a_zeta, s = 1/2 | 6.762709e-3 | 6.762708e-3 | 6.7 |
| a_R, s = 1/4 / 1/2 | 1.838499e-4 / 1.838579e-4 | 1.838495e-4 / 1.838580e-4 | 5.7 / 6.8 |
| box relation r | 0.01322353414 | 0.01322353414 | all |
| phi_e (both from the deck's slice) | -0.05581258252693 | -0.05581258252693 | 13.1 |
| a_map along the relation, each at its own state | 6.963785e-3 (lead's N_f state) | 6.962410e-3 (lockstep) | 3.7 |
| a_map along the relation, both at the lead's state | 6.963785e-3 (DOP853, 5-point) | 6.963873e-3 (exact) | 4.9 |
| Z2(iii) | -2.887 per cent | -2.868 per cent | 2.2 |
| Z2(iii') | -0.247 per cent | -0.228 per cent | 1.1 |
| Z1 c2 along Pi, reader / reference vs exact | +3.4e-5 / -0.124 | exact 1.33413e-9 | reader 4.5 |
| Z1 c2 along phi, along the relation (reader) | -6.1e-5, -6.0e-5 | exact | 4.2 |
| Z1 c1, all directions (reader) | within 3.5e-10 | exact | 9.5 |

The (iii) and (iii') differences come from where a_map is expanded: the lead takes the test's
expansion state from its own DOP853 background, 8.56e-9 in phi and 4.2e-4 in Pi (0.03 e-folds)
from the box's lockstep state; with a_map at the lead's state my (iii') is -0.249 per cent. Both
readers pass (iii') and fail (iii) as written. (`fig/fig_compare_lead.png`.)

## 5. Not done, limits

- G3 amplitudes [VERIFIED for the map, not for a G3 lattice]: the lead's V, dV and map_rk4, taken
  verbatim from its source, against my map (run E-20261125-173501-2644c27, `fig/fig_large_amp.png`):
  along the box relation with |zeta_1| <= 3 e-folds the difference is at most 2.2e-9 in N after
  the common offset (my own step change 6.8e-13); on the background trajectory moved by |tau| <= 3
  the lead's map gives N_b - tau within 1.8e-9, mine within 8.0e-13. 2e-9 is 4e-9 of sigma_lin of
  the G3 box. [JUDGEMENT, not tested:] the lead's floor is float64 cancellation in dV near the
  inflection point. No G3 lattice exists yet, so the per-cell agreement there is not shown.
- Z1's clause "on homogeneous runs (noise off)" for a shifted initial slice: not done (no
  noise-off run was made).
- Third-order terms of the map: per cell rms 8.9e-10 (s = 1/4), 7.1e-9 (s = 1/2), cubic in s; not
  examined further.
- I did not judge the lead's A4 preview or the LM landmarks.

Figures (each looked at): `fig/fig_closed_form.png`, `fig/fig_z0_z2.png`, `fig/fig_fd_scan.png`,
`fig/fig_momentum_map.png`, `fig/fig_relation.png`, `fig/fig_compare_lead.png`, `fig/fig_large_amp.png`.
