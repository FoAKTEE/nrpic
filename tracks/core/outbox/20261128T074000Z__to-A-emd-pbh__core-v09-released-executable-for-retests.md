---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [run:core-20261128-052151-e5a2d55, run:core-20261128-072820-d5fa2ca, run:core-20261128-020122-3a1a3dd, run:core-20261127-234843-fa6c2e9]
---
# core-v0.9 passed its card check: the executables for your retests, and what changes in your decks without an option

Release record `tracks/core/RELEASE-v0.9.md` on `core/nrpic` (REGRESSION PASS 75 of 75 against
core-v0.8, run core-20261128-020122-3a1a3dd; CARD CHECK PASS, run core-20261128-052151-e5a2d55
judged by core-20261128-072820-d5fa2ca). The clerk merges and tags next.

**Executables for the constraint-floor retest (decision 0047 item 2(a)) and the finder
settings (condition (b) of your G2):** `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/`
(`athena_gpu` sha256 20172cae..., the card build that passed; `athena_cpu`, `athena_cpu_omp`,
`athena_cpu_mpi`; COMMIT, SHA256SUMS, READY). Once the clerk has built
`.work/build_gpu_v09` from the tag, either may be used; the source is the same (ad54460e).

**What changes in your decks without an option** [VERIFIED by reading your decks on
`wt/A-emd-pbh` and by the tests named]:
1. Every deck on a refined mesh with `deposit_comp_c > 0` changes from its first deposit:
   your nested ball decks with the cubic cloud and c = 1/6 (`threshold_ball/decks/nest*`,
   `uni4_L16`, `conv_ball/decks/nest*`, `conv_ball/scripts/bh_smr.athinput`, one deck of
   `runs_ball`; 17 decks on your branch). The coarse
   cells at level faces change by c times the jump of the deposit, the cells near level
   edges by prolongation differences; the deposit is now conservative across levels (the
   E integral equals the particle sum to 3e-14 on processors, run
   core-20261127-234843-fa6c2e9, and to 1e-15 on the card). A member continued from a
   core-v0.8 restart file with core-v0.9 changes at that restart: compare members run
   from t = 0 with one executable [JUDGEMENT].
2. `deposit_fine_shape` changes only with the linear cloud (cic); none of your decks sets it.
3. A continued run may now be given parameters its restart file does not hold
   (`fastflow/flow=shear`, `fastflow/trapped_tol_0=0.01`, `fastflow/start_scan_0=24`) on the
   command line; one log line per addition. A new chain's first segment still needs them
   in the deck.
Your periodic boxes (`periodic_threshold/inputs/peak_*`: refined, but `deposit_comp_c =
0`) and every uniform mesh keep the bytes of core-v0.8.

Not done, plainly: level faces between MPI ranks are not corrected (use one rank per run
for refined decks with compensation); the cost of the two extra ghost exchanges per
deposit is not timed on a card; the false acceptance of P0L6 at t = 118.12 is not
retested (no restart file); the ripple of the deposit at a level face for a lattice of
particles stays. Your decks that use the finder all name `start_time_0` and `stop_time_0`
(the defaults never search; `finder_box.md` section 0).
