# What G2 of B-emd-gw still lacks (batch 11, 2026-11-24; series 6 added in batch 11b)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell; the start-step floor now tested at 128 cells, J4), a first full-GR kinetic
run (now also the population box to a = 143), constraint norms against time, a slice mosaic with
zoom boxes, failed runs on record.

Lacking, in the order the track will close them:

1. Full GR against the Newtonian mode (decision 0013, multi-code row): done against the 64^3
   fidL8 box by the sigma1 a scaling (halo counts and masses, H1; near field, A1). The
   same-particle Newtonian reference at 128^3 is queued (B-20261124-131438-5d7e049); its
   comparison (N2-N4, `population/scripts/compare_newton.py`) is the halo-by-halo GR-minus-Newton
   statement. The 0.028 run stops at a = 30.7 in the densest core; restarts X0-X3 are queued
   (B-20261124-133533-cb0bb7d) to tell slice, step and slicing condition apart. Not established:
   what the high-k excess of the metric's TT energy after halo formation is.
2. Shearing dust (arXiv:2003.08014): L2 now has values (-0.828, -0.830, -0.835 at N_y = 32-128,
   near CosmoGRaPH's -0.8183, far from gevolution and GRAMSES) but no convergence: the field
   carries relative constraint means of 0.1-0.4 from a = 2.25 on at every N_y. At N_y = 64 it
   converges in particles along y to about -0.820 (1-8 per cell); at 4 per cell the mesh gives
   -0.822, -0.831, -0.839 at N_y = 64, 128, 256 (differences 9.4e-3, 7.9e-3: order about 0.25,
   away from CosmoGRaPH; series 6, B-20261124-140856-911ded9, summary -172643-d1e88c7). L2 is not
   converged in this code; the weak-field comparison rests on S1-S4, M1, L1. A run that could name
   the cause (an amplitude without stream crossing before t_A at three meshes) is not yet queued.
   S3 has a floor of 2-3e-5 (N_y = 256).
3. Gauge leg of the three-way convergence: one slicing point (f = 1 at N_y = 64, P10 holds); a
   convergent gauge leg (a second slicing or shift at three meshes) and its figure are missing.
4. Constraints: Hr of the FLRW run grows about as N^2 with the mesh; the population's mean
   constraint violations grow after halo formation (Hr_mean 2.85e-2, Mr_mean 0.20 at a = 141).
5. Package products (the verification-ladder schematic C10 exists since batch 11): gauge convergence figure (C11), G2
   sections of the working note with the checker (C17), a fresh verifier (C18), a reproducibility
   list (C6), schematics (C16); one script per figure where analyze_b.py and analyze_f.py draw
   several (C15).
