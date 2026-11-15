# Writing guide: working note of Track D (S4, black-hole growth and dark-matter dress)

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
   appendix (the Supplemental Material of the note) lists every number with the id of the
   registered run that produced it. Run ids appear in the ledger appendix and nowhere else;
   the main text and the captions follow 4.1 and 5.5. The scripts that build the ledger
   (`scripts/ledger.py`, `scripts/run_all.py`, the run table of `scripts/common.py`) name
   the track's documents and runs they check; the checker's 5.5 and 5.8 hits there and in
   the ledger appendix are accepted under this exception.
2. Evidence labels of the program ([VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY])
   stay out of the typeset text; the main text says in words what is established, what is
   our choice, and what is open. The labels live in the journals and the ledger.

When the note becomes the track's paper (G4), the ledger moves to the Supplemental Material
and the run ids to the reproduction package.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | why an expanding pressureless medium has an exact vacuum-bubble solution; what the self-similar infall and the adiabatic spike are; why capture by the black hole removes low-angular-momentum matter |
| Dark-matter and primordial-black-hole cosmologists | the 3+1 split, slicing and lapse, apparent horizon and its area mass, Hamiltonian and momentum constraints, the moving puncture |
| Readers of the cosmological-coupling debate | what the coupling exponent measures, why a vacuum black hole is predicted to have exponent zero by both sides, what a numerical upper limit can and cannot say |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; Three questions (problem); Set-up; Tests so far; Plan and open items; Summary; appendices: parameters, ledger |
| Subsection of the problem | the three questions | growth law; spike in the strong field; null test of coupling |
| Subsection of the set-up | the configurations and the method | black hole in a vacuum bubble; black hole in dust that reaches it; numerical methods (last) |
| Subsection of the tests | one baseline per subsection | the exact bubble and its constraints; the horizon-mass floor; the spike in the probe limit; secondary infall and capture |

Special cases entered as limits (2.2): Schwarzschild as the nonrotating limit of the Kerr
spike; the Newtonian self-similar dress as the weak-field limit (turnaround radius much
larger than the black hole); the vacuum bubble as the limit of the growth problem with no
matter reaching the black hole.

## Allowed numbers (4.1)

- Exact analytic factors and powers: r^(-9/4), r^(-3/2), (4/(3 pi))^(2/3), 2M, 4M (the
  capture angular momentum), 8 pi, 16 pi, 3/2, 2/3, h^4, 1 + 6 ln a, 2^(2/3), 12 (mH)^2.
- Structural integers: three questions, four baselines (D-pre-1 to D-pre-4 become "four
  baselines"), two definitions of the accreted energy, two resolutions, three-way convergence,
  five gates.
- Labels: gates G0-G4; the first run and its vacuum control (no project labels such as ES-1).
- Parameter values that define the figures: wall at 36 M, Schuecking radius 40 M, dust to
  106 M, M/8 and M/16, 500 M, 4e6 solar masses, eps = 0.01, a/a_i = 4, sigma_i, the
  exponents k = 0, 1, 3 of the hypotheses.
- Everything else (orders, residuals, times, masses, costs) is in the ledger appendix.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole, BH (in the text) | any |
| vacuum bubble | Einstein-Straus hole, ES bubble | this note |
| wall (innermost comoving dust shell) | ES wall, bubble surface | this note |
| apparent-horizon mass, area mass | horizon mass (when the finder is meant) | numerical relativity |
| collisionless matter, particles | dust (unless the pressureless fluid or the exact LTB shells are meant) | kinetic theory |
| dress | mini-spike (for the matter that passed the centre once) | dark matter |
| spike | density spike (for the probe-limit profile) | dark matter |
| coupling exponent k | coupling strength | cosmological coupling |
| noise floor | error bar (for the horizon-mass drift) | this note |
| slicing, lapse | gauge (for the lapse alone) | numerical relativity |
| Numerical methods | pipeline, harness | any |

## Project names (5.8)

Never in the main text or captions (allowed in the ledger appendix only, exception 1):
`ES-1`, `V-1`, `D-pre-1` to `D-pre-4`, `nrpic_cf`, `nrpic_geodesic`, `make_es`,
`athinput`, `nrpic-run`, `puncture_drift`, `secondary_infall`, `einstein_straus`, script
names, run directory names, the cluster and its hardware. Checker call from `note/`:
`--forbid 'ES-1|V-1|D-pre|nrpic_cf|nrpic_geodesic|make_es|athinput|nrpic-run|puncture_drift|secondary_infall|einstein_straus|anta|A100|Slurm'`.

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| architecture | which parts of the calculation exist, which are carried over, which are new | none |
| es | the slice is vacuum and time-symmetric near the black hole, Einstein-de Sitter in the dust; the wall expands on the exact curve while inner tracers fall in | wall 36 M, Schuecking radius 40 M, dust to 106 M |
| constraints | residuals of the data fall at fourth order offline and faster inside AthenaK | none |
| floor | the horizon mass of a vacuum black hole holds to the floor before the boundary excursions; the coarser run drifts | M/8, M/16, 500 M |
| spike | the relativistic spike vanishes at 4Gm and peaks above the Newtonian one; particles on geodesics hold the equilibrium | 4e6 solar masses |
| infall | the self-similar profile approaches r^(-9/4) only deep inside; the black hole swallows cold and warm dust | eps = 0.01, a/a_i = 4 |
| timeline | the five gates, what each needs and where the track stands | none |
