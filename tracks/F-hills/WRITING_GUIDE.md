# Writing guide: working note of F-hills (S12, the Hills mechanism near a black hole)

The per-paper layer of the paper-writing principles (Sec. 0) for the track's REVTeX working
note `note/main.tex`. This file and `NOTATION.md` sit one level above the manuscript
directory `note/` (7.1). Where this guide is more specific than the principles, it governs
the note. Started 2026-11-15 with note v0 (gate G0, wave 2).

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). The note is the
  track's internal working paper and grows into its paper at gate G4.
- Where the methods go: the note is a scoping and verification record, so the set-up and
  the methods are in the main text; the parameters of the passages go to an appendix table;
  every number goes to the ledger appendix.
- Tone: letter-like concision, American English, no hype.

## Two exceptions for the working note (program rules over 4.1 and 5.5)

1. Program rule 4 (CLAUDE.md): a number enters a note only with a run id. The ledger
   appendix (the note's Supplemental Material) lists every number with the id of the
   registered run that produced it, and the source locator (file and line) of every number
   taken from a paper. Run ids, locators and file names appear in the ledger appendix and
   nowhere else; the main text and the captions follow 4.1 and 5.5. The scripts that build
   the ledger (`scripts/ledger.py`, `scripts/run_all.py`, the run table of
   `scripts/common.py`) name the track's documents and runs; the checker's 5.5 and 5.8 hits
   there and in the ledger appendix are accepted under this exception.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]) stay
   out of the typeset text; the main text says in words what is established, what is the
   track's choice, and what is open. The labels live in the journals and stage documents.

The dedicated section on how the code was born from existing codes (5.5) belongs to the
paper of the method, not to this track note; the use of language-model agents is stated in
the Introduction and the acknowledgments.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | the Hills mechanism; tidal radius and penetration factor; the restricted three-body problem; what the energy unit means |
| Stellar dynamicists (hypervelocity stars, binaries near massive black holes) | moving punctures; approximate constraint data and junk radiation; the marginally bound orbit; why a mass ratio of a few is the reach of full numerical relativity |
| Gravitational-wave astronomers (extreme- and intermediate-mass-ratio inspirals) | which member is captured, on what orbit, and why the separation is a three-body event |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; The Hills problem near a black hole (problem); Set-up and numerical methods; Tests so far; Plan and open questions; Summary; appendices: parameters, ledger |
| Subsection of the problem | what fixes the answer | scales of the encounter; the plunge bound; objects and observables |
| Subsection of the set-up | the parts of the calculation | the calculation (architecture); reference solutions; the passages in full relativity; numerical methods (last) |
| Subsection of the tests | one test per subsection | Newtonian limit; geodesic baseline in its own regime; the two references at mass ratios four and ten; the first passages; mesh and cost |
| Tests, split for G1 (2026-11-21, lead, on the note helper's request) | reference against full relativity | "Reference solutions: tests and predictions" (the subsections above); "Full relativity: data, members, mesh, and the first passage" (data at the start, a single member, mesh and tree with cost, the first passage) |

Special cases entered as limits (2.2): the restricted three-body problem enters as the
q -> infinity limit of the full Newtonian problem; the Newtonian problem as the
r_p >> r_g limit of the geodesic baseline; the geodesic baseline as the m_b -> 0 limit of
the full-relativity passage.

## Allowed numbers (4.1)

- Exact analytic factors and powers: 4 q^(2/3), q^(1/3), q^(-2/3), (5/64), 1/Gamma^2, 2M,
  4M (marginally bound radius and angular momentum of a parabolic orbit).
- Structural integers: three bodies, two reference models, three objects (a, b, c), two
  orientations, five gates, three resolutions.
- Labels: gates G0-G4; objects (a), (b), (c); members m_1, m_2.
- Parameter values that define the figures: mass ratios q = 4 and 10; binary separations
  a_b = 5 M and 3 M; pericentres of the first passages; start at four tidal radii; finest
  cells m/8 and m/16; the plunge radius 2.5 M of the geodesic baseline; the comparison radius
  4M; the binary mass 1e-6 M of the geodesic scan; the shift damping eta m = 2 and 0.25, the
  momentum P = m/4 and the cells m/4 of the single-member and data figures (added 2026-11-21).
- Everything else (fractions, energies, MeshBlock counts, card-hours, deviations) is in the
  ledger.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole, BH (in the text) | any |
| heavy black hole (mass M), members (m_1, m_2) | big BH, primary, light holes | this note |
| tidal radius r_t | Hill radius (when r_t is meant) | Hills mechanism |
| penetration factor D = r_p/r_t (and beta = 1/D in the geodesic scan) | impact parameter | Hills mechanism |
| separated / disrupted binary | broken binary | Hills mechanism |
| ejected member, captured member | escaper, bound star | Hills mechanism |
| plunge (crosses r = 2.5 M inward) | capture by the black hole (in the geodesic model) | this note |
| geodesic baseline (exact Schwarzschild acceleration plus Newtonian pair force) | HRNA (in the text) | this note |
| marginally bound orbit | ISCO (for parabolic orbits) | relativity |
| moving punctures | Bowen-York holes | numerical relativity |
| junk radiation | spurious waves | numerical relativity |
| Numerical methods | pipeline, harness | any |
| registered run | job, simulation id | this program |

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`HRNA`, `newton3`, `geodesic_binary`, `three_punctures`, `nr_first`, `hrna.py`,
`nrpic_cf`, `puncture_setup`, `athinput`, `nrpic-run`, `core-v0`, `F-pre`, `lead_checks`,
script names, run directory names, the machine and card names. Checker:
`--forbid 'HRNA|newton3|geodesic_binary|three_punctures|nr_first|hrna\.py|nrpic_cf|puncture_setup|athinput|nrpic-run|core-v0|F-pre|lead_checks|anta|A100'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| schem_architecture | what exists, what is carried over, what is new | none |
| fig_newton | the restricted problem reproduces the published edges and the deep-limit saturation | 3000 phases per D, parabolic, coplanar |
| fig_geodesic | the geodesic baseline separates more retrograde binaries than Newton, as in the published scan | binary mass 1e-6 M, beta 0.1-10 |
| fig_rp_scan | at q = 4 and 10 the two references disagree in kind: geodesic plunges where Newton keeps the member | q = 10 (a_b = 3 M), q = 4 (a_b = 5 M), start at 4 r_t |
| fig_passage | the first passages: which member leaves differs between the references from about 100 M on | the two passage inputs |
| fig_cost | the m/8 passages fit one card; m/16 at q = 10 does not | m/8, m/16 |
| schem_timeline | the gates and what each waits for | none |
| schem_dataflow | a passage from the input through chained card segments, readers and references to the note | none |
| fig_constraints | the constraint residual of the three-black-hole data at the start, three variants | cells m/4 to m/16 |
| fig_single | a single member: tracker speed and horizon mass under two shift dampings | P = m/4, eta m = 2 and 0.25, cells m/8 |
| fig_tree | the MeshBlock tree along the passage and its cost | m/8, m/16 |
| fig_smoke | the first card segments of the passage: rate, memory, trackers, horizons | P1 input, m/8 |
