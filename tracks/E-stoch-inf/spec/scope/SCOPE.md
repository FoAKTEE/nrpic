# Scope of Track E (S11) at the feasibility gate G0: owner's version 1

Owner E-stoch-inf. Version 0 was written by the E-pre-1 helper (commit 87ba18e); this
version is the lead's rewrite of 2026-11-15 for the G0 package: it fixes the open choices
(section 4), adds the parameter ranges, the verified reference statements, the test plan
by row of brief section 10, what core's implementation already shows, the compute estimate
and the recommendation to the group. Checklist of the gate: `../../stage/G0/CHECKLIST.md`;
artefacts and run ids: `../../stage/G0/EVIDENCE.md`; what the gate lacks:
`../../stage/G0/OPEN.md`. Labels: [VERIFIED] read at the locator or measured by a
registered run, [BACKGROUND], [JUDGEMENT], [TO VERIFY].

Locator keys (sources in `kb-data/raw/arxiv/<id>/<version>/src/`, all ingested by kb,
`kb-data/manifests/inventory.json`, record status ok): P1 = 2512.14649 v2 `PRD_v2.tex`;
P0 = 2401.08530 v2; P2 = 2502.06783 v3 `main_V2PRD.tex`; TH = 2610.32592 v1; BZ =
2606.14853 v2 `Manuscript.tex`; FKTT = 1308.4754 v2 (Fujita, Kawasaki, Tada, Takesako; the
key was "VS" before 2026-11-19, which named the wrong authors); JM = 2206.11234 v2; ST = 2405.10692 v2.

## 1. Problem statement

Science question of S11 (brief 447): once quantum fluctuations enter the full
Einstein-scalar equations as stochastic sources, how far do the statistics of large
perturbations differ from stochastic delta-N, and what do gradients, shear and the
constraints do during ultra-slow roll (USR)?

Feasibility question of this gate (brief 798): can this repository's AthenaK, extended by
core with a minimally coupled scalar field and the Langevin sources of Launay, Rigopoulos
and Shellard (P0, P1), reproduce the slow-roll (SR) and USR test cases of P1, accepted
against the freezing criterion derived from BZ, at a cost per realisation the program can
afford? Code base settled: this repository's AthenaK (decisions 0004, 0010); P1's
GRTeclyn/ISTORIz (P1:480-482) is neither used nor built.

In scope for G0-G2: the reproduction (S11 deliverable 1), stochastic delta-N reference
statistics for the same potentials (E-pre-3), reproducible noise (E-pre-4, brief M11).
Later: compaction-function statistics (deliverable 2, G3), field-to-particle hand-over (3),
eternal inflation (4).

## 2. Parameter ranges

| Quantity | SR (quadratic) | USR (Higgs inflection) | Locator |
|---|---|---|---|
| Potential | m^2 phi^2/2 | Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2)/(3 (3 phi^2 + 2 v^2)^2) | P1:405-409 |
| Printed parameters | eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl | Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl | P1:411-413 |
| Derived | phi0 = -14.0950 Mpl, m = 1.73494e-6 Mpl, eps1(N*) = 1.1107e-2, V(N*) = 2.690e-2 in Mpl = 100 units | dphi/dN(N0) = 0.102682, H0 = 9.5902e-6 Mpl, USR (eps2 > 3) from N* + 2.52 to N* + 6.55, eps1 min 9.7e-13 | two independent integrators: runs E-stoch-inf-20261115-122806-ef0d039 (helper) and E-20261115-135532-3f958a1 (lead) |
| N* - N0, N_f - N* | 5, 8 | 3, 10 | P1:419-420 ("~"); fixed here as integers, which reproduce P1 Fig. 1 |
| Lattice | N = 256, L k_sigma* = 2 pi, k_max = N k_sigma*/4 = 64 dk, a* = 1 | same | P1:509-519 |
| Window | tanh, s = 5, sigma = 1 | same | P1:503-506, 519 |
| Gauge | geodesic slicing alpha = 1, beta = 0; no damping, no AMR; periodic | same | P1:482-483 |
| Courant factor theta | 0.25 (section 4); temporal test at 0.125, 0.0625 | same | not in P1 (SPEC U1); P2 used 0.025 (P2:492); one mode per step needs theta < 0.64 (P1:727) |
| Steps at 256^3 | 1304 | 1630 | N_T = N sigma Delta N/(2 pi theta) (P1:721); `../../codebase/figs/cost.json` |
| Convergence ladder | N = 32, 64, 128 with k_max/dk = 8 | same | P1:747-773 |
| Sensitivity (G2) | s = 2.5, 5, 10; sigma = 0.5, 1, 2; theta; N | same | DESIGN_REVIEW 8.1 L9 [JUDGEMENT] |
| Delta-N reference | band dk-64 dk, end surface N* + 15, sigma <= 0.01, 1e6 realisations | same | `../../langevin/README.md`; runs E-stoch-inf-20261115-130139/-130137-176cdd6 |

## 3. Statements of the key references, verified at the source

| Statement | Locator | Checked by |
|---|---|---|
| S_R = R_k Wddot + [2 Rdot_k + (3 - eps2) H R_k] Wdot; S_Pi = Mpl sqrt(2 eps1) S_R | P1:297-310 | spec helper; lead (read) |
| S_K = -eps1 S_R, S_Kt_ij = a^2 eps1 (delta_ij/3 - k_i k_j/k^2) S_R; constraints carry no source | P1:370-375, 378-392 | spec helper |
| The two cases and their parameters; N* - N0 ~ 5, ~ 3; N_f - N* ~ 8, ~ 10 | P1:405-424 | spec helper; lead (read) |
| Geodesic slicing, AMR and constraint damping off, periodic; GRTeclyn core | P1:480-483 | lead (read) |
| Window with s = 5, sigma = 1; L k_sigma* = 2 pi; k_max = N k_sigma*/4; N = 256, a* = 1, Mpl = 100 | P1:503-519 | spec helper; lead (read) |
| Hamiltonian violation of second order (~1e-10 for noise ~1e-5); a flipped noise sign gives first order | P1:538-541 | spec helper; lead (read) |
| Step count and the bound theta < n sigma/(2 pi) | P1:714-730 | spec helper; lead (read) |
| Without metric perturbations R_k^2 ~ H^4 in SR, stronger in USR; deformed MS equation; eps << 1 is not sufficient | BZ:150-156, 177-212, 264-268 | spec helper; lead (read) |
| Geodesic-gauge initial data (P2:317-327, label eq:eqInitialConditions; not eq. 17, SPEC 5.3 note) and the dictionary delta Pi = d/dt delta phi - phidot Psi_G | P2:262-322 | spec helper (symbolic run); lead (derivation) |
| Courant 0.025; 256^3 "less than a few hours on 64 to 152 processors" | P2:492 | spec helper; lead (read) |
| Draw prefactors dk^(3/2) and (dk/sqrt(2 pi))^(3/2), mutually inconsistent | P2:876-884 | spec helper (run); lead (read) |
| Drift-diffusion moments and the first-passage formalism | FKTT:341-364 | langevin helper |
| Quadratic benchmark m = Mpl, phi_in = phi_UV = sqrt42, phi_end = sqrt2 | JM demonstration.tex 18-55 | langevin helper; lead (own quadrature) |

Errata (details in `../SPEC.md` section 9 and the package READMEs):

| Erratum | Locator | Evidence |
|---|---|---|
| delta Pi of the initial data: the printed term -sqrt(2 eps1) H Mpl Psi_G vanishes in the geodesic gauge; the data need -sqrt(2 eps1) Mpl H Psi_B | P2:320 with 308, 262, 270, 490 | linear Hamiltonian residual 4 eps1^2 H^3 a^2 k^-2 Rdot with the printed form, 0 corrected (run E-stoch-inf-20261115-123146-82d2fd4, rerun identical in E-20261115-135531-0c4e629); lead's re-derivation from P2's dictionary (owner JOURNAL, L-I) |
| Draw normalisation: L^(-3/2) is right; the printed prefactors give (2 pi)^3 and (2 pi)^(3/2) too much power | P2:876-884; TH appendix:487-491 | run E-stoch-inf-20261115-122934-9ac98d8 (rerun identical) |
| Importance-sampling weight sign | JM method.tex 78, 151 | run E-stoch-inf-20261115-125312-dafadc4 |
| v0/4 as the leading pole in general | JM appendix.tex 168-173 | run E-stoch-inf-20261115-125658-e3eaef3 |
| Friedmann denominator lacks 3 Mpl^2; the "very shallow maximum" is an exact stationary inflection point at -sqrt2 v | P1:108, 534 | lead (read); langevin helper |
| USR in the text from N ~ 3.5 to 8, about one e-fold later than P1's Fig. 1 | P1:534 | runs E-stoch-inf-20261115-122806-ef0d039 and E-20261115-135532-3f958a1 |

## 4. Exit criteria and the owner's decisions at G0 [JUDGEMENT, for the group to confirm]

Choices the helpers left to the owner, fixed here:

1. Courant factor theta = 0.25 for G1; test L6 at 0.125 and 0.0625 decides whether a
   smaller one is needed.
2. Backreaction level 0 (Friedmann background in the mode functions) for the first
   reproduction, level 1 (box means) as a variant. Level 2 of P1 is not implemented: a
   stated difference, bounded by P1's own ablation (at most about 1e-4 relative in the
   spectrum, P1:520, 777-790).
3. N* - N0 = 5 (SR) and 3 (USR), N_f - N* = 8 and 10; delta-N end surface at least 3
   e-folds after the last noise.
4. Acceptance thresholds (SPEC 7.2-7.3):
   - A1 background: box means of phi, Pi, K within 1e-4 relative of the Friedmann reference
     (SR), 1e-3 (USR, where delta Pi/Pi_b becomes large, P1:534-536).
   - A2 per mode (same alpha_k, no cosmic variance): |R^NR_k/(W_k R_k alpha_k) - 1| < 0.02
     for every lattice mode with k <= k_max/2 at N_f in SR; the reference uses the lattice's
     discrete wave number. [Amended by the owner on 2026-11-19, wording only: the reference
     mode function R_k is the continuum one of the code's mode equation at k = |n| dk, which
     is what the code injects through the window; the stencil-k^2 reference accumulates the
     sub-horizon dispersion error and fits worse (6.2e-3 against 1.2e-4 at 256^3, ladder
     JOURNAL entry 6). Both pass 0.02. The threshold is unchanged.]
   - A3 freezing: SR, for every mode with N_f - N_k >= 6, the per-mode power ratio between
     N_k + 4 and N_f equals the full-MS ratio within 1 percent (drift of ln Delta below
     2.5e-3 per e-fold, a twentieth of the FLRW lattice's -4 eps1); USR, modes k <= 3 dk
     within 10 percent of the full MS at N_f (the deformed equation is off by 1.4 to 8.4).
   - A4 constraints: H/[H] and M/[M] of second order during the entry (they scale with the
     square of the noise amplitude when it is halved); the sign-flip control is first order
     (P1:541).
   - A5 spatial convergence (N = 32, 64, 128, k_max/dk = 8): order between 4 and 6 before
     the floor.
   - A6 temporal convergence: order 4 +- 0.5 in theta.
   - A7 reproducibility: bit-identical across MeshBlock layouts and restart (NOISE_SPEC
     A11, A12); rank count when the field runs on several ranks.
   - A8 one-point statistics against the lattice sum and the sigma <= 0.01 delta-N
     reference only.
   Results against A1-A7 after wave 2 (SR, scouting runs with core's tested-branch
   executable `core/scalar-2` a58e95b, decision 0013): `../../ladder/README.md` and
   `../../stage/G1/`. A4 in the strict form above FAILS in the paper's set-up
   (k_max = N/4) at every N; A5 passes only with an operational "before the floor" chosen
   after the data were seen. Proposed rewordings are in section 4b; they are not in force.
5. Downgrade (brief 462): if by G1 the SR or USR reproduction fails A3, or one 256^3
   realisation costs more than 5 card-hours (half the allotment, decision 0006), the track
   becomes a supplier of delta-N statistics to Track A.

## 4b. Proposed amendments after wave 2 (not in force; proposed to orch 2026-11-19)

Formulated after the ladder's data were seen (ladder JOURNAL entries 9 and 11, core's
message scalar2-ready); they would change the owner's thresholds, which decision 0013
accepted, so they go to the orchestrator as a proposal (outbox 20261119) and A4/A5 above stay
as written until it rules.

- A4': split H and M_i into the parts odd and even in the noise amplitude s with a mirrored
  pair (s = +-1) and one halving of s. (a) The even part with its box mean removed scales by
  4.00 +- 0.05 when s is halved and agrees between the two finest resolutions within 5
  percent where it lies above the floor (P1's resolution-independent second-order plateau,
  P1:538-541). (b) The odd part is discretisation error: it scales by 2.00 +- 0.05 when s is
  halved and converges at the order of A5; it may exceed the even part once shells with
  fewer than eight cells per wavelength enter (from ln(N/8) e-folds after N* in the
  paper's set-up). (c) The record <|H|/[H]> stays within 10 x 1e-10 (P1:538-539) and
  <|M|/[M]> below 1e-3 ([M] is first order in s, P1:540-541, so <|M|/[M]> is first order).
  (d) The sign-flip control has an odd part at least 1e3 times that of the proper run. The
  record ratios are no order test (they hold the uniform residual H0 of the time
  integration, which does not depend on s).
- A5': "before the floor" = where the finer odd part exceeds three times the floor, the
  floor being the part that does not scale with s and grows with N (N^2.5 measured between
  128 and 256). Factor and floor model were fixed after the data were seen [JUDGEMENT].

Gates: G0 (brief 798) = specification, code-base assessment and compute estimate complete,
then the group's decision. G1 = SR spectrum (A2), freezing (A3), constraints converge (A4,
A5), with A1, A6, A7 recommended (`../../stage/G1/STATUS.md`). G2 = USR reproduced (A2, A3,
P-h of SPEC 7.1) and sensitivity (L9). G3 = tail statistics against E-pre-3 (A8).

## 5. Test plan by row of brief section 10

| Row (owner) | Test | Reference | Status 2026-11-15 |
|---|---|---|---|
| Slow-roll and USR cases (E): power spectrum | L3 linear modes, L7 SR ladder and 256^3; A2 | full-MS mode functions, run E-stoch-inf-20261115-122806-ef0d039 | reference ready; waits for core's initial slice |
| same: freezing | A3 on L7 (SR), L8 (USR) | full vs deformed MS (`../fig/fig_freezing.png`), independently confirmed (run E-20261115-135532-3f958a1) | reference ready |
| same: constraints | L5 single kick with negative control; A4, A5 | P1:538-541, 747-773 | waits for core's constraint diagnostics |
| same: background | L1 homogeneous FLRW; A1 | Friedmann reference (two integrators agree) | core's own test run; E's check pending |
| same: time integration | L6; A6 | D4 of run E-stoch-inf-20261115-123936-b2ec5c7 | waits for a run with kicks |
| same: one-point statistics (G3) | A8 | runs E-stoch-inf-20261115-130137/-130139-176cdd6 | reference ready |
| Reproducible random numbers (C, E) | U1-U9 with validator A0-A15 | `../../noise/ref/` | U1-U8 done on core's executable (section 6); U9 pending |

Test ids L0-L9: `../../codebase/DESIGN_REVIEW.md` 8.1; A1-A8: section 4 above; U, A0-A15:
`../../noise/NOISE_SPEC.md` 9-10.

## 6. What core's implementation already shows (`core/scalar-field` 836ac86)

[Record of 2026-11-15, kept as written. Since then: release core-v0.3 (the field merged,
the window increment formed without cancellation) and core's tested branch `core/scalar-2`
(initial slice at N*, constraint record, NRSFDMP2 dumps), which the slow-roll ladder used;
see section 8 and `../../ladder/README.md`.]

Read in the source (`athenak/src/scalar_field/scalar_field_noise.cpp`) [VERIFIED by
reading]: the kicks of SPEC 2.2 in the sign-safe form, d_t Pi += alpha_b (Pi_b/H) I_R,
d_t Khat += -alpha_b eps1 I_R, d_t At_ij += alpha_b eps1 (delta_ij I_R/3 - T_ij); the
projector from the stencil wave number of the centred first difference (default); window
derivatives equal to SPEC 3 term by term; the mode equation d2R/dtau2 + (3 - eps2) H dR/dtau
+ (k/a)^2 R = 0, which is the e-fold form of SPEC 2.3; eps2 = 6 + 2 V'/(H Pi_b) - 2 eps1 =
-d ln eps1/dN (both checked by hand); mode functions and background advanced with the
driver's own low-storage coefficients in every stage, so each stage evaluates its sources
at its own time (DESIGN_REVIEW request R5 met); amplitudes with the keys of NOISE_SPEC 4;
no FFT. Missing for G1: the initial slice at N* (SPEC 5.3; the problem generator offers
`wave`, `flrw`, `plane`), constraint ratios [H], [M] and R^NR output, a card build, the
interface document; level 2 (not needed for G1).

Core's own runs, read in `scratch/core/`, not yet reported by core [TO VERIFY by core's
report]: five existing set-ups byte-identical after the change (core-20261115-132758-ba37619);
homogeneous slow roll in conformal and geodesic gauge at Courant 0.5, 0.25, 0.125
(core-20261115-133955-836ac86).

The lead's runs with core's processor executable (`wt/core-scalar/.work/exe/athena_cpu_836ac86`,
sha256 65ff2162...00144, read only) [VERIFIED by run]: the noise unit test of
`../../noise/NOISE_SPEC.md` section 9 in a scaled base case (N = 32, nmax2 = 100, 120
cycles; the 64^3 x 300 case costs 95 min per run on the serial processor build, run
E-20261115-135218-bdf4710). Runs E-20261115-135523-a32c3a6 (U1-U8), validations
E-20261115-140502-2957846, diagnostic E-20261115-140553-0b75e1e:
- frozen tanh: every test passes; exact reconstruction from the keys to 4.1e-14 of the rms
  (A1), 1, 8 and 64 MeshBlocks bit-identical (A11), restart bit-identical (A12), N = 16
  against 32 to 2.4e-15 (A13), seeds independent (A15), spectrum, Gaussianity, correlation
  function, band limit (A2-A4, A10). This also confirms the dump convention (increment of
  the step ending at the dump cycle).
- Markov Heaviside: every test passes.
- Markov tanh: every test passes except A1 (1.07e-10 against 1e-11): sqrt(W(t) - W(t - dt))
  for modes long past crossing amplifies a one-ulp difference of W between libm and numpy;
  active modes agree to 4e-14 of their amplitude (`fig_lu_diag.png` of the diagnostic
  run). A numerical-hygiene request to core (cancellation-free increment); the
  Mukhanov-Sasaki model uses frozen amplitudes and closed-form window derivatives and is
  not affected.
Not yet exercised by any run: the Mukhanov-Sasaki model, the kicks, the coupling of the
field to Z4c under noise.

## 7. Risks

`../../RISKS.md` (R1-R14). Deciding for the gate: R1 (G1 waits for the initial slice and
the diagnostics), R2 (a hook defect the generator tests cannot see; L5, L6), R4 (freezing
failing for a reason other than a defect), R9 (cost of tail statistics at G3), R10
(competition with the authors of P1).

## 8. Compute estimate on this machine

Inputs [VERIFIED]: Z4c on one A100 at 2.0e7 zone-cycles/s, 128^3, nghost 4
(`docs/TESTLOG.md:46`); the processor build at 1.35e4-1.5e4 zone-cycles/s per core (runs
E-stoch-inf-20261115-122727-a1c2237, E-20261115-135218-bdf4710); A100 80 GB
(`harness/env/machines/anta.sh:17`). Assumed [JUDGEMENT]: field, Tmunu and kicks add 15
percent; synthesis at 3e12 flop/s on the card.

| Item | Card-hours | Note |
|---|---|---|
| SR 256^3, theta = 0.25, 1304 steps | 0.36-0.41 | 1.0-1.1 s per step, 20 GB |
| USR 256^3, theta = 0.25, 1630 steps | 0.45-0.51 | |
| Both at theta = 0.025 (P2's value) | 8-9 | only if L6 demands it |
| Ladder N = 32-128 and L9 at 128^3 | < 0.3 | |
| L0-L6 | minutes of card time | processor build serial and slow (R12) |
| **Total to G2 at theta = 0.25** | **about 1.5-2** | of 10 GPU-hours (decision 0006) |
| Each further 256^3 realisation (G3) | 0.4-0.5 | 1e3 realisations: 400-500 card-hours |

Checked by hand: 256^3 = 1.68e7 cells at 2e7 zone-cycles/s is 0.84 s per step, 0.97 s with
15 percent, plus 4-14 percent synthesis. 512^3 needs 157-204 GB and does not fit one card.

Measured since (wave 2, supersedes the assumptions above) [VERIFIED by run]: core measured
the field and sources at 128^3 (Z4c 1.98e7, with the field 1.39e7, with the sources 1.20e7
zone-cycles/s; run core-20261115-143907-cea4c86): the overhead is 65 percent, not 15. The SR
case at 256^3 in P1's set-up (548958 modes, 1386 steps to N* + 8.10, theta = 0.25, dumps and
the constraint record every step) ran in 1811 s on one A100: 1.30 s per step, 0.503
card-hours per realisation, peak memory 19.6 GB (ladder run E-20261115-172618-f948386; jobs
B and C 1.13-1.30 s per step). USR is not measured; scaled by the step count of the
verifier's cosmic-time span (1701 against 1368 steps, `../../stage/G0/VERIFIER.md` V7) it
would be about 0.63 card-hours [JUDGEMENT]. Theta = 0.25 is justified by A6 (time error of
R^NR below 3e-4 at theta = 0.25, order 3.93-4.08; runs E-20261119-142317-c851f27,
E-20261119-145230-ff0dff2), so the verifier's case theta = 0.025 (6-15 card-hours per
realisation, above the downgrade threshold) is not needed.

## 9. Recommendation to the group [JUDGEMENT]

**Continue** to G1 and G2 (reproduce the SR and USR cases of P1 in AthenaK) at the scope of
section 4, and decide the scope of G3 (tail statistics, S11 deliverable 2) at G2, once the
cost of one realisation has been measured on a card. Not shrink now, not downgrade.

Reasons:
1. The specification is complete and its numbers are reproduced independently (two
   integrators for the backgrounds and the freezing reference; the delta-Pi erratum
   re-derived from P2's own dictionary; the delta-N benchmark by a second method).
2. The implementation already exists in the code base the group chose: core's
   `core/scalar-field` (836ac86) has the field, the kicks in the specified form, the
   stencil-consistent projector, mode functions integrated in lockstep with the RK stages
   and the noise without a Fourier library; its generator passes the validation written
   before the code existed, bit-identical across MeshBlock layouts and restart (section 6).
3. Cost: about 1.5-2 card-hours to G2 at Courant 0.25 against 10 allotted; one 256^3
   realisation 0.4-0.5 card-hours, ten times below the downgrade threshold. [Updated
   2026-11-19: measured 0.50 card-hours for one SR realisation at 256^3 (run
   E-20261115-172618-f948386), ten times below the threshold; the ladder used 1.42
   card-hours in all.]
4. The downgrade path costs nothing extra: the delta-N solvers and reference statistics
   for both potentials exist now and can serve Track A whatever is decided.

Cost of continuing to G2: core's work package (initial slice at N*, constraint and output
diagnostics, card build, interface document; outbox 2026-11-15T14:10Z), Track E's analysis
of AthenaK output (R^NR, per-mode amplitudes, constraint ratios), about 2 card-hours.

Conditions under which the recommendation turns to shrink or downgrade: the freezing
criterion A3 fails in SR at level 0 and level 1 (downgrade, section 4 item 5); a measured
256^3 realisation above 5 card-hours (downgrade); at G2, 1e3 realisations (400-500
card-hours) beyond any allotment the group will grant (shrink G3 to smaller boxes or to
importance-sampled delta-N with a few NR realisations as a check).

The decision to continue, shrink or downgrade is the group's; this document stops here.

## 10. Stage timeline [JUDGEMENT]

| Gate | Content | Depends on | Indicative (charter 9.2) |
|---|---|---|---|
| G0 | this package; group decision | orch | week 2 (now) |
| G1 | SR case: A1-A7 at 256^3 and the ladder | core: initial slice, diagnostics, card build; E: R^NR analysis | week 8 |
| G2 | USR case; sensitivity L9; first cost measurements of many realisations | G1 | month 4 |
| G3 | tail statistics vs delta-N (A8); compaction function | G2 decision on scope | month 9 |
| G4 | paper | G3 | month 12 |
