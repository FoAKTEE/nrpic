# JOURNAL of package repro/continue (Track E, batch R2, 2026-11-24)

Helper package: the five card runs of the reproduction of arXiv:2512.14649 that were closed as
"failed" only because their chains reached MAX_SEGMENTS before tlim, continued to their end from
their own newest restart file, as new registered runs. Labels, original run ids and the files
that join them: `HANDOFF.md`.

## Entry 0 (2026-11-24 04:58 PST): how far each run got, and why it stopped

Source: the chain directories `scratch/E-stoch-inf/<run>/chain/` (events.log, STATUS, config.sh,
segment logs) and a development pass of `scripts/check_restart.py` (header parse only; the
registered pass with checksums follows in entry 2). [VERIFIED from those files]

| Label | Original run | tlim | Records reached | Newest restart | Why it stopped |
|---|---|---|---|---|---|
| RSF256 | E-20261123-035925-8439d79 | 8.5 | cycle 82 (seg 1), t = 0.50 | sr.00000.rst, t = 0, cycle 0 | seg 1 (job 4943) SIGTERM after 2 min; seg 2 (job 4960) resumed from t = 0 and got SIGTERM after 1 min 44 s; seg 3 refused: MAX_SEGMENTS = 2 |
| RNC256 | E-20261123-045030-c20bcb3 | 4.5 (override) | cycle 116, t = 0.71 | sr.00000.rst, t = 0, cycle 0 | seg 1 (job 4946) SIGTERM after 2.6 min; seg 2 refused: MAX_SEGMENTS = 1 |
| CL256U | E-20261123-065855-265732a | 10.4375 | cycle 777, t = 4.77 | usr.00002.rst, t = 4.000622, cycle 652 | seg 1 (job 4948) SIGTERM after 2 s (before any restart); seg 2 (job 4970) from the deck, SIGTERM after 15 min; seg 3 refused |
| CL256S | E-20261123-090727-4b6e5a5 | 8.5 | cycle 1015, t = 6.23 | sr.00003.rst, t = 6.000933, cycle 978 | seg 1 (job 4958) SIGTERM after 1 min 44 s; seg 2 (job 4982) from sr.00000.rst, SIGTERM after 19 min; seg 3 refused |
| AL2S | E-20261123-152119-38957ba | 8.5 | cycle 1227, t = 7.528778 | sr256_l2.00004.rst, t = 7.528778, cycle 1227 | seg 1 (job 4984) SIGTERM after 12 min (no restart beyond t = 0); seg 2 (job 5004) from t = 0 to the wall-clock stop (50 min) at cycle 1227; seg 3 refused |

None of the five stopped for a reason of its own: every stop is a SIGTERM from outside (the
preemption of 2026-11-23) or the wall-clock limit, and every refusal is MAX_SEGMENTS. No segment
log has a non-zero exit, a guard stop, a NaN, or a restart-read error. The restart cadence of the
decks is dt = 2.0 of code time, so a kill loses up to 2.0 of code time (six to fourteen minutes of
card time): two of the five (RSF256, RNC256) never got past their first restart output after t = 0
and start again from the initial slice stored in the t = 0 restart file.

Restart files (header against size, AthenaK outputs/restart.cpp; sidecar against its own counts,
scalar_field_io.cpp): all five newest files have size = header + nmb x data_size exactly, nmb = 1
(one MeshBlock of 256^3 with 4 ghost cells), data_size = 264^3 x nz4c x 8 = 3238354944 with
nz4c = 22 an integer, no holes, a finite tail (the tail is ghost cells of the shift, zero in these
decks, so the registered pass also reads the mid-plane of chi and alpha); the sidecars have the
magic NRSFRST1, extents (1, 2, 264, 264, 264) (phi, Pi; AL2S (1, 4, ...) with R and Pi_R of level
2 on the mesh) and the size their counts give. The
dump counters stored in the sidecars: RSF256 1 (next 0.25), RNC256 1 (next 0.5), CL256U 8 (next
4.175004), CL256S 13 (next 6.5), AL2S 16 (next 8.0), so the continuations write their dumps under
the numbers that follow the original's.

The executables: the chain copies `chain/athena` of the four scope runs and of AL2S have the
sha256 of the original manifests (release core-v0.6 card build ea473498...; branch card build
core_noise-level2 46810949...), and so do the byte copies `scratch/E-stoch-inf/tmp/continue/exe/
rc-v06-gpu` and `rc-nl2-gpu` that the continuations exec (named without "athena", so that a kill
by name from another project, `pkill -x athena`, cannot reach them).

## Entry 1 (2026-11-24 05:05 PST): predictions, written before the continuations are submitted

The predictions of the original runs stand unchanged: repro/scope `JOURNAL.md` entry 1 (P1, P2,
P3, P6, P7 for RSF256, RNC256, CL256S, CL256U) and repro/ablation `JOURNAL.md` entry 1 (P-A1,
P-A3 (iii) for AL2S). They are judged by package repro/figs on the joined runs, not here. Gate
G2, kind production, the same executable (byte copy, same sha256), the same deck and the same
overrides as the original; the only change is `-r <original newest restart>` in place of
`-i <deck>` for the first segment (wrapper `scripts/athena_resume.sh`).

What this package predicts about the joins (refuted as stated):

J1 (start). Each continuation's first log line after setup shows cycle = c_rst and time = t_rst
of entry 0, and every step has dt = 6.135923152e-03, the dt stored in the restart header (same
step as the original). Refuted by another cycle, time or dt.

J2 (overlap, exact). Where the original wrote records past its newest restart (the killed
segment), the continuation writes the same cycles again: RSF256 cycles 1-82 (segment 1) and 1-~67
(segment 2), RNC256 1-116, CL256U 653-777, CL256S 979-1015; AL2S has none (it stopped at the
restart cycle). On those cycles every column of `.sf.hst` and `.sf.con.hst` is bit-identical
(17 significant digits as printed): no particle deposition, one card, the same binary and launch
configuration, and a periodic box whose restart is exact (CLAUDE.md, machine section). A relative
difference up to 1e-12 would be the order of card reductions (named, not a defect); above 1e-10 a
defect of the restart to report to core. The same holds for the duplicated cycles inside the
original files (RSF256 segments 1 and 2 both started at t = 0).

J3 (no jump). At the junction (last original record with cycle <= c_rst, first continuation
record), the change of every record column is no larger than three times the largest change
between consecutive records among the ten before the junction. This is the only check for AL2S.
Refuted by a larger change in any column.

J4 (dumps). The continuation's first dump numbers follow the original's: RSF256 00001 (t = 0.25),
RNC256 00001 (t = 0.5), CL256U 00008 (t = 4.175), CL256S 00013 (t = 6.5), AL2S 00016 (t = 8.0).
Dumps that exist in both directories (RSF256 00001, 00002; RNC256 00001; CL256U 00008, 00009) are
byte-identical. Refuted by another number or a byte difference.

J5 (cost). Each continuation reaches tlim in one segment, exit 0, "Terminating on time limit",
unless preempted: wall time RSF256 30-40 min (USF256, E-20261123-021204-2f573ec, took 40 min for
1702 cycles with 41 metric dumps; RSF256 has 1386 cycles and 34 metric dumps left), RNC256 13-17
min (734 cycles at 1.2 s), CL256U 17-22 min (1050 cycles at 1.07 s), CL256S 7-9 min (408 cycles),
AL2S 6-8 min (159 cycles at 2.3 s); about 1.4 card-hours in all. Card time asked: one segment of
0.983 card-hours each, 4.92 in all, within the package's 5. A preemption makes the chain refuse
its next segment (MAX_SEGMENTS = 1); the run is then closed and continued once more from its new
newest restart, which this package does while it has card time asked left.

## Entry 2 (2026-11-24 05:20 PST): submitted; restart checksums match the originals' records

`scripts/submit_continue.sh RSF256 RNC256 CL256U CL256S AL2S` (05:05-05:19 PST) registered and
submitted the five continuations, all five at once under decision 0031 item 5:
RSF256 E-20261124-130529-da8c917 (job 5160), RNC256 E-20261124-130629-61fe0b0 (5161), CL256U
E-20261124-130711-a5dec67 (5165), CL256S E-20261124-130952-4be980b (5166), AL2S
E-20261124-131359-49afe29 (5168). A dry run of CL256S printed the manifest first (nothing
registered). Each manifest lists the byte copy of the executable, the restart file and its
sidecar as inputs with sha256; for all ten files the sha256 equals the line of the original's
`sha256sums.txt` (written by `nrpic-run finish` of the original on 2026-11-23), so the files
are those the originals wrote and closed [VERIFIED: manifests against sha256sums.txt].

The cards were not free at submission: `scontrol show node anta` gave AllocTRES gres/gpu=2 with
no job of this account running (another user's jobs), and twelve jobs of other owners of this
account pending ahead or beside ours (A, B, C, D, core). The five wait in the queue; nothing has
run. The registered pass of `check_restart.py` (with checksums) runs on processors meanwhile.
