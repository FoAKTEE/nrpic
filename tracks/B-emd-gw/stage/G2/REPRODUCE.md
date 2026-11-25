# Reproducibility list of gate G2 (C6)

Written by the lead of batch 21 (2026-11-25) from the run manifests under `tracks/B-emd-gw/runs/`.
Each row: what the run establishes, its run id, the commit it ran at, the launcher, the command
(first words; the full command, the inputs with sha256 and the output checksums are in the manifest),
and the executable where the manifest names one. To repeat a run: check out the commit in a
worktree, then `harness/bin/nrpic-run submit --kind scouting --gate G2 --package <the package>
-- <the command>` (card runs through `harness/bin/nrpic-queue add`); outputs land under
`scratch/B-emd-gw/<new run id>/` and compare against the recorded `sha256sums.txt` (processor runs
repeat byte for byte; card runs with deposition do not, CLAUDE.md).

| What | Run | Commit | Launcher | Command (start) | Executable |
|---|---|---|---|---|---|
| FLRW dust, 128 cells to a = 1000 (C7) | `B-20261121-202335-3e6a898` | 3e6a8982f | chain | `scripts/submit_chain.sh $S/B-20261121-202335-3e6a898 wt/B-emd-gw/tracks/B-emd-gw/flrw_conv/inputs/mode_prod...` | `.work/build_gpu_v03/src/athena` (f9f2dc1273) |
| shearing dust, first judged series (C1, C9) | `B-20261123-015919-dec4392` | dec4392fd | local | `python3 tracks/B-emd-gw/shear/scripts/summarize_series.py $S/B-20261121-202830-417af0c` | - |
| shearing dust L2, narrow fans (C1, C9) | `B-20261124-134209-4584052` | 45840526b | local | `python3 tracks/B-emd-gw/shear/scripts/run_cases.py --list tracks/B-emd-gw/shear/inputs/series3.txt --npar 3...` | `.work/build_cpu_v06/src/athena` (91fc59b392) |
| shearing dust L2, 4 per cell, N_y = 64-256 (C2) | `B-20261124-140856-911ded9` | 911ded992 | local | `python3 tracks/B-emd-gw/shear/scripts/run_cases.py --list tracks/B-emd-gw/shear/inputs/series6.txt --npar 1...` | `.work/build_cpu_v06/src/athena` (91fc59b392) |
| population GR, sigma1 = 0.014, zero shift (C4) | `B-20261123-014847-f295ab4` | f295ab46b | chain | `scripts/submit_chain.sh $S/B-20261123-014847-f295ab4 wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_gr_r...` | `.work/build_gpu_v06/src/athena` (ea47349850) |
| population GR, sigma1 = 0.028, zero shift (stop) | `B-20261123-035002-bcc82bd` | bcc82bd7d | chain | `scripts/submit_chain.sh $S/B-20261123-035002-bcc82bd wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_gr_r...` | `.work/build_gpu_v06/src/athena` (ea47349850) |
| population restarts X0-X3 from t = 8 | `B-20261124-210432-6c4d005` | 6c4d005db | batch | `scripts/gpu_batch.sh $S/B-20261124-210432-6c4d005/batch.list` | `.work/build_gpu_v06/src/athena` (ea47349850) |
| population gauge leg, Gamma driver | `B-20261124-210431-6bf48af` | 6bf48af9c | chain | `scripts/submit_chain.sh $S/B-20261124-210431-6bf48af wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_gr_r...` | `.work/build_gpu_v06/src/athena` (ea47349850) |
| population particle leg, 8 per cell (cut) | `B-20261124-223926-33194d9` | 33194d9e7 | chain | `scripts/submit_chain.sh $S/B-20261124-223926-33194d9 wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_gr_r...` | `.work/build_gpu_v06/src/athena` (ea47349850) |
| Newtonian mode, same particles, 0.014 | `B-20261124-172958-fc4a2cf` | fc4a2cfa0 | local | `.work/build_cpu_v06/src/athena -i wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_newton128.athinput -d $...` | - |
| Newtonian mode, same particles, 0.028 | `B-20261124-172958-73b0662` | 73b06621f | local | `.work/build_cpu_v06/src/athena -i wt/B-emd-gw/tracks/B-emd-gw/population/inputs/pop_newton128.athinput -d $...` | - |
| analysis, zero-shift GR runs | `B-20261124-131918-e71996f` | e71996fed | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --run s014:$S/B-20261123-014847-f295ab4:0.014 --ru...` | - |
| analysis, gauge leg | `B-20261125-115558-2ab4161` | 2ab416134 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --run gd:$S/B-20261124-210431-6bf48af:0.014 --newt...` | - |
| analysis, the 0.028 stop | `B-20261125-115619-ad8b3f4` | ad8b3f4d3 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_stop028.py --base $S/B-20261123-035002-bcc82bd --cases $...` | - |
| comparison of the legs | `B-20261125-121830-9ecb59c` | 9ecb59ca4 | local | `python3 tracks/B-emd-gw/population/scripts/compare_legs.py --base $S/B-20261124-131918-e71996f/analysis_gr_...` | - |
| analysis, Newtonian mode | `B-20261125-122434-060d53d` | 060d53d80 | local | `python3 tracks/B-emd-gw/population/scripts/analyze.py --case=newton_s014:$S/B-20261124-172958-fc4a2cf/newto...` | - |
| GR against Newton, zero shift | `B-20261125-165836-70b17b6` | 70b17b6c8 | local | `python3 tracks/B-emd-gw/population/scripts/compare_newton.py --gr $S/B-20261124-131918-e71996f/analysis_gr_...` | - |
| GR against Newton, Gamma driver | `B-20261125-165845-0621554` | 062155410 | local | `python3 tracks/B-emd-gw/population/scripts/compare_newton.py --gr $S/B-20261125-115558-2ab4161/analysis_gr_...` | - |
| band test of N4 | `B-20261125-170116-0b635a0` | 0b635a018 | local | `python3 tracks/B-emd-gw/population/scripts/n4_band.py --newton $S/B-20261125-122434-060d53d/analysis_n128.j...` | - |
| same particles, one estimator | `B-20261125-170535-84c9ba5` | 84c9ba525 | local | `python3 tracks/B-emd-gw/population/scripts/vel_check.py --gr $S/B-20261123-014847-f295ab4 --newton $S/B-202...` | - |
| note: figures, schematics, ledger | `B-20261125-171148-563a6f0` | 563a6f027 | local | `.venv/bin/python tracks/B-emd-gw/note/scripts/run_all.py` | - |

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw/`. Decks: `tracks/B-emd-gw/population/inputs/`,
`tracks/B-emd-gw/flrw_conv/inputs/`, `tracks/B-emd-gw/shear/inputs/`; scripts: the `scripts/` directory of each
package; note: `tracks/B-emd-gw/note/scripts/run_all.py` (one script per figure). Open: the runs still in the
queue (q0007, q0042, q0044) are added when they end.
