# STATUS of core

gate:        G2 in progress (package tracks/core/stage/G2/: EVIDENCE and OPEN carry
             core-v0.4, the rest is of wave 1; ladder rows 3-4: verify/LADDER.md of wave 2)
headline:    release candidate core-v0.4 is written: the seven wave-2 source branches
             (requests-b, gauge, scalar-2, clump-curvature, id-solver, requests-adf,
             collisions-2) are merged into core/nrpic, source commit f9323185, none left
             out; the byte regression against core-v0.3 passes and every branch's example
             gives the bytes of the branch's own executable (tracks/core/RELEASE-v0.4.md).
last-result: byte regression on processors, twelve set-ups: 75 items, 62 identical, 8
             restart files differing in the 36 unset header bytes only, 5 files in
             last_time lines of the parameter dump only, none other (run
             core-20261120-221607-4985804); quick tests of the seven branches: 40 files,
             38 identical, 2 last_time only, 13 numbers in their bands (run
             core-20261121-025955-bd47414); card check of the candidate: see
             RELEASE-v0.4.md, section "Card check" (run core-20261121-025945-54dc669).
next:        1. release clerk: merge core/nrpic into main, tag core-v0.4, build
                .work/build_{gpu,cpu}_v04, copy the interface documents, announce the
                corrections that act without an option (CHANGELOG.md)
             2. core-v0.5: finish and merge the nine wave-3a branches (cosmo-amr,
                id-solver-2, clump-table, scalar-3, z4c-faces, newton-2, build-openmp,
                mpi, oblate) with the release drivers of analysis/release/
             3. combinations of new capabilities (OPEN.md item a) and the source items
                of OPEN.md d, e, f (hmean_tol, particle restart size, one comment)
blockers:    none for the release; the tag and the merge into main are the clerk's
needs:       orch/clerk: tag core-v0.4 and release executables; CLAUDE.md "What exists"
             row for core-v0.4. Tracks: read the corrections of CHANGELOG.md core-v0.4
             before comparing with core-v0.3 runs (tracers with m = 0, restart bytes,
             last_time of final outputs, oblique linear wave).
offers:      /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/ (athena_cpu,
             athena_gpu, READY with every new option and one example input each,
             COMMIT, SHA256SUMS, branches/READY.<branch>); release drivers
             tracks/core/analysis/release/{regress_v04,quick_v04,card_v04}.py
budget:      G2: 5.5 card-hours used by core's packages (nrpic-run budget, 2026-11-21);
             this package asked 0.2 card-hours (one job) of its one card-hour
