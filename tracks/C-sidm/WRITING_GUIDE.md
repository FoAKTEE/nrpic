# Writing guide: working note of C-sidm (S3, relativistic collapse of a self-interacting core)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with note v0 (gate G0).

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is the
  track's internal working paper and grows into its paper at gate G4.
- Where the methods go: the note is a scoping and verification record, so the set-up and
  the methods are in the main text; model parameters go to an appendix table; every number
  goes to the ledger appendix.
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix (the note's Supplemental Material) lists every number with the id of the
   registered run that produced it, and the source locator (file and line) of every number
   taken from a paper. Run ids, locators, file names and the cost of existing runs appear in
   the ledger appendix and nowhere else; the main text and the captions follow 4.1 and 5.5.
   The scripts that build the ledger (`scripts/ledger.py`, `scripts/run_all.py`, the run
   table of `scripts/common.py`) name the track's documents and runs; the checker's 5.5
   and 5.8 hits there and in the ledger appendix are accepted under this exception.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY])
   stay out of the typeset text; the main text says in words what is established, what is
   the track's choice, and what is open. The labels live in the journals and the stage
   documents.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | what self-interacting dark matter is; gravothermal collapse; why the core's history is too slow to evolve; what the Knudsen number measures |
| SIDM and black-hole-seed astrophysicists | Einstein-Vlasov steady states; binding-energy turning point; radial pulsation onset; the 3+1 evolution with particles |
| Kinetic-theory and plasma readers | Maxwell-Juttner gas; Moller speed; direct-simulation Monte Carlo pairing in cells |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; From gravothermal collapse to a relativistic instability (problem); Set-up and numerical methods; Tests so far; Plan and open questions; Summary; appendices: parameters, ledger |
| Subsection of the problem | what fixes the answer | time scales; equilibrium families; the Knudsen number; observables |
| Subsection of the set-up | the parts of the calculation | the calculation (architecture); collisions; numerical methods (last) |
| Subsection of the tests | one test per subsection | equilibrium sequences and onsets; collision references and kernels; particles in a box; initial data in the code |

Special cases entered as limits (2.2): the King model enters as the b = 1 member of the
truncated thermal family; the non-relativistic collision rate enters as the low-temperature
limit of the Maxwell-Juttner rate; the collisionless cluster enters as the Kn -> infinity
end and the perfect fluid as the Kn -> 0 end of one scan.

## Allowed numbers (4.1)

- Exact analytic factors and powers: 4 pi, 16/pi, 1/2, 5/3, 2 (pairs), (N - 1),
  Kn^-3, e^{y_0} - 1.
- Structural integers: three equilibrium families, two adiabatic indices, three ways of
  convergence (particle number, cell size, domain size), five gates, three compiler
  settings, thirteen particle models.
- Labels: gates G0-G4; tests T0-T12 of the box; waves 1-5.
- Parameter values that define the figures: b = 0.1 (thermal core), b = 1 (King),
  sigma/m = 1, 5, 100 cm^2/g, core masses 200 M_sun and 1.9e9 M_sun, the planned scan
  Kn_c = 0.3-100, temperatures theta = 0.02 and 0.01 of the box (in captions only).
- Everything else (onsets, residuals, constants K, costs, Kn values) is in the ledger.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole, BH (in the text) | any |
| self-interacting dark matter (SIDM) | dark-matter fluid | cosmology |
| thermal core (truncated Maxwell-Boltzmann core) | F21 model, F21 family | this note |
| binding-energy maximum (turning point) | eps max | relativistic stellar dynamics |
| radial-pulsation onset | FEM onset, omega2 zero | relativistic stellar dynamics |
| Knudsen number Kn | mean-free-path ratio (undefined) | kinetic theory |
| Moller speed | relative velocity (when the invariant is meant) | kinetic theory |
| collision cell | mesh cell (when the pairing cell is meant) | DSMC |
| Numerical methods | pipeline, harness | any |
| registered run | job, simulation id | this program |

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`nrpic_cf`, `nrpic_geodesic`, `tmb.py`, `evstatic`, `make_box`, `an_step`, `nrpic-run`,
`athinput`, `F21`, `G26`, `core-v0.3`, `C-pre`, script names, run directory names, the
machine and card names. Checker: `--forbid 'nrpic_cf|nrpic_geodesic|tmb\.py|evstatic|make_box|an_step|nrpic-run|athinput|F21|G26|core-v0|C-pre|anta|A100'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| fig_knudsen | real cores sit twenty decades below the reachable Knudsen numbers; the conversion constant varies little across models | sigma/m = 1, 5, 100 cm^2/g; core masses 200 and 1.9e9 M_sun |
| schem_architecture | what exists, what is carried over, what is new | none |
| fig_sequences | the three criteria of the thermal core separate; the King and monoenergetic turning points | b = 0.1, b = 1 |
| fig_collisions | the references agree with independent checks; the code's kernels sit far inside their tolerances | three compiler settings |
| fig_box_step | the code moves particles exactly in the collisionless box | theta = 0.02, 0.01 |
| schem_timeline | the gates and what each waits for | none |
