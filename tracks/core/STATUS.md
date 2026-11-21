# STATUS of core

gate:        G2 in progress (package tracks/core/stage/G2/: OPEN carries core-v0.6,
             core-v0.5 and core-v0.4, EVIDENCE core-v0.4, the rest is of wave 1; ladder
             rows 3-4: verify/LADDER.md of wave 2)
headline:    release candidate core-v0.6 is written (tracks/core/RELEASE-v0.6.md, first
             line REGRESSION PASS): core/newton-2, core/z4c-faces and core/id-solver-2
             merged on top of core-v0.5, source commit 984bde68, four executables
             published in scratch/core/exe/core_nrpic_v06/. The card check of the merged
             card executable is queued (job 4800); the card executables of the three
             branches ran on a card and agree with processors. core/clump-table and
             core/oblate were not closed and are left out.
last-result: byte regression against core-v0.5 75 of 75 identical
             (core-20261121-130202-7cf7db8; MPI build core-20261121-132245-c02f6b7);
             quick tests 38 of 38 files identical with the branch executables and the
             release (core-20261121-130813-710b3cc); solver regressions repeated: id_far
             = robin gives the bytes of core-v0.5 for matter at rest, 79 of 79 files of
             eight second-pass cases identical (core-20261121-131148-6efd1b8,
             core-20261121-131250-f8df905); solved puncture with the faces options:
             record of the solve unchanged; card check Kc of the solver held
             (core-20261121-125651-edde517); faces k1 7.3e-12 from processors
             (core-20261121-083511-2cff9df); release card build of core-v0.5 PASS
             (core-20261121-075439-58c2787).
next:        1. job 4800 (run core-20261121-132052-f330004): nrpic-run finish, then
                card_v06.py and card_v05.py (commands in RELEASE-v0.6.md, section "Card
                check of athena_gpu"); outcome against prediction K6 of the journal into
                that section, into READY of core_nrpic_v06 and into the journal
             2. clerk: merge core/nrpic into main, tag core-v0.6, release builds,
                interface texts z4c_faces.md, id_solver2.md, REQUESTS_NEWTON2.md,
                newtonian_mode.md to coord/INTERFACES/, announce the default far field
                of id_solve
             3. next release: core/clump-table (near its end on 2026-11-21T13:37Z) and
                core/oblate (must merge main first); packages from REQUESTS_WAVE3.md
blockers:    none
needs:       orch/clerk: the merge and the tag (2). Tracks A, D, F: a slice solved by
             id_solve on a mesh with no periodic face changes against core-v0.5 (psi by
             1e-8 to 1.5e-6, W of moving matter by 2.7e-3 of its maximum); id_far = robin
             restores the old bytes for matter at rest.
offers:      scratch/core/exe/core_nrpic_v06/ (athena_cpu, athena_gpu, athena_cpu_omp,
             athena_cpu_mpi, READY with one example per new option); release drivers
             tracks/core/analysis/release/ (regress_v04, quick_v06, card_v06, card_v05,
             hst_pair_v06); CHANGELOG section core-v0.6 (26 options)
budget:      G2: 6.57 card-hours used by core, 0.60 reserved, 32.83 left (nrpic-run
             budget, 2026-11-21 13:42Z); this session used 0.024 (Kc) and reserved 0.3
             (job 4800)
