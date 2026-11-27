# Writing guide: the reproduction of two papers on stochastic inflation (working note)

The per-paper layer of the paper-writing principles (skill Sec. 0) for the working note
`manuscript/main.tex` of package repro/note (Track E, decision 0028). This file and
`NOTATION.md` sit one level above the manuscript (7.1). Started 2026-11-24. Where this guide
is more specific than the principles, it governs the note.

## Journal and tone (2.8)

- Format: Physical Review D style, REVTeX 4.2 (`aps,prd,twocolumn`). Internal working note
  of the program; the subject is a reproduction, so the set-up and its differences from the
  papers' set-up are in the main text (one subsection per paper); the parameters are in an
  appendix table; every number is in the ledger appendix.
- Tone: letter-like concision, American English, no hype. A finding about a paper is stated
  as what the paper prints, what we computed, and how they differ; never as an accusation.
  What only the authors could settle is said once, plainly.

## Two exceptions for the working note (program rules over 4.1 and 7.5)

1. Program rule 4: a number enters the note only with a run id or a source locator. The
   ledger appendix (the Supplemental Material of the note) lists each number with its
   source: the registered run (id) or the line of a paper's source file. Run ids and
   line locators appear in the ledger appendix and in the parameter appendix and nowhere
   else. The main text and the captions follow 4.1. The scripts in `manuscript/scripts/`
   name the runs and labels they read; the checker's 7.5 and 7.7 hits there are accepted
   under this exception, and so are the hits in the ledger appendix (`tables/ledger.tex`), whose
   source column names records of the program by path.
2. Decision 0031 item 3: the note says which code each run used. The lattice runs used the
   release of the code, the comparison of the backreaction levels a reviewed development
   version; the checker's 7.6 hits on "version" and "defect" in Sec. III I and in the appendix
   on the parameters are accepted under this rule. Commit hashes stay out (they are in the
   ledger's run records only through the run ids).
3. The evidence labels of the program ([VERIFIED], [JUDGEMENT], [TO VERIFY]) stay out of
   the typeset text; the main text says in words what was measured, what is our reading,
   and what is open. The labels live in the package journal and in `notes/`.

## Readers (1.2)

| Community | Minimum background the note supplies |
|---|---|
| Numerical relativists | slow-roll parameters, ultra-slow roll, horizon crossing, the comoving curvature perturbation and its freezing; coarse-graining window and stochastic sources |
| Early-universe cosmologists | the 3+1 split, geodesic slicing, BSSN and Z4c, the Hamiltonian and momentum constraints and their magnitudes |
| Readers of stochastic calculus | Ito and Stratonovich readings of one equation, the Ito correction, Euler-Maruyama and Heun schemes |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; Stochastic sources in general relativity (what both papers do, the computer-algebra checks); The lattice reproduction (second paper); The ultra-slow-roll lattice against criteria fixed in advance (G2 of the track, batch 15: runs at several amplitudes, linear agreement and resolution, second order of the constraints with its one failure, independent check); The one-patch reproduction (first paper); Discussion; Summary; appendices in the order of first citation: misprints, scenarios and parameters, set-up item by item, verdicts, ledger |
| Subsection of the lattice section | the observable | set-up and its differences; background; spectra; one-point statistics and constraints; anisotropic extrinsic curvature; convergence; backreaction; numerical methods precede the first result |
| Subsection of the one-patch section | the question that fixes the answer | the system; the background and its step; stochastic interpretation; the statements of the text |

Special cases entered as limits (2.2): the one-patch Langevin system is the limit of the
lattice equations without gradients and shear; level 0 of the backreaction is the limit of
level 2 without local coefficients; slow roll is the limit of the inflection case far
from its plateau.

## Allowed numbers (4.1)

- Exact analytic factors and powers: k^3/(2 pi^2), sigma^2/3 (ratio of the USR noise
  amplitude), alpha^3, alpha^5, alpha^2 (powers of the lapse in the Ito term and the noise),
  e^{3N} (growth of the noise on the plateau), 3 - eps2, 3H/(2 pi), eps2 = 6 and 3 (USR).
- Structural integers: two papers, two scenarios, three levels of backreaction (0, 1, 2),
  four set-up differences plus one (five), four RK stages, sixth-order stencils, four
  figures of the first paper, nine figures of the second, seventeen misprints, two readings.
- Labels: levels 0, 1, 2; Figs. 1-9 of the second paper and Figs. 1-4 of the first.
- Parameter values that define the figures and cases: lattices 32^3-256^3; k_max = (N/4) dk
  and 8 dk; sigma = 1; s = 5; the Euler step 0.01 e-folds and its alternatives 0.005,
  0.001; record times N_b = 3, 4, 5, 6; noise window 2 <= N_b < 6; fifty thousand paths;
  "four cells per shortest wavelength", "about thirteen cells" (the threshold of the
  momentum constraint); "one part in ten thousand" (the second paper's own bound, quoted); the
  windows 0.5 <= N <= ln 8 (plateau ratio) and 0.5 <= N <= ln 64 (sign flip); four lattices.
- Comparison factors stated in words where the argument needs them: "a factor of about
  three to four" (one-point bands), "one to two decades" (constraint levels), "three to five
  decades" (sign flip), "about fifteen times higher" (the spectrum a published width would
  need), "a factor sixteen per halving" (fourth order in time), "less than a factor of three"
  (spectral departure from 128^3 to 256^3), "within a fifth of one" (plateau ratios), "about five
  decades" and "about four decades" (median sign-flip jumps), "more than a decade", "more than three
  decades" and "a few times lower" (per-cell tails of the Hamiltonian ratio against the stated order). Their values are in the ledger.
- Section on the criteria (batch 15): nine criteria, eleven runs (nine on 256^3, two on 320^3),
  amplitudes lambda = +-1, +-1/2, +-1/4, a first and a second seed, the factor four (second order) and
  two (first order) per halving, (5/4)^4 and (5/4)^6, |n| about 25, three times the noise level,
  -4/17 and 1/16 (exact factors of the difference statistics), "a few parts in a thousand", "one to
  three decades", "about five decades" (control), "four cells" (shortest mode), sixteen cells (zoom).
- Section on the tail statistics (G3, batch 34): 128^3 and 160^3 lattices; mirrored pairs; thresholds of three and four
  standard deviations (the figure parameters nu = 3, 4); "three combined standard errors" (the threshold of a
  difference); "the factor four" (constraints); "71 of the 128 pairs" (the pairs read so far) and "two hundred and fifty-six
  boxes" (the full set); "one part in a few hundred" (the width excess, if it stands); "about five times" (mirroring gain,
  if it stands).
- Everything else (residuals, ratios, moments, widths) is in the ledger appendix.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| ultra-slow roll (USR) | constant roll | inflation |
| comoving curvature perturbation | zeta | cosmology |
| freezing | conservation | cosmology |
| coarse-graining window | cutoff filter | stochastic inflation |
| stochastic sources | noise terms (for the lattice) | this note |
| Mukhanov-Sasaki solution | MS | this note |
| geodesic slicing | synchronous gauge (in the text) | numerical relativity |
| level 0, 1, 2 of the backreaction | Starobinsky approximation | 2512.14649 |
| Ito reading, Stratonovich reading | Ito interpretation of Mathematica | stochastic calculus |
| one-patch Langevin system | separate-universe code | this note |
| card-hours | GPU-hours | this program |

## Project names (7.7)

The note never names the program's intermediate products or harness: run labels, package
directories, helper scripts, executables. Checked automatically (comments included; the
hits inside `scripts/` are accepted under exception 1):

- nrpic-run
- nrpic-stage
- REPRO_MAP
- SETUP_AUDIT
- RESULTS\.md
- P256v6
- USF256
- RSF256
- CL256
- AL[012][SU]
- M64[SU]
- repro/
- scratch/
- athena_gpu
- U256
- U320
- g2prod
- judge_
- SCOPE

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| pipeline | the two reproductions side by side and what each compares with | none |
| background | box means on the lattice equal the Friedmann solution in both scenarios | 64^3, Table I |
| spectra (SR, USR) | entering modes rise to the Mukhanov-Sasaki spectrum and freeze | 256^3, k_max = 64 dk |
| one-point contrasts (USR) | entry, double feature of the field, late momentum, R grows and freezes; constraints | 256^3 |
| K spectra | isotropic and anisotropic extrinsic curvature through the crossings | 256^3 |
| convergence | spectra converge at close to sixth order up to 128^3 (between five and six with the verifier's reference), then a floor at the longest shells of 256^3; constraint plateaus equal on the three finer lattices | 32^3-256^3, k_max = 8 dk |
| ablation | level 2 against 0 near one part in ten thousand; level 1 is a scheme difference | 256^3 |
| sign flip | flipping the momentum source makes the constraints first order | 256^3 |
| ladder (schematic) | criteria fixed in advance, release runs, two readers, outcome with its one failure | none |
| mosaic | the USR curvature perturbation at N_f resolved to its shortest mode (box, quarter, sixteen cells) | 256^3, first seed, lambda = 1 |
| resolution | departure per mode falls between fourth and sixth order above |n| ~ 25; a flat third-order part below | 256^3 and 320^3 |
| halving | the even part of the constraints falls by four per halving; one momentum-constraint miss with the fixed level; three-amplitude level | 256^3, lambda = 1, 1/2, 1/4 |
| ladder G3 (schematic) | what was fixed before the production runs, the release runs, the two readers, the outcome as read so far | none |
| G3 mosaic | the delta-N curvature perturbation of one box at N_f and its nonlinear part, at three magnifications | 128^3, first seed, lambda = 1 |
| one-point (G3) | lattice and one-patch densities of zeta at the own width, and their ratio to the Gaussian | 128^3, pairs read so far |
| tails (G3) | tail fractions against the threshold; the judged points at three and four standard deviations with their errors | same |
| pairs (G3) | skewness of single boxes scatters, the pair mean does not; the even-part coefficient per pair | same |
| Langevin background | Euler at step 0.01 reaches the slope, the converged background stops on the plateau | Table II |
| Langevin moments and PDFs | Ito reading at step 0.01 matches the paper's shapes | Table II |
