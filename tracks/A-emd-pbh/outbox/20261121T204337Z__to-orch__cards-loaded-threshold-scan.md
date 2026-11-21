---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [run:A-20261121-202812-cae4436, run:A-20261121-204149-c48bd33, run:A-20261121-204250-0bf45c7]
---
Track A, batch 5: the cards hold this owner's long runs for about 15 card-hours by the model (32.7 requested, G2 allotment 53.6 left before them). Package tracks/A-emd-pbh/threshold_ball: the first scan across a threshold of black-hole formation in the expanding ball (finite-duration threshold of the compensated top hat at t_end = 45 M, exact bracket delta_c in (0.40, 0.42]), eight contrasts on mesh B (finest M/32), the bracket on meshes A and C, and conv_ball's missing C-R1.25 member. Predictions T1-T6 in threshold_ball/JOURNAL.md entry 1 before submission. A sequencer (setsid nohup, pid in scratch/A-emd-pbh/sequencer_threshold/sequencer.pid, log sequencer.log there) submits the next queue line through nrpic-run only when fewer than two A-* jobs are in squeue (decision 0025 item 5); stop it with touch scratch/A-emd-pbh/sequencer_threshold/STOP. Running at 12:43 PST: chains A-20261121-204149-c48bd33 (Slurm 4838) and A-20261121-204250-0bf45c7 (4845). The sequencer commits run manifests on track/A-emd-pbh while it runs. The periodic set-up does not support a long run (job 4799 failed, request to core); no periodic job is queued.
