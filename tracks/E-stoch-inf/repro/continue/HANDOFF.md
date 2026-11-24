# HANDOFF of package repro/continue (Track E, batch R2)

State: 2026-11-24 05:20 PST. The five continuations are registered and submitted (gate G2,
production, one segment of 0.983 card-hours each, 4.92 asked in all); all five wait in the
Slurm queue behind other owners' jobs and another user's jobs that hold both cards. Nothing has
run yet. This file is rewritten when they end.

## Per label

All paths under `/data/haiyangw/nrpic/scratch/E-stoch-inf/`. "Restart" is the original's file
the continuation starts from (sha256 equal to the original's `sha256sums.txt`, checked from the
continuation's manifest).

| Label | Original run (package) | Restart: file, t, cycle | Continuation run | Slurm job | tlim |
|---|---|---|---|---|---|
| RSF256 | E-20261123-035925-8439d79 (repro/scope) | rst/sr.00000.rst, 0.0, 0 | E-20261124-130529-da8c917 | 5160 | 8.5 |
| RNC256 | E-20261123-045030-c20bcb3 (repro/scope) | rst/sr.00000.rst, 0.0, 0 | E-20261124-130629-61fe0b0 | 5161 | 4.5 |
| CL256U | E-20261123-065855-265732a (repro/scope) | rst/usr.00002.rst, 4.000622, 652 | E-20261124-130711-a5dec67 | 5165 | 10.4375 |
| CL256S | E-20261123-090727-4b6e5a5 (repro/scope) | rst/sr.00003.rst, 6.000933, 978 | E-20261124-130952-4be980b | 5166 | 8.5 |
| AL2S | E-20261123-152119-38957ba (repro/ablation) | rst/sr256_l2.00004.rst, 7.528778, 1227 | E-20261124-131359-49afe29 | 5168 | 8.5 |

`scripts/conts.json` lists the continuation runs per label (a second continuation, if a
preemption cuts one again, is appended there in order).

## Files of a continuation

In `scratch/E-stoch-inf/<continuation run>/`, with the original's base name (`sr`, `usr`,
`sr256_l2`):
- `<base>.sf.hst`, `<base>.sf.con.hst`: records from cycle c_rst + 1 on, WITHOUT the two header
  lines (AthenaK appends on a restart; the header is in the original's file; the columns are the
  same).
- `<base>.sf.NNNNN.dump`, `.modes` (AL2S also `.rmodes`): numbers continue the original's
  (the dump counter is in the restart sidecar): RSF256 from 00001, RNC256 from 00001, CL256U
  from 00008, CL256S from 00013, AL2S from 00016.
- `rst/`: the continuation's own restart files; `chain/`: segment logs (`seg001.job<id>.a1.log`).

## How to read original and continuation as one run

Records: concatenate the original's file and then the continuation's file(s) and, for every
cycle, keep the LAST line that has it. This also resolves the original's own repeated cycles (a
segment that resumed from an earlier restart wrote those cycles again). The result runs from
cycle 0 to the last cycle without a gap. `scripts/join_check.py` writes exactly these joined
files (`<label>.sf.hst`, `<label>.sf.con.hst`, header of the original) into its output
directory, with `<label>.dumps.tsv` (per dump number: time, cycle and the file to read).

Dumps: per number, take the file of the latest run that has it (the continuation where both
have one; journal prediction J4 says they are byte-identical, checked by `join_check.py`).

Until the join check has run, treat the joined runs as not yet verified.

## Run next

```
cd /data/haiyangw/nrpic/wt/E-stoch-inf
for r in E-20261124-130529-da8c917 E-20261124-130629-61fe0b0 E-20261124-130711-a5dec67 E-20261124-130952-4be980b E-20261124-131359-49afe29; do scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/E-stoch-inf/$r | head -2; done
# when a chain is DONE or FAILED: harness/bin/nrpic-run finish <run>
# then the registered join check (processors):
harness/bin/nrpic-run submit --kind production --gate G2 --package tracks/E-stoch-inf/repro/continue --launcher local --cores 1 \
  --preregistered tracks/E-stoch-inf/repro/continue/JOURNAL.md#entry-1 --purpose "repro/continue join check J1-J4" \
  -- python3 tracks/E-stoch-inf/repro/continue/scripts/join_check.py --out '$NRPIC_RUN_DIR'
```

A continuation cut again by a preemption shows FAILED (MAX_SEGMENTS = 1 reached): close it
with `nrpic-run finish`, then continue it from its own newest restart:
`FROM=<that run> RST=<its newest rst file name> tracks/E-stoch-inf/repro/continue/scripts/submit_continue.sh <LABEL>`
and append the new run id to `scripts/conts.json`.
