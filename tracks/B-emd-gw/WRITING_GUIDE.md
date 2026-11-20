# Writing guide: working note of Track B (S2, gravitational waves from early-matter-era structure)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with the note v0 (gate G0), by the note helper of wave 2;
additions for v1 (note README Requests 1-2) and v2 (criterion 1, second round) made on
2026-11-20 by the note helper of wave 3, round 1.

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is an internal
  working paper of the program and grows into the track's paper at gate G4.
- Where the methods go: the note is a scoping and verification record, so the set-up and
  the methods are in the main text; scenario parameters go to an appendix table; every
  number goes to the ledger appendix.
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix (the Supplemental Material of the note) lists every number with the id of the
   registered run that produced it, and the source locator (file and line) of every number
   taken from a paper. Run ids, locators and file names appear in the ledger appendix and
   nowhere else; the main text and the captions follow 4.1 and 5.5. The scripts that build
   the ledger and the figures (`scripts/ledger.py`, the run table of `scripts/common.py`, the
   docstrings and input paths of `scripts/fig_*.py` and `scripts/schem_*.py`) name the
   track's documents, runs and files they read; the checker's 5.5 and 5.8 hits there and in
   the ledger appendix are accepted under this exception.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]) stay
   out of the typeset text; the main text says in words what is established, what is our
   choice and what is open. The labels live in the journals and in `stage/G0/`.

When the note becomes the track's paper (G4), the ledger moves to the Supplemental Material
and the run ids to the reproduction package.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | why an early matter era makes structure early; the Zel'dovich pancake and shell crossing; why particles continue where a dust fluid stops |
| Cosmologists of stochastic backgrounds | the 3+1 split, slicing (lapse) and shift; the transverse-traceless (TT) part of a metric perturbation and why it is gauge dependent at second order; what the Weyl scalar measures |
| Collisionless-dynamics and N-body readers | why plane symmetry forbids radiation; what "relativistic correction" means in a box comparable to the Hubble radius |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; What radiates (the problem); The calculation (set-up and methods); Tests so far; The first source in full relativity; Plan and open questions; Summary; appendices: parameters, ledger |
| Subsection of the problem | what fixes the signal | symmetry (the plane-symmetric null); the first source and its second-order strain; the radiation band and the relativistic depth |
| Subsection of the calculation | the parts of the calculation, methods last | the expanding periodic box; gravitational-wave diagnostics; numerical methods |
| Subsection of the tests | one test per subsection, in the order of the calculation | linear waves in the box (axis-aligned wave, oblique flat wave, standing wave of the expanding box; both diagnostics); diagnostics on code output; the pancake through shell crossing; the background; the Newtonian baseline; the Newtonian mode of the code; independent rechecks |
| Subsection of the first source (Sec. V) | aspects of the strain | against the second-order formula (with the widened window of the smaller amplitude); its spatial gauge; through shell crossing; the noise floor of a jittered particle lattice |

Note v2 (2026-11-20): Sec. IV A carries G1 criterion 1 (the oblique flat wave and the standing
wave of the expanding box, each read with both diagnostics against an exact solution and a
prediction written before the runs); Sec. V A the amplitude scaling of the departure from second
order (delta = 0.0025 against 0.01) and Sec. V D the jittered-lattice null and the run-to-run
floor of the card. Results being analysed in parallel (particle-number and mesh legs, 32^3
companions, the amplitude x10 rounding check of the expanding box) are named as pending in one
sentence each, without numbers.

Special cases entered as limits (2.2): the plane-symmetric pancake is the zero member of the
crossed-wave family; the Newtonian solution is the weak-field limit of the pancake (the
departure scales as (H/k)^2); the vacuum box is the zero-matter limit of the expanding box.

Story (Sec. 10, steps 1-3 done in the journal of the note package; step 4, reviewer
subagents, not run in v0): the question (how much radiation, when does Newtonian gravity
fail) -> turning point 1, the plane-symmetric pancake radiates nothing, so the first source
is a family with a built-in null and a second-order closed form -> turning point 2, the code
and the diagnostics reproduce an exact wave at the orders of their stencils -> turning point
3, the full-relativity pancake runs through shell crossing; its departure from Newtonian
gravity is converged and scales with (H/k)^2, and its constraint violation is lattice
sampling -> what is open (the gauge piece of the projection, the noise floor, the scan).

## Allowed numbers (4.1)

- Exact analytic factors and powers: 5/12, 5/6, 7/2, 3/2, 1/3, 2/3, 1/a, (H/k)^2, a^(-3/2),
  t^(2/3), 8/15, 1/(64 pi G), the factor 16 between the (H/k)^2 of the two pancake boxes.
- Structural integers: two diagnostics, two polarizations, three convergence legs (particle
  number, cell size, slicing), five gates, two particles per cell and direction (eight per
  cell), four boxes of the planned scan.
- Exact factors of note v1 and v2: a = 1 + 1/delta (Zel'dovich first crossing),
  (k Delta x)^2/12 (force excess of the seven-point stencil), 1 + eps^2 (amplitude dependence of
  the next order), (delta a)^2 (relative size of the next order), the factor 16 = (0.01/0.0025)^2
  between the two amplitudes of the first source, 3/5 (late potential of a mode without
  peculiar velocity), the slopes -2 and -1 of `fig_newton`, the orders four and six of the
  stencils and the time integrator (as words: "fourth order", "sixth order").
- Structural words and integers: "seven-point" (stencil), two diagnostics, two polarizations,
  two spatial gauges, two jitter amplitudes, four resolutions.
- Labels: gates G0-G4; checks T1-T8 of the baseline; risks R1-R9; the modes (k, k, 0) and
  (k, -k, 0); the wave directions (1, 1, 1) (flat oblique wave) and (1, 1, 0) (expanding box).
- Parameter values that define the figures: delta = 0.05 and boxes of one and four initial
  Hubble radii (pancake); 32, 64, 96 cells; delta = 0.01 and 0.0025, box of four initial Hubble
  radii, ratios (1, eps, 0) with eps = 0, 0.1, 0.3, 1 (first source); meshes 64^3 and 32^3; eight
  particles per cell (two per direction); jitter of 0.3 and 0.1 cells (null); amplitude 10^-6
  and 32 cells (wave dumps); N = 16, 32, 48, 64 (oblique and expanding-box waves); box side four
  initial Hubble radii (expanding-box wave); N = 16, 32, 64 (Newtonian pancake) and 32, 64, 128
  (ellipsoid); boxes of two, four, eight initial Hubble radii (radiation band).
- Everything else (errors, orders, residuals, crossing times, costs, ratios of measured to
  predicted, windows in the scale factor) is in the ledger.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| early matter-dominated era (early matter era) | EMD (in the text) | cosmology |
| collisionless matter, particles | dust (unless the pressureless fluid is meant) | kinetic theory |
| shell crossing | orbit crossing, caustic (except for the density caustic itself) | cosmology |
| transverse-traceless (TT) part | TT mode, tensor part (when the projection is meant) | gravitational waves |
| flat (Fourier) TT projection | Lambda projection, gw_diag | this note |
| York TT part | covariant TT projection (when the decomposition on the curved slice is meant) | numerical relativity |
| conformal-time slicing | conformal lapse, production lapse | numerical relativity |
| initial Hubble radius | Hubble length (as a box unit) | cosmology |
| crossed waves | first source (in the text) | this note |
| particle-mesh reference | pm.py | this note |
| registered run | job | this program |
| Numerical methods | pipeline, harness | any |
| oblique wave | (1,1,1) run, test F | this note |
| standing tensor mode of the expanding box | test X, expanding wave | this note |
| Weyl diagnostic | Weyl-6, FD6 Weyl, Psi4x | this note |
| low-storage fourth-order Runge-Kutta scheme of the code | RK4()4[2S], 2S, rk4 | numerical methods |
| jittered lattice | jitter run, jit0p3 | this note |
| run-to-run floor | reproducibility check, e1_rep | this note |
| departure from second order | dev | this note |
| plus and cross polarizations | + pol., x pol. | gravitational waves |

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`gw_diag`, `gwdiag`, `periodic_z4c`, `verify_cosmo`, `first_source`, `make_east`,
`nrpic_cosmo`, `z4c_linear_wave`, `athinput`, `pm.py`, `nrpic-run`, `newton_tests`, `fslib`,
`wlib`, `make_waves`, `requests-b`, `conv_compare`, `predict_2s`, script names, run directory
names, the cluster and its hardware. Checker call from `note/` (v2):
`--forbid 'gw_diag|gwdiag|periodic_z4c|verify_cosmo|first_source|make_east|nrpic_cosmo|z4c_linear_wave|athinput|pm\.py|nrpic-run|anta|A100|Slurm|newton_tests|fslib|wlib|make_waves|requests-b|conv_compare|predict_2s'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| source | the strain of the crossed waves is linear in the second-wave ratio with the closed-form coefficient; the box of four Hubble radii puts the radiation band at the box modes | delta = 0.01, box 4; boxes 2, 4, 8 |
| architecture | which parts of the calculation exist, which are carried over, which are new | none |
| waves (v2: four panels) | (a, b) the axis-aligned wave: errors as the stencils predict, both diagnostics recover it; (c) oblique flat wave: both diagnostics carry the predicted evolution error, and differ from each other by the stencil error of the Weyl evaluation only; (d) standing mode of the expanding box: the errors are those of the code's time integrator, the cross polarization on the prediction at every N | amplitude 10^-6; 32 cells; N = 16-64; directions (1,1,1), (1,1,0); box four |
| dataflow | from initial data through the code to the note, every arrow a registered run | none |
| pancake | the relativistic departure from Newtonian gravity is converged and scales as (H/k)^2; two particles per cell and direction remove most of the constraint violation before crossing | delta = 0.05; boxes 1 and 4 |
| baseline | the Zel'dovich ellipsoid gives the 7/2 power law at small amplitude and departs from it at large amplitude | none |
| scan | the strain follows s g over the first decade of expansion; the null stays at rounding; two meshes agree | delta = 0.01; eps = 0.1, 0.3, 1; 64^3, 32^3 |
| gauge | the computed spatial-gauge piece reconciles two gauges; the magnetic Weyl part agrees where the strain does not | eps = 1; 64^3 |
| newton | the error of the Newtonian mode is the stencil's force excess; the crossing time converges at second order | N = 16, 32, 64; 32, 64, 128 |
| r2 (v2) | (a) the jittered lattice puts into the box modes the strain the second-order formula predicts from its noise potential, a few hundredths of the smallest signal; (b, c) the departure from second order shrinks with the amplitude and collapses when plotted against a delta: it is the next order | delta = 0.01, 0.0025; eps = 0.3, 1; jitter 0.3, 0.1 cells; 64^3; eight per cell |
| timeline | the five gates, what each needs and where the track stands | none |
