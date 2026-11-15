# Wave 1: what was started (2026-11-15T11:03Z)

Started by the orchestrator as one workflow. The first start (run wf_a60491aa-2e6) was
stopped after thirteen minutes and restarted (run wf_279f8732-d1e) with decision 0010:
one code base. The packages that the brief had as standalone prototypes (A newton, B
baseline, C collide, D spike and secondary_infall, E codebase and noise, F newton3) now
write specifications, semi-analytic references and tests, and core writes the capability
into AthenaK. At most sixteen agents
work at a time. Models: decision 0009. Every helper commits path-limited in its owner's
worktree; the lead of each owner checks the helpers' work, writes the stage package,
STATUS, JOURNAL, HANDOFF and outbox, and pushes the branch.

| Owner | Helpers (work packages) | Lead delivers |
|---|---|---|
| orch (main) | harness:context (nrpic-ctx, templates, nrpic-wt, nrpic-doctor, self-tests, BOARD); harness:runs+config (nrpic-run, nrpic-env, nrpic-stage, figure libraries, proposed Claude Code configuration under harness/claude/, not installed) | the orchestrator reviews |
| kb | K0-K1 (environment, schema, manifests, verify-downloads), then papers K2-K3 and code K6-K7 in parallel | gate package KB-G1: download report, ingestion of priority-3 papers, code and parameter index, first answers |
| core | doc (corrections to brief section 2, interface documents from the code); verify (ladder, regression suite, release proposal); six source items in AthenaK by Fable in temporary worktrees: id (initial data with extrinsic curvature, table format 2; branch core/id-extrinsic), rng (reproducible random numbers; core/rng), then on top of rng: coll (relativistic Monte Carlo collisions; core/collisions) and scalar (scalar field with stochastic hook; core/scalar-field); newton (Newtonian reference gravity for the same particles; core/newton); mp (several black holes with momentum and spin; core/multi-puncture) | merge of the source branches that pass, G2 report, changelog, tag proposal |
| A-emd-pbh | scope; expball (A-pre-1); criteria (A-pre-2); newton (A-pre-3); gauge (A-pre-4) | G0 package, G1 status |
| B-emd-gw | scope; periodic_z4c (B-pre-1); gw_diag (B-pre-3); baseline (B-pre-4); verify_cosmo (B-pre-2, B-pre-5 against cosmo/, first pancake) | G0 package, G1 status |
| C-sidm | scope; collide (C-pre-1, C-pre-2); gravothermal (C-pre-3); equilibria (C-pre-4) | G0 package, G1 status |
| D-bh-dress | scope; einstein_straus (D-pre-1); spike (D-pre-2); secondary_infall (D-pre-3); puncture_drift (D-pre-4) | G0 package, G1 status |
| E-stoch-inf | spec (E-pre-1); codebase (E-pre-2); langevin (E-pre-3); noise (E-pre-4) | G0 feasibility package with a recommendation for the group |
| F-hills | novelty (F-pre-5, scope); newton3 (F-pre-1); geodesic_binary (F-pre-2); three_punctures (F-pre-3, F-pre-4 plan) | G0 package, G1 status |

Shared inputs written by the orchestrator before the start: CLAUDE.md, the charter,
decisions 0001 to 0009, coord/INTERFACES/spherical_id_format2.md,
coord/notes/derivations_to_check.md (three derivations the tracks must re-derive),
harness/bin/nrpic-fetch-arxiv (the only way to download from arXiv).

Card time named in the tasks: core id, rng, coll, scalar, newton, mp 3 each, verify 2, lead 3; B verify_cosmo 1;
D puncture_drift 3 card-hours; everything else on processors.

After the wave the orchestrator reviews every stage package, accepts interface proposals
into coord/INTERFACES, merges core into main, creates the tags, regenerates the board and
writes the digest.
