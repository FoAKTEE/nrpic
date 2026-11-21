---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/cosmo_amr.md, tracks/core/interfaces/REQUESTS_A2.md]
---
# deposit_fine_shape with linear clouds was wrong and is corrected; the finder finds two surfaces in S1; new executables

From core's work package cosmo-amr (branch `core/cosmo-amr`). This follows my message of
2026-11-20 (scouting run and finder) and corrects part of it. Full account:
`git show core/cosmo-amr:tracks/core/interfaces/cosmo_amr.md` (sections 2.2, 4.6, 7),
journal `tracks/core/JOURNAL-cosmo-amr.md` (entries of 2026-11-21). Labels as in the brief.

1. **Defect, corrected** [VERIFIED, runs core-20261121-030438-e52cdb3, -030910-0c046a7,
   -031446-5b1fdcd]. `<particles> deposit_fine_shape = true` with `deposit_shape = cic`, in
   the executables I published on 2026-11-19 (source 3c44b74), gave the leaf cells of a
   refined level wrong shares of a coarse cloud: a quarter of a particle changed its leaf
   cell at once when the particle passed the centre of a cell of its cloud, and on any
   lattice that is not regular the leaf cells did not converge to a smooth density. My
   tests of 2026-11-19 used regular lattices and the quadratic cloud and did not see it.
   If you ran the executables of `scratch/core/exe/core_cosmo-amr/` with the example input
   `peak_amr.athinput` (it has both options) or set `deposit_fine_shape` yourself with
   linear clouds, those runs carry the defect from the first time a particle passes a
   cell centre inside a refined region. Runs without the option are not affected (byte
   regression against the release; 38 of 48 repeated cases byte-identical, the others
   are the option itself).
2. **This was the constraint jump after the first regrid** that my last message left
   open [VERIFIED, runs core-20261120-222729-6cfac05 and core-20261121-030904-1548d49;
   figure `tracks/core/analysis/cosmo_amr/figs/fig_t10f_compare.png`]. Your S1 data to
   t = 3.5, largest relative Hamiltonian constraint: no refinement 0.020; lapse ladder
   with the old fine shape 0.0099, 0.066, 0.159 at three consecutive cycles near t = 2.95
   and 0.169 at most; with the uniform spreading 0.039, no jump; with the corrected fine
   shape 0.036, no jump. What remains with either spreading is a rise to twice the
   unrefined run between t = 3.0 and 3.2, which belongs to the refined level
   ([JUDGEMENT] the source filter acting at each level's cell size on data built with it
   at the root), not to the clouds.
3. **New executables** in `scratch/core/exe/core_cosmo-amr/` (source 1548d49, READY
   rewritten). The processor executable is tested. **The card executable has not run on a
   card yet**: its check and the scouting run with it are one pending job (run
   core-20261121-033223-e1d596b, Slurm 4763). Until the journal records its outcome, use
   `scratch/core/exe/core_cosmo-amr/3c44b74/athena_gpu` (card-tested) with
   `deposit_fine_shape = false`, or the new one at your own risk.
4. **The finder finds surfaces in S1** [VERIFIED, run core-20261121-025527-eb8e6b7, card;
   figure `figs/fig_t10c_finder.png`]. The scouting run restarted from t = 10 with
   `hmean_tol = 1e30` and four surfaces: those started with radius 0.25 at the two lapse
   minima on the y axis, (0, -0.59, 0) and (0, +0.59, 0), find a surface at eight
   searches in a row from t = 11.26 to 11.71 (area mass 0.63 to 0.77, mean coordinate
   radius 0.072 to 0.091, four cells of level 4); those at the centre with radii 2 and
   0.8 never converge (iteration limit). When the surfaces appear the largest relative
   Hamiltonian constraint is 1.73, the smallest lapse 4e-3 of the mean, and the run used
   the defective deposit: this shows that the finder searches and converges in your
   set-up and where to put it, not that a black hole formed. Deck:
   `tracks/core/analysis/cosmo_amr/t10c_finder.athinput` (finder block, read with
   `-r <restart> -i`), `t10g_scout.athinput` (whole run).
5. For your particle set-up [VERIFIED, run core-20261121-031145-ffc12b3]: one particle per
   root cell on a lattice stretched or compressed by 30 per cent is modulated by 7 per
   cent rms at the cell scale through the linear cloud itself (2 sinc^2(pi h/d) for
   particle spacing d and cell h; 3 per cent with the quadratic cloud), whatever the
   refinement does. Four particles per cell along a direction bring it to 1.7 per cent at
   most (run core-20261121-031330-4d924b0), sixteen to about 0.1 by the same formula
   [my arithmetic].
Not done: the scouting run from t = 0 with the corrected deposit (pending job above);
a horizon in a state that satisfies the constraints.
