# periodic_diag: journal (helper of A-emd-pbh, batch 6, 2026-11-21)

Predictions are written before each test; outcomes follow, also when a prediction failed.

## 2026-11-21 21:20Z, entry 0: what is known, candidates, predictions (written before any run)

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

## 2026-11-21 21:27Z, entry 1: outcome of U0 (run A-20261121-212150-20ffbb6), and what it changes

U0 (uniform 64^3, the card deck's physics, relaxed lapse with lapse_leak 20) stopped on the
guard at t = 10.76 (cycle 70, exit 3; 4 minutes on 6 threads). H-norm2 (`peak.z4c.user.hst`)
7.3e-3 at t = 2.50, 8.0e-3 at 2.71, 2.5e-2 at 2.94, 6.1 at 3.18, 50 at 3.42. The jump time
falls inside my predicted window (2.5-4) and the step there is dt/dx = 0.733-0.746, as
predicted. But the line outputs (tab 4 to 7, x axis through the peak) refute the mechanism
I named for it: beta^x and Gam^x stay smooth and odd in x through t = 3.67, while the LAPSE
goes bad first: alpha_max rises again from t = 1.9 on (1.0766 at t = 1.91, 1.1055 at 2.50,
where the relaxed lapse should fall monotonically towards exp(6TH)), and at t = 3.18 alpha
has dips to 0.85 at |x| = 0.78, at 3.67 an irregular pattern 0.62-1.03.
Reading [JUDGEMENT, to be tested]: on the root mesh the step reaches 0.14 at t = 1.40 and
0.23 at 3.0, so lapse_leak x dt = 2.9 to 4.7, beyond the RK4 real-axis limit 2.79: the
relaxation term itself is integrated unstably (the deck header's own rule, leak x dt < 2.7,
holds on the card's level 4, 20 x 0.0195 = 0.39, but not on a 64^3 root mesh). So U0 does
not reproduce the card's mechanism; it shows a second one, of coarse meshes only. The
remaining U cases (U1 to U7) are dropped: all of them carry the same stiff relaxation.

Seen before the registered Test B run (a smoke test of `scripts/vonneumann.py` on a 9^3
grid of wave vectors, scratch/A-emd-pbh/tmp/vn_test, not evidence): shift threshold 0.685
at dx = 0.0195 (0.77 without the Kreiss-Oliger term: with it the grid-scale eigenvalues
leave the narrow tip of the RK4 region near 2.83i); lapse with leak 20 on the root mesh
unstable from dt/dx = 0.405. Test B's prediction stands as written; the registered run on a
41^3 grid decides.

## 2026-11-21 21:28Z, entry 2: predictions for the G series (uniform, frozen lapse) and R

G series: `inputs/diag_uniform.athinput` with the lapse frozen (lapse_oplog 0, lapse_advect
0, lapse_leak 0: d_t alpha = 0 apart from the Kreiss-Oliger term; alpha keeps the data's
values 0.81-1.0), so that neither the 1+log speed nor the stiff relaxation enters. The step
is then min(dx, 0.25 dx/(alpha sqrt chi)) and dt_expansion; dt/dx should pass 0.7 near
t = 2.5. Cases (`scripts/run_uniform.sh`):
- G0 Gamma-driver as the card deck, cfl 1.0: grid-scale (cell-to-cell alternating) growth of
  beta^x and Gam^x on the line output, then of H, starting within 3 cycles of the first
  step with dt/dx above the Test B threshold for dx = 0.3125 (about 0.65), at t between 2
  and 3.5; guard stop or H-norm2 above 1 before t = 12.
- G1 as G0 with cfl_number 0.5: no growth to t = 12; H-norm2 at t = 12 within a factor 10
  of its value at t = 2.
- G2 as G0 with zero shift: no growth to t = 12 (same criterion).
- G3 as G0 with the S1 data, G4 as G0 with TSC deposit and no filter: onset within one
  cycle of G0's (the step history is set by the background, not by the matter).
Refuted: G0 without growth (then the Gamma-driver at Courant 0.7-1 is stable in this code and
the card's cause is elsewhere), G1 or G2 with growth, G3/G4 with an onset more than 2
cycles from G0's.

R series (the card deck itself on processors, `scripts/run_refined.sh`; level 4 has dx =
0.0195, so lapse_leak x dt <= 0.39 and the stiff relaxation of U0 cannot act):
- R0 (as job 4799, to t = 2.7): H_max (cstat, every cycle) jumps between t = 2.27 and 2.50;
  dt per cycle equal to the card's to 1e-4 relative before the jump; grid-scale beta^x on
  level 4 in the line outputs (every 0.1) by t = 2.4.
- R2 (zero shift, cfl 1.0, to t = 3.0): no jump; H_max below 0.05 to t = 3.0.
- R1 (cfl_number 0.5, to t = 3.0), only if the processors allow: no jump.
