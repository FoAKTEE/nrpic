# STATUS of F-hills

gate:        G0 package submitted 2026-11-15 (stage/G0/SCOPING.md, EVIDENCE.md, OPEN.md; stage
             check not run); G1 in progress, not met (stage/G1/STATUS.md: 2 of 4 track criteria met)
headline:    Both baselines reproduce the literature (restricted Newtonian: 0911.1136/1804.02911;
             geodesic+Newtonian: 2404.16270), and at q = 10 they disagree in kind: for r_p = 7-12 M
             the geodesic model captures a member in 69-96 percent of phases, Newton in none; the
             first NR passage (q = 10, r_p = 8 M, 32-36 card-hours) is specified and tests this.
last-result: - lead checks V1-V4b: newton3 10/10 tests; geodesic_binary T1-T4 same numbers; scale
               estimate identical; restricted problem reproduced by independent code at nine
               (sense, D) points (runs F-hills-20261115-144857-b5b0bce ... -145544-a314517)
             - V5b: newton3's member energy (two-body with M) is not conserved at q = 10 when the
               other member is captured; conserved values +1.613 (q = 10) and +1.312 (q = 4) units,
               not +1.75/+1.53 (run F-hills-20261115-145559-a314517)
             - V6/V7: HRNA vs Newton for the G1 input and an r_p scan (runs
               F-hills-20261115-145251-090f5dc, -145915-71abf93; stage/G0/checks/figures/)
             - helpers: novelty verdict (novelty/NOVELTY.md), newton3 P0-P8, geodesic_binary
               T1-T4/S1-S4/C1-C2, three_punctures PLAN (inputs, measured MeshBlock trees)
next:        1. When core/multi-puncture is released: R0 (processors), R2, R4, then the passage P1
                (commands and predictions in stage/G1/STATUS.md).
             2. Fix newton3's finite-q energy (barycentric definition, V5b) and rerun finiteq, P3
                and the three_punctures scans; write the NR readers (trackers, horizons, energies).
             3. Second-agent check of the novelty verdict and of V6/V7; the 2402.02178 (inclined
                Kerr) comparison for F-pre-2.
blockers:    core/multi-puncture not released / not in CLAUDE.md (core, orch); G2/G3 compute beyond
             the allotment and q = 10 convergence beyond one card (orch/user, core)
needs:       outbox/20261115T1507Z__*: orch (l. 275 correction, allotment and mass ratio, 0005
             timing, second-agent check, start of P1); core (release, pairwise common horizon,
             unequal-mass gauge, two cards or 32^3 blocks, moving clump data, optional HRNA pair
             force); C-sidm (clump models); kb (index sources, four locators)
offers:      Newtonian three-body driver tracks/F-hills/newton3/hills3/threebody.py
             (initial_state_json gives barycentric positions/momenta for nrpic_cf; energies at
             finite q: use the barycentric definition until fixed); HRNA reference
             tracks/F-hills/geodesic_binary/hrna.py (Schwarzschild and Kerr-Schild); Hills inputs
             tracks/F-hills/three_punctures/inputs/*.athinput; measured MeshBlock trees for
             three-scale meshes (three_punctures runs -131109-634fb86, -131348-634fb86)
budget:      0 card-hours used of 40 (decision 0006); 6.8 processor core-hours in 71 manifests
             with wall times (the 7 novelty manifests carry none; seconds each)
