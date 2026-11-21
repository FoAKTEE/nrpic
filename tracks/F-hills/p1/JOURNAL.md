# JOURNAL of package p1 (F-hills, wave 3 round 1): resuming the passage P1

Run F-20261119-150017-b45ec5f (`scratch/F-hills/F-20261119-150017-b45ec5f`, written only by its
chain). Labels [VERIFIED] (a run, a log or a file at its locator), [JUDGEMENT], [BACKGROUND],
[TO VERIFY]. Times: the machine logs in PST (UTC - 8); UTC where marked Z.

## Entry 0 (2026-11-20 22:15Z): what ended segment 7, before any resubmission

State found [VERIFIED, files of the run directory]:
- `chain/STATUS` = FAILED; `chain/events.log` last line `2026-11-19 19:35:43 seg=7 job=4684
  STATUS FAILED (athena exit status 143)`; segment counter `chain/segment` = 7; `chain/config.sh`
  ATHENA_WALL 00:50:00, SLURM_TIME 00:59:00, MAX_SEGMENTS 26, EXE_SRC = the tracker wrapper.
- `chain/athena` (sha256 0b71067a...) equals `nr_first/scripts/athena_keep_trackers.sh` and the
  manifest's exe; `chain/input.athinput` equals `nr_first/inputs/p1_q4.athinput` (45c73f71...);
  the release card executable is unchanged (f9f2dc12..., as in the manifest).
- Seven segments ran (Slurm 4650, 4669, 4672, 4675, 4678, 4681, 4684). Segments 1-6 ended on the
  wall-clock limit at t = 14.27, 30.57, 47.65, 65.88, 85.11, 103.34 (logs `chain/seg00k.*.log`,
  lines "Terminating on wall clock limit"). `sacct`: 50:05-50:09 each; segment 7 00:25:06, state
  FAILED, ExitCode 1:0. Sum 5 h 25 min 45 s = 5.43 card-hours.
- `chain/seg007.job4684.a1.log`: read `rst/hills.00021.rst` (1352 MeshBlocks), "Setup complete",
  last line `elapsed=1.456147e+03 cycle=28700 time=1.121094e+02`, then only the footer `# exit=143
  end=2026-11-19T19:35:43-08:00`; no AthenaK termination message, no error text. The gpumem csv
  runs to 19:35:43.037 at 70843 MiB and 94-100 percent utilisation: the card was busy and full to
  the last sample, no memory growth.
- Restart files (headers read: time, cycle, MeshBlocks): 00019 t = 95.0 (24320, 1296), 00020
  t = 100.0 (25600, 1226), 00021 t = 103.336 (26454, 1352; wall-clock stop), 00022 t = 110.0
  (28160, 1156; written 19:28). Sizes follow 20.8 kB + 2433044 B per MeshBlock to within 133 B
  for 00000, 00021 and 00022, so 00022 is complete.

Why the planner's reading (preemption) is wrong [VERIFIED]:
- The machine has one partition (`scontrol show partition`: preempt, PriorityTier 10), and
  `PreemptType = preempt/partition_prio`: a job can only be preempted by one of a partition with
  a higher tier, and there is none. A preempted job is recorded as PREEMPTED (or CANCELLED);
  4684 is FAILED with ExitCode 1:0, which is the chain script's own `exit 1` after it wrote
  FAILED (submit_chain.sh line 269). The batch script was not signalled (its TERM trap, lines
  173-177, did not fire: the outcome would have been TERM and a resubmission, line 264).
- Another user's job 4685 was submitted at 19:10:34 (`sacct -j 4685`: Submit), waited, and
  started at 19:35:43 because 4684 had just freed the card, not the other way round.

Cause [VERIFIED to the second; JUDGEMENT only in that the signal itself is not logged]:
- At 2026-11-20T03:35:41.642Z (19:35:41.6 PST) a Claude Code session of another project of the
  same Unix account (its transcript under `~/.claude/projects/`, session bffc8ad0) ran the shell
  command `pgrep -fa "[r]un_regressions.py" | cut -c1-120; pkill -f "[r]un_regressions.py";
  sleep 1; pkill -x athena; ...` to stop its own regression run. `pkill -x athena` sends SIGTERM
  to every process of the user whose name is exactly `athena`. P1's process had that name: the
  wrapper ends with `exec "$REAL"`, REAL = `.work/build_gpu_v03/src/athena`. One second later
  (19:35:43) P1's athena exited with 143 = 128 + SIGTERM. AthenaK installs no signal handler
  (`grep -rn "SIGTERM\|signal(" athenak/src` finds nothing), so it died at once, without a
  restart file. The chain script and `_athena_job.sh` have other process names (the spooled
  batch script; `_athena_job.sh`), were not signalled, and the chain classified the exit as a
  failure (submit_chain.sh line 236).
- It is the only command of that kind in that transcript in the hours around (15 kill commands
  with "athena" in it over its whole history; this is the only bare `pkill -x athena`). The same
  session is still active (transcript written at 14:04 PST today).
- Lost work: t = 110.0 to 112.11 (2.1 M, about 7 min of card time) plus the tracker rows to
  112.38, which the resumed chain recomputes.

What would refute this: a log showing that athena of job 4684 got its signal from Slurm
(slurmd log, not readable here), or a command time in the transcript more than a few seconds
from 19:35:43. Neither is the case in what I can read.

Consequence for the resume [JUDGEMENT]: a second `pkill -x athena` by that or another session
would kill P1 again. The wrapper honours `NRPIC_REAL_ATHENA`; I point it at a byte-identical
copy of the release card executable named `p1-ak03-gpu`
(`scratch/F-hills/tmp/p1/exe/p1-ak03-gpu`, sha256 f9f2dc12..., equal to the manifest's input;
`ldd`: absolute library paths, no RPATH), so the process is no longer called `athena`. This
does not protect against `pkill -f athena` (the cmdline of `_athena_job.sh` contains "athena",
and it forwards TERM). sbatch exports the environment (default `--export=ALL`; `clean_sbatch`
removes only SLURM_* and SBATCH_*), so the variable reaches every resubmitted segment; if it
were lost, the wrapper falls back to the release path, the same binary.
Budget: my cap is 10 card-hours (5.43 used before); MAX_SEGMENTS = 18 allows 11 more segments,
11 x 0.836 h = 9.2 card-hours, instead of the 19 that MAX_SEGMENTS = 26 would allow.

## Entry 1 (2026-11-20 22:40Z): prediction for the resumed chain, written before submission

1. The first resumed segment (number 8) reads `rst/hills.00022.rst` (t = 110.0, cycle 28160,
   1156 MeshBlocks): it is the newest by modification time and complete. Refuted if it renames
   a file to `.bad` (submit_chain.sh lines 226-235) or starts from another file.
2. Trackers: the wrapper copies the live `hills.co_*.txt` (seg 7, t = 103.34-112.38) to
   `trk_keep/<stamp>/`; the resumed segment writes from t = 110.0. After
   `nrread.read_trackers` joins them, every tracker has rows without a gap larger than two
   output intervals across t = 103-120 and no jump in position at t = 110 larger than the
   step-to-step motion. Refuted by a gap or a jump.
3. Rate: each full 50-min segment advances 15-21 M (segments 2-6: 16.3-19.2 M; segment 7 at
   1.54 cycles/s = 18.1 M per 50 min). Refuted outside that band.
4. Tree: P1 prediction item 1 (JOURNAL.md of the track, line 306) gave 1716-2400 MeshBlocks.
   That band is ALREADY refuted on the low side by the segments run so far (trees 1576, 1282,
   1366, 1310, 1352 at the starts of segments 3-7, 1156 at t = 110; restart headers and logs),
   and the outcome entry says so. For the rest of the run I predict 1000-1800 MeshBlocks
   [JUDGEMENT: the nests of the bound member and the hole overlap; the leaving member's nest
   adds blocks again] and never above the 2700 slots. Refuted by a slot-limit stop or a tree
   outside 1000-1800.
5. Cost: 170 M remain; at 15-21 M per segment that is 9-11 segments, 7.5-9.2 card-hours, inside
   MAX_SEGMENTS = 18. Refuted if a segment fails for a reason other than an outside signal, or
   if the chain reaches MAX_SEGMENTS before tlim = 280.
6. The process of the resumed segments is called `p1-ak03-gpu` (checked with `ps` when a
   segment runs). Refuted if `ps` shows `athena`.

## Entry 2 (2026-11-20 22:21:54Z): chain resumed

`squeue -u $USER` before: no F-hills job (jobs of core and C only); `chain/jobid` 4684 no longer
known to Slurm. Command (from `/data/haiyangw/nrpic/wt/F-hills`, at 22:21:53Z):

    ATHENA_EXE=/data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh \
    NRPIC_REAL_ATHENA=/data/haiyangw/nrpic/scratch/F-hills/tmp/p1/exe/p1-ak03-gpu \
    MAX_SEGMENTS=18 JOB_NAME=F-20261119-150017-b45ec5f \
    scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f \
        /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/inputs/p1_q4.athinput

Result [VERIFIED]: `chain started ...: job 4738`; `--status`: STATUS QUEUED, job 4738 PENDING
(Priority); events.log `2026-11-20 14:21:54 seg=7 job=login submitted job 4738`; config.sh
rewritten with MAX_SEGMENTS=18, the same EXE_SRC, ATHENA_WALL and SLURM_TIME. The planner's
command had MAX_SEGMENTS=26; I set 18 to keep the 10 card-hour cap (entry 0). Not through
`nrpic-run submit`: same run id, directory, input and executable content.

## Entry 3 (2026-11-20 22:50Z): intermediate analysis at t = 112 M, prediction before it runs

Data: the run directory as segment 7 left it (trackers to t = 112.38 after joining
`trk_keep/`; horizons, history and waveforms to about t = 112.2). I have looked at the logs and
restart headers (entry 0) but not at trajectories, horizon masses, history or waveforms. Which
items of the P1 prediction (track JOURNAL.md lines 305-320) can be decided now:

Item 1, health (decidable except "to t = 280" and the segment count):
- 1a three trackers with rows from t = 0 to 112.4 after the join, no gap above two output
  intervals. Refuted by a missing tracker or a gap.
- 1b tree 1716-2400 MeshBlocks: decided before this analysis from the logs (entry 1, item 4):
  REFUTED on the low side. The analysis only tabulates it.
- 1c 1900-2200 MeshBlock-cycles/s in every full segment (from the segment logs' "MeshBlock-cycles"
  and "cpu time used"). Refuted if a full segment is outside.
- 1d no non-finite value in trackers, history, or horizon rows after the first good search.
- 1e history Volume constant: relative change below 1e-3 over t = 0-112 [JUDGEMENT; the excised
  cells are a negligible part of the domain]. Refuted above.
Item 3, member horizons (decidable at t = 100 M): masses only from rows with hrms < 1e-3, members
from t >= 0.5 M. Growth m(t = 100) / m(first good) - 1 for each member: the prediction said
10-18 percent by t = 200 if the single-puncture rate 0.6-1.1e-4 per m persists, which is 4.6-8.5
percent at t = 100 (100 M = 772 member masses at 0.1295) [arithmetic]; refuted below 2 or above
25 percent. Heavy hole: first good search (hrms < 1e-3) near t = 4 M; its mass grows by less than
1 percent by t = 100 [JUDGEMENT, its cells per mass are 8 times those of a member].
Trajectories against the baselines over t = 0-112 (not an item of the P1 prediction; my
prediction now) [JUDGEMENT]:
- 3a the binary is still bound and not wider than 2 a_b = 10.2 M at t <= 100 (Newton passes
  10.2 M at t = 115.65, HRNA at 134.6; `nr_first/results/baselines_p1.json`); refuted if
  |x_1 - x_2| > 10.2 M before t = 100.
- 3b the centre of mass of the binary passes its closest approach to M between t = 95 and 115
  (Newton 104.35) at a coordinate distance of 7-10 M (Newtonian conic 9.81 M; GR turning point
  9.25 M areal, smaller in the puncture's coordinates); refuted outside either range.
- 3c before t = 60 the NR distances from M agree with Newton to within 15 percent (far from the
  hole, with the coordinate speeds of the members reduced by the gauge, E3: f = 0.76 at 4 m);
  refuted above.
Item 2 (which member leaves, separation by t = 200, no common horizon by 280) is not decided at
t = 112; it is judged after the pericentre of the second member, around t = 120-150. Item 4
(junk energy at the spheres by t = 150) is not decidable; the cumulative E_rad to t = 112 is only
recorded.
The eih report's shared expectation (m1 = comp0 enters the region where GR captures; its
numbers are [TO VERIFY] context, not a criterion) can be judged when m1's distance from M has
passed its minimum: a capture shows as m1's tracker reaching M's horizon (coordinate distance
below about 1.5 M) or as a jump of the heavy hole's horizon mass; no capture as a minimum
followed by a growing distance. If m1 is still approaching at t = 112, it is judged later.
Energies (newton3_fix convention): E_i against the barycentre of M and the other member is not
conserved before the binary separates; only plotted.

## Entry 4 (2026-11-20 22:45Z): outcome of the intermediate analysis (t <= 112.38 M)

Runs [VERIFIED]: F-20261120-222808-0e709b6 (`nr_first/scripts/p1_analysis.py` as given, `--out`
to its run directory; `results/p1_analysis.json`, `figures/fig_p1_analysis.png`),
F-20261120-223001-3ca60fa (first pass of `scripts/run_all.sh`) and F-20261120-223252-ca18a81
(second pass, adds the binary's relative orbit, the common-horizon diagnostics and the ledger
from restart times; `results/p1_checks.json`, `ledger.json`, `baseline_tracks.json`, the five
figures). All figures read. The baseline trajectories reproduce `nr_first/results/
baselines_p1.json` (Newton r_min 12.068 / 5.777 M, CM pericentre 104.35 M; HRNA E1 -0.49995 u,
E2 +0.9703 u, r_min 5.2065 / 14.399 M).

THE MAIN RESULT: the binary merged at t = 48.8 M, before the passage [VERIFIED].
- |x_1 - x_2| falls monotonically from 4.95 M at t = 0: below 2 M at t = 39.2, 1 M at 44.1,
  0.5 M at 46.3, 0.1 M at 48.8, then to round-off (`fig_separations.png`,
  `fig_p1_analysis.png`). The relative orbit (`fig_tracks_plane.png`, right) leaves the
  circle of Newton and HRNA after about 10 M and curls into the centre in about a third of a
  revolution (binary period 145 M).
- Both member finders find a common horizon from t = 48.81 (finder 0) and 49.06 M (finder 1),
  mass 0.2686 at first, median 0.2684, slowly drifting to 0.2688 at t = 112
  (`fig_horizons.png`, middle). Last separate members: 0.13698 (t = 46.50) and 0.13901
  (t = 46.81). The merger happened 24.9 M from M and 19.8 M from the grid origin (the centre of
  the extraction spheres).
- The binding energy from tracker positions and velocities is about -0.52 units at t = 1-20 M
  against Newton's -0.31 (`fig_energies.png`; units 4.96e-3 M): the members' relative
  coordinate motion is slow from the first M on (kinetic part about 0.32 of Newton's if the
  potential part is Newton's [arithmetic]).
- No reference has this. Newton: |x_1 - x_2| between 3.7 and 5.3 M to t = 100; HRNA 5-7.4 M;
  EIH from the input state (eih `results/p1.json`, [TO VERIFY] context): with the velocity
  reading the binary widens beyond 2 a_b at t = 64.9, with the canonical reading it survives.
  The gravitational-wave inspiral time of a binary with a = 5.11 M, m1 = m2 = 0.125, e = 0.033
  is about 3400 M (Peters' formula, (5/256) a^4 / (m1 m2 (m1 + m2)) [BACKGROUND formula,
  arithmetic]).
- Cause [JUDGEMENT, TO VERIFY]: a numerical loss of the members' orbital motion at m/8 (8 cells
  per member mass, coordinate horizon about 7 cells in radius, E3), not physics: E3 measured
  coordinate speeds of single boosted members at 0.52-0.76 of the boost speed at the same
  resolution and gauge, and here the relative motion is slow from the start. A common horizon
  is gauge invariant, so the merger is real in the simulation. What would decide it: the
  isolated binary (the two members only, same a_b, momenta and gauge) at m/8 and at m/16 for
  about 60 M; if it merges at m/8 and not at m/16, resolution is the cause. Request to the
  lead (REQUESTS.md).

Items of entry 3:
- 1a trackers: three, 28771 common rows from t = 0 to 112.383, seven files each (six kept +
  live), largest gap one step (3.906e-3 M), largest step 1.35e-3 M against a median of
  0.83e-3 (no jump), all finite. MET.
- 1b tree 1716-2400: REFUTED on the low side (decided before, entry 1): 1016-1870 MeshBlocks
  over t = 0-112 (restart headers; 1870 at t = 5, 1016 at t = 75), below 1716 from t = 20 on;
  never near the 2700 slots.
- 1c 1900-2200 MeshBlock-cycles/s: segments 1-6 give 2242, 2186, 2171, 2061, 2028, 1963.
  REFUTED by segment 1 (2 percent above); 2-6 inside. The rate falls with the tree (fewer
  blocks per kernel launch [JUDGEMENT]).
- 1d no non-finite value: trackers, the 225 history rows, the good horizon rows and the
  radiated energies are finite. MET.
- 1e history Volume: relative change exactly 0. MET.
- Item 3, member horizon growth at t = 100 M: NOT JUDGEABLE as stated, the members do not exist
  after t = 48.8. The rate before the merger is: m2 +7.4 percent by t = 46.8, m1 +5.7 percent
  by 46.5, i.e. 2.0e-4 and 1.6e-4 per member mass, 1.5-1.9 times the top of the predicted
  0.6-1.1e-4: the rate part FAILED (it would have given 12-16 percent at t = 100, inside the
  2-25 percent band, if it had stayed linear).
- Heavy hole below 1 percent by t = 100: +0.28 percent (1.00419 first good at t = 4.0, 1.00705
  at t = 100). MET. After t = 93 its good searches fall on three branches 3e-4 apart in
  relative mass (finder scatter, `fig_horizons.png` bottom).
- 3a binary bound, not wider than 10.2 M at t <= 100: formally MET (|x_1 - x_2| <= 4.95), but
  only because it merged; the assumption behind it (an intact binary at the passage) FAILED.
- 3b closest approach of the centre of mass at t = 95-115 at 7-10 M: NOT DECIDED; at t = 112.38
  the remnant is 11.82 M from M and still approaching at 0.21 (Newton's CM passed its
  pericentre 9.76 M at t = 104.35). It is refuted unless the remnant turns before t = 115,
  which would be outside 7-10 M; the resumed segment 8 decides.
- 3c distances within 15 percent of Newton before t = 60: REFUTED, 33.5 percent (m1) and 31.9
  percent (m2). The NR motion lags: the heavy hole moved 5.1 M by t = 112 against 8.0 in
  Newton.
P1 prediction item 2 (separation by t = 200, one member ejected, one bound): REFUTED at
t = 48.8 M, there is no binary left to separate. Its last clause (no common horizon with the
heavy hole by t = 280) is open: the remnant (0.268) passes M from t of about 115 on.
Item 4 (junk energy at the spheres): not judged here (package junk_gauge). Recorded: E_rad to
t = 112.25 M of 2.6e-4 (R = 40), 9.9e-5 (48), 5.4e-5 (70), 7.1e-6 M (90); the merger at 19.8 M
from the centre emits after t = 48.8, so later parts of these curves are not junk.
The eih expectation (m1 enters the region where GR captures): REFUTED for P1's data in the
sense that it cannot happen: m1 merged with m2 24.9 M from M and never came closer to M than
the remnant now is (11.8 M at t = 112.38).

Decision on the chain [JUDGEMENT]: I leave it running (authorised: 10 card-hours). The rest of
P1 is no longer a Hills passage, but it still gives the full-length health record (G1 T4 as a
long three-hole run), the junk and burst signals at the spheres, and a full-GR close encounter
of the remnant (0.268) with M at about 10 M, where the gravitational-wave loss at pericentre
(about 4e-4 M for a parabolic orbit at 10 M [BACKGROUND formula, arithmetic]) exceeds the
orbit's Newtonian energy. Stopping it is the lead's call (REQUESTS.md, item 3); stopping is
`scripts/submit_chain.sh --stop <rundir>`, and the run can be resumed later from its restart
files.
