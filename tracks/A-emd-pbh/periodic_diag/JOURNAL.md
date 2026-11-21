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

## 2026-11-21 21:41Z, entry 3: outcome of Test B (run A-20261121-212800-d7f31a4; `fig_vonneumann.png` looked at) and of G0 (run A-20261121-212941-9e68be1, case G0)

Test B. Gamma-driver subsystem: unstable for dt/dx > 0.685 on the card's level 4 (dx =
0.0195), > 0.65 on the root mesh (dx = 0.3125, where eta dt is no longer small); without
the Kreiss-Oliger term 0.77 and 0.80. The first unstable wave vector is the 3D grid-scale
corner (pi, pi, pi) in both. Largest |R| per step at dx = 0.0195: 1.10 at dt/dx = 0.70,
1.98 at 0.80, 2.10 at 0.81, 2.30 at 0.825, 5.8 at 1.0. Light: stable to dt/dx = 1.2.
1+log lapse with leak 20 (alpha0 1.06, chi0 0.12): stable to 0.9675 on level 4, but on the
root mesh unstable from 0.405 (|R| = 22.5 at 0.81), the stiff relaxation of entry 1.
Against the prediction: the shift threshold 0.685 lies just below my band [0.70, 0.78]
(the Kreiss-Oliger term LOWERS it: the grid-scale eigenvalues acquire a real part -1.5 dt/dx
and leave the narrow tip of the RK4 region near 2.83i) but above the refutation bound 0.65;
the growth at 0.81, 2.10, lies just above my band [1.2, 2.0]; lapse and light on level 4
stable up to 1 within 3 per cent (lapse 0.9675): as predicted. The card's level-4 step was
0.80-0.83 at cycles 240-251, i.e. inside the unstable range, and from cycle ~205 on above
0.685 [Test A will put numbers on it].

G0 (uniform 64^3, lapse frozen, Gamma-driver, cfl 1.0; to t = 12, no guard stop, 66 cycles):
dt/dx passes 0.65 at t = 2.37 (cycle 21) and reaches 1.0 at t = 4.7. H_max falls smoothly
from 1.45e-2 (t = 1.8) to 3.5e-3 (t = 7.47), then grows: 4.0e-3 (7.79), 1.75e-2 (8.10),
7.7e-2 (8.41), 1.78 (8.72), i.e. by 4.4, 4.4 and 23 per cycle at dt/dx = 1.0 (Test B: 6.5 per
step at the root mesh). Line output at t = 8.72: beta^x and Gam^x alternate in sign from cell
to cell (beta^x +0.0126, -0.0181, +0.0148, -0.0127 ... at x = -1.72 ... -0.78; Gam^x +-0.2 to
0.34), alpha (frozen) and Khat smooth; at t = 7.79 still smooth and odd in x; the x -> -x
symmetry of the data is broken by the growing part (a round-off seed). After the burst the
light-speed limit (which counts |beta|) cuts the step to dt/dx = 0.2-0.9 and H_max settles at
0.3-2.
Judgement against entry 2: the growth and its form (grid-scale beta and Gam, nothing in the
frozen lapse) are as predicted; the TIME is refuted: onset at t = 8.1, 20 cycles after dt/dx
passed 0.65, not within 3 cycles. My prediction ignored the seed: here the data are smooth,
the shift starts at zero, and the grid-scale part grows from round-off; the amplification
accumulated over the step history must reach about 1e12 before H shows it [to be computed
from Test B along the run's own steps in the analysis].

## 2026-11-21 21:41Z, entry 4: predictions for G5 and G6 (seeded by white noise), written before they run

G0 grew from round-off. To bracket the threshold with a seed present, two more frozen-lapse
cases on the uniform mesh carry white noise of relative amplitude 1e-10 in every evolved
field (`<problem> noise_amp = 1e-10`, the robustness option of nrpic_cosmo), to t = 10:
- G5 (cfl 1.0): grid-scale growth of beta^x / Gam^x and of H_max starts earlier than in G0
  (onset t < 7.5, against 8.1), because the seed is about six orders above round-off.
- G6 (cfl 0.6, so dt/dx <= 0.6 < 0.65): no growth to t = 10; H_max stays within a factor 2
  of G1's at equal t (G1: cfl 0.5 without noise).
Refuted: G5 not earlier than G0 (then the seed does not set the onset), G6 with growth
(then the threshold on the root mesh lies below 0.6, and Test B is wrong for this code).

## 2026-11-21 22:06Z, entry 5: G1 and G2 outcomes (run A-20261121-212941-9e68be1); the first G5/G6 attempt

G1 (cfl 0.5, lapse frozen, Gamma-driver; to t = 12, 100 cycles, time limit): no growth;
H_max falls smoothly to 1.25e-3 at t = 12. G2 (zero shift, cfl 1.0; to t = 12, 54 cycles,
dt/dx = 1.0 from t = 4.7 on): no growth; H_max 1.57e-3 at t = 12. Both as predicted.
With G0 this isolates the Gamma-driver at a large step: same data, same frozen lapse, same
step history as G0 in G2; only the step (G1) or only the shift (G2) changed, and the growth
is gone in both.

First G5/G6 attempt (run A-20261121-220411-b7dd9ce): both cases stopped at once with
"Parameter 'noise_amp' in block 'problem' on command line not found" (AthenaK accepts on
the command line only parameters the deck declares); nrpic-run closed the run as completed
because the driver script returns 0. No result; superseded by the next run with the deck
`inputs/diag_uniform_seed.athinput` (noise_amp = 1e-10 declared, tlim 10). Prediction of
entry 4 unchanged.

## 2026-11-21 22:26Z, entry 6: G5 and G6 outcomes (run A-20261121-220510-6c46032); a failed Test A attempt

G5 (seeded 1e-10, cfl 1.0, lapse frozen; to t = 10, 54 cycles): the same step history as G0
(dt/dx 0.65 at t = 2.37, 1.0 from t = 5.0); H_max leaves its smooth decline at t = 7.47
(6.8e-3 against 3.8e-3 one cycle before; G0 3.5e-3 at that time), 5.3e-2 at 7.79, 0.355 at
8.10, 1.02 at 8.32; then the light-speed limit cuts the step and H_max stays at 0.2-0.7.
G6 (seeded, cfl 0.6; to t = 10, 73 cycles, dt/dx = 0.600 from t ~ 2): no growth; H_max falls
smoothly to 1.84e-3 at t = 10 (G1, cfl 0.5 without noise: 1.80e-3 at t = 10). G6 as
predicted (within a factor 2 of G1, no growth): a step of 0.6 dx is below the threshold
with a seed present.
G5 against entry 4: "earlier than G0, onset t < 7.5": formally yes (first departure at
7.47 against G0's 7.79-8.10), but only by about one cycle. With 4 to 6 per cycle at dt/dx =
1, a seed six orders above round-off should have moved the onset by eight cycles. So my
entry-3 reading "G0 grows from round-off" is REFUTED: G0's own grid-scale seed is already
within a factor of about 10 of the 1e-10 noise. [JUDGEMENT, not tested] the particle
sources (shot noise of 262,144 particles deposited with CIC; the momentum density enters
d_t Gam^i directly) seed the grid-scale shift mode in every particle run, so the onset in
a particle run comes a fixed number of cycles after the step passes the threshold.

Test A first attempt (run A-20261121-222439-65eebaa) failed in my script: the onset search
took the t = 0 line (H_max 0.49, the data's own constraint violation) as the first line
above ten times the baseline. Fixed (search after t = 1) in `card_onset.py` and the same
in `analyse_runs.py`; rerun next.

Test A second attempt (run A-20261121-222459-4cb257c) ran, but its per-level split of the
line outputs found only levels 4 and 0: my equal-spacing test used a tolerance of 1e-6
while the tab files print x to six digits. Fixed (1e-3 relative) in both analysis scripts;
the onset and step numbers of that run do not depend on it. Rerun next.

## 2026-11-21 22:27Z, entry 7: Test A outcome (run A-20261121-222539-c4e42fe; fig_card_onset.png looked at), uniform-run figure, and predictions for a cheaper remedy

Test A (the card's own outputs; numbers from card_onset.json):
- The level-4 step passes the Test B threshold 0.685 at cycle 201 (t = 1.70) in P0L and at
  cycle 207 (t = 1.77) in S1L, and 0.73 at cycle 218 (t = 1.94); it reaches 0.825 (P0L) and
  0.829 (S1L) before the jump. The two members' steps agree to 1.8 per cent up to t = 2.3.
- First cstat line after t = 1 with H_max above ten times its 0.3-2 median: t = 2.397 in P0L
  (0.84; previous line 0.0149 at 2.269), t = 2.490 in S1L (0.97; previous 0.0161 at 2.363).
- The linear amplification of Test B accumulated over the card's own steps from the
  threshold crossing: 10^5.8 (P0L) and 10^6.3 (S1L) to the last quiet line, 10^8.4 and 10^9.1
  to the first jump line; between those two lines 10^2.7 predicted against an observed
  growth of H_max by more than 10^1.75 (0.0149 to 0.84; the earlier value is the physical
  constraint violation, so the unstable part grew by more). The scaled amplification curve
  follows the observed rise in the figure (top right) for both members, and S1L's later
  jump matches its later threshold crossing.
- Line outputs: at t = 2.01 the cell-to-cell part of beta^x on level 4 is 4e-6 against a
  maximum of 0.016 (no visible alternation); at t = 4.00 Gam^x alternates on level 4 (1.9e-2
  of 0.20), level 3 (3.5e-2 of 0.13) and level 2 (7.5e-3), not on levels 1 and 0 (7e-5,
  1.5e-4); alpha shows no alternation above its print precision on any level (5e-6).
Judgement against entry 0: crossing of 0.73 between t = 1.8 and 2.1: yes (1.94); members'
steps within 5 per cent: yes (1.8); no visible alternation at 2.01: yes; at 4.0 grid-scale
beta^x and Gam^x inside the refined region and not outside: yes, but "inside level 4 far
above outside it" is REFUTED as worded: at t = 4.0, 1.5 time units after the jump, level 3
carries a larger alternation than level 4. The snapshots (every 2.0) cannot show where it
began; the guard's first bad cell was on level 4 in both members, and Test B makes levels 3
and coarser stable at these steps (dt/dx_3 <= 0.42). [JUDGEMENT: origin on level 4,
spreading to levels 3 and 2 by t = 4; not shown by a run.]

Uniform-run figure (run A-20261121-222626-2cb28d0, fig_uniform.png looked at): G0 and G5 jump
at t = 8.1-8.7 after their step has sat at dt/dx = 1 since t = 5; G1, G2, G6 decline
smoothly to t = 10-12; U0's lapse (bottom left) leaves its relaxation track at t = 2.5 and
its alternation (bottom right) rises at t = 3.2 before that of beta^x.

Predictions for a cheaper remedy than a smaller step (the Gamma-driver speed is
sqrt(4 shift_Gamma/3) in coordinate units):
- Test B' (vonneumann.py --mu 0.3): the shift threshold rises above dt/dx = 1.0 for both cell
  sizes (scaling of the wave part alone gives 0.685 x sqrt(0.75/0.3) = 1.08; the KO term does
  not scale).
- G7 (seeded, lapse frozen, shift_Gamma 0.3, cfl 1.0, to t = 10): no growth; H_max within a
  factor 2 of G2's (zero shift) at equal t.
Refuted by a threshold below 1.0 in B' or growth in G7.

## 2026-11-21 22:28Z, entry 8: Test B' outcome (run A-20261121-222713-efe9eb8); G7 not run

Test B' (shift_Gamma 0.3): the shift threshold is 0.94 at dx = 0.0195 and 0.90 at dx = 0.3125
(|R| at dt/dx = 1: 1.24 and 1.49); without the Kreiss-Oliger term no instability up to 1.2.
My prediction "above 1.0" is REFUTED: the KO term (diss 0.5, real part -1.5 dt/dx at the
grid-scale corner) moves the grid-scale eigenvalues out of the RK4 region well before the
wave part alone would (the scaling estimate 1.08 holds only without KO). So lowering
shift_Gamma alone does not make cfl_number 1.0 safe. G7 is not run: by Test B' it is
linearly unstable at dt/dx = 1 but grows by only 1.49 per step on the root mesh, so from
the 1e-10 seed it would need about 46 cycles at dt/dx = 1 (t ~ 19) to show, beyond the
planned t = 10; a no-growth outcome to t = 10 would not discriminate.

## 2026-11-21 22:29Z, entry 9: why every G case reported exit 2 (a check of scripts/cpu_run.sh, no simulation)

All G cases ended on their time limit with a normal athena log, yet run_uniform.sh printed
"exit 2" and cpu_run.sh wrote no footer. With ATHENA_EXE=/bin/true (scratch/A-emd-pbh/tmp/
cpu_run_check, cpu_run_check2) cpu_run.sh prints "awk: fatal: cannot use gawk builtin
`load' as variable name" and exits 2: the footer's awk takes `-v load=...`. So athena
returned 0 in the G runs and the 2 is the footer's. In U0 (guard, status 3) the script left
at `wait` under set -e, which is why that exit status was athena's. Reported to core in the
draft message (item iii); none of our results depends on it.

## 2026-11-21 22:30Z, entry 10: predictions for U8 and U9 (isolating the stiff relaxation of U0), written before they run

U0 mixed the Gamma-driver and the relaxed lapse on the root mesh. Two cases without shift:
- U8 (relaxed lapse, lapse_leak 20, zero shift, cfl 1.0, to t = 12): the lapse leaves its
  relaxation track once lapse_leak x dt passes about 2.5-2.8 (dt ~ 0.13-0.14, t ~ 1.3-1.5)
  and H jumps (H_max above ten times its 0.3-2 median) between t = 2 and 4; guard stop or
  blow-up before t = 12.
- U9 (as U8 with lapse_leak 5, so lapse_leak x dt <= 1.6): no jump to t = 12 (the background
  lapse settles near exp(1.2 H) instead of exp(6 T H) with T = 0.05, so the early step is
  smaller; that is the price).
Refuted: U8 without a jump (then the shift, not the relaxation, failed in U0), U9 with one.
