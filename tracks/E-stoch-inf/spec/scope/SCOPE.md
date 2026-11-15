# Scope of the feasibility gate of Track E (S11)

Owner E-stoch-inf; written by the E-pre-1 helper on 2026-11-15 as input to the G0 stage
package. Sources: brief lines 445-465 (S11), 785-802 (track sheet), 544-547 (M11), 834-860
(verification row "Slow-roll and USR cases of stochastic inflation"); `coord/CHARTER.md`
sections 9.8 and "What differs"; decisions 0004, 0006, 0010; `../SPEC.md`. Labels as in the
brief.

## 1. Problem statement

The science question of S11: once quantum fluctuations enter the full Einstein-scalar
equations as stochastic sources, how far do the statistics of large perturbations differ from
stochastic delta-N, and what do gradients, shear and the constraints do during ultra-slow roll
(brief 447). The feasibility gate asks something narrower, which this track can answer before
any science run:

> Can this repository's AthenaK, extended by core with a minimally coupled scalar field and the
> Langevin sources of Launay, Rigopoulos and Shellard (arXiv:2401.08530, 2512.14649), reproduce
> the slow-roll and USR test cases of arXiv:2512.14649, accepted against the freezing criterion
> derived from arXiv:2606.14853, at a cost per realisation that the program can afford?

What is in scope for G0: the reproduction specification (`../SPEC.md`), the linear reference
solutions that the acceptance tests need (`../ref/`, runs listed in `../README.md`), the code
base (settled: AthenaK, decisions 0004 and 0010), the compute estimate (`../SPEC.md` 11.2), and
the requests to core. Out of scope until G1 or later: statistics of the compaction function
(deliverable 2 of S11), the field-to-particle hand-over (3), eternal inflation (4), the
stochastic delta-N and lattice comparisons of E-pre-3, the random-number interface work of
E-pre-4 beyond what SPEC section 5.4 states.

## 2. Exit criteria

### G0 (feasibility gate; brief 798)

G0 is passed when all of the following hold and the group has decided to continue, shrink or
downgrade:

1. Reproduction specification complete, every number with a locator: `../SPEC.md` (this
   package). Done, with the unstated items (SPEC section 8) and errata (section 9) listed.
2. Code base decided: AthenaK of this repository (decision 0010; decision 0004 settled).
3. Compute estimate: SPEC 11.2 (0.4 to 0.5 card-hours per 256^3 realisation at Courant factor
   0.25, about 4 to 5 at 0.025) against the allotment of 10 card-hours (decision 0006).
   [JUDGEMENT: the throughput is measured for Z4c alone; the overhead of the scalar and the
   FFTs is assumed, not measured.]
4. Core has accepted the requests of SPEC section 10 (scalar field, stochastic sources at
   stage times, GPU FFT, initial data, diagnostics) with a date, since Track E's G1 cannot be
   reached without them (unlike the G1 "baseline without new core work" of the other tracks).

### G1 (track sheet, brief 798, made concrete in SPEC 7.2 and 7.3) [JUDGEMENT on the numbers]

- Slow roll: the background (A1, box means to 1e-4), the per-mode linear check (A2, within 2
  percent for k <= k_max/2), the freezing criterion (SPEC 7.3: power ratio between N_k + 4 and
  N_f equal to the full-MS value within 1 percent for k <~ 7 dk), and constraint convergence
  (A4, A5).
- Recommended in addition: temporal convergence (A6) and reproducibility across layouts (A7).

### G2 (brief 798)

The USR case reproduced (SPEC 7.3: k <= 3 dk within 10 percent of the full MS; P-e, P-h of SPEC
7.1), and the sensitivity to the window parameters (s, sigma) and to the resolution.

### Downgrade trigger (brief 462)

If by G1 the slow-roll or the USR reproduction fails the freezing criterion, or one realisation
costs more than the budget allows, Track E becomes a supplier of initial-condition statistics to
Track A from a non-NR stochastic delta-N solver. Proposed threshold for "more than the budget
allows" [JUDGEMENT]: one 256^3 realisation above 5 card-hours, half the allotment.

## 3. Risks

| Id | Risk | Likelihood, impact | Mitigation |
|---|---|---|---|
| R1 | The scalar field, the sources, the FFT and stage-time sources do not exist in AthenaK; Track E's G1 waits for core | certain dependence; high impact on the schedule | requests in SPEC 10 and README; decision 0010 puts the work in core's current wave; this track supplies the reference tables and tests |
| R2 | AthenaK has no FFT; the noise needs one inverse transform per source component and stage | high, medium | single-card cuFFT or Kokkos-FFT for 256^3; distributed FFT only for larger boxes |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping, binning and tolerances open (SPEC 8), and print several wrong formulas (SPEC 9: delta Pi of the initial data, draw normalisation, extraction factors, 4 pi in the K equation) | certain, medium | reference computations T1-T4 fix the background, the normalisation and the initial data; per-mode check A2 needs no published tolerance |
| R4 | AthenaK's integrator (low-storage RK4()4[2S]) and its use of the step-start time in the right-hand side differ from ISTORIz's classical RK4 | certain, low to medium | sources evaluated at the stage abscissae (request to core); temporal convergence test A6 |
| R5 | Unit conversion (G = 1 in AthenaK vs Mpl = 100 in the papers) | medium, high if wrong | conversion in SPEC 2.5; background test A1 against the reference catches a wrong factor |
| R6 | The geodesic gauge breaks down where perturbations collapse; USR outliers reach R ~ 10 (P1:534) | low for the test cases (P2:770), high for later science | stop at the published N_f; a gauge study belongs to G2 |
| R7 | The momentum constraint grows to ~ 1e-2 late in USR (P1:541) and fails at domain walls in other models (P2:756) | medium, medium | accept the published level for the reproduction; resolution study at G2 |
| R8 | Results depend on the window (s, sigma) and on the gauge (brief 462); sigma = 1 sits at horizon crossing, where classicality is argued only by the quantum-interactivity analysis of the thesis (TH chap_QCl:337-370, 445-447) | medium, medium | reproduction with the published s = 5, sigma = 1; sensitivity at G2 |
| R9 | Tail statistics need many realisations: at 0.4 to 5 card-hours each, 10^3 realisations at 256^3 cost 400 to 5000 card-hours [arithmetic on SPEC 11.2] | high for G3, none for G0 | smaller boxes, importance sampling, or the downgrade path |
| R10 | Competition with the authors of the formalism and code (Launay et al.), who announce the same science (P1:587) | high, medium | target what they leave open (tail statistics, hand-over to EMD, comparison with E-pre-3); novelty search before G1 |
| R11 | The stochastic formalism itself is debated (noise non-Gaussianity, separate-universe validity at sudden transitions; brief 264) | medium, affects the science, not the reproduction | keep level-0 and level-2 backreaction as variants; report the dependence |
| R12 | Reproducibility: FFT results depend on the domain decomposition at round-off level | medium, low | A7 accepts FFT round-off; the white noise itself comes from the counter-based generator of core/rng |
| R13 | Budget: 10 card-hours to the next gate (decision 0006) | medium, medium | Courant factor near 0.25 (allowed: one mode per step needs theta < 0.64, P1:727); processor runs for the ladder at N <= 64 |
