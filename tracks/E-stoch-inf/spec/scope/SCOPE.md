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
2606.14853 v2 `Manuscript.tex`; VS = 1308.4754 v2; JM = 2206.11234 v2; ST = 2405.10692 v2.

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
| Geodesic-gauge initial data (eq. 17) and the dictionary delta Pi = d/dt delta phi - phidot Psi_G | P2:262-322 | spec helper (symbolic run); lead (derivation) |
| Courant 0.025; 256^3 "less than a few hours on 64 to 152 processors" | P2:492 | spec helper; lead (read) |
| Draw prefactors dk^(3/2) and (dk/sqrt(2 pi))^(3/2), mutually inconsistent | P2:876-884 | spec helper (run); lead (read) |
| Drift-diffusion moments and the first-passage formalism | VS:341-364 | langevin helper |
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
     discrete wave number.
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
5. Downgrade (brief 462): if by G1 the SR or USR reproduction fails A3, or one 256^3
   realisation costs more than 5 card-hours (half the allotment, decision 0006), the track
   becomes a supplier of delta-N statistics to Track A.

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
sha256 65ff2162...00144, read only): LU_RESULTS

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

## 9. Recommendation to the group

RECOMMENDATION

The decision to continue, shrink or downgrade is the group's; this document stops here.
