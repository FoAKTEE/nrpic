# STATUS of core

gate:        G2 in progress (package tracks/core/stage/G2/: OPEN carries core-v0.5 and
             core-v0.4, EVIDENCE core-v0.4, the rest is of wave 1; ladder rows 3-4:
             verify/LADDER.md of wave 2)
headline:    release core-v0.5 is closed: its card executable passed the card check
             (K1 to K6), the release processor build gives the candidate's bytes on the
             twelve regression set-ups, the open card results of packages cosmo-amr and
             mpi are judged, every track has its answer on what core-v0.4 and core-v0.5
             serve, and scripts/submit_chain.sh survives outside kills (decision 0021
             item 6, tested). One card job is pending (release card build, job 4775).
last-result: card check of the candidate PASS (core-20261121-074846-e830785); release
             processor build against the candidate 75 of 75 identical
             (core-20261121-075456-a505400); cosmo-amr T14b case Sf PASS
             (core-20261121-075446-4944747), T10g judged (two of five predictions failed
             as written, core-20261121-075138-9b502d7); mpi job 4733: two cards hold the
             m/16 mesh (57.5 GB per card), the m/8 mesh runs at 0.66 of one card
             (core-20261121-080037-2ee9973); mpi P7g held; chain test PASS
             (core-20261121-080619-6a0793f; its first run failed through its own fake).
next:        1. job 4775 (run core-20261121-075439-58c2787): nrpic-run finish, then
                card_v05.py and card_pair.py against core-20261121-070946-1907f7b
                (HANDOFF.md); outcome into RELEASE-v0.5.md section "Release builds
                against the candidate" and the journal (prediction G of 07:47Z)
             2. clerk: merge core/nrpic into main (submit_chain.sh, docs/FORMATS.md, the
                interface texts changed today: cosmo_amr, mpi, collisions, cosmo_gauge,
                REQUESTS_ADF, REQUESTS_WAVE3)
             3. core-v0.6: finish core/id-solver-2, core/clump-table, core/newton-2,
                core/oblate, core/z4c-faces; new packages from REQUESTS_WAVE3.md (tracker
                file appended on restart W2, in-situ Fourier modes W18, relative lapse
                excision W15, finder hrms criterion W1, collisions on several ranks W22)
blockers:    none
needs:       orch/clerk: merge of core/nrpic into main after job 4775 is judged (or
             before: the source of the release does not change; only scripts/ does).
             Tracks: read the core-v04-v05-answers messages of 2026-11-21.
offers:      release executables .work/build_{gpu,cpu}_v05 (CLAUDE.md);
             scratch/core/exe/core_nrpic_v05/ (four executables, READY with the card
             check); triage tracks/core/interfaces/REQUESTS_WAVE3.md; release drivers
             tracks/core/analysis/release/ (regress_v04, quick_v05, card_v05, card_pair);
             scripts/tests/test_submit_chain.py
budget:      G2: 6.07 card-hours used by core, 0.72 reserved, 33.21 left (nrpic-run
             budget, 2026-11-21 08:15Z); this session reserved 0.1 (job 4775)
