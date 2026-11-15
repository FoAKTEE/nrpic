# Writing guide: working note of Track E (S11, stochastic inflation in numerical relativity)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with the note v0 (gate G0, feasibility).

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is an internal
  working paper of the program; it grows into the track's paper at gate G4.
- Where the methods go: the note is a specification and feasibility record, so the set-up and
  the methods are in the main text; parameters go to an appendix table; every number goes to
  the ledger appendix.
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix (the Supplemental Material of the note) lists the numbers with the id of the
   registered run that produced them; paper locators (file and line) of the source papers
   stay in the track's specification (`spec/SPEC.md`, `spec/scope/SCOPE.md`), which the
   ledger names. Run ids appear in the ledger appendix and nowhere else; the main text and
   the captions follow 4.1 and 5.5. The scripts that build the ledger
   (`scripts/ledger.py`, `scripts/common.py`, `scripts/costmodel.py`) name the track's
   documents and runs they check; the checker's 5.5 and 5.8 hits there and in the ledger
   appendix are accepted under this exception.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]) stay
   out of the typeset text; the main text says in words what is established (by a run or at
   the source), what is our choice, and what is open. The labels live in the journals, the
   README and the claims table `note/tables/claims.md`.

When the note becomes the track's paper (G4), the ledger moves to the Supplemental Material
and the run ids to the reproduction package.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | slow-roll parameters, horizon crossing, the comoving curvature perturbation and its freezing; the separate-universe picture and stochastic delta N |
| Early-universe cosmologists | the 3+1 split, geodesic slicing, BSSN/Z4c, Hamiltonian and momentum constraints, Courant factor, MeshBlocks |
| Statisticians of the noise | Fourier convention, coarse-graining window, Markov versus frozen draws, counter-based random numbers |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; The problem and the test cases; Set-up and numerical methods; Reference solutions and tests; Cost and the decision at the gate; What is open; Summary; appendices: parameters, errata, ledger |
| Subsection of the problem | what fixes the answer | stochastic sources; the two test cases; acceptance criteria |
| Subsection of the set-up | the parts of the calculation | the code; the noise; the initial slice; numerical methods (last) |
| Subsection of the tests | one test per subsection | freezing reference; delta-N reference; reproducible noise; errata of the sources |

Special cases entered as limits (2.2): the separate-universe Langevin system enters as the
limit of the NR calculation without gradients and shear; FLRW lattices enter as the limit
without metric perturbations (the deformed Mukhanov-Sasaki equation).

## Allowed numbers (4.1)

- Exact analytic factors and powers: 2 pi, 8 pi^2, k^3/(2 pi^2), -4 eps1 (the decay rate of
  the deformed equation), e^(-2 dN), H^4, 3 - eps2 (friction), ln(N/4).
- Structural integers: two test cases, three noise schemes, five gates, three levels of
  backreaction (0, 1, 2), four RK stages, six kick components, sixth-order stencils.
- Labels: gates G0-G4; acceptance criteria A1-A8; noise tests A0-A15; ladder tests L0-L9;
  levels 0-2 of the stochastic backreaction.
- Parameter values that define the figures and the cases: N = 256, k_max = 64 dk, sigma = 1,
  s = 5, Courant factor 0.25, sigma = 0.01, 0.1, 1 of the delta-N references, the e-fold
  counts N* - N0 = 5, 3 and N_f - N* = 8, 10, N_e = N* + 15, the threshold eps2 = 3 of USR.
- Everything else (residuals, ratios, costs, slopes) is in the ledger appendix.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| ultra-slow roll (USR) | USR phase, constant-roll (unless meant) | inflation |
| comoving curvature perturbation R | zeta (different gauge), curvature (alone) | cosmology |
| freezing of super-horizon modes | conservation (unless the identity is meant) | cosmology |
| coarse-graining window, window scale k_sigma = sigma a H | filter, cutoff | stochastic inflation |
| stochastic sources, kicks (in the code) | noise terms (in equations) | this note |
| Mukhanov-Sasaki equation, full; deformed equation | MS with/without gravity | 2606.14853 |
| separate-universe approximation, stochastic delta N | delta N formalism (without stochastic) | stochastic inflation |
| geodesic slicing | synchronous gauge (in the text) | numerical relativity |
| level 0, 1, 2 of the stochastic backreaction | Starobinsky approximation (except once, for orientation) | 2512.14649 |
| card-hours | GPU-hours (decision texts use both) | this program |

## Project names (5.8)

The note never names the track's intermediate products or harness: no helper package
names (spec, codebase, langevin, noise as directory names), no `nrpic-run`, no file names
outside the ledger. Search list for the checker:
`--forbid 'nrpic-run|nrpic-stage|SCOPE\.md|SPEC\.md|EVIDENCE|langevin/|codebase/|wt/|scratch/'`.
