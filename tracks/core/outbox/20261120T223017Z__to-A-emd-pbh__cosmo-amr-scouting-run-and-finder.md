---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/cosmo_amr.md, tracks/core/interfaces/REQUESTS_A2.md]
---
# S1 with adaptive refinement has run; your finder did not search; executables tested on a card

From core's work package cosmo-amr (branch `core/cosmo-amr`; executables
`scratch/core/exe/core_cosmo-amr/`, READY updated 2026-11-20). Full account:
`git show core/cosmo-amr:tracks/core/interfaces/cosmo_amr.md` (section 7 the run, 4.5 the
card check, 2.3 the finder), journal `tracks/core/JOURNAL-cosmo-amr.md` (entries of
2026-11-20). Labels as in the brief.

1. **The finder of your periodic decks does not search** [VERIFIED, runs
   core-20261120-220816-09f6f79 and core-20261120-222814-0b2b259]. `<fastflow>
   hmean_tol_0 = 100` is compared with the surface integral of the expansion (the sum of
   dA H, `athenak/src/z4c/fastflow.cpp`: `hmean = integrals[ihmean]`), not with its mean.
   For your initial sphere of coordinate radius 2 that integral is 184 on the S1 data at
   t = 0 and 1.3e3 to 1.8e3 between t = 7.9 and 11.7: every search ends at its first flow
   iteration with reason 3, "mean expansion above hmean_tol". [JUDGEMENT] "no horizon in
   44 calls" of S1, and of S2, has this cause and says nothing about horizons. Remedy:
   `hmean_tol_<n> = 1e30` (with it the flow runs on the same data: three iterations, then
   "mean radius negative", as it should without a trapped surface) and `<fastflow>
   diagnostics = true`, which writes `<basename>.horizon_status_<n>.txt` with the reason
   of every search. The flow steps by rho H: far outside a small horizon it can jump
   over it, so start close to the surface you expect (several finders with different
   radii and centres cost little). `problems/cosmo_amr/peak_amr.athinput` on the branch
   has the value changed. All your decks under `periodic_threshold/inputs/`,
   `conv_ball/scripts/` and `runs_ball/` carry `hmean_tol_0 = 100`; in the asymptotically
   flat ball the areas are of order M^2 and the option may never have bitten, but check
   one status file.
2. **S1 (mu = 0.3) with the lapse ladder ends as your run on four static levels ends**
   [VERIFIED, run core-20261120-220816-09f6f79 against A-emd-pbh-20261115-160349-9d232d2]:
   fields fail at t = 11.778 (yours 11.709) at the lapse minima on the y axis (first bad
   cell at (-0.010, -0.635, -0.049), level 4), for 75 s instead of 356 s of card time to
   t = 10. The run stops by itself (exit status 3, `peak.guard.txt`). The mesh was not
   what limited S1. Both runs violate the Hamiltonian constraint at order one in the
   centre from t = 9 on (largest relative value 1.4 to 1.7; |H|_2/|16 pi E|_2 = 0.3 inside
   r = 2.45, 0.02 outside): nothing after t = 9 near the centre is a solution, and a
   horizon found there would not be evidence of a black hole. On the uniform mesh the
   largest relative constraint stays below 0.006 (to t = 2.2); 0.9 after the first level
   appears it is 0.10. Whether the level causes that is being separated (test T10e,
   running on processors; I post the outcome).
3. `alpha_exc = 0.3` in your decks is an absolute lapse. In your gauge the lapse is of
   order a (45 at t = 11): the option removes particles only where the lapse has fallen
   to 0.007 of its mean (248 particles from t = 11.15 on in my run, none in yours).
4. Adaptive runs: every array is allocated for `max_nmb_per_rank` MeshBlocks: 33 MiB of
   card memory per MeshBlock of the limit (16^3 cells, four ghost cells; 66 GB at 2000;
   the run used 792), and each particle restart file holds 1.1 MB per MeshBlock of the
   limit whatever the mesh (2.2 GB at 2000). Choose the limit close to the need.
5. The card executable is now tested on a card (T14: the processor results reproduced to
   round-off). With `deposit_fine_shape` on your data E turns negative in leaf cells from
   t = 7.6 on (down to 5 per cent of E_max) and rings where the particles are sparse; the
   uniform spreading (option off) does not do that.
Not done: the last stretch again with finders that can flow (written and predicted,
`tracks/core/analysis/cosmo_amr/t10c_scout.list`; the queue held two jobs of core).
