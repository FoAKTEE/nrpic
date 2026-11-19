# G1 evidence of F-hills: artefacts with paths and run ids

Paths relative to the worktree root `wt/F-hills`. Manifests: `tracks/F-hills/runs/<run_id>/manifest.json`;
outputs: `/data/haiyangw/nrpic/scratch/F-hills/<run_id>/` (not in git). The criteria and their
state: `STATUS.md` beside this file. The wave-1 baselines (F-pre-1, F-pre-2, novelty, mesh plan)
and their runs are listed in `../G0/EVIDENCE.md`, which this file extends; the lead's checks of
wave 1 (V1-V7) are there too.

## F-pre-1 Newtonian baseline, corrected energies (newton3_fix, wave 2)

Code `newton3/hills3/threebody.py` (member_energies, classify, evolve_states), tests
`newton3/tests/test_hills3.py` (15), README section "Member energies at finite mass ratio".
Runs: tests F-20261115-174058-ad4fb17; old against corrected F-20261115-174139-3340bf3 (figure
redrawn F-20261115-175000-8e2ab28: `newton3/figures/fig_energy_definition.png`); P3 rerun
F-20261115-174142-0d549b5 (analysis F-20261115-175000-d2dc283); passages
F-20261115-174142-2a79515 (superseded: stalled trajectories counted as survivors),
F-20261115-174959-3188846, F-20261115-180351-b8eb386 (`newton3/results/passages.json`,
`figures/fig_passages.png`); finite q F-20261115-174959-9e8a361 (stopped: oversubscribed),
F-20261115-175232-d399e83 (analysis F-20261115-180351-440afa2; `figures/fig_finite_q.png`,
`fig_finite_q_definition.png`, `fig_full_vs_restricted.png`).
Lead: tests 15/15 F-20261119-145509-fb91531 (V10).

## F-pre-2 relativistic baseline (geodesic_binary, wave 1; second check, wave 2)

`../G0/EVIDENCE.md` section F-pre-2; second check `../G0/SECOND_CHECK.md` and its runs
F-20261115-175542-b49d687 (failed), F-20261115-175549-456bf4a, F-20261115-175614-5cc133d,
F-20261115-175620-df20ffe, F-20261115-175636-5432651, F-20261115-175637-a592d7a,
F-20261115-180835-66e13b2, F-20261115-181007-80649f5 (superseded), F-20261115-181106-52c4613.

## F-pre-3/F-pre-4: three-hole data, single punctures, readers, passage (nr_first, waves 2 and 2b)

Journal `nr_first/JOURNAL.md` (E1-E11), README `nr_first/README.md`.

| item | runs | outputs in git |
|---|---|---|
| E1 trees of the q = 4 data | F-20261115-173543-29e87e8 (stopped after part (a)); F-20261115-173106-57c4b4c, F-20261115-173112-a9e18a3 (stopped, incidents) | journal |
| E2 t = 0 constraints against resolution | F-20261115-173547-a02af7d, F-20261115-181053-d52f22d, F-20261115-181434-b9c8916 | `nr_first/figures/fig_c0_constraints.png`, `results/c0_constraints.json` |
| E3 single punctures S3, S2 (card) | F-20261115-173601-2fae2dc (failed: 1632 > 1600 slots); analyses F-20261119-143214-5f5dc3a, lead rerun F-20261119-145619-8246322 | `figures/fig_e3_single_gauge.png`, `results/e3_single_analysis.json` (from the rerun) |
| E3a analysis on core's run A | F-20261115-182100-613c9c6 | journal |
| S1 (m/16) | F-20261115-173606-efcbf69 (withdrawn before start) | journal |
| E4 readers | F-20261115-173719-923135a (failed prediction), F-20261115-173821-b2c969a, F-20261119-143507-d74f101, F-20261119-143508-5d90bbd, F-20261119-143627-1a84aa5, F-20261119-143632-0f6e57d, F-20261119-143633-dfd3607, F-20261115-181805-f9c3473 | `figures/fig_test_nrread_synthetic.png`, `results/test_nrread_synthetic.json`, `results/e4_test2_s3_s2.json`, `results/e4_test3_p1smoke.json` |
| E5 trackers across restarts | F-20261115-173930-deef41a, F-20261115-181049-ab04d03 | `scripts/athena_keep_trackers.sh`, journal |
| E6 baselines of P1 | F-20261115-174102-ffa764f | `figures/fig_baselines_p1.png`, `results/baselines_p1.json` |
| E7 P1 smoke (card) | F-20261115-174602-c6879fe; analyses F-20261119-143449-e7bf692, F-20261119-144544-d9c8542 | `figures/fig_e7_p1smoke.png`, `results/e7_p1smoke_analysis.json` |
| E8 finder of m2 at t = 0 | F-20261115-182223-17ca48a | journal |
| E9 passage analysis on synthetic files | F-20261115-183737-49f0a7f | journal |
| E10 S2g (card) | F-20261119-143443-f11ebb9 (pending, Slurm 4640); E10a F-20261119-144351-b448f38 | `figures/fig_e10a_s3_s2_compare.png`, `results/e10a_s3_s2_compare.json` |
| E11 why 1632 MeshBlocks | F-20261119-143851-47595bd (failed: header offset), F-20261119-143931-4fbf2d0, F-20261119-144024-988d5c9, F-20261119-144425-10a94b7 | `figures/fig_e11_tree_check.png`, `results/e11_tree_check.json`, `results/e11_tree_path.json` |
| C0 analysis scripts | F-20261115-174432-291868f | scripts |
| P1 passage (card chain) | F-20261119-150017-b45ec5f (Slurm 4650, submitted 15:00Z) | `STATUS.md` here |

## Lead's checks of wave 2b

`../REVIEW-wave2.md`; script `stage/review_wave2/review_check.py`; runs F-20261119-145434-82c05f2
(V8: S3/S2 and the smoke from the raw AthenaK files; `fig_review_nr.png` in the run directory),
F-20261119-145449-245e984 (V9: GR invariants of the start states; `fig_review_gr.png`),
F-20261119-145509-fb91531 (V10), F-20261119-145619-8246322 (E3 rerun).

## Working note (wave 2)

`note/main.pdf` (v0, G0 content and the baselines); runs F-20261115-174648-25514db (N1),
F-20261115-175639-ce844e5 (N2), F-20261115-180428-fc8172f (N3), F-20261115-180609-abc9f6e (N4).
The G1 results of the NR runs are not in the note yet.

## Not part of G1 (wave 3a, beside wave 2b)

The 1PN (EIH) three-body reference `eih/` of a wave-3a helper, with its own runs
(F-20261119-143503-3cd3592 onwards); handed to the next lead, not reviewed here.
