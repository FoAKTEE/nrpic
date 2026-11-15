# Wave 2: what was started (2026-11-15T15:21Z)

Wave 1 returned with all 48 agents done; its integration is recorded in decisions 0011 to
0015, the tags core-v0.1, core-v0.2, core-v0.3 and the merge of core into main. Wave 2 is
one workflow (run wf_ff7cb963-6ef); the work packages are in
`scratch/orch/wave2_owners.json` (untracked) and summarised here.

| Owner | Helpers | Lead delivers |
|---|---|---|
| orch (main) | harness:fixes (nrpic-run and nrpic-stage after wave 1, fetch helper with metadata and PDF modes); harness:clerk (coord/BRIEF_ERRATA.md, derivations checked, board, digest 2026-W46, coord/REQUESTS.md) | the orchestrator reviews |
| kb | serve (pending requests, upstream check); claims (K8, K9); embed (K4, K5) | KB-G2 package or updated KB-G1 |
| core | seven source items in AthenaK by Fable, each on its own branch and publishing a tested executable under scratch/core/exe/: gauge (lapse for expanding matter, puncture in dust, mass-scaled shift damping), coll2 (collision energy defect, Track C's requests), scalar2 (initial slice at N*, constraint diagnostics, card build), bfix (Track B's requests: linear-wave generator, output for the wave analysis), dfix (tracer defect on cards, restart defect, accretion diagnostics, point mass in the Newtonian mode, pairwise common horizon), clump (curvature of moving clumps that satisfies the momentum constraint), idsolve (elliptic solve of the scalar constraint on the mesh); verify (ladder rows 3 and 4, open G2 items) | merge, byte regression, changelog, tag proposal core-v0.4, G2 package, answers to every request |
| A-emd-pbh | runs_ball (SR-1, SR-2 against the exact solution); periodic_threshold (design and two scouting runs); newton_scan; criteria2; note; verifier | stage packages G0, G1 |
| B-emd-gw | first_source (crossed-wave scan, gauge-or-wave check); newton_tests; note; verifier | stage packages G0, G1 |
| C-sidm | box_tests (collision operator of the release); models; threshold_scan (first cluster runs with collisions); note; verifier | stage packages G0, G1 |
| D-bh-dress | es_runs (black hole in the vacuum bubble and its vacuum control); kerr_spike; newton_infall; note; verifier | stage packages G0, G1 |
| E-stoch-inf | analysis; ladder (slow roll, waits for core's scalar executable); note; verifier | stage packages G0, G1 |
| F-hills | nr_first (constraints of three-black-hole data, two single-puncture runs, readers; passage P1 prepared); newton3_fix; second_check; note | stage packages G0, G1; may start P1 at mass ratio four |

Card time named in the tasks: core source items 1 each, verify 2.5, lead 2; A 3;
B 2; C 3; D 3; E 3; F 2 card-hours; P1 (about 15) only if the queue is empty at the end.
