# Writing guide: working note of Track B (S2, gravitational waves from early-matter-era structure)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with the note v0 (gate G0), by the note helper of wave 2.

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
| Section | the steps of the argument | Introduction; What radiates (the problem); The calculation (set-up and methods); Tests so far; Plan and open questions; Summary; appendices: parameters, ledger |
| Subsection of the problem | what fixes the signal | symmetry (the plane-symmetric null); the first source and its second-order strain; the radiation band and the relativistic depth |
| Subsection of the calculation | the parts of the calculation, methods last | the expanding periodic box; gravitational-wave diagnostics; numerical methods |
| Subsection of the tests | one test per subsection, in the order of the calculation | linear waves in the box; diagnostics on code output; the pancake through shell crossing; the background; the Newtonian baseline |

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
- Labels: gates G0-G4; checks T1-T8 of the baseline; risks R1-R9; the modes (k, k, 0).
- Parameter values that define the figures: delta = 0.05 and boxes of one and four initial
  Hubble radii (pancake); 32, 64, 96 cells; delta = 0.01, box of four initial Hubble radii,
  ratios (1, eps, 0) (first source); amplitude 10^-6 and 32 cells (wave dumps); boxes of two,
  four, eight initial Hubble radii (radiation band).
- Everything else (errors, orders, residuals, crossing times, costs) is in the ledger.

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

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`gw_diag`, `gwdiag`, `periodic_z4c`, `verify_cosmo`, `first_source`, `make_east`,
`nrpic_cosmo`, `z4c_linear_wave`, `athinput`, `pm.py`, `nrpic-run`, script names, run
directory names, the cluster and its hardware. Checker call from `note/`:
`--forbid 'gw_diag|gwdiag|periodic_z4c|verify_cosmo|first_source|make_east|nrpic_cosmo|z4c_linear_wave|athinput|pm\.py|nrpic-run|anta|A100|Slurm'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| source | the strain of the crossed waves is linear in the second-wave ratio with the closed-form coefficient; the box of four Hubble radii puts the radiation band at the box modes | delta = 0.01, box 4; boxes 2, 4, 8 |
| architecture | which parts of the calculation exist, which are carried over, which are new | none |
| waves | the box propagates an exact wave with the errors its stencils predict; both diagnostics recover the wave from code output | amplitude 10^-6; 32 cells |
| pancake | the relativistic departure from Newtonian gravity is converged and scales as (H/k)^2; two particles per cell and direction remove most of the constraint violation before crossing | delta = 0.05; boxes 1 and 4 |
| baseline | the Zel'dovich ellipsoid gives the 7/2 power law at small amplitude and departs from it at large amplitude | none |
| timeline | the five gates, what each needs and where the track stands | none |
