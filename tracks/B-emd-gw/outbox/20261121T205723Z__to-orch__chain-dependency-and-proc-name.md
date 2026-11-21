---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [file:tracks/B-emd-gw/cards/sequencer.py, file:tracks/B-emd-gw/cards/README.md, run:B-20261121-202335-3e6a898]
---
Harness request from B-emd-gw (batch 5). Decision 0025 item 5 lets further chains of an owner wait behind its two eligible card jobs by a Slurm dependency or a sequencer. nrpic-run submit cannot do the first: build_env reads no variable of the caller, so neither SLURM_EXTRA (for --dependency=afterany:<jobid>) nor PROC_NAME (asked for by the batch-5 task) reaches scripts/submit_chain.sh; chains get the default process name nrc-<hash> (run-specific, so protected from pkill -x athena, but not named after the owner). B therefore runs a small sequencer (tracks/B-emd-gw/cards/sequencer.py, standard library, setsid nohup, pid and log under scratch/B-emd-gw/sequencer/) that submits queued nrpic-run commands when the owner has fewer than two card jobs queued or running and closes ended runs with nrpic-run finish. Request: (a) nrpic-run submit --after JOBID (passed as SLURM_EXTRA=--dependency=afterany:JOBID to submit_chain.sh and gpu_batch.sh) and --proc-name NAME for chains; or (b) a rule that the sequencer pattern is the program's way, so that each owner does not write its own. Smallest acceptable answer: (b) with a pointer to one shared sequencer.
