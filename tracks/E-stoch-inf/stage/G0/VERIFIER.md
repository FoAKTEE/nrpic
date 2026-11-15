# Independent verification of Track E's G0 and G1 material (wave 2)

Verifier: helper of E-stoch-inf, fresh reader, given the artefacts and not the conclusions.
Date 2026-11-15. Worktree commit at start: 4c87b13 (after `git merge main`).

Read before the verdicts: the scoping text `../../spec/scope/SCOPE.md` (it names the claims),
the derivation `../../spec/SPEC.md` sections 1-9, core's source of release core-v0.3
(`athenak/src/scalar_field/*.cpp`, `pgen/nrpic/scalar_field_tests.cpp`, `z4c/z4c_newdt.cpp`,
`z4c/z4c_tasks.cpp`, `utils/finite_diff.hpp`), the track's cost model
`../../codebase/ref/cost.py` and its output, the run manifests, and the sources at the
locators (P1 = 2512.14649 v2 `PRD_v2.tex`; P2 = 2502.06783 v3 `main_V2PRD.tex`; TH =
2610.32592 v1 `appendix.tex`; BZ = 2606.14853 v2 `Manuscript.tex`; P1's Fig. 1 PDFs).
Not read before the verdicts: the owner's STATUS, HANDOFF, JOURNAL, RISKS, the lead's
EVIDENCE, OPEN, CHECKLIST of this directory, `../G1/STATUS.md` and every helper's JOURNAL or
README. The comparison with them is the last section.

Labels: [VERIFIED] recomputed or rerun here with the run id given; [JUDGEMENT] my inference;
[TO VERIFY] open. Predictions and outcomes, including the failed ones: `JOURNAL.md`.

## Runs

| Run id | What | Status |
|---|---|---|
| E-20261115-174606-3c67607 | V1-V5, V8: my own code (`scripts/`) | completed |
| E-20261115-175051-b67c97e | rerun of the track's spec/ref T1-T4, unchanged; leaf-by-leaf comparison | completed |
| E-20261115-174515-4d30c15 | V6/V7, first attempt | failed (my error: run directory passed unexpanded) |
| E-20261115-174600-81652ff | V6/V7: release processor executable, core's MS deck, 11 AthenaK runs | completed |
| E-20261115-180056-d62ee5a | V2b: nonlinearity of the USR box (delta N proxy) | completed |
| E-20261115-180348-d799c68 | V7: cost arithmetic from the track's inputs and my operation count | completed |
| E-20261115-180445-e72dad6 | V7 addendum: the same, calibrated with core's card measurement | completed |

All on processors (no card time; none was allotted to this package). Figures in `fig/`,
JSON in `results/`; every figure was looked at before it was relied on.

## Verdicts

### V1 Background of the two cases (SCOPE 2, "Derived"; SPEC 6) — CONFIRMED

Own integrator in cosmic time (variables phi, dphi/dt, ln a; the track integrates in
e-folds). SR: phi0 = -14.094995, m = 1.734945e-6, H* = 9.486915e-6, eps1(N*) = 1.110710e-2,
V(N*) = 2.69005e-2 (Mpl = 100 units). USR: dphi/dN(N0) = 0.1026820, H0 = 9.590198e-6,
eps2 > 3 from N*+2.523 to N*+6.550, eps1 minimum 9.716e-13 at N*+8.33. Every number agrees with
SCOPE/SPEC to the printed digits (largest relative difference 1.6e-3, on the two-digit
"9.7e-13"). Read against P1's own Fig. 1 (`64usr_back__MeanRolls.pdf`,
`64quad_back__MeanRolls.pdf`): eps1 peak 2.4e-2 at about 1.6, inset minimum about 0.975e-12 near
8.4, V plateau 2.383e-2 — agree. Break attempt: the other reading of the H0-fixing velocity
(dphi/dt = -V'/V, P2:408) gives eps1(N0) = 3.0000 (kinetic domination, no inflation), so the
dN reading is forced. The SPEC's two text errata here also hold at the source: P1:108 lacks
the 3 Mpl^2 of the Friedmann denominator (read), and the field passes the stationary
inflection point -sqrt2 v. Side note: the quadratic panels of P1 Fig. 1 end near N*+7.6, so
"N_f - N* = 8" (Table I "~8") is a choice, not a reproduction of the figure.
[VERIFIED, run E-20261115-174606-3c67607, `fig/fig_v1_background.png`; track's own T1 rerun
identical, run E-20261115-175051-b67c97e]

### V2 Freezing reference and criterion A3 (SPEC 7.3; SCOPE 4.4 A3) — CONFIRMED

Own mode integration (background and modes jointly in cosmic time; the deformed equation
written as delta phi on unperturbed FLRW, not in BZ's f-form; Bunch-Davies start at
max(N0, k = 1000 aH), not the track's k = 100 aH). SR: full Delta_R(N_f) = 1.0104-1.0121 x
H^2/(8 pi^2 eps1) at crossing (claim 1.010-1.012); drift of the full spectrum from N_k+4 at
most 2.5e-4 per e-fold; deformed drift -0.0509 to -0.0560 per e-fold (claim -0.051 to -0.055;
-4 eps1); deformed/full at N_f 0.654 (dk) to 0.794 (64 dk) (claim 0.65-0.79); the A3
discriminant at k = dk is 0.815 (claim 0.82), twenty times the 1 percent tolerance. USR:
deformed/full at N_f = 8.402, 1.442, 1.180, 1.067, 1.0028, 0.99999 at k/dk = 1, 2.83, 4, 5.66,
11.3, 64 (claims 8.40, 1.4, 1.18, 1.07, 1.003, 1.0000); full Delta_R at N_f rises to 1.017 at
64 dk. [VERIFIED, run E-20261115-174606-3c67607, `fig/fig_v2_modes.png`, `fig/fig_v2_ratio.png`]

Break attempt (V2b): in the USR box the UV modes end at Delta_R of about 1 while A3 tests the
modes k <= 3 dk at Delta_R 1e-5 to 4e-4; could mode coupling spoil the per-mode test? Delta-N
proxy (separate universe, surface N*+12.5): f_NL = 0.009-0.011 for kicks at N*+2 to N*+4.2;
N(kick) stays within 3 percent (kick at N*+3) and 4.5-8 percent (N*+4.2) of linear for kicks
up to 6 H/2pi although one H/2pi moves the end of USR by about one e-fold; the local-quadratic
contamination of the A3 modes at f_NL = 0.011 is r of about 8e-5 (A3 tolerates about 5e-3;
f_NL = 0.1 would reach it). The criterion survives this attempt. [VERIFIED as a proxy, run
E-20261115-180056-d62ee5a, `fig/fig_v2b.png`; gradients and the NR extraction are not in it]

### V3 Erratum of the initial delta Pi (P2:320; SPEC 5.3) — CONFIRMED

Derived by hand from P2's dictionary (P2:262-308): delta Pi = d/dt delta phi - phidot Psi_G
with delta phi = sqrt(2 eps1) Mpl (R - Phi_B + H chi), chi(t*) = 0, chi-dot = Psi_G - Psi_B;
the Psi_G terms cancel and -sqrt(2 eps1) Mpl H Psi_B remains. Independent sympy check of my
own linearised constraints (3-Ricci of a^2 (1 - 2 Phi), (4/3) K_b delta K, delta rho = Pi_b
delta Pi + V' delta phi): residual 4 H^3 Rdot a^2 eps1^2/k^2 with the printed form, 0 with the
corrected one and with the dictionary form; M = 0; delta K = 3 eps1 H (R - Phi_B). Size of the
printed form's violation relative to [H] for de Sitter modes at t*: 1.1e-3 at k = aH, 1.3e-6 at
64 aH — first order, so A4 would catch it. [VERIFIED, run E-20261115-174606-3c67607,
`fig/fig_v3_violation.png`; track's T4 rerun identical]

### V4 Erratum of the draw normalisation (P2:876-884; SPEC 5.4) — CONFIRMED

By hand: with s_k = N^(-3/2) RFFTN{Delta} and unnormalised IRFFTN, <f^2> = c^2 sum |f_k|^2,
and the QFT normalisation (P2:840-845) needs sum |f_k|^2/L^3, so c = L^(-3/2) = (dk/2 pi)^(3/2);
P2:393 fixes dk = 2 pi/(N dx), so no convention rescues the printed dk^(3/2) (P2:880) or
(dk/sqrt(2 pi))^(3/2) (P2:881), which also disagree with each other. Own numpy test (L = 3,
64 seeds): ratio 1.000 +- 0.017, 248.0 +- 4.3 ((2 pi)^3 = 248.05), 15.75 +- 0.27
((2 pi)^(3/2) = 15.75). TH appendix:477 shows the thesis' own correction of C.
[VERIFIED, run E-20261115-174606-3c67607, `fig/fig_v4_norm.png`; track's T3 rerun identical]

### V5 Core's sources implement P1's (SCOPE 6) — CONFIRMED (on release core-v0.3)

Read in `scalar_field_noise.cpp` of the release (SCOPE cites the earlier 836ac86) and checked
with sympy: eps1 = 4 pi Pi_b^2/H^2 (G = 1); eps2 = 6 + 2V'/(H Pi_b) - 2 eps1 = -dln eps1/dN;
the window derivatives w1, w2 (cpp:524-542) equal the derivatives of W; the shell factor is
S_R = L[W R] - W L[R] (P1:302-304); dPi = (Pi_b/H) I equals Mpl sqrt(2 eps1) S_R for Pi_b > 0
and is sign-safe otherwise; the kicks (dK = -eps1 I, dAt = eps1 (delta/3 - qq/q^2) I) leave
the linear H unchanged and the discrete M unchanged with the stencil projector, whose symbol
equals the NGHOST = 4 coefficients of `finite_diff.hpp`. Also read: Pi = phidot/alpha
(rhs.cpp:44), Z4c_ExplRK waits for SF_Kick (z4c_tasks.cpp:65), Tzz = I_R - Txx - Tyy.
With the continuum projector the residual of M after one kick reaches 1e-2 of |q_h||dK| at
k_max dx = pi/2 off the axes (`fig/fig_v5_projector.png`). [VERIFIED, run
E-20261115-174606-3c67607]. Not checked: that the amplitude of the kicked field equals
W R alpha (A2); no run with physical mode functions exists.

### V6 Reproducibility of the noise (SCOPE 6; A7) — CONFIRMED, and extended

SCOPE 6 rests on the power model at 836ac86 and says the Mukhanov-Sasaki model, the kicks and
the coupling have never run. I ran core's own MS deck (`problems/scalar/noise_ms.athinput`,
kicks of Pi, Khat, At, field coupled to Z4c) on the release processor executable at N = 32,
nmax2 = 64, with my own reader of the NRSFDMP1 dumps: one 32^3 MeshBlock, eight 16^3, four
32x16x16 and a restart of the 16^3 run at cycle 13 are byte-identical in all 16 dumped fields
at every common cycle (0-52). The negative control (Pi kick sign flipped, P1:541) raises
max |M| by 4.4e4, 4.7e4, 5.3e3, 290 at cycles 13-52 and max |H| by 5e4: the kicks of the code
preserve the constraints at first order. My prediction that the continuum projector would
raise max |M| tenfold held only at cycles 26 and 39 (29x, 41x), not at 13 and 52 (1.05x,
1.07x), where both runs sit on a floor that grows from 1e-12 to 8.5e-11 with delta K constant
(a first-order truncation floor at k_max dx = pi/2 is my reading [JUDGEMENT], untested).
[VERIFIED, run E-20261115-174600-81652ff, `fig/fig_v6.png`] Not rerun by me: the power-model
U-tests and the Markov-tanh A1 case on v0.3 (other helpers' runs E-20261115-170727-d15df12,
-172423-5234cce were running; the cancellation-free increment is in the release source,
cpp:572-577).

### V7 Compute estimate (SCOPE 8, 9.3) — NOT CONFIRMED (not measurable without cards)

What holds: N_T = N sigma Delta N/(2 pi theta) (P1:721) because Z4c takes dt = cfl x min dx
(z4c_newdt.cpp:26-58); 2.0e7 zone-cycles/s is at `docs/TESTLOG.md:46` (128^3, no matter);
the arithmetic 0.84 s per 256^3 step is right; my operation count of the synthesis kernel
(cpp:596-652) reproduces the track's 0.16 s per step for 128^3 MeshBlocks at 3e12 flop/s.
What I found: (a) the step count is 4-5 percent low, because the cosmic time from N* to N_f is
8.39/H* (SR) and 10.44/H* (USR), not 8 and 10 (1368 and 1701 steps instead of 1304 and 1630);
(b) the synthesis cost depends on the MeshBlock size: per step 4.8e11 flop with 128^3
MeshBlocks, 9.7e11 with 64^3, 2.6e12 with 32^3 (0.86 s at 3e12 flop/s, doubling the cost per
step); on processors the noise costs 0.32 s per cycle with 8^3 MeshBlocks and is inside the
timing scatter with one 32^3 MeshBlock, consistent with the count at 3.4 Gflop/s (run
E-20261115-174600-81652ff, `fig/fig_v7_timing.png`; my prediction of the ratio could not be
decided); (c) the throughput of Z4c with the field at 256^3, the 15 percent field overhead and
the 3e12 flop/s are unmeasured; the 20 GB memory figure was not checked. Arithmetic with the
track's inputs, my cosmic-time spans and my operation counts (card-hours per realisation,
MeshBlocks 128^3 / 64^3 / 32^3): theta = 0.25: SR 0.43 / 0.49 / 0.69, USR 0.53 / 0.61 / 0.86;
theta = 0.025 (P2's value): SR 4.27 / 4.89 / 6.94, USR 5.31 / 6.08 / 8.63 (run
E-20261115-180348-d799c68; steps 1368, 1701 and 13675, 17010; 1.15 x 256^3/2e7 s for Z4c and
field plus the synthesis at 3e12 flop/s). So at theta = 0.25 the margin to the 5 card-hour
threshold of SCOPE 4.5 is real whatever the MeshBlock size, but at theta = 0.025 the USR
realisation exceeds it even with 128^3 MeshBlocks (SCOPE 8 gives 8-9 card-hours for both
cases together, i.e. 4-4.5 each). [JUDGEMENT from VERIFIED inputs]

### V8 Delta-N reference numbers behind A8 (SPEC 7.2) — CONFIRMED

Lattice sum over 1 <= |n| <= 64 divided by the continuum integral: 1.0805 for the SR spectrum
of my V2 run (claim 1.0805), 1.0731 for a flat spectrum. The 42-45 percent excess of a
sigma = 1 separate-universe Langevin solver has an analytic counterpart: a massless de Sitter
mode kicked in at k|tau| = sigma and evolved without gradients ends at
|1 + i sigma - sigma^2/3|^2 = 1 + sigma^2/3 + sigma^4/9 of the true power, 4/9 = 44.4 percent
at sigma = 1, 0.33 percent at 0.1, 3.3e-5 at 0.01 (numerical = closed form to 4e-15).
[VERIFIED, run E-20261115-174606-3c67607, `fig/fig_v8.png`]. The Langevin solver itself and
the 1e6-realisation reference statistics were not rerun.

## The three weakest points of the plan

1. **The cost margin and the time step are coupled and untested.** The recommendation rests on
   "one 256^3 realisation 0.4-0.5 card-hours, ten times below the downgrade threshold"
   (SCOPE 9.3). That holds at theta = 0.25 with 128^3 MeshBlocks. Theta = 0.25 is chosen
   because A6 has not run yet (no run with kicks and physical modes exists). P2 used 0.025. At
   that value the step count of SCOPE is also 4-5 percent low, and one realisation costs 4.3
   (SR) and 5.3 (USR) card-hours with 128^3 MeshBlocks, 6.9 and 8.6 with 32^3 (V7). The USR
   case would then cross the downgrade threshold of SCOPE 4.5. The first card run should measure
   the time per step at 256^3 with the field and noise for two MeshBlock sizes. A6 should come
   before any G2 cost statement.
2. **G1 depends on pieces that do not exist in the release.** The pgen of core-v0.3 offers only
   `wave`, `flrw` and `plane` (scalar_field_tests.cpp:74-80). The coarse-grained initial slice
   at N* (SPEC 5.3, with the delta Pi erratum of V3) is missing, and so are the R^NR and [H], [M]
   outputs. No run has carried physical mode functions through the kicks to R^NR, so A2 (the
   amplitude W R alpha of the kicked field) is untested. V5 and V6 cover the algebra, the signs,
   the first-order constraint preservation and the reproducibility; they do not cover the
   amplitude. A homogeneous start before N* would avoid the slice but would not be P1's set-up.
   That difference must be stated if it is used.
3. **The USR case ends at the border of diffusion domination.** At N_f the classical drift per
   e-fold equals the quantum step H/2pi (ratio 0.98 at N*+8.3), Delta_R reaches 1 at 64 dk, and
   one H/2pi kick moves the end of USR by about one e-fold. A delta-N surface placed at N*+10
   lies just past the stationary inflection point, and kicked paths stall there (my first V2b
   trial). In the N = 256 box all noise has entered by N*+4.2, and my delta-N proxy finds the
   response near-linear (f_NL = 0.011), so A3-USR at G2 survives (V2b). The plan, however,
   carries the same linear-noise, level-0 set-up into G3 tail statistics. Any larger box or later
   noise cut feeds noise computed from a classical background into a diffusion-dominated phase.
   The delta-N reference's end surface also needs care near the inflection point. G2 should state
   the validity window explicitly.

## Addendum to V7, written after reading the track's review: calibration with core's card measurement

The stage report (C4) cites a card measurement by core that I had not seen: run
core-20261115-143907-cea4c86 (`scratch/core/.../summary.json`: one A100, 128^3, 64^3
MeshBlocks, nmax2 = 1024: Z4c 1.983e7, with the field 1.389e7, with field and sources 1.204e7
zone-cycles/s). Calibrating my operation count with it gives an effective synthesis rate of
1.3e12 flop/s (the track assumed 3e12) and, per 256^3 realisation (MeshBlocks 128^3 / 64^3 /
32^3): theta = 0.25: SR 0.60 / 0.74 / 1.21, USR 0.74 / 0.92 / 1.51 card-hours; theta = 0.025:
SR 5.99 / 7.41 / 12.13, USR 7.45 / 9.21 / 15.09. [run E-20261115-180445-e72dad6; extrapolation
from 128^3 assumes the same per-cell cost at 256^3, JUDGEMENT] At theta = 0.25 the margin to
the downgrade threshold holds for every MeshBlock size; at theta = 0.025 both cases exceed it
for every MeshBlock size.

## Comparison with the track's own review

Read only after the verdicts and the three weak points above were committed (commit d799c68):
`EVIDENCE.md` (the lead's verification), `OPEN.md`, `CHECKLIST.md`, `STAGE_REPORT.md`,
`VERIFY_RESULTS.md`, `../G1/STATUS.md`, `../../RISKS.md`, `../../note/scripts/costmodel.py`.
No `REVIEW.md` exists; the lead's review is EVIDENCE section 2-3.

Agreements (same conclusion by a different route):
- V1: the lead's own integrator and mine agree with SPEC 6 to the printed digits. One small
  difference: the lead reports USR eps1(N*) = 1.31625e-2 and H* = 9.362350e-6. SPEC has
  1.3164e-2 and 9.36232e-6, and I get 1.316389e-2 and 9.362319e-6. My integrator supports the
  helper's numbers; the lead's are off by 1.1e-4 and 3e-6 relative, perhaps from a different
  N* convention. This is irrelevant for the plan.
- V2: the lead checked one SR mode and one USR mode (deformed/full 2.08 at the mode leaving at
  N*+0.7, k = 2 dk); I get 2.069 at k = 2 dk and cover twelve shells per case. Same SR slopes.
- V3, V4: the lead re-derived both errata by hand. I add an independent symbolic check, a
  numerical draw test and the size of the printed form's violation (1.1e-3 of [H] at
  crossing).
- V8: the lead's rerun with 1e5 realisations gives a variance ratio of 1.4433 +- 0.0067 at
  sigma = 1. My analytic de Sitter value is 13/9 = 1.4444, and the lattice factor 1.0805 is
  identical.
- The track's T1-T4 reproduce bit for bit in my rerun as in the lead's (E-20261115-135531-0c4e629).

Differences (what my verification adds or contradicts):
1. **Courant factor and cost are coupled (V7; my weak point 1).** OPEN item 7 says the
   recommendation "does not hinge" on the measured cost because the threshold is ten times
   above the estimate. C4 recomputes with core's measurement (0.57-0.71 SR, 0.71-0.88 USR) and
   keeps the conclusion. That is right at theta = 0.25 only. The track's range covers 64^3-128^3
   MeshBlocks and theta = 0.25. It does not state that at P2's theta = 0.025, which R13 keeps
   as the fallback if L6 shows a dependence, the calibrated cost is 6.0-15 card-hours per
   realisation, above the 5 card-hour threshold of SCOPE 4.5. If L6 forces theta = 0.025, the
   track meets its own downgrade criterion. The track's estimate also does not account for
   the 4-5 percent longer cosmic time from N* to N_f (my figures are about 5 percent above
   C4's for the same MeshBlocks), or for the larger synthesis cost of MeshBlocks smaller than
   64^3.
2. **The MS model with kicks has now run (V6).** The lead's L-U runs tested the power model on
   836ac86, and SCOPE 6 and R2 note that the kicks had never run. My V6 runs core's MS deck on
   the release: bit identity across layouts and restart holds with kicks and coupling on, and
   the Pi-sign negative control raises the constraints by 3e2-5e4. That is first evidence on
   R2's "kick signs". It is not the planned single-kick test L5, and it does not test the
   amplitude (A2).
3. **The release differs from what SCOPE 6 read.** SCOPE 6 and EVIDENCE 3 cite 836ac86; the
   release core-v0.3 contains the cancellation-free window increment (cpp:572-577) that OPEN
   item 9 asks for. I did not rerun the Markov-tanh A1 test; other helpers' runs on v0.3 were
   in progress.
4. **USR near the diffusion-dominated border (my weak point 3) is not in RISKS.** R6
   (geodesic slicing, outliers R ~ 10) and R11 (formalism debated) are near, but neither
   names three findings. The background reaches drift/diffusion of about 1 at N_f. A delta-N
   end surface at N*+10 sits just past the stationary inflection point, where kicked paths
   stall. The linear-noise, level-0 set-up of G3 would be fed into that regime by any larger
   box. My V2b also gives the track a positive result that is not in its documents: the per-mode
   USR test A3 is not spoiled by delta-N nonlinearity (f_NL = 0.011, response linear to a few
   percent up to 6 H/2pi kicks).
5. **The G1 dependency (my weak point 2) agrees with R1 and G1/STATUS.** I confirm in the
   release source that the pgen has only `wave`, `flrw` and `plane`
   (scalar_field_tests.cpp:74-80).
6. Not covered by me but checked by the lead: the Langevin benchmarks (<N>, var N), the noise
   validator's self-test and U1-U8, codebase D1-D4 and memory, and the processor throughput.
   Not covered by either: the unit mapping of SPEC 2.5 and the extraction factors E6 (hand
   derivations, OPEN item 8), the end-of-inflation delta-N statistics, the importance sampling.
7. Naming: CHECKLIST C18 and STAGE_REPORT look for `VERIFIER_REPORT.md`, but this package was
   asked to write `VERIFIER.md`. The stage check will report the verifier as missing until the
   lead links or renames it.
