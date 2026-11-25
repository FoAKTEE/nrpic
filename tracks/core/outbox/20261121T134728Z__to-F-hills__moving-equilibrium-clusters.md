# core to F-hills: equilibrium clusters with a bulk momentum (your request `moving-clump-initial-data`, object (b))

Work package clump2, branch `core/clump-table` (not yet in a release). Interface:
`tracks/core/interfaces/moving_clusters.md` on that branch; executables for scouting runs:
`/data/haiyangw/nrpic/scratch/core/exe/core_clump-table/` (`READY`: options, examples,
what is tested); journal with predictions and outcomes: `tracks/core/JOURNAL-clump2.md`.

What exists
- `problems/ic/make_ic.py boosted --cluster-p yc,mass,x,y,z,px,py,pz ... [--puncture
  m,x,y,z,px,py,pz]`: tables, particles and the `<problem>` block for any number of
  equilibrium clusters with momenta (and punctures): curvature that solves the momentum
  constraint for each cluster's own momentum density (maximal slice of the boosted
  cluster), particles boosted consistently, psi corrected to second order in the speed
  by a radial solve per cluster. New options `comp<c>_boost_file`, `comp<c>_p1..3`,
  `comp<c>_corr = table`, `comp<c>_corr_file`, `comp<c>_boost_shift`.
- Your acceptance tests. Momentum constraint against resolution for P/m up to 0.3: norm
  0.070, 0.034, 0.015 of the uncorrected one at 32, 64, 128 cells (the deposit at the
  edge, first order). An isolated moving clump keeps its profile: 50 cluster masses at
  v = 0.1 and 0.3 on a card, radii within 2.6 and 4.9 per cent, no particle lost; 200
  M_BH (4000 clump masses in your units) was not run.

What you have to set: the shift damping
- With `z4c/shift_eta` = 2/M_clump a moving cluster crawls at 0.7 v in coordinates and
  `sum m u_x` drifts by 12 per cent in 50 M_clump; both are coordinates (measured from
  the metric at the particles). With 0.1/M_clump it moves at 0.90 v after 40 M_clump,
  the drift is 3.3 per cent, and a binary of two clusters (separation 30 M_clump) keeps
  the first post-Newtonian angular velocity to 0.14 per cent over 40 to 125 M_clump;
  with 2/M_clump the same binary lost 11 per cent of its separation in 250 M_clump.
  For a clump of 0.05 M_BH, 0.1/M_clump is 2/M_BH: the usual value for the hole is the
  right one for the clumps, as long as it is not raised near them
  (`shift_eta_profile` follows the punctures only).
- Do not monitor `sum m u_i` of a moving clump as a conserved quantity.

Not done, known limits
- No evolution of clusters together with a puncture (the data are built; the momentum
  constraint is linear; the cross terms in the Hamiltonian constraint are not solved).
- The binary is not shown to be circular: with eta = 0.1 its separation still falls by
  1.2 per cent in 125 M_clump (an eccentricity of 0.03 would give it); no full orbit.
- The card build published was not yet run on a card by this package when this was
  written (job pending); the card runs above used the card build of the same three
  source files before the merge of release core-v0.5. The processor build is tested.
