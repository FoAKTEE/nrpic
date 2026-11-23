# What G2 of B-emd-gw still lacks (batch 10a, 2026-11-22)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell; `flrw_conv/`), a first full-GR kinetic run, constraint norms against
time, failed runs on record.

Lacking, in the order the track will close them:

1. Full GR against the Newtonian mode (decision 0013, multi-code row): the first population
   run in full relativity (sigma1 = 0.014, Slurm 4921, queued) and its comparison with the
   Newtonian fidL8 run by the sigma1 a scaling and with the design's signal estimate
   (predictions G1-G4, population/JOURNAL.md); then sigma1 = 0.028 on re-solved data.
2. Shearing dust (arXiv:2003.08014): L2 (beta = 0.5, HL = 4), the case that separates the
   codes, has no number (the ray analysis returns NaN at every mesh); S3 does not converge
   monotonically over N_y = 32-128.
3. Gauge leg of the three-way convergence: the f = 1 lapse run stopped at the guard
   (t = 0.578); no other gauge or boundary variation has been run.
4. Constraints: Hr of the FLRW run and the constraint means of the shear cases at small HL grow
   with resolution (round-off is a candidate, not tested).
5. Floor of the growth-rate amplitude at 128 cells: attributed to the start step from runs at
   32 cells; J4 (Slurm 4922) tests it at 128 cells.
6. Package products: verification-ladder schematic, a gauge convergence figure, a slice
   mosaic with zoom boxes (from the population box), G2 sections of the working note with the
   checker, a fresh verifier (VERIFIER.md), a reproducibility list.
