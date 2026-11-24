# Reproduction of arXiv:2512.14649 and arXiv:2401.08530: state on 2026-11-24 15:30 PST

Decisions 0028, 0029, 0031, 0032, 0034. Owner Track E, packages `tracks/E-stoch-inf/repro/`.

The working note is complete: `tracks/E-stoch-inf/repro/note/manuscript/main.pdf` on branch
`track/E-stoch-inf` (26 pages, REVTeX; written with the paper-writing skill; guide and
notation one level above the manuscript; ledger of 133 rows in 11 tables, each with the
fresh verifier's verdict). No row is pending. The verdict per figure and statement of both
papers is Table IV of the note and the table in `tracks/E-stoch-inf/repro/note/README.md`.

Packages: `scope` (map of nine figures, Table I and 33 statements; audit of 26 set-up
items), `langevin` (the one-patch part of arXiv:2401.08530), `equations` (both papers'
equations checked and mapped to the source; 17 misprints), `ablation` and `continue` (card
runs), `figs`, `note`, `verify` (two passes of a fresh verifier). Level 2 of the stochastic
backreaction is on branch `core/noise-level2` (written on Opus, reviewed on Fable: results
unchanged; the reviewed card build's own card run waits in the shared queue).

Open, as the note states them:
- the spread of the fields over the lattice is 3.5 to 4 times narrower in our runs than in
  the published one-point figures while the published spectra agree with ours (cause
  open; a judgement from reading the figures, confirmed by the verifier's own reading);
- the published bound on the backreaction (one part in ten thousand) holds at large scales
  and fails at the shortest scales of the inflection case, as the published figure shows;
- the level reached with a flipped noise sign is a hundred times below the printed one;
- a floor in the spectral convergence at the longest wavelengths of the largest lattice,
  a property of the resolved field; whether it is second order in the amplitude needs a
  run at half the noise amplitude (queued by the lead);
- one-patch part: the published figures follow only from a forward Euler background at
  the paper's step and from the Ito reading; the skewness of the lapse differs by about
  seven per cent between two implementations;
- not recomputed by the verifier: the extrinsic-curvature spectra, the gauge families,
  nine of the seventeen misprints, the constraint field from the metric, seven per-cell
  percentile rows of the slow-roll run;
- the skill's step of parallel reviewers was replaced by one self-review.
