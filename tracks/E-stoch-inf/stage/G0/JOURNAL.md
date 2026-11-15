# Journal of the G0 verifier (helper of E-stoch-inf, wave 2)

Fresh reader. Read so far, in this order: CLAUDE.md, coord/CHARTER.md to "Owners", brief
445-465, 785-802, 834-860, orch rulings after wave 1, decisions 0010-0015,
`spec/scope/SCOPE.md` (the scoping text: it names the claims), `spec/SPEC.md` sections 1-9
(the derivation), core's `athenak/src/scalar_field/scalar_field_noise.cpp` (main, release
core-v0.3), `athenak/src/z4c/z4c_newdt.cpp`, `docs/TESTLOG.md:44-47`, and the sources at
the locators P1 (2512.14649 v2 PRD_v2.tex) 95-130, 290-430, 478-541; P2 (2502.06783 v3)
180-200, 240-330, 395-470, 486-494; BZ (2606.14853 v2) 145-215. Not read before the
verdicts: the owner's STATUS, HANDOFF, JOURNAL, RISKS, the stage/G0 EVIDENCE, OPEN,
CHECKLIST, the G1 STATUS and every helper journal or README.

## Claims chosen (the plan rests on them; SCOPE sections 2, 4, 7.3 of SPEC, 8, 9)

- V1 background of both cases (SCOPE 2 "Derived"; SPEC 6).
- V2 freezing reference and criterion A3 (SPEC 7.3; SCOPE 4.4 A3).
- V3 erratum of the initial delta Pi (P2:320; SPEC 5.3).
- V4 erratum of the draw normalisation (P2:876-884; SPEC 5.4).
- V5 core's stochastic sources implement P1's sources (SCOPE 6).
- V6 the noise generator of the release is reproducible (SCOPE 6, A7).
- V7 compute estimate, 0.4-0.5 card-hours per 256^3 realisation, total 1.5-2 (SCOPE 8, 9.3).
- V8 delta-N reference: lattice-sum factor 1.0805 and the 42-45 percent excess at sigma = 1
  (SPEC 7.2 A8).

## Predictions (written before any of my runs)

P-V1. My own integrator (cosmic time, variables phi, dphi/dt, ln a; not the track's e-fold
form) gives for SR phi0 = -14.0950, m = 1.73494e-6, H* = 9.48692e-6, eps1(N*) = 1.1107e-2,
V(N*) = 2.690e-2 in Mpl = 100 units, and for USR dphi/dN(N0) = 0.102682, H0 = 9.5902e-6, USR
(eps2 > 3) from N* + 2.53 to N* + 6.55, eps1 minimum near 9.7e-13. Refuted if a value differs
by more than 1e-4 relative or a phase boundary by more than 0.02 e-fold. Break attempt: the
other reading of the H0-fixing velocity (dphi/dt instead of dphi/dN) must change the USR
history visibly (else the claim that the dN reading "reproduces Fig. 1" is empty).

P-V2. My own mode integration (deformed equation written as delta phi on unperturbed FLRW,
full equation as the R form, both from the same delta phi data, Bunch-Davies start at
max(N0, k/aH = 1000)): SR full Delta_R(N_f) / [H^2/(8 pi^2 eps1)] at crossing in 1.00-1.02;
super-horizon drift of the full spectrum from N_k + 4 below 2.5e-3 per e-fold; deformed drift
-0.05 +- 0.005 per e-fold (-4 eps1); deformed/full at N_f 0.65 (k = dk) to 0.79 (64 dk) within
0.02. USR deformed/full at N_f: 8.4 at k = dk, about 1.18 at 4 dk, near 1 at 64 dk (each within
10 percent). Refuted by a USR ratio at dk outside 7.5-9.3 or a SR drift of the full solution
above 2.5e-3 per e-fold.

P-V3. A symbolic linearised Hamiltonian constraint of my own (3-Ricci of a^2 (1 - 2 Phi)
delta_ij, 4/3 K_b delta K, delta rho = Pi_b delta Pi + V' delta phi) vanishes identically for
the corrected delta Pi and leaves +-4 eps1^2 H^3 a^2 k^-2 Rdot for the printed one; the
momentum constraint vanishes for both. Refuted by any other residual.

P-V4. A white-noise draw scaled by L^(-3/2) reproduces <f^2> = sum |f_k|^2/L^3 (the QFT
normalisation), and the prefactors dk^(3/2) and (dk/sqrt(2 pi))^(3/2) give (2 pi)^3 and
(2 pi)^(3/2) times too much power. Refuted if the printed prefactors match the QFT
normalisation under P2's own Fourier convention (I read P2:835-884 at the source first).

P-V5. Reading core's source of release v0.3: kicks d_t Pi += alpha (Pi_b/H) I_R, d_t K +=
-alpha eps1 I_R, d_t At += alpha eps1 (delta/3 - qq/q^2) I_R; window derivatives equal to the
symbolic derivative of W; the kicks leave the linearised H and M unchanged with the stencil
wave numbers of the first difference. Refuted by a sign or factor difference.

P-V6. On the release processor executable, the frozen tanh power model gives bit-identical
noise fields for 1 and 8 MeshBlocks and across a restart. Refuted by any differing byte.

P-V7. Step counts N_T = N sigma Delta N/(2 pi theta) hold because Z4c takes dt = cfl dx (read
in z4c_newdt.cpp); with H decreasing, the cosmic-time span is int dN/H, larger than Delta N/H*
by a few percent (SR) — so the step count of SCOPE is low by that factor. The cost per step
rests on 2e7 zone-cycles/s measured at 128^3 without matter; I expect the scalar field and the
noise synthesis to add more than the assumed 15 percent on processors, but the card figure
cannot be checked without card time (none is allotted to this package).

P-V8. For a scale-invariant spectrum the lattice sum over 1 <= |n| <= 64 divided by the
continuum integral ln 64 is 1.08 within 0.01; the separate-universe excess at sigma = 1 is
|1 + i sigma - sigma^2/3|^2 - 1 = sigma^2/3 + sigma^4/9 = 4/9 = 0.444 for a massless field in
de Sitter (the kick phi_k plus the displacement Pi_k/3 that the gradient-free evolution adds
after the kick at k = sigma a H), so 42-45 percent is expected. Refuted by a lattice factor
outside 1.07-1.09 or an analytic excess outside 0.40-0.48.

## Predictions added before the AthenaK runs (V6, V7), after reading the release source

P-V6 (replaces the frozen-tanh wording above; the power model is the one the track's U-tests
already ran, SCOPE 6 says the Mukhanov-Sasaki model with kicks and coupling has never run).
Core's deck `problems/scalar/noise_ms.athinput` (MS model, kicks of Pi, Khat, At, field coupled
to Z4c), N = 32, nmax2 = 64 (k_max = N/4), 52 cycles, dumps every 13 cycles, release processor
executable (sha256 d983155b...c25c): one 32^3 MeshBlock (B32), eight 16^3 (B16), four 32x16x16
(B3216) and a restart of B16 at cycle 13 (RST) give byte-identical dumps (all 16 fields:
phi, Pi, chi, K, alpha, H, M_i, E and the six noise fields) at every common cycle. Negative
control (Pi kick sign flipped, NEG): max |M| at least 100 times that of B16 (first against
second order, P1:541). Continuum projector (CONT): max |M| at least 10 times that of B16
(first order, but about 1e-2 smaller than NEG, my V5 figure). Refuted by any differing byte
between layouts or restart, or NEG/B16 < 100.

P-V7 (timing on one core, 32^3, 12 cycles). Operation count of the synthesis from the kernel
(scalar_field_noise.cpp:596-652), per stage, 6 fields: nf (M b + P b^2 + X b^3) per MeshBlock
(M modes, P (nx, ny) pairs, X distinct nx): N = 32, nmax2 = 225: 6.7e6 complex MACs with one
32^3 MeshBlock, 3.4e7 with 64 MeshBlocks of 8^3 (ratio 5.0). Prediction: the added time of the
noise, [t(T225b8) - t(T0b8)] / [t(T225) - t(T0)], lies in 3-8. At 256^3, nmax2 = 4096 the same
count gives per step 4.8e11 flop with 128^3 MeshBlocks (the track's cost.py assumption,
0.16 s at 3e12 flop/s, consistent with its 4-14 percent) but 2.6e12 flop with 32^3 MeshBlocks
(0.86 s, doubling the cost per step): the card estimate holds only with large MeshBlocks.

## Outcomes (registered runs; numbers from the JSON files of the run directories)

Runs: E-20261115-174606-3c67607 (V1-V5, V8), E-20261115-175051-b67c97e (rerun of the
track's T1-T4), E-20261115-174515-4d30c15 (V6/V7, FAILED: the literal "$NRPIC_RUN_DIR" was
passed unexpanded; a stray directory of that name in the worktree root was removed by its
literal path), E-20261115-174600-81652ff (V6/V7 rerun, completed).

O-V1 (prediction held). SR: phi0 -14.094995, m 1.734945e-6, H* 9.486915e-6, eps1(N*)
1.110710e-2, eps2(N*) -2.21331e-2, V(N*) 2.69005e-2 (Mpl = 100 units), eps1(N*+8) 1.34959e-2;
USR: dphi/dN(N0) 0.1026820, H0 9.590198e-6, H* 9.362319e-6, eps1(N*) 1.316389e-2, eps1(N_f)
1.0083e-12, eps1 min 9.716e-13 at N*+8.33, eps2 > 3 from N*+2.523 to N*+6.550, eps2 max 6.000,
eps1 max 2.408e-2 at N*+1.62. Every value agrees with SCOPE/SPEC to the printed digits
(largest relative difference 1.6e-3 on the 2-digit "9.7e-13"). Read against P1's own Fig. 1
(64usr_back__MeanRolls.pdf rasterised in scratch, not committed): eps1 peak 2.4e-2 at about
1.6, inset minimum about 0.975e-12 near 8.4, V plateau 2.383e-2; agrees. Break attempt: the
dphi/dt reading of the H0-fixing velocity gives eps1(N0) = 2.9999998 (kinetic domination, no
inflation), so the dN reading is the only viable one. Note: the quadratic panels of P1 Fig. 1
end at about N*+7.6, not N*+8 (Table I "~8").

O-V2 (prediction held). SR full/[H^2/(8 pi^2 eps1)]_cross = 1.0104-1.0121 (k = dk-64 dk);
super-horizon drift of the full spectrum from N_k+4 at most 2.5e-4 per e-fold (k <= 32 dk);
deformed drift over [N_k+3, N_f] -0.0509 to -0.0560; deformed/full at N_f 0.654 (dk) to 0.794
(64 dk); A3 discriminant: the deformed power ratio [N_k+4 -> N_f] is 0.815 of the full one at
k = dk (claim 0.82). USR deformed/full at N_f: 8.402 (dk), 3.69 (1.41 dk), 2.56 (1.73 dk),
2.07 (2 dk), 1.442 (2.83 dk), 1.180 (4 dk), 1.067 (5.66 dk), 1.020 (8 dk), 1.0028 (11.3 dk),
0.99999 (64 dk). Full Delta_R at N_f in USR: 1.02e-5 (dk) rising to 1.017 (64 dk).
New observation, not in the prediction: in the USR box the UV modes end with Delta_R of
about 1 while A3 tests the modes k <= 3 dk at Delta_R 1e-5 to 4e-4 — see V2b.

O-V3 (prediction held). Linearised H residual with the printed delta Pi:
4 H^3 Rdot a^2 eps1^2/k^2; with the corrected form and with delta Pi derived from P2's
dictionary: 0; M: 0; dK = 3 eps1 H (R - Phi_B) identically. Size of the printed form's
violation relative to [H] for de Sitter modes at t*: 1.1e-3 at k = aH, 1.3e-6 at 64 aH, first
order in the noise (so the A4 second-order test would catch it).

O-V4 (prediction held). <f^2>/(sum |f_k|^2/L^3) over 64 seeds, L = 3: 1.000 +- 0.017 with
L^(-3/2); 248.0 +- 4.3 with dk^(3/2) ((2 pi)^3 = 248.05); 15.75 +- 0.27 with
(dk/sqrt(2 pi))^(3/2) ((2 pi)^(3/2) = 15.75). P2:393 defines dk = 2 pi/(N dx), so no hidden
convention rescues the printed prefactors.

O-V5 (prediction held). All symbolic identities zero: eps1 = 4 pi Pi_b^2/H^2; eps2 = 6 +
2V'/(H Pi_b) - 2 eps1 = -dln eps1/dN; w1, w2 equal the first two derivatives of W (numerical
spot check max 1.4e-14); S_R = L[W R] - W L[R]; the kicks leave the linear H unchanged and the
discrete M unchanged with the stencil projector; the sixth-order stencil symbol of
finite_diff.hpp equals core's StencilWaveNumber; S_Pi/S_R = Mpl sqrt(2 eps1) for Pi_b > 0.
Read in the source: Pi = phidot/alpha (rhs.cpp: rhs.phi = alpha Pi), Z4c_ExplRK waits for
SF_Kick (z4c_tasks.cpp:65), Tzz = I_R - Txx - Tyy. With the continuum projector the discrete M
residual of one kick reaches 1e-2 of |q_h||dK| at k_max dx = pi/2 off the axes.

O-V6. Bit identity HELD: B16 (8 MeshBlocks), B3216 (4) and RST (restart of B16 at cycle 13)
equal B32 byte for byte in all 16 dumped fields at every common cycle (0, 13, 26, 39, 52;
26-52 for RST). Negative control HELD: max |M| NEG/B16 = 4.4e4, 4.7e4, 5.3e3, 290 at cycles
13-52 (max |H| ratio 5e4 at 13); NEG differs from B32 by up to 7.5e-7. Continuum projector
prediction PARTLY FAILED: max |M| CONT/B16 = 1.05, 29, 41, 1.07 at cycles 13, 26, 39, 52 —
above 10 only while the high-k off-axis modes are being kicked (the window passes k_max near
t = 3.4 of 4); at cycle 13 only low-k modes have entered and at 52 both runs sit on the same
floor, which grows from 1e-12 to 8.5e-11 with delta K constant at 2.2e-7: a first-order
truncation floor at k_max dx = pi/2 (my reading; P1:541 reports the same effect at the last
crossing) [JUDGEMENT; not tested by halving the amplitude].

O-V7 (prediction NOT DECIDED). zone-cycles/s on one core, 12 cycles, four runs in parallel:
T0 10847, T64 10548, T225 10943, T0b8 8830, T225b8 8125. Time per cycle: noise cost at one
32^3 MeshBlock -0.03 s (T225 vs T0: inside the scatter, about 1-3 percent), at 64 MeshBlocks
of 8^3 +0.32 s (9 percent of 3.7 s). The ratio of the prediction is undefined (denominator in
the noise); the b = 8 cost matches the operation count (1.08e9 flop per cycle) at 3.4 Gflop/s,
which predicts 0.06 s at b = 32, below the scatter. The MeshBlock-size dependence of the
synthesis is therefore seen at b = 8 only. Z4c alone was not timed.

O-V8 (prediction held). Lattice sum / continuum: 1.0731 for a flat spectrum, 1.0805 for the
SR spectrum of my V2 run at N_f (claim 1.0805). Separate-universe excess at sigma = 1: 4/9 =
0.4444 (numerical = closed form to 4e-15); 3.3e-3 at sigma = 0.1, 3.3e-5 at 0.01.

O-rerun. The track's T1/T2 (ms_reference.py), T3 (norm_test.py --n 64 --seeds 8) and T4
(ic_constraint_check.py) reproduce their original outputs exactly: 545 + 272 + 273 + 92
numeric leaves with relative difference 0, the symbolic strings identical
(run E-20261115-175051-b67c97e, compare.json).

## V2b prediction (written before the registered run; a trial in scratch showed f_NL about 0
## for kicks at N*+2 and kicked paths that never reach a surface at N*+10)

P-V2b. Along the USR background the classical drift per e-fold |dphi/dN| falls to the
quantum step H/2pi or below (minimum ratio 0.5-2 near N*+8), i.e. the end of the USR run is
diffusion-dominated; and with the local quadratic proxy, f_NL = 0.1 already gives a low-k
contamination r(dk) of order the A3 tolerance (5e-3), f_NL = 2.5 gives r(dk) > 1. Refuted if
the drift/diffusion ratio stays above 10, or r(dk, f_NL = 0.1) < 5e-4.

Trial of V2b in scratch (not registered, end surface N*+12.5): f_NL = 0.0089, 0.0110, 0.0111,
0.0112 for kicks at N*+2, 3, 3.5, 4.2; drift/diffusion minimum 0.983 at N*+8.33, 1.00 at N_f;
r(dk) = 6.5e-3 at f_NL = 0.1, 4.1 at f_NL = 2.5. So the first half of P-V2b held, but the
model's own f_NL is 0.011, which gives r of about 8e-5 (per-mode deviation about 1 percent),
well inside the A3 tolerance: the weakness I suspected is not shown by the delta-N proxy.
Added prediction before the registered run: N(kick) at N*+4.2 stays within 6 percent of its
linear term for kicks up to 6 H/2pi (N'' delta phi/(2 N') = 0.045 at 6 H/2pi from the trial's
N', N''), and within 2 percent at N*+3. Refuted by a larger departure (that would mean the
kicks of the USR box are non-perturbative in delta N although f_NL is small).
