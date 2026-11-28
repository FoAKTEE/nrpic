# Parameters that the restart file does not hold, given to a continued run

Owner core. Branch `core/faces-finder` (batch 34a, 2026-11-27), candidate for release
core-v0.9; proposal for `coord/INTERFACES/restart_parameters.md`. Item 1 of
`tracks/core/NEXT_SOURCE.md` (decision 0042 item 4; Track D and Track F: `<fastflow>
diagnostics` in chains started without it; Track B `restart-new-parameters`: `<z4c>
dt_gauge`, `dt_lightspeed`; Track F `finder-diagnostics-on-restart`). Evidence:
`tracks/core/JOURNAL-faces-finder.md` (entries 3 and 5), run
core-20261127-234458-4baaaa4, script `tracks/core/analysis/restart_diag/diag_restart.py`.
Executables: `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/`.

## 1. What changes [VERIFIED]

A run continued with `-r <file>.rst` takes its parameters from the input stored in the
restart file. Up to release core-v0.8 the command line could change a stored parameter
but not add one: `athena -r x.rst fastflow/diagnostics=true` ended with "Parameter
'diagnostics' in block 'fastflow' on command line not found" when the first input had
not named it. The only way in was an input file next to `-r` (`-r x.rst -i add.athinput`).

Now, in a run started with `-r`:

```
athena -r run.00012.rst fastflow/diagnostics=true z4c/dt_gauge=0.9 [...]
```

- a parameter that the stored input does not hold is ADDED, and so is a block that it
  does not hold; the log (standard output, rank 0) gets one line per addition:
  `Parameter added on restart from the command line: <fastflow> diagnostics = true`;
- an input file given with `-i` next to `-r` adds as before, and the log now names what
  it added (not what it replaced):
  `Parameter added on restart from the input file: <fastflow> diagnostics = true`;
- the added parameter is part of the input from then on: every restart file the
  continued run writes holds it (comment `# added from the command line on restart`),
  so the next segment of a chain needs no repetition, and repeating it is harmless (it
  then replaces the value, without a line in the log);
- a name that holds anything but letters, digits and `_` (block or parameter) is refused
  with the old error, so that a path with `=` in it is not taken for a parameter.

A fresh start (`-i` without `-r`) is unchanged: a parameter on the command line that the
input does not hold is a fatal error, which catches misspelt names. On a restart a
misspelt name is now added silently apart from its log line, and the code never reads
it: read the log lines.

No option. No output of a run that does not use it changes (byte regression, READY).

## 2. Test [VERIFIED, processors, run core-20261127-234458-4baaaa4]

`diag_restart.py` (deck `problems/tests/by_horizon_coarse.athinput` with a restart file
every cycle; continuations to cycle 2), expectations of prediction R:

| Case | Command | Outcome |
|---|---|---|
| a | `-r rst fastflow/diagnostics=true` | exit 0, status file written, its lines equal those of b, log line "from the command line" (core-v0.8: exit 1) |
| b | `-r rst -i add.athinput` | exit 0, status file, log line "from the input file" |
| c | `-r rst` | exit 0, no status file, no such line |
| d | fresh start, `fastflow/no_such_option=1` | exit 1 with the old message |
| e | `-r rst fast-flow/x=1` | exit 1 with the old message |
| R2 | `-r rst zz_block/x=1` (a block the input does not hold) | exit 0, log line `<zz_block> x = 1` (run core-20261128-001433-ddd0f14) |

The restart files that case a wrote hold `diagnostics = true # added from the command
line on restart` in their stored input.

## 3. For chains

`scripts/submit_chain.sh` passes the arguments it was started with to every segment,
the first one included. The first segment is a fresh start, so an option the deck does
not name still cannot be given to a NEW chain on its command line: put it into the deck.
For a chain that is continued from its restart file by a wrapper (`nrpic-queue add --cmd
'...'`, or the chain script started on a run directory that already holds restart
files), the arguments reach only continued segments and the new rule applies: this is
the case of Tracks D and F (finder diagnostics and the finder options of core-v0.8 and
of this branch in running chains) and of Track B (`dt_gauge`). Not tested inside a chain
on a card in this session [TO VERIFY by the first track that uses it; the processor test
above is the same code path].

Options that are read only at the start of a run and whose state is in the restart file
are not made changeable by this: what a parameter does when it appears in a continued
run is the business of the module that reads it. `<fastflow> diagnostics`,
`polish_iterations_<n>`, `flow`, `start_scan_<n>`, `trapped_tol_<n>` and `<z4c> dt_gauge`,
`dt_lightspeed` are read at every start and act from the first cycle of the continued
run [by reading; the first tested above].
