# Gate review: B-emd-gw G2 (independent reviewer, batch 38)

Reviewer session of batch 38, 2026-11-27 (PST evening). Decision 0019 item 3. I produced none
of this work. Tag check: `git tag -l 'stage/B-emd-gw/*'` lists G0-pass-20261119 and
G1-pass-20261121 only; G2 is not signed. This file is written in two commits: the predictions
of my own check (section 2) first, before the check ran; the rest afterwards.

## 2. Reviewer's own check R (predictions, written before the run)

Script `stage/G2/gate_review/review_check.py` (my own readers; the line-record format read from
`athenak/src/particles/nrpic_io.cpp` NrpicWriteLine, the history columns from their headers; of
the lead's code only the definition of the band power, `compare_legs.py` band_rms2, is taken,
so that my number is the same quantity). It covers what the fresh verifier did not recompute
(VERIFIER.md section 4, "cannot claim" 6): the track's own G2 criterion C7 (sub-percent scale
factor and growth rate, converging in particle number and mesh) and the particle-number leg of
the band strain; and it tabulates the gauge leg against a.

Seen before writing these predictions: the lead's numbers in `flrw_conv/README.md` ("Verdict"),
CHECKLIST.md and VERIFIER.md; the decks of the population legs (the particle leg at eight per
cell, B-20261124-223926-33194d9 and its continuation, runs `pop_gr_run.athinput` with
`shift_Gamma = 0.0`: zero shift); the list of dump epochs with spectra in the three analysis
files. No number of my own was computed before this commit.

- RA1 (C7, growth rate, sub-percent). In every run of leg B (16, 32, 64, 128 cells at one
  particle per cell; 32 cells at 8 and 27 per cell) the largest |f - f_ref| for a >= 3 is below
  1e-3. The prediction fails between 1e-3 and 1e-2; the criterion itself fails at 1e-2 or above.
- RA2 (C7, mesh). The median |f - f_ref| for a >= 3 falls at every halving of the spacing,
  16 -> 32 -> 64 -> 128, by a factor of at least 4 from 16 to 32 and from 32 to 64. Refuted if
  any halving leaves it equal or larger.
- RA3 (C7, particle number). At 32 cells the medians at 8 and 27 per cell are at most 1.5 times
  the median at one per cell. Refuted above 1.5.
- RA4 (agreement with the lead). My medians (window 0.5 in ln a, a least-squares fit of the
  wave, normalised by the line mean) are within a factor 3 of the lead's 6.7e-5, 4.9e-6, 3.0e-7
  (16, 32, 64 cells) and within a factor 10 of 2.8e-8 (128 cells). Refuted outside.
- RB1 (C7, scale factor). Leg F: the largest relative error of alpha_min, alpha_max, the proper
  volume and the mean K against a(t) = (1 + t/2)^2 is below 1e-6 for the lattices at rest (a0) at
  16, 32, 64 cells, and below 1e-4 with position noise (a1, a2). The criterion fails at 1e-2.
- RB2 (C7, scale factor, mesh). At rest the error falls from 32 to 64 cells by at least 8.
- RC1 (C2, particle-number leg). Band rms |k| <= 8 k_f (corrected spectra), 128^3 zero shift,
  eight over one particle per cell, within 3e-3 of one at every common dump (a = 56 to 132).
  Refuted outside 1e-2.
- RD1 (C2, gauge leg). The same band rms, Gamma driver over zero shift at 128^3, within 5 per
  cent of one at every dump with a <= 36. Refuted if it leaves 0.95-1.05 at some a <= 36.
