# STATUS of core

gate:        G2 in progress (package tracks/core/stage/G2/: OPEN carries core-v0.5 and
             core-v0.4, EVIDENCE core-v0.4, the rest is of wave 1; ladder rows 3-4:
             verify/LADDER.md of wave 2)
headline:    release candidate core-v0.5 is written: core/scalar-3, core/build-openmp,
             core/cosmo-amr and core/mpi are merged into core/nrpic on top of release
             core-v0.4, source commit c3eb42e0, none of the four left out; the byte
             regression against core-v0.4 passes (tracks/core/RELEASE-v0.5.md). Four
             executables are published; the card one has not run on a card yet.
last-result: byte regression on processors, twelve set-ups: 75 of 75 items identical
             for the serial build (run core-20261121-063859-e410ee3) and for the MPI
             build without mpirun (core-20261121-065743-1202666); the threaded build
             at one thread: 31 of 75, the rest at rounding level (my prediction
             failed; core-20261121-070623-077b056). Quick tests PASS: 23 files of five
             examples identical to the branch executables; threaded deposit with and
             without the fine shape repeats bit for bit at 4 threads; swarm and
             cluster on 1 and 2 ranks give the package's files (runs
             core-20261121-065009-29b855c, judged in core-20261121-065726-bf06a85).
             T14b of package cosmo-amr judged from its finished card job: held
             (core-20261121-063923-5ed0a51).
next:        1. card check of athena_gpu: Slurm job 4772 (run
                core-20261121-070946-1907f7b): nrpic-run finish, then card_v05.py
                (HANDOFF.md); write the outcome into RELEASE-v0.5.md, the READY and
                the journal
             2. release clerk: merge core/nrpic into main, tag core-v0.5, build
                .work/build_{gpu,cpu}_v05, copy the interface documents, announce the
                five things that act without an option (CHANGELOG.md)
             3. core-v0.6: finish and merge core/id-solver-2, core/clump-table,
                core/newton-2, core/oblate, core/z4c-faces; port to several ranks what
                stops there (OPEN.md item c); the source items of OPEN.md k and l
blockers:    none for the release record; the card check waits for the queue
needs:       orch/clerk: tag core-v0.5 and release executables after the card check;
             CLAUDE.md "What exists" row for core-v0.5. Tracks: exit status 3 is the
             guard's stop; the finder's summary and the tracker file now lie in the
             -d directory; athena_cpu_omp is not a byte reference. Packages cosmo-amr
             and mpi: write the outcomes of T14b/T10g and of P7g and job 4733 into
             their journals (the lead judged T14b and read P7g, RELEASE-v0.5.md).
offers:      /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/ (athena_cpu,
             athena_gpu, athena_cpu_omp, athena_cpu_mpi, READY with every new option
             and one example input each, COMMIT, SHA256SUMS, branches/READY.<branch>);
             release drivers tracks/core/analysis/release/{regress_v04,quick_v05,
             card_v05}.py and card_v05.list
budget:      G2: 5.61 card-hours used by core's packages, 1.10 reserved (nrpic-run
             budget, 2026-11-21); this package used none yet and reserved 0.2 (job
             4772) of its one card-hour
