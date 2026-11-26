# Rerun list of gate G2 (item C6)

Every number of the G2 package comes from one of the registered runs below. Each row gives the run id, its
kind, its status and the command as its manifest records it (run from the worktree root of `track/A-emd-pbh` at
the commit the manifest names; card runs went through the shared queue). Written by the lead of batch 28 from the
manifests under `tracks/A-emd-pbh/runs/`; `nrpic-stage verify` re-runs the note scripts and `VERIFY`.

## C1 (i), C2, C7, C8: expanding ball, mesh/particle/radius/boundary legs

| run | kind | status | command |
|---|---|---|---|
| A-20261121-120257-a2eb839 | scouting / local | completed | `python tracks/A-emd-pbh/conv_ball/scripts/analyse.py --card /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-083336-6a82131:C --prior A=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-085252-f4ed504/A_numbers.json --prior B=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-085252-f4ed504/B_numbers.json --prior A-L32=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-085252-f4ed504/A-L32_numbers. ...` |
| A-20261125-151126-7f79a83 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/c18_answer.py --out "$NRPIC_RUN_DIR" --jobs 4` |

## C1 (i): threshold of the ball, eight amplitudes; C-d0.42 on M/64

| run | kind | status | command |
|---|---|---|---|
| A-20261124-131120-5c974ce | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/analyse.py --out "$NRPIC_RUN_DIR" --jobs 4 --member B-d0.42 --member B-d0.40 --member A-d0.42 --member A-d0.40 --member B-d0.45 --member B-d0.50 --member B-d1.00 --member B-d0.70 --member B-d0.35 --member B-d0.20 --member C-R1.25` |
| A-20261125-115027-17b419e | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/analyse.py --out "$NRPIC_RUN_DIR" --jobs 2 --member C-d0.42 --member B-d0.42` |

## C1 (iii): Szekeres readers (N64/N128, N128/N256, N256 tau 30 and 40)

| run | kind | status | command |
|---|---|---|---|
| A-20261126-024724-425ed7f | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/szekeres/scripts/analyse_code_runs.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/szk_members_b23 --prep /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241 --members N64 N128 --label n64n128` |
| A-20261126-023245-1dd80ad | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/szekeres/scripts/analyse_code_runs.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/szk_members_b23 --prep /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241 --members N128 N256 --label n128n256` |
| A-20261126-212138-49b9a2d | scouting / local | running | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/szekeres/scripts/analyse_code_runs.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/szk_members_b28 --prep /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241 --members N256t30=N256 --label n256t30` |
| A-20261126-212141-7eeb046 | scouting / local | running | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/szekeres/scripts/analyse_code_runs.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/szk_members_b28 --prep /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241 --members N256t40=N256 --label n256t40` |

## C1 (iii): Szekeres card runs

| run | kind | status | command |
|---|---|---|---|
| A-20261125-213939-0ad9f29 | scouting / batch | failed | `scripts/gpu_batch.sh /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-213939-0ad9f29/batch.list` |
| A-20261125-231808-0784bc9 | scouting / chain | completed | `scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-231808-0784bc9 /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/szekeres/inputs/szekeres_geodesic_card.athinput mesh/nx1=256 mesh/nx2=256 mesh/nx3=256 meshblock/nx1=128 meshblock/nx2=128 meshblock/nx3=128 problem/id_file=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223422-8cc4241/N256/fields.bin particles/particle_fil ...` |

## C1 (ii): P0L6 against LTB, finder status

| run | kind | status | command |
|---|---|---|---|
| A-20261125-044641-7d5bd16 | scouting / chain | completed | `scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-044641-7d5bd16 /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak6.athinput problem/id_file=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3/fields.bin particles/particle_file=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3/particles_track ...` |
| A-20261126-022753-f9e9c40 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/line_trapped.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-044641-7d5bd16 --label P0L6 --out "$NRPIC_RUN_DIR/D2" > "$NRPIC_RUN_DIR/D2.log" 2>&1; OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/compare_ltb.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-044641-7d5bd16 --re ...` |

## C1 (iv) A2: S1L crossing (shift-invariant), probe, Newtonian controls

| run | kind | status | command |
|---|---|---|---|
| A-20261126-022438-a08cc5f | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_invariant.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261123-025907-97bab8d --out "$NRPIC_RUN_DIR"` |
| A-20261126-023551-f800cf5 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_probe_check.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261123-025907-97bab8d --out "$NRPIC_RUN_DIR"` |
| A-20261126-022631-dafbb4f | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_crossing.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160633-e38d321/N-z128 --clock newton --label 'N-z128 (Newton)' --out "$NRPIC_RUN_DIR/N-z128" > "$NRPIC_RUN_DIR/N-z128.log" 2>&1 && OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_compare.py --gr /data/haiyangw/nrpic/scratc ...` |

## C1 (iv) A2H: S1L-h run and its three readings (figure reruns with labels)

| run | kind | status | command |
|---|---|---|---|
| A-20261126-125306-0653547 | scouting / chain | completed | `scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput problem/id_file=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-032537-f1060e7/S_mu0.15/fields.bin particles/particle_file=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-032537-f1060e7/S_mu0.15/particles.nrp ti ...` |
| A-20261126-213147-f274b2e | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_invariant.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 --out "$NRPIC_RUN_DIR" --reference 12.3 --band 12.5 15.2` |
| A-20261126-213150-1441107 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_crossing.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 --out "$NRPIC_RUN_DIR" --label S1L-h` |
| A-20261126-213153-563fb0a | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_probe_check.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 --out "$NRPIC_RUN_DIR" --tmax 220` |
| A-20261126-213414-261dd64 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_invariant.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 --out "$NRPIC_RUN_DIR" --reference 12.3 --band 12.5 15.2 --label S1L-h` |
| A-20261126-213459-0ce5ee6 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/periodic_threshold/scripts/a2_crossing.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261126-125306-0653547 --out "$NRPIC_RUN_DIR" --label S1L-h --band 12.5 15.2 --reference 12.3` |

## C3: constraint norms, K4, smoothed edge (mesh leg G, particle leg H)

| run | kind | status | command |
|---|---|---|---|
| A-20261124-132342-d5dc06e | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/constraint_conv.py --out "$NRPIC_RUN_DIR"` |
| A-20261125-150851-5545f8e | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/k4_compare.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-120525-8fb946e --out "$NRPIC_RUN_DIR"` |
| A-20261126-022624-c663e0f | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/edge_compare.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160633-594a474 --extra S2c-A0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-161154-62ce3dc/S2c-A0 --extra S2c-B0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-161154-62ce3dc/S2c-B0 --extra S2c-A=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125 ...` |
| A-20261126-024922-97a2f14 | scouting / local | completed | `bash tracks/A-emd-pbh/threshold_ball/scripts/edge_n8.sh $NRPIC_RUN_DIR` |
| A-20261126-212340-4ea9fb2 | scouting / local | completed | `bash -c OMP_NUM_THREADS=1 python -I tracks/A-emd-pbh/threshold_ball/scripts/edge_compare.py --run /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160633-594a474 --extra S2c-A0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-161154-62ce3dc/S2c-A0 --extra S2c-A=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-161154-62ce3dc/S2c-A --extra S2c-B=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-1 ...` |

## C5, C10, C11, C13, C16, C17: note figures, schematics, ledger

| run | kind | status | command |
|---|---|---|---|
| A-20261126-213903-08eaf25 | scouting / local | running | `bash -c OMP_NUM_THREADS=1 .venv/bin/python tracks/A-emd-pbh/note/scripts/run_all.py --out "$NRPIC_RUN_DIR"` |

