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
| radiated box measure, N4 second part | `B-20261125-172136-3e920ab` | 3e920ab | local | `python3 tracks/B-emd-gw/population/scripts/n4_rad.py --n128 $S/B-20261125-122434-060d53d/analysis_n1...` | - |
| mesh leg 256^3, zero shift (q0007; guard stop a = 102, closed failed) | `B-20261125-093500-242d3a3` | 242d3a3 | chain | `scripts/submit_chain.sh $S/B-20261125-093500-242d3a3 ...` | `.work/build_gpu_v06/src/athena` |
| particle leg continued, 8 per cell (q0042) | `B-20261125-221742-5100a22` | 5100a22 | batch | `scripts/gpu_batch.sh $S/B-20261125-221742-5100a22/batch.list` | `.work/build_gpu_v06/src/athena` |
| 0.028 box, Gamma driver from t = 8 (q0044) | `B-20261126-011415-449c8ce` | 449c8ce | batch | `scripts/gpu_batch.sh $S/B-20261126-011415-449c8ce/batch.list` | `.work/build_gpu_v06/src/athena` |
| gauge at a second mesh: 256^3, Gamma driver (q0060) | `B-20261126-105021-6343c13` | 6343c13 | chain | `scripts/submit_chain.sh $S/B-20261126-105021-6343c13 ...` | `.work/build_gpu_v07/src/athena` |
| equal-mass analysis of the 256^3 zero-shift leg (M2, M3) | `B-20261126-022356-52c2460` | 52c2460 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --equal-mass --no-stop --no-figures --worke...` | - |
| equal-mass analysis of the shifted 0.028 box (S2, S3) | `B-20261126-022403-82f6e69` | 82f6e69 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --equal-mass --no-figures --workers 2 --run...` | - |
| equal-mass halo catalogues of base and gauge leg | `B-20261126-022407-87e8803` | 87e8803 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --equal-mass --halos-only --no-figures --wo...` | - |
| equal-mass analysis of the joined particle leg (Q1) | `B-20261126-022838-27fab1b` | 27fab1b | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --equal-mass --no-figures --workers 1 --tim...` | - |
| histories of six legs (M1, M4, P8C2, Q1, S1) | `B-20261126-024849-87e72b7` | 87e72b7 | local | `python3 tracks/B-emd-gw/population/scripts/fig_leg_histories.py $S $NRPIC_RUN_DIR` | - |
| GR against Newton, equal masses, zero shift (N2e, GN1e) | `B-20261126-024936-1ee0a16` | 1ee0a16 | local | `python3 tracks/B-emd-gw/population/scripts/compare_newton.py --gr $S/B-20261126-022407-87e8803/analy...` | - |
| GR against Newton, equal masses, Gamma driver | `B-20261126-024941-647553b` | 647553b | local | `python3 tracks/B-emd-gw/population/scripts/compare_newton.py --gr $S/B-20261126-022407-87e8803/analy...` | - |
| note: figures, schematics, ledger (batch 23) | `B-20261126-025137-7686b91` | 7686b91 | local | `python3 tracks/B-emd-gw/note/scripts/run_all.py` | - |
| histories of seven legs (GM1, GM4) | `B-20261126-212502-e9e4f4e` | e9e4f4e | local | `python3 tracks/B-emd-gw/population/scripts/fig_leg_histories.py $S $NRPIC_RUN_DIR` | - |
| legs against the base, equal-mass halos (M2, M3, Q1 high-k) | `B-20261126-212541-b647c59` | b647c59 | local | `python3 tracks/B-emd-gw/population/scripts/compare_legs.py --base $S/B-20261124-131918-e71996f/analy... --halo-base ...` | - |
| shifted 0.028 box at the same stage (S2, S3) | `B-20261126-212604-a508e94` | a508e94 | local | `python3 tracks/B-emd-gw/population/scripts/judge_s028gd.py $S/B-20261126-022403-82f6e69/analysis_gr_...` | - |
| equal-mass analysis of the 256^3 Gamma-driver box (GM2, GM3; running at the end of batch 28) | `B-20261126-212212-c54d979` | c54d979 | local | `python3 tracks/B-emd-gw/population/scripts/analyze_gr.py --equal-mass --no-stop --no-figures --workers 5 ...` | - |

`$S` = `/data/haiyangw/nrpic/scratch/B-emd-gw/`. Decks: `tracks/B-emd-gw/population/inputs/`,
`tracks/B-emd-gw/flrw_conv/inputs/`, `tracks/B-emd-gw/shear/inputs/`; scripts: the `scripts/` directory of each
package; note: `tracks/B-emd-gw/note/scripts/run_all.py` (one script per figure). Batch 28 added the rows of
batches 23 and 28 (commit column: the run id's suffix, the commit the run was registered at).
