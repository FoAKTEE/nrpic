# periodic_diag: journal (helper of A-emd-pbh, batch 6, 2026-11-21)

Predictions are written before each test; outcomes follow, also when a prediction failed.

## 2026-11-21 21:35Z, entry 0: what is known, candidates, predictions (written before any run)

Known (card job 4799, run A-20261121-131600-02b5d41, deck
`periodic_threshold/inputs/peak_leak.athinput`, release core-v0.5 card build):
- P0L: `peak.cstat.hst` (every 8 cycles) has H_max 0.0149 at t = 2.269 (cycle 240),
  0.840 at t = 2.397 (cycle 248), 179 at t = 2.506 (cycle 256); |K| range opens from
  [-0.62, -0.59] to [-0.97, +0.02] at cycle 256. `peak.z4c.user.hst`: H-norm2 7.3e-3 at
  t = 2.01, 3.7e4 at t = 2.51. Guard stop at t = 4.815 on level 4 at (0.459, 0.459, -0.518).
- S1L: H_max 0.016 at t = 2.363, 0.97 at t = 2.490, 79 at t = 2.599; guard stop at
  t = 15.08 on level 4 at (-0.38, -0.32, 0.26).
- `peak.nrpic.hst` (every cycle) of P0L: the step grows smoothly, dt = 0.01563 at cycle 240,
  0.01630 at cycle 251 (dt/dx = 0.80 to 0.83 on level 4, dx = 0.01953), and is cut from
  cycle 252 on, after the jump.
- The deck differs from the earlier periodic runs of this track that did not fail early
  (S1/S2, wave 2, `peak_smr4.athinput`, same mesh): cfl_number 1.0 with dt_lightspeed 0.25
  instead of cfl_number 0.25; Gamma-driver shift (shift_Gamma 0.75, eta 2, advection)
  instead of zero shift; 1+log lapse with lapse_leak 20 instead of the harmonic-type lapse
  with the K-driver. core's own decks with dt_lightspeed (problems/cosmo_amr/*.athinput)
  and with the Gamma-driver (problems/ball/ball_leak.athinput) all use cfl_number 0.25.

Candidates and my reading of the source before any run [JUDGEMENT]:
- C1 the step. `athenak/src/z4c/z4c_newdt.cpp`: dt = cfl_number x min(dx, dt_lightspeed x
  min dx/c) with c = alpha sqrt(chi gt^dd) + |beta^d|. The Gamma-driver (z4c_calcrhs.cpp:
  d_t beta^i = shift_Gamma Gam^i - eta beta^i, and d_t Gam^i contains
  gt^jk d_j d_k beta^i + (1/3) gt^ij d_j d_k beta^k with the CONFORMAL inverse metric) has
  the longitudinal coordinate speed sqrt(4/3 x 0.75 x gt^xx) = 1, independent of chi; the
  light speed is alpha sqrt(chi) = 0.3 to 0.37 at t = 2.4. So the light-speed limit lets
  the step grow to dt/dx = 0.8 on level 4 while the shift mode then has Courant number 0.8.
  With the sixth-order stencils of nghost = 4 (second-derivative symbol 6.044 at the grid
  scale), RK4 (imaginary-axis limit 2.83) and no dissipation, the 3D grid-scale (corner)
  shift mode is stable only for dt/dx < 2.83 / sqrt(0.75 x (3 + 1/3) x 6.044) = 0.728.
- C2 a refinement event: the mesh is static (no regrid); level boundaries at |x| = 0.625,
  1.25, 2.5, 5. C3 the lapse relaxation: stiff term of rate 20, 20 dt = 0.33 < 2.79 (RK4
  real-axis limit). C4 the first shell crossing: none before t = 5 in the exact reference
  (R1, A-20261121-130103-e007f42: turnaround at tau >= 41). C5 the deposit across levels,
  shape or filter. C6 the guard: it only checks and fires at 4.8, after the jump. C7 an
  output or diagnostic event: hst every 0.5, lines every 2.0, cstat every 8 cycles; none
  at t = 2.3-2.4.

### Test A: the card outputs read again (analysis run; no simulation)
Script `scripts/card_onset.py`: per-cycle dt/dx on level 4 from `peak.nrpic.hst`, the
cstat series, and the line outputs of t = 2.01 and 4.0 (beta^x, Gam^x, alpha, H along x).
Prediction: dt/dx on level 4 crosses 0.73 between t = 1.8 and 2.1, before the jump; the two
members' dt agree to 5 per cent up to t = 2.3 (same background); at t = 2.01 no visible
cell-to-cell sign alternation in beta^x; at t = 4.0 beta^x and Gam^x alternate in sign from
cell to cell inside level 4 (|x| < 0.625) with an amplitude far above that outside it.
Refuted if dt/dx never exceeded 0.73 before the jump, if the dt histories of the members
differ by more than 20 per cent while the jump is simultaneous, or if the t = 4 disturbance
is smooth or larger outside level 4 than inside.

### Test B: linear stability of the discrete subsystems (reference computation)
Script `scripts/vonneumann.py`: amplification factor of RK4 for the frozen-coefficient
linear subsystems with the code's stencils (sixth-order first and second derivatives, mixed
derivatives as products, Kreiss-Oliger operator of nghost = 4 with diss = 0.5): the
Gamma-driver (beta, Gam; shift_Gamma 0.75, eta 2, gt = identity), the lapse (alpha, Khat;
speed sqrt(2 alpha chi)) and light (speed alpha sqrt(chi)), maximized over the Brillouin
zone, against dt/dx.
Prediction: the shift subsystem is unstable above a threshold dt/dx in [0.70, 0.78]; its
largest growth factor per step at dt/dx = 0.81 lies between 1.2 and 2.0 (the card's H_max
grew by 1.65 per cycle between cycles 240 and 248); the lapse and light subsystems at
alpha = 1.06, chi = 0.12 are stable up to dt/dx = 1. Refuted by a shift threshold above
0.85 (then the card's 0.80-0.83 is linearly stable) or below 0.65 (then the jump would have
come near t = 1.6).

### Tests U: uniform 64^3 mesh (deck `inputs/diag_uniform.athinput`, `scripts/run_uniform.sh`)
Release core-v0.6 threaded processor build. Same physics as the card deck without the
static levels: the step is set by the root cells (dx = 0.3125), by the light speed of the
whole box and, early, by dt_expansion = 0.05.
- U0 (as the deck): the jump happens here too (H-norm2 up by more than 100 within a few
  cycles) once dt/dx passes about 0.73, which I expect between t = 2.5 and 4 (later than on
  the card: here the largest light speed of the box sets the step); guard stop or blow-up
  before t = 12.
- U1 (cfl_number 0.5) and U6 (0.65): no jump to t = 12; H-norm2 within a factor 10 of its
  t = 2 value.
- U2 (zero shift, cfl_number 1.0): no jump to t = 12.
- U3 (lapse_leak 0, pure 1+log): the jump persists, when dt/dx passes about 0.73.
- U4 (TSC deposit, no filter) and U5 (S1 data): jump at the time of U0 within 10 per cent.
- U7 (cfl_number 0.8): jump (later than U0 or at the same time, dt/dx capped at 0.8).
Refuted: U0 without a jump (the uniform mesh does not reproduce it: refinement matters),
U1/U6/U2 with a jump (the step or the shift is not the cause), U3 without a jump (the
relaxation is involved), U4/U5 at a time different by more than 10 per cent (the matter or
the deposit is involved).

### Tests R: the card deck itself on processors (`scripts/run_refined.sh`), if time allows
- R0 (as job 4799, to t = 2.7): the jump between t = 2.27 and 2.50 as on the card; dt per
  cycle equal to the card's to 1e-6 relative before the jump.
- R1 (cfl_number 0.5, to t = 5.0): no jump; past the card's guard stop at 4.8.
- R2 (zero shift, cfl_number 1.0, to t = 3.0): no jump.
