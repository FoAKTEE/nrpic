# Writing guide: working note of Track A (S1, primordial black holes in an early matter era)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with the note v0 (gate G0).

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is an
  internal working paper of the program and grows into the track's paper at gate G4.
- Where the methods go: the note is a scoping and verification record, so the set-up and the
  methods are in the main text; parameters go to an appendix table; every number goes to
  the ledger appendix.
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix (the Supplemental Material of the note) therefore lists every number with the
   id of the registered run that produced it, and the source locator (file and line) of
   every number taken from a paper. Run ids, locators and file names appear in the ledger
   appendix and nowhere else; the main text and the captions follow 4.1 and 5.5.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY])
   stay out of the typeset text; the main text states what is established, what is our
   choice, and what is open, in words. The labels live in the journals and the ledger.

When the note becomes the track's paper (G4), the ledger moves to the Supplemental Material
and the run ids to the reproduction package.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | why a pressureless matter era has no Jeans length; what the hoop conjecture and the Zel'dovich pancake say; what "threshold" means without pressure |
| Primordial-black-hole and early-universe cosmologists | the 3+1 split, slicing and lapse, apparent horizon, Hamiltonian and momentum constraints; why particles differ from a dust fluid after shell crossing |
| Collisionless-dynamics readers | the Lemaitre-Tolman-Bondi shells, trapped spheres, the Misner-Sharp mass |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; The threshold problem; Initial data and evolution (set-up); Tests of the set-up (results so far); Plan to the next gates; Summary; appendices: parameters, ledger |
| Subsection of the threshold problem | what fixes the answer | amplitude and shape; outcome of a run; what the estimates predict |
| Subsection of the set-up | the two set-ups and the method | the expanding ball; the periodic box; numerical methods (last) |
| Subsection of the tests | one test per subsection | constraints of the initial data; exact evolution of the scouting data; independent re-derivations; analytic criteria |

Special cases entered as limits (2.2): the marginally bound ball enters as the limit of the
LTB slice with zero binding energy; the spherical outcome enters as the zero-ellipticity
limit of the threshold line; the Newtonian reference enters as the weak-field limit.

## Allowed numbers (4.1)

- Exact analytic factors and powers: 8 pi, 4 pi, 16 pi, 2M/R, (HR)^2, 3/2, 2/3, 12/5, 5/3,
  15/pi, the factor e (Euler's number) between the two amplitude measures, t^(2/3),
  mu^(-3/2), h^2, h^4.
- Structural integers: three outcome classes, four hypotheses, six analytic criteria, five
  gates, two set-ups, two slicings, three ways of convergence (particle number, cell size,
  ball radius or box size).
- Labels: gates G0-G4; hypotheses H1-H4; tests A1-A7; the scouting runs SR-1, SR-2.
- Parameter values that define the figures: e = 0.2 (the comparison ellipticity),
  p = 0, sigma_H = 0.01, a_end/a_H = 100, R_b H_i = 0.9, R_b = 2 r_m and 3 r_m,
  t_end = 250 t_H and 1000 t_H, H R_b = 1/2 of the scouting data.
- Everything else (orders, residuals, times, masses, costs) is in the ledger appendix.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole, BH (in the text) | any |
| early matter-dominated era (early matter era) | EMD (in the text) | cosmology |
| collisionless matter, particles | dust (unless the pressureless fluid is meant) | kinetic theory |
| expanding ball | expanding dust ball initial-data module, expball | this note |
| periodic box | phase 1 | this note |
| apparent horizon | horizon (when the finder is meant) | numerical relativity |
| first trapped sphere | horizon formation (for the exact solution) | numerical relativity |
| slicing; geodesic slicing; conformal-time slicing | gauge (for the lapse alone) | numerical relativity |
| threshold amplitude | critical amplitude (no critical scaling is implied) | this note |
| Zel'dovich-hoop line | analytic threshold (unnamed) | this note |
| Numerical methods | pipeline, harness | any |
| registered run | job, simulation id | this program |

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`expball`, `runs_ball`, `periodic_threshold`, `nrpic_cf`, `nrpic_cosmo`, `make_field`,
`athinput`, `nrpic-run`, `scope_calc`, script names, run directory names, the cluster and
its hardware. Checker call from `note/`:
`--forbid 'expball|runs_ball|periodic_threshold|nrpic_cf|nrpic_cosmo|make_field|athinput|nrpic-run|scope_calc|anta|A100|Slurm'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| landscape | the particle threshold of Yoo et al. lies an order of magnitude below the hoop line and next to the finite-duration amplitude; the ball holds only small amplitudes | e, p = 0; R_b H_i = 0.9; t_end |
| criteria | the analytic criteria spread over two orders of magnitude and disagree about the dependence on ellipticity | sigma_H = 0.01, a_end/a_H = 100 |
| architecture | which parts of the calculation exist, which are carried over, which are new | none |
| constraints | the constraint residuals of smooth data fall at the order of the differences; a sharp edge does not converge | none |
| ball | the core turns around and crunches inside an expanding envelope; the horizon mass grows after first trapping; geodesic slicing needs a shrinking step | H R_b = 1/2 |
| timeline | the five gates, what each needs and where the track stands | none |
