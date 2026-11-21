# cards: the queue of B-emd-gw's long runs and its sequencer

Decision 0025 items 4-5: at most two card jobs of the owner eligible to run at a time; further
runs wait in `queue.json` and `sequencer.py` submits them (and starts the processor runs that
make their inputs) when a slot is free and the inputs are ready; it also closes ended runs with
`harness/bin/nrpic-run finish`. Predictions of every queued run are in the journal of its
package before it is queued.

- Start (from the worktree root; one instance only, check `pid` first):
  `setsid nohup /usr/bin/python3 -I tracks/B-emd-gw/cards/sequencer.py >> /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log 2>&1 < /dev/null &`
- See: `tail /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log`,
  `cat /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/state.json` (queue name -> run id),
  `ps -p $(cat /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/pid)`.
- Stop: `touch /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/STOP` (exits at its next pass,
  at most five minutes), or `kill <pid>` with the number in that `pid` file. Never by pattern.
- Change the queue: edit `queue.json`, commit; the next pass reads it. An entry already in
  `state.json` is never submitted again.
