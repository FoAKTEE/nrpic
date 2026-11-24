# HANDOFF of package repro/continue (Track E, batch R2)

State: 2026-11-24 06:15 PST. The five continuations are registered and submitted (gate G2,
production, one segment of 0.983 card-hours each, 4.92 asked in all). NONE HAS RUN YET: both
cards are held by another user's job on the priority partition (job 5162, started 05:09 PST,
time limit one day, so possibly until 2026-11-25 05:09 PST). A sequencer that outlives the
session (`scripts/autocontinue.sh`, pid in `scratch/E-stoch-inf/repro_continue_seq/pid`) closes
each continuation when it ends, continues a preempted one from its newest restart, and runs the
registered join check when all five are settled. Nobody has judged a continuation yet.

## Per label

All paths under `/data/haiyangw/nrpic/scratch/E-stoch-inf/`. "Restart" is the original's file the
continuation starts from (intact by header, size and sidecar; sha256 equal to the original's
`sha256sums.txt`; runs E-20261124-131957-94811a9 and the five manifests).

| Label | Original run (package) | Restart: file, t, cycle | Continuation run | Slurm job | tlim |
|---|---|---|---|---|---|
| RSF256 | E-20261123-035925-8439d79 (repro/scope) | rst/sr.00000.rst, 0.0, 0 | E-20261124-130529-da8c917 | 5160 | 8.5 |
| RNC256 | E-20261123-045030-c20bcb3 (repro/scope) | rst/sr.00000.rst, 0.0, 0 | E-20261124-130629-61fe0b0 | 5161 | 4.5 |
| CL256U | E-20261123-065855-265732a (repro/scope) | rst/usr.00002.rst, 4.000622, 652 | E-20261124-130711-a5dec67 | 5165 | 10.4375 |
| CL256S | E-20261123-090727-4b6e5a5 (repro/scope) | rst/sr.00003.rst, 6.000933, 978 | E-20261124-130952-4be980b | 5166 | 8.5 |
| AL2S | E-20261123-152119-38957ba (repro/ablation) | rst/sr256_l2.00004.rst, 7.528778, 1227 | E-20261124-131359-49afe29 | 5168 | 8.5 |

If a continuation is preempted, the sequencer starts another one; the CURRENT list of
continuation runs per label, in order, is `scratch/E-stoch-inf/repro_continue_seq/state.tsv`
(lines with status `submitted`; the label's last status says done, cut, broken, held, ...).
`scripts/conts.json` holds only the five of this session.

## Files of a continuation

In `scratch/E-stoch-inf/<continuation run>/`, with the original's base name (`sr`, `usr`,
`sr256_l2`):
- `<base>.sf.hst`, `<base>.sf.con.hst`: records from cycle c_rst + 1 on, WITHOUT the two header
  lines (AthenaK appends on a restart; the header is in the original's file; same columns).
- `<base>.sf.NNNNN.dump`, `.modes` (AL2S also `.rmodes`): numbers continue the original's (the
  dump counter is in the restart sidecar): RSF256 from 00001, RNC256 from 00001, CL256U from
  00008, CL256S from 00013, AL2S from 00016.
- `rst/`: the continuation's own restart files; `chain/`: segment logs (`seg001.job<id>.a1.log`).

## How to read original and continuation(s) as one run

Records: concatenate the original's file and then each continuation's file in order and, for
every cycle, keep the LAST line that has it. This also resolves the original's own repeated
cycles (a segment that resumed from an earlier restart wrote them again; they are identical,
journal entry 5, run E-20261124-134642-a9271b9). The result runs from cycle 0 to the last cycle
without a gap. `scripts/join_check.py` writes exactly these joined files (`<label>.sf.hst`,
`<label>.sf.con.hst`, header of the original) into its output directory, with
`<label>.dumps.tsv` (per dump number: time, cycle and the file to read); the rule was tested on a
completed run split at one of its restarts (run E-20261124-133152-214f0af: joined records equal
the run's own).

Dumps: per number, the file of the latest run that has it (where original and continuation both
have one, J4 predicts byte-identical files; checked by `join_check.py`).

Until the join check has run and a session has read it, treat the joined runs as not verified.

## See, stop, run next

```
cat /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/{pid,state.tsv}; tail /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/seq.log
touch /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/STOP     # stops the sequencer within 5 min; chains go on
squeue -a | head; scontrol show job 5162 | grep -E 'StartTime|EndTime'   # the job holding the cards
```

When the sequencer has exited after `all labels settled`, its last lines name the join-check run
(`registered E-...`): read `join_check.json` and look at `fig_join.png` in that run's directory,
judge J1-J4 of JOURNAL.md entry 1 (J1 as amended in entry 3), write the outcome as a journal
entry, update this file, and commit `scripts/conts.json` with the full lists from `state.tsv`.
If the sequencer is gone before that (machine restart, STOP, deadline 2026-11-26 06:00 PST),
start it again with the command at the top of `scripts/autocontinue.sh`; it continues from
`state.tsv`. Run the join check by hand with
`harness/bin/nrpic-run submit --kind production --gate G2 --package tracks/E-stoch-inf/repro/continue --launcher local --cores 1 --preregistered tracks/E-stoch-inf/repro/continue/JOURNAL.md#entry-1 --purpose "repro/continue join check J1-J4" -- python3 tracks/E-stoch-inf/repro/continue/scripts/join_check.py --conts <conts json> --out '$NRPIC_RUN_DIR'`.

Run next: `tail /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_continue_seq/seq.log`
