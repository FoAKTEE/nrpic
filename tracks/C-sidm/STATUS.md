# STATUS of C-sidm

gate:        G0 package written 2026-11-15 (tracks/C-sidm/stage/G0/), awaiting review;
             G1 not met (blocked on core's collision operator)
headline:    references, specification and tests of the collision operator, the spherical
             baseline (F21) and near-threshold particle models are done and cross-checked by
             independent solvers; no collisional run exists because core/collisions has no
             committed code yet
last-result: lead review: three independent equilibrium solvers agree to 3e-8 (F21 b = 0.1
             eps max at Z(0) = 0.5404; King y_max = 0.334032); closed-form Moller rate
             confirmed to 5e-7 by a 3D quadrature; fluid onset Z(0) = 0.6348 (b = 0.1,
             gamma = 1 + p/u) confirmed at two resolutions; Kn fixed as lambda_c/H_c with
             sigma~ = 168.9/Kn for the King threshold model (runs
             C-sidm-20261115-131130-3077a99, -131135-3077a99, -132327-eab8e41)
next:        1. when core commits the operator: T0, T1, T2, T10 on processors
                (collide/TESTS.md), then T3-T5, T9, T11; measure the cost per pair
             2. wave-2 card runs: collisionless monoenergetic threshold scan (6.6 card-h)
                and King b = 1 scouting (5.6); first collisional cluster runs CC1/CC2
                (stage/G1/STATUS.md section 4)
             3. F21 b = 0.1 particle models (evstatic with exp((1 - E/E0)/b) - 1); fluid onset
                with the Juttner Gamma_1; growth-rate pipeline on the first paper's runs
blockers:    core/collisions has no commit beyond the rng merge (core); card time beyond
             20 GPU-h for G2/G3 (orch); nrpic-run cannot read the hand manifests (orch)
needs:       core: commit the operator + interface + T0 (outbox ...__to-core__collision-operator);
             stream-2 table in rng.md (...__to-core__rng-stream2-table); perturbation recipe
             (...__to-core__perturbation-recipe); static curved metric for T12
             (...__to-core__static-curved-metric); view on a GR-hydro anchor
             (...__to-core__grhydro-reference)
             orch: brief corrections (...__to-orch__brief-corrections); card budget
             (...__to-orch__gpu-allotment); nrpic-run schema (...__to-orch__nrpic-run-manifest-schema)
             kb: literature fetch, index of locators and source typos (two outbox files)
             E-stoch-inf: info on stream 2 (...__to-E-stoch-inf__rng-stream2)
offers:      collision-operator specification and tests: tracks/C-sidm/collide/ (SPEC.md,
             TESTS.md, REFERENCES/ with 62 tests, test_vectors.json for core's T0);
             truncated Maxwell-Boltzmann solver with exact radial-pulsation FEM:
             tracks/C-sidm/gravothermal/tmb.py; static Einstein-Vlasov solver and exact
             samplers (King, polytropes, shells): tracks/C-sidm/equilibria/evstatic.py;
             13 near-threshold particle models (scratch/C-sidm/C-sidm-20261115-120610-b4592be)
budget:      0 GPU-hours used of 20 (coord/DECISIONS/0006); processors only so far
