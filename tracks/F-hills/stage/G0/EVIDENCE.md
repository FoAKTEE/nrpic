# G0 evidence of F-hills: artefacts with paths and run ids

Paths relative to the worktree root `wt/F-hills`. Manifests: `tracks/F-hills/runs/<run_id>/manifest.json`
(force-added: `runs/` is in `.gitignore`); outputs: `scratch/F-hills/<run_id>/` (not in git).
Run ids use UTC except the novelty helper's seven (local time UTC-8, e.g. 045435 = 12:54:35 UTC).

## Scoping document of this gate

`tracks/F-hills/stage/G0/SCOPING.md` (problem, parameters, exit criteria, test plan, verified
references, risks, compute, lead's check). The file name `REPORT.md` asked by the task was refused
by the session's write tool (it rejects report-named files from sub-sessions); the content is the
same.

## Lead's checks (this session; predictions and outcomes in `tracks/F-hills/JOURNAL.md`)

| id | what | run | outputs in git |
|---|---|---|---|
| V1 | newton3 unit tests, 10/10 pass | F-hills-20261115-144857-b5b0bce | manifest |
| V2 | geodesic_binary T1, T2, T3, T4 re-run, same numbers | F-hills-20261115-144919-b5b0bce, -144922-, -144927-, -144935-b5b0bce | manifests |
| V3 | novelty scale estimate re-run, 905 numbers identical | F-hills-20261115-144954-b5b0bce | manifest |
| V4 | independent restricted parabolic problem vs newton3 at nine (sense, D) | F-hills-20261115-145246-090f5dc | `stage/G0/checks/v4_summary.json`, `checks/figures/fig_v4_restricted.png` |
| V4b | the same with wide-bound samples run to 300 r_t, at retrograde D = 0.3 and 0.38 only (correction of 2026-11-19: "all nine agree" was wrong; retrograde D = 0.1, 0.2 rest on V4 with dP 0.0023, 0.0063) | F-hills-20261115-145544-a314517 | `checks/v4b_summary.json` |
| V5, V6 | full Newton and HRNA from the two input files; phase scans | F-hills-20261115-145251-090f5dc | `checks/v5v6_summary.json`, `checks/figures/fig_v5v6_q10.png`, `fig_v5v6_q4.png` |
| V5b | ejected member's energy: two-body with M oscillates, barycentric constant | F-hills-20261115-145559-a314517 | `checks/v5b_summary.json`, `checks/figures/fig_v5b_energy.png` |
| V7 | r_p scan q = 10 (7-13 M) and q = 4 (9.8-16 M): full Newton, fixed-hole Newton, HRNA | F-hills-20261115-145915-71abf93 | `checks/v7_summary.json`, `checks/figures/fig_v7_rp_scan.png` |

Script of all lead checks: `tracks/F-hills/stage/G0/checks/lead_checks.py` (subcommands v4, v4b, v5v6,
v5b, v7); interpreter `scratch/F-hills/venv-gb/bin/python` (uv venv with numba, numpy, scipy,
matplotlib).

## F-pre-5 novelty search and scale (helper `novelty/`)

- Verdict and closest papers: `tracks/F-hills/novelty/NOVELTY.md`; search log
  `novelty/search/SEARCH_LOG.md` (25 INSPIRE and 7 web queries, limits stated).
- Scale estimate: run F-hills-20261115-045435-f62d553, `novelty/results/scale_F-hills-20261115-045435-f62d553.json`,
  figures `novelty/figures/fig_scale_plane.png`, `fig_rmb_check.png`, `fig_pdis_q10.png`.
- Cost model (superseded for object (a) by three_punctures): runs F-hills-20261115-045438-f62d553,
  F-hills-20261115-045918-e7d0a66; `novelty/results/cost_*.json`, `novelty/figures/fig_cost.png`.
- Failed run on record: F-hills-20261115-045124-ae6bca8 (`python3 -I` hid numpy); superseded:
  -045332-ae6bca8, -045407-bf52f4e, -045410-bf52f4e.
- Draft scope used for this package: `novelty/scope/SCOPE.md`.

## F-pre-1 Newtonian baseline (helper `newton3/`)

- Code: `newton3/hills3/{integrate,orbits,restricted,threebody,reference}.py`; tests `newton3/tests/test_hills3.py`.
- Results with runs: `newton3/README.md` (tables P0-P8), `newton3/results/*.json`, figures `newton3/figures/`.
- Key runs: coplanar scan F-hills-20261115-130237-cbfaf6b (+ deep F-hills-20261115-132156-efddfc0,
  analysis -133222-9cb10db); general F-hills-20261115-130239-cbfaf6b (+ -132159-efddfc0, analysis
  -133200-05ee76a); SKR curves -132703-0bfc352; BKRS and H1 -132942-2f7ad7f; full vs restricted
  -130630-c1d003c (analysis -133203-05ee76a); finite q -132019-bfe00a9 (analysis -133207-05ee76a);
  start distance -131801-907e5fe (analysis -133205-05ee76a); convergence -131754-907e5fe,
  -132433-7d0c6dd; tests -130253-6fc800e, -133436-8bfc259; example -132240-42345c2.
- Failed analysis runs on record: -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889.

## F-pre-2 relativistic baseline (helper `geodesic_binary/`)

- Code: `geodesic_binary/hrna.py`, `scan.py`, tests `geodesic_binary/tests/t1..t4_*.py`.
- Results with runs: `geodesic_binary/README.md`, `geodesic_binary/JOURNAL.md`, `geodesic_binary/results/*.json`,
  figures `geodesic_binary/figures/` (14 PNG).
- Key runs: T1 F-hills-20261115-125915-9518508, T2 -125918-9518508, T1b -130007-80eb1b9, T3
  -130124-76059c5, T4 -133219-90eeecd; S1 -130405-ce17dcf (analysis -142554-c10b371); single
  encounters -130724-982aba0, -134350-d16b473; S2 -134255-a3c22f8; S3 -130922-634fb86; S4
  -133124-c799a81; C1 -142810-aad3f24 (analysis -143837-0fa01c7); C2 -135732-cace755 (analysis
  -144217-0fa01c7).
- Failed runs on record: -125858-0232c4c (T1), -131944-360a12e (S4 first attempt), -143824-2c937bc.

## F-pre-3/F-pre-4 plan (helper `three_punctures/`)

- Plan: `three_punctures/PLAN.md`; inputs `three_punctures/inputs/hills_q10_m8.athinput`,
  `hills_q4_m8.athinput`, `junk_single_P028.athinput`; figures `three_punctures/figures/`.
- Runs: Newtonian phase scans F-hills-20261115-130342-0471114, -130755-982aba0 (q = 10),
  -131832-907e5fe, -131933-907e5fe (q = 4); MeshBlock trees -131109-634fb86, -131348-634fb86;
  junk analysis of core's card runs -131605-634fb86; plan numbers -132220-efddfc0, -132430-7d0c6dd.
- Note: commit 0fae693 also carries the sibling manifests -131944-360a12e and -132433-7d0c6dd
  (contents unchanged).

## Core artefacts read (branch `core/multi-puncture`, read with `git show`)

`tracks/core/interfaces/multi_puncture.md` (parameters, cost, tests, open items),
`tracks/core/JOURNAL-mp.md`, `problems/puncture/by_triple.athinput`; core runs cited there.

## Wave 2 (helpers, 2026-11-15) and wave 2b (2026-11-19)

Review by the lead: `../REVIEW-wave2.md`; predictions and outcomes of the lead's checks V8-V11 in
`tracks/F-hills/JOURNAL.md` (lead, wave 2b).

| package | what | runs |
|---|---|---|
| second check (`SECOND_CHECK.md`, `JOURNAL.md`, `second_check/`) | novelty verdict, independent baselines, capture plane, start state in GR | F-20261115-175542-b49d687 (failed), F-20261115-175549-456bf4a, F-20261115-175620-df20ffe, F-20261115-175614-5cc133d, F-20261115-180835-66e13b2, F-20261115-175636-5432651, F-20261115-175637-a592d7a, F-20261115-181007-80649f5 (superseded), F-20261115-181106-52c4613 |
| newton3_fix (`newton3/`) | Jacobi-split member energies, tests, passages, finite-q rerun, puncture input | F-20261115-174058-ad4fb17, F-20261115-174139-3340bf3, F-20261115-174142-0d549b5, F-20261115-174142-2a79515 (superseded), F-20261115-174959-3188846, F-20261115-174959-9e8a361 (stopped), F-20261115-175000-8e2ab28, F-20261115-175000-d2dc283, F-20261115-175232-d399e83, F-20261115-180351-440afa2, F-20261115-180351-b8eb386 |
| note (`note/`) | working note v0, figures, ledger, claims check | F-20261115-174648-25514db, F-20261115-175639-ce844e5, F-20261115-180428-fc8172f, F-20261115-180609-abc9f6e |
| nr_first (`nr_first/`, wave 2) | mesh probe, t = 0 constraints, readers, tracker wrapper, baselines, finder, card batches | F-20261115-173106-57c4b4c, F-20261115-173112-a9e18a3, F-20261115-173543-29e87e8, F-20261115-173547-a02af7d, F-20261115-173601-2fae2dc (card, failed: slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a (failed), F-20261115-173821-b2c969a, F-20261115-173930-deef41a, F-20261115-174102-ffa764f, F-20261115-174432-291868f, F-20261115-174602-c6879fe (card smoke), F-20261115-181049-ab04d03, F-20261115-181053-d52f22d, F-20261115-181434-b9c8916, F-20261115-181805-f9c3473, F-20261115-182100-613c9c6, F-20261115-182223-17ca48a, F-20261115-183737-49f0a7f |
| nr_finish (`nr_first/`, wave 2b) | E3, E7, E10a, E11 outcomes; reader fix; S2g and P1 submitted | F-20261119-143214-5f5dc3a, F-20261119-143443-f11ebb9 (S2g, card, pending), F-20261119-143449-e7bf692, F-20261119-143507-d74f101, F-20261119-143508-5d90bbd, F-20261119-143627-1a84aa5, F-20261119-143632-0f6e57d, F-20261119-143633-dfd3607, F-20261119-143851-47595bd (failed), F-20261119-143931-4fbf2d0, F-20261119-144024-988d5c9, F-20261119-144351-b448f38, F-20261119-144425-10a94b7, F-20261119-144544-d9c8542 |
| lead, wave 2b | V8 raw-file recheck, V9 GR reading, V10 newton3 tests, E3 rerun; P1 chain | F-20261119-145434-82c05f2, F-20261119-145449-245e984, F-20261119-145509-fb91531, F-20261119-145619-8246322, F-20261119-150017-b45ec5f (P1, card chain) |
