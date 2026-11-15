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
