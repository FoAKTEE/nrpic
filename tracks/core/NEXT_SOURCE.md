# Next source session of core (one Fable session of about two hours, before Friday 2026-11-27)

Written 2026-11-25T12:20Z by the core lead (batch 17) from `interfaces/REQUESTS_WAVE3.md`,
`stage/G2/OPEN.md` (sections core-v0.7 and core-v0.6) and the requests in core's inbox
(`harness/bin/nrpic-ctx inbox`, items 1-22). Order: what a gate waits for first, small and
default-off items before large ones, so that the session can close what it starts. Every item
leaves runs without its option byte-identical (byte regression `analysis/release/regress_v04.py`
against `.work/build_cpu_v07/src/athena`, 75 items) and goes onto its own branch from
`core/nrpic` with a READY and a new directory under `scratch/core/exe/` (never replacing a
published one: `EXE_PROVENANCE.md`). Source facts below were read at the source of `core/nrpic`
on 2026-11-25 [VERIFIED by reading]; numbers of tracks are theirs, not recomputed by core.

## For the Fable session, in this order

1. **Outputs that survive a restart** (gates: Track F G1, criterion C8, the vacuum passage A2
   runs as a chain that preemptions cut many times; core G2, C6 reproducibility; every chained
   run of every track).
   - (a) Tracker file (W2, F `tracker-files-on-restart`, accepted 2026-11-19): 
     `z4c/compact_object_tracker.cpp` `OpenOutput` opens `<base>.co_<n>.txt` with truncation
     at the first record of every start, so a continued run loses the earlier trajectory.
     Fix: append when the mesh starts from a restart file, header only on a fresh start.
   - (b) Restart defect 2 (OPEN.md core-v0.7 item b): the mesh history files get their header
     lines again at every continuation. Fix: no header when continuing.
   - (c) Restart defect 1 (item a): `<base>.cons.hst` loses one record when the restart file
     was written one or two cycles before the record is due (the deposits of those cycles
     are not in the restart file). Fix: carry the pending deposit sums in the `.prt`
     companion, or write the record from the state at the restart.
   - Test: case S2 of `analysis/release/quick_v07.py` (continuation from a restart written
     just before a record) and a tracker deck (`problems/puncture/by_binary.athinput`, two
     segments): every output of the continued run equal, line for line, to the uninterrupted
     run (headers once, the record at t = 1.6875 present, the tracker file the union of both
     segments). Reference: the uninterrupted runs, which exist (S2 of run
     core-20261125-023641-7a1c47d; to be made for the tracker deck on processors).
2. **Horizon finder: a converged mass, and excision that follows a growing hole** (gates:
   Track D G2, the null-test floor and the growth criterion of `g2long`; Track A G2 reads
   horizon masses to 1e-4 in its threshold scan).
   - (a) D `finder-stopping-rule` item 2: `fastflow.cpp:914` stops at the first iteration
     whose mass changes by less than `mass_tol_<n>` (absolute; default 1e-2). Add, off by
     default, a stop on the residual (summary column 9, area mean of the squared expansion)
     or a fixed number of polishing iterations after the mass rule is met.
   - (b) D `ah-excision-growth-guard`: `particles/nrpic.cpp:455` excises only while
     `rr_min < 4.0*initial_radius`. Add `<particles> ah_exc_max_growth` (default 4, nothing
     changes) or a guard relative to the last accepted radius.
   - Tests: (a) re-search of D's V-1L restart dumps on processors with D's tools
     (`git show track/D-bh-dress:tracks/D-bh-dress/g2long/tools/probe_long.py`): with the
     new rule and the default `mass_tol` the mass at every dump from 100 to 500 M within
     2e-5 of the tight rule; cost per call on a card stated. (b) D's ES-FL deck to 240 M
     with the option: removals by reason 3 continue past 219.5 M. References: D's
     tight-rule masses V-1L 1.000980-1.000998 (judgement run D-20261124-172508-c847ee4,
     `fp_analyse.json`); D's workaround run ES-FLK (`initial_radius_0 = 1.6`).
   - With it, the interface lines D asks for (item 1 of both requests: what `mass_tol`
     means, the 1.8e-4 angular offset of ntheta 16, the guard, what `z4c.user.hst`
     integrates near a hole).
3. **figstyle without a creation date** (Track E `figstyle-reproducible-pdf`, not blocking,
   five minutes): `python/nrpic/figstyle.py` `save()` calls `fig.savefig(...)` without
   metadata; pass `metadata={"CreationDate": None}` for the PDF (and honour
   `SOURCE_DATE_EPOCH`). Test: one figure script run twice gives byte-identical PDFs.

## Not for this session, in order (named so that the next round can plan them)

4. **core/oblate into a release** (gates: core G2 ladder row 3; Track A asked for a ruling on
   the oblate/prolate row). Not a Fable item: the branch (tip 4f01a81f, 2026-11-20) merges
   main, reruns its T1 (conformal factor equal to the potential of a homogeneous oblate
   spheroid to float32 rounding) and T2 (byte-identical without the component), publishes
   with READY; then the lead reviews it. Reference: the analytic potential the branch
   already uses; collapse runs at M/8 (first horizon 41.875 M, `JOURNAL-oblate.md` entry 9
   on the branch, not judged by the lead).
5. **The drift of collisionless clusters on the M/8 mesh** (gates: core G2 ladder row 4;
   Track C G2, whose King controls collapse on their own at 534.8 and 549.3 M). Not a source
   item yet: diagnosis first. Core's row-4 control of y_c = 0.73625, STABLE by the 300-M
   rule, collapses at 421.25 M (fates run core-20261125-120724-246d2a5). Whether the drift
   rate depends on N (particle noise) or not (the scheme) is decided by runs at a second N:
   Track C queued N = 1e4 and 1e6 controls; core's row 4 has a second cell size or N as its
   open item. Only an N-independent drift becomes a source item, with C's reproducing deck.
6. **The cure of the relaxed lapse around a hole** (W30; gates: Track D G2/G3 runs around a
   hole with `lapse_leak`; core-v0.7 has the mitigation `lapse_leak_hole` only). Design work
   (candidates a-c in REQUESTS_WAVE3.md W30); tests owed: D's V-1GB and ES-1GB to 200 M
   within the band of the control without `lapse_leak` (6.8e-5 late), the collapse test of
   core/gauge-2, the byte regression. Larger than two hours.
7. Later, no gate waits now: W18 in-situ Fourier modes (Track B, for the 256^3 GW cadence,
   reply by 2026-12-11); W25 sub-steps of E's lockstep record (E gates U-A2 to k <= 32 dk
   meanwhile); W22 collisions on several ranks (C, test T10 on 1 and 4 ranks); W6 ADM
   energy on spheres (C); W1 an hrms criterion of the finder (F); F's wave extraction
   beyond l = 8 and the HRNA pair-force specification; W31 ii, a step limit for
   `lapse_leak` x dt.

## Already served without new source (answers owed, no session needed)

- Restart on SIGTERM (Track C item 2 of `control-drift-and-sigterm-restart`, Track F
  `restart-on-sigterm`): in release core-v0.7 a run that receives SIGTERM finishes its
  cycle, writes a restart file and exits 143; chains need the chain script of core-v0.7
  (`coord/INTERFACES/preempted_runs.md`). Not tested under a real preemption (OPEN.md
  core-v0.7 item f).
- Track B `newton-fft-threaded`: a processor test, not a source change: `newton_poisson =
  fft` with `athena_cpu_omp` at one thread against `athena_cpu` on a reduced copy of B's
  deck; a line in the READY. The lead or a package can run it.
- Track C item 1 (drift rate of core's controls): the 50-M window means are in the fates
  runs core-20261124-130055-9fc9901 and core-20261125-120724-246d2a5 (`windows_50M` of
  `row4_fate.json`), at one N (1e4) only.
