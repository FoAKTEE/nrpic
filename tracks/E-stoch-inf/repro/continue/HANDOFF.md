# HANDOFF of package repro/continue (Track E)

State: 2026-11-24 13:30 PST, second session (batch R3). Four of the five cut card runs of the
reproduction of arXiv:2512.14649 are continued to their tlim and join their originals without a
jump (join check E-20261124-212343-7e9c4b2, JOURNAL entry 12). RSF256 (SR 256^3 with metric
dumps, Figs. 2, 3, 6a) is joined up to cycle 895 (t = 5.49 of 8.5) and its fourth continuation
waits in the shared card queue as **q0034** (label `rsf256-cont`, priority 0). The sequencer
of the first session is stopped for good (decisions 0033, 0034): no process of this package
runs; nothing submits beside the queue. No run of this package is open in `nrpic-run`.

## Per label: original and continuations, in order

All run directories under `/data/haiyangw/nrpic/scratch/E-stoch-inf/`. Every continuation
starts from the restart named by `nrpic_resume=` in its `.nrpic/launch.json`. Status as closed
by `nrpic-run finish` (a continuation cut by its segment cap and continued by a later run is
`stopped`).

| Label | Original (package) | Continuations (status, started from) | tlim | Joined |
|---|---|---|---|---|
| RSF256 | E-20261123-035925-8439d79 (repro/scope) | E-20261124-130529-da8c917 (stopped; orig sr.00000.rst, records 1-29) -> E-20261124-201031-4c41e7b (stopped; orig sr.00000.rst, record 1) -> E-20261124-202134-0b1ce0c (stopped; orig sr.00000.rst, records 1-895, dumps 00001-00021, restarts sr.00001, sr.00002) -> **q0034** (from 0b1ce0c rst/sr.00002.rst, t 4.000622, cycle 652, dump counter 17) | 8.5 | 0-895 so far |
| RNC256 | E-20261123-045030-c20bcb3 (repro/scope) | E-20261124-130629-61fe0b0 (completed; orig sr.00000.rst) | 4.5 | 0-734, dumps 00000-00009 |
| CL256U | E-20261123-065855-265732a (repro/scope) | E-20261124-130711-a5dec67 (stopped; orig usr.00002.rst) -> E-20261124-201048-33a3a39 (completed; orig usr.00002.rst) | 10.4375 | 0-1702, dumps 00000-00020 |
| CL256S | E-20261123-090727-4b6e5a5 (repro/scope) | E-20261124-130952-4be980b (completed; orig sr.00003.rst) | 8.5 | 0-1386, dumps 00000-00017 |
| AL2S | E-20261123-152119-38957ba (repro/ablation) | E-20261124-131359-49afe29 (completed; orig sr256_l2.00004.rst) | 8.5 | 0-1386, dumps 00000-00017 |

The same lists, machine-readable: `scripts/conts.json` (label -> continuation run ids in order).

## Files

In each continuation's directory, with the original's base name (`sr`, `usr`, `sr256_l2`):
`<base>.sf.hst`, `<base>.sf.con.hst` (records from cycle c_rst + 1 on, WITHOUT the two header
lines; same columns as the original's), `<base>.sf.NNNNN.dump` and `.modes` (AL2S also
`.rmodes`; numbers continue the original's from the counter stored in the restart sidecar),
`rst/` (its own restart files), `chain/` (segment logs `seg001.job<id>.a1.log`, `events.log`).

READ THE JOINED FILES, not the pieces: run E-20261124-212343-7e9c4b2 wrote, per label,
`<label>.sf.hst` and `<label>.sf.con.hst` (header of the original, every cycle from 0 once) and
`<label>.dumps.tsv` (per dump number: time, cycle, the file to read). For RSF256 these hold
cycles 0-895 and dumps 00000-00021 only, until the join below is rerun.

## Join rule

Records: concatenate the original's file and then each continuation's file in the order of
`conts.json` and keep, for every cycle, the LAST line that has it (this also resolves the
original's own repeated cycles). Dumps: per number, the file of the latest run that has it.
Checked by `scripts/join_check.py`: every cycle recorded twice is identical as printed (17
digits; 1592 lines compared over the five labels, all identical), every dump held twice is
byte-identical, every continuation starts at c_rst + 1 with the restart's dt and its first dump
number is the sidecar's counter, no joined file has a gap; at a junction the change of every
column is at most 3 times the neighbouring changes, or (at the two cycle-0 junctions, RNC256 and
RSF256) identical to the earlier run's own step there (JOURNAL entries 11, 12: the literal J3 of
entry 1 is refuted at cycle 0 by column 16, rms |M_bssn - M_adm|, which is the run's own first
step).

## RSF256: queue entry q0034 and the command that joins it

`harness/bin/nrpic-queue show q0034` (state, and once dispatched `run_id` and `job_ids`);
`harness/bin/nrpic-queue list --owner E-stoch-inf`. The entry submits `nrpic-run submit
--launcher chain --gpu-hours 3` (3 segments of 59 min; one is enough, about 17-22 min, the other
two absorb preemptions) with the wrapper `scripts/athena_resume.sh`, the byte copy
`scratch/E-stoch-inf/tmp/continue/exe/rc-v06-gpu` (sha256 ea473498...), deck
`tracks/E-stoch-inf/repro/scope/inputs/sr_paper.athinput`, `nrpic_resume=` 0b1ce0c's
`rst/sr.00002.rst`; package `tracks/E-stoch-inf/repro/continue` must be committed (clean) when
the dispatcher takes it. Prediction K2 (JOURNAL entry 9).

When it has ended (`harness/bin/nrpic-run status <run_id>` shows the chain DONE or FAILED; the
queue never finishes runs):

```
cd /data/haiyangw/nrpic/wt/E-stoch-inf
R=<run_id from nrpic-queue show q0034>
harness/bin/nrpic-run finish $R
# ended at tlim ("Terminating on time limit" in scratch/E-stoch-inf/$R/chain/seg*.log):
#   append $R to "RSF256" in tracks/E-stoch-inf/repro/continue/scripts/conts.json, commit
#   (path-limited), then:
harness/bin/nrpic-run submit --kind production --gate G2 --package tracks/E-stoch-inf/repro/continue \
  --launcher local --cores 1 --preregistered tracks/E-stoch-inf/repro/continue/JOURNAL.md#entry-9 \
  --input tracks/E-stoch-inf/repro/continue/scripts/conts.json \
  --purpose "repro/continue join check of RSF256 with its fourth continuation (K2)" \
  -- python3 tracks/E-stoch-inf/repro/continue/scripts/join_check.py --out '$NRPIC_RUN_DIR' --labels RSF256
```

Then read `join_check.json` (`complete`, `J1_pass`, `J2_pass`, `J3_pass`, `J4_pass`,
`records_gapless`) and look at `fig_join.png`; judge K2 (first record 653 at t_rst + dt; cycles
653-895 identical with 0b1ce0c; first dump 00017; dumps 00017-00021 byte-identical; end at t 8.5,
cycle 1386; joined 0-1386 and 00000-00034) in a journal entry; the joined
`RSF256.sf.{hst,con.hst}` and `RSF256.dumps.tsv` of that run replace those of
E-20261124-212343-7e9c4b2 for package repro/figs. The byte comparisons of five 3.4 GB dumps take
a few minutes.

If it is cut again and its chain ends FAILED with the segment cap: finish it with `--status
stopped`, append it to `conts.json`, and queue the next continuation from ITS newest restart:
`DRY=1 GPU_HOURS=3 RESUME=<scratch/E-stoch-inf/$R/rst/sr.NNNNN.rst> scripts/submit_continue.sh
RSF256` prints the arguments; give them to `harness/bin/nrpic-queue add --label rsf256-cont2
--priority 0 -- ...` (as q0034, JOURNAL entry 10). If it wrote no restart of its own, start
again from 0b1ce0c's `rst/sr.00002.rst`.

## Run next

`harness/bin/nrpic-queue show q0034`; nothing else of this package waits.
