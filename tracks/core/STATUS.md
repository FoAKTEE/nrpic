# STATUS of core

gate:        G2 in progress (package tracks/core/stage/G2/, not passed: ladder rows 3-4 PARTIAL, no tag yet)
headline:    the six wave-1 branches (rng, collisions, scalar field, initial data with
             extrinsic curvature, Bowen-York punctures, Newtonian mode) are merged into
             core/nrpic at 609a875 (proposed core-v0.3); the merged source reproduces
             twelve existing set-ups byte for byte and the verify suite to the printed
             digits, and every new capability passes its own tests.
last-result: byte regression baseline vs merged identical on 12 set-ups (processor runs
             core-20261115-145316..150256, -145323-5407341, -145448-3629622; card
             -145921-3629622, -150426-9377fe8); verify suite G 104/104, O 13/13, F 13/13,
             L 10/10 on the merged executables (core-20261115-065452/065901/065903/065904-
             3629622); combined format-2 + Bowen-York curvature adds to float32 rounding
             (core-20261115-150404-9377fe8); quick reruns of rng, collisions, scalar and
             Newtonian tests equal the branch numbers (tracks/core/stage/G2/EVIDENCE.md).
next:        1. ladder rows 3-4 on core-v0.3: prolate collapse at a second resolution and
                oblate collapse; bisection of the cluster stability threshold (about 2
                card-hours)
             2. the wave-2 source items the tracks wait for: initial slice at N* for E,
                lapse condition against the surface front for A and D, mass-scaled shift
                damping for F, collision energy correction with C, B's output requests
             3. finish the id analysis (T2d interior H, T3 crash) and the 13.4 figures,
                working note and verifier report of the G2 package
blockers:    tags core-v0.1/v0.2/v0.3 and the merge into main wait for the orchestrator
             (outbox 20261115T1510Z__to-orch__core-tags-v01-v02-v03.md)
needs:       orch: tags and merge; interface documents into coord/INTERFACES; anchor the
             runs/ ignore rule; docs/ ownership; CLAUDE.md "What exists" and executables
             (outbox 20261115T1510Z__to-orch__*). C, E, A, F: independent checks of the
             merged capabilities (outbox 20261115T1510Z__to-<track>__*). kb: paper
             metadata, Salmon et al. 2011.
offers:      core/nrpic at 609a875: <particles> collisions, <scalar_field> (with
             stochastic sources), nrpic_cf tables of format 2, Bowen-York punctures with
             puncture_setup, <particles> pusher = newton, utils/rng.hpp; executables
             wt/core/.work/build_cpu_609a875/src/athena, build_gpu_609a875/src/athena;
             interface documents tracks/core/interfaces/*.md; CHANGELOG tracks/core/CHANGELOG.md
budget:      about 3.4 GPU-hours used in wave 1 (lead 0.10, packages 3.3) of 40 to the next gate (decision 0006)
