# Journal of package code_kb (kb helper, wave 3 round 1)

Package: upstream watch of AthenaK (decision 0015), K7 module descriptions and task-list
order (brief 12.7), a test with evidence for each of the 25 paper-code links (request
kb paper-code-links, coord/REQUESTS.md:82), the `<z4c> nco` question, the parameter index.
Card cap 0. Every number below carries a run id or a file:line locator.

## 2026-11-20 22:19 UTC, entry 0: state at start

- Worktree wt/kb at 8b24b590 (main merged by another helper of this round); no earlier
  session of this package: `tracks/kb/code_kb/` did not exist, git status clean.
- Last watch: run kb-20261115-154646-234060c, snapshot
  `kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261115T154646Z.json` (124 branches,
  main c5a0d7f9155a; compared with 20261115T132754Z: nothing new, moved or removed). Its
  report went to `tracks/kb/served/watch/code_watch_upstream.md`; `kb/reports/
  code_watch_upstream.md` still holds the 132754Z baseline report.

## W1 prediction (upstream watch), written before the run

Criterion for a message to core (brief 12.7 as the task states it): src/particles or src/z4c
changed on some branch since snapshot 20261115T154646Z, or a branch name contains pic,
vlasov, nrpic or deposit.

Expectation [JUDGEMENT]: five days have passed (2026-11-15 to 11-20). AthenaK upstream moved
main every few weeks in 2026 (main tip dated 2026-09-11 when the watch first looked), so I
expect a handful of branches to have moved (0 to 10), main possibly unchanged, and at most a
few branches with changed src/z4c or src/particles files. I expect no branch name with pic,
vlasov, nrpic or deposit, and still no branch whose src/particles mentions tmunu or deposit.
So the criterion fires only if some moved branch touched src/particles or src/z4c; I give
that about even odds.

Refuted (each separately): a branch named with pic/vlasov/nrpic/deposit; any branch whose
src/particles mentions tmunu or deposit (that would be particle back-reaction upstream, the
coupling this program built); more than 10 moved branches; main moved.

## W1 outcome (run kb-20261120-221925-1630d0b, 22:19 UTC)

Snapshot `kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261120T221926Z.json`, report
`kb/reports/code_watch_upstream.md` (commit 9d3deb38). [VERIFIED by the run]
- 124 branches; main still c5a0d7f9155a; 1 new (`m1-nucleon-recoil` bde60760ee36), 1 removed
  (`spill/largesim-m1`), 3 moved (`ahfind`, `project/bbh`, `project/largesim-m1`).
- No branch name with pic, vlasov, nrpic or deposit; no branch whose src/particles mentions
  tmunu or deposit (0 of 124); 7 branches read the metric only (as on 11-15); nrpic/vlasov
  under src/: 0 branches; src/z4c mentions particles: 0 branches.
- src/z4c changed on `project/bbh` (z4c_wave_extr.cpp) and on `project/largesim-m1`
  (z4c.hpp, z4c_amr.cpp, z4c_amr.hpp, z4c_tasks.cpp); src/particles changed nowhere.
- Prediction: held in every part (moved 3, within 0-10; main unchanged; no flagged name; no
  back-reaction upstream). The criterion fires (src/z4c changed on two branches), so a
  message to core is due. The new branch has no previous inspection, so the watch does not
  say whether its src/particles or src/z4c differ from main: W2 measures that.

## W2 prediction (line counts of the changes), written before the run

Script `scripts/watch_diff.py` compares the blobs of the two snapshots (moved branches) and
the new branch against main. Expectation [JUDGEMENT], from the tip subjects: project/bbh
changes z4c_wave_extr.cpp by fewer than 30 lines ("Skip zero local contributions");
project/largesim-m1 changes z4c_tasks.cpp by adding a Weyl communication guard (under 50
lines) and z4c_amr.* by a refinement criterion (under 300 lines). m1-nucleon-recoil differs
from main in src/z4c (it branched from a newer upstream state than the main tip of
2026-09-11) but not in src/particles. Refuted: any src/particles difference on any branch;
more than 500 changed lines in one file.

## W2 outcome (run kb-20261120-222055-dd59ec1, 22:21 UTC)

`scratch/kb/kb-20261120-222055-dd59ec1/watch_diff.{md,json}`. [VERIFIED by the run]
- project/bbh z4c_wave_extr.cpp +2/-0 (prediction under 30: held).
- project/largesim-m1: z4c_tasks.cpp +12/-17 (held, under 50: the Weyl tasks are now gated
  on a flag `weyl_exchange_active` set where the receives are posted, instead of comparing
  the float time with the last output time), z4c_amr.cpp +103/-0, z4c_amr.hpp +14/-0 (held,
  under 300), z4c.hpp +1/-0.
- m1-nucleon-recoil against main: 61 files of src/z4c differ, none of src/particles (held).
  Among them a new horizon finder (src/z4c/BHaHAHA_horizon_finder.*, src/z4c/bhahaha/, 52
  files added) replacing FastFlow in the task list (task Z4c_FastFlow renamed Z4c_Horizon);
  z4c_tasks.cpp +8/-22: Z4c_CalcRHS gains `M1_SetTmunu` as a second optional dependency
  beside `MHD_SetTmunu` (M1 radiation fills Tmunu too; module radiation_m1 now mentions
  tmunu); z4c_calcrhs.cpp +46/-2: option `rz4`, a radial factor exp(-r^2/rz4^2) on the
  Theta right-hand side including its matter term 8 pi alpha E.
- FAILED in one part: "no file with more than 500 changed lines" is refuted on
  m1-nucleon-recoil (fastflow.cpp +573/-256, bhahaha/bah_bcstruct_set_up.c +613,
  BHaH_defines.h +516). The cause is that the new branch is compared with main of
  2026-09-11, two months older than its tip (2026-11-13); the moved branches all stayed
  under 120 lines per file.
- For this program: no upstream branch hands particle sources to Z4c; the upstream Tmunu
  interface gains a second writer (M1) on two branches, still refreshed at every
  Runge-Kutta stage through the optional dependency of Z4c_CalcRHS. [JUDGEMENT] Nothing to
  merge; worth core's attention if core ever rebases on upstream z4c_tasks.cpp (the
  dependency list of Z4c_CalcRHS and the new Theta factor touch the lines that read Tmunu).

## M1 prediction (task-list order, written before `kb code modules` exists), 22:35 UTC

Test: `kb code modules` extracts, from the source at the indexed commits (local/nrpic
5deee18, IAS-Astrophysics/athenak c5a0d7f), the ExecuteTaskList calls of Driver::Execute,
the module assembly order of MeshBlockPack::AddPhysics, and every AddTask/QueueTask call.
Prediction (from FIRST_QUESTIONS question 9 and particles_tasks.cpp:30-45 at 5deee18):
- local/nrpic: NrpicSaveMetric is the only particle task before the stage loop
  (before_timeintegrator); NrpicPush, NrpicExcise (which reassigns MeshBlocks: the
  redistribution), optional NrpicCollide, NrpicDeposit and NrpicDiagnostics are in
  after_timeintegrator, i.e. once per step after all Runge-Kutta stages; no particle task
  is in before_stagen/stagen/after_stagen; Z4c's CalcRHS is in stagen (every stage) with
  optional dependencies MHD_SetTmunu and SF_SetTmunu (scalar field: a per-stage source,
  not particles).
- upstream: particle tasks (Push, NewGID, communication) in before_timeintegrator, none
  mentions tmunu; DynGRMHD::SetTmunu queued as MHD_SetTmunu in the run queue (stagen), so
  the sources are refreshed at every stage before Z4c_CalcRHS.
Refuted if: any particle task of local/nrpic is registered in a per-stage list; the
deposit is not in after_timeintegrator; upstream has no per-stage task that mentions
tmunu; or the driver does not run before_timeintegrator once before and
after_timeintegrator once after the stage loop.

## 2026-11-21 23:12 UTC, entry 1: restart after the cut of 2026-11-20 22:35 UTC

- State found: W1 and W2 done and committed (5ab9e791; outbox
  `tracks/kb/outbox/20261120T222130Z__to-core__upstream-watch.md`); the M1 prediction above
  was uncommitted (committed now, 188630d3). A private copy held `code_modules.py`, the
  `kb code modules` routing in `code_cli.py` and `tests/test_code_modules.py` (written
  2026-11-20 22:29-22:33 UTC) and a trial report `scratch/kb/code_kb/tmp/code_modules_try.md`
  (22:31 UTC). I did not read the trial report before writing the outcome of M1 below; the
  prediction M1 (22:35 UTC) was written after that trial file existed, so it may not be blind
  to it [JUDGEMENT]. The registered run below is the test of record.
- The watch is not run again: it ran 25 h ago (kb-20261120-221925-1630d0b) within this
  wave, and the package rule is never to redo finished work.
- Module code: the private copy was refreshed from the worktree (other helpers changed kb/
  since), the three files restored; 11 of 12 module tests passed, `first_sentences` did not
  split before a numbered item ("2. deposit."): SENT_RE now also splits before a digit; then
  12 of 12. Whole suite in the worktree: one failure, `test_meta_papers.py::
  test_additions_file_is_valid` (61 additions against 26 expected), outside this package
  (ingest3's request). Committed ad45d05f.

## P4 prediction (parameter index at main), written before the run

main carries tags core-v0.1 to core-v0.6 (`git tag -l`; core-v0.6 = 984bde68 is an ancestor
of main 47ab19ab). The index records local/nrpic at 5deee18 (ingested 2026-11-19 16:15 UTC);
`git diff --stat 5deee18 main -- athenak/src problems`: 124 files, +16528/-154; under
src/particles and src/z4c 38 files, +8522/-94. Expectation: `kb ingest repo --this --ref
main` indexes local/nrpic at 47ab19ab with more files than 790 (by about 20 to 40: new
nrpic_*.cpp/hpp of v0.4 to v0.6 and new inputs), more symbols than 4634 (by 300 to 900) and
more parameter reads than 1242 (by 100 to 250: the 61 + 25 + 26 options of v0.4 to v0.6
plus their sub-keys). `kb link check` after `kb link load`: 25 links, at most 2 with problems
(a symbol moved to another file or a line range changed; the paper side cannot change).
Refuted if: the ingest fails; the counts do not grow; more than 2 links are bad.

## P4 outcome (run kb-20261121-231826-3b32fc1, 23:18-23:19 UTC)

`scratch/kb/kb-20261121-231826-3b32fc1/{main_sha,ingest_repo,link_load,link_check}.txt`.
[VERIFIED by the run]
- local/nrpic indexed at 47ab19ab7162 (main): 869 files (was 790), 5030 symbols (4634),
  1386 parameter reads (1242), 8038 input parameters (4257), 5467 chunks; 9.2 s.
- `kb link load`: 25 links; `kb link check`: 25 links, 0 with problems.
- Prediction: held for symbols (+396, predicted 300 to 900), parameter reads (+144,
  predicted 100 to 250) and the link check (0 bad, predicted at most 2). FAILED for files:
  +79, predicted +20 to 40. The added files since 5deee18 are 23 under athenak/src, 51 under
  problems/ and 5 under python/nrpic (`git diff --name-only --diff-filter=A 5deee18 47ab19ab`),
  79 in all: I underestimated the new example inputs (core publishes an example input per
  option).

## M1 outcome (runs kb-20261121-231936-a33f7f1 and kb-20261121-232013-52c350a)

- First run: `kb code modules` without `--db` read `db/current`, the snapshot
  kb-20261119-a782f1e, in which local/nrpic is still at 5deee18 (the default of every kb read
  command, brief 12.10; the re-index went into the working database `db/kb.sqlite`). Kept
  on record: it is the test at the commit the prediction names. Second run with `--db
  kb-data/db/kb.sqlite`: local/nrpic at 47ab19ab (156 files in the five directories: z4c 30,
  particles 29, pgen 64, mesh 17, bvals 16) and upstream at c5a0d7f9155a (119 files: 26, 4,
  56, 17, 16); 392 and 372 task registrations. Report `kb/reports/code_modules.md` (from the
  second run), `kb-data/build/code/<repo>/modules.json`. [VERIFIED by the runs]
- At both 5deee18 and 47ab19ab (report "Task lists", table rows 4 to 8): Driver::Execute
  runs `before_timeintegrator` once per cycle (driver.cpp:581 at 47ab19ab), then
  `before_stagen`, `stagen`, `after_stagen` inside `for (int stage=1; stage<=(nexp_stages);
  ++stage)` (584-590), then `after_timeintegrator` once (594). Particle tasks of the nrpic
  path: NrpicSaveMetric in `before_timeintegrator`; NrpicPush, NrpicExcise, NrpicCollide (only
  if `coll.on`), NrpicDeposit, NrpicDiagnostics in `after_timeintegrator`
  (particles_tasks.cpp:34-51 at 47ab19ab, read by hand as well); the upstream particle tasks
  (Push, NewGID, SendCnt, ...) sit after the block `if (is_nrpic)` that returns, so they do
  not run for nrpic particles. No particle task in a per-stage list. Z4c::CalcRHS<2,3,4> is
  queued at Task_Run (= `stagen`, numerical_relativity.cpp) with optional dependencies
  MHD_SetTmunu, SF_SetTmunu (z4c_tasks.cpp:48-59). The tasks that touch tmunu:
  DynGRMHD::SetTmunu and ScalarField::SetTmunu (stagen, each stage), Particles::NrpicDeposit
  (after_timeintegrator, via NrpicDepositSources, NrpicFilterSources, NrpicStepSources,
  NrpicAddLambda), Z4c::CalcRHS (stagen), Z4c::ADMConstraints_ (after_stagen, reads it).
- Upstream c5a0d7f: particle tasks Push ... ClearSend in `before_timeintegrator`, none touches
  tmunu; DynGRMHD::SetTmunu in `stagen` (dyn_grmhd.cpp:199) and Z4c::CalcRHS with the single
  optional dependency MHD_SetTmunu: the sources are refreshed at every stage.
- Prediction M1: held in every part at both commits. The statement of FIRST_QUESTIONS
  question 9 still holds at main 47ab19ab: the particle sources are deposited once per step
  after the last Runge-Kutta stage and held through the stages of the next step; upstream
  refreshes them at every stage. [VERIFIED]
- Not tested by this: whether `nexp_stages` > 1 for the integrators the runs use (rk3 or
  rk4 in the inputs); the extraction reads the loop, not its count.

## L1 prediction (verdicts of the 25 paper-code links), written before the search, 23:24 UTC

Rule: verified = the named test has an entry in docs/TESTLOG.md or cosmo/TESTLOG.md with a
recorded outcome (numbers), a record that ties it to a run (directory with the input deck
and output, or a committed figure/table), a commit that carries the entry, and the input
reaches the linked symbol (problem generator, pusher, metric, deposit options on the code
path); claimed = no test found, or the test does not reach the symbol, or no record of the
run; refuted = a record contradicts the link.
Expectation [JUDGEMENT]: the DT entries of 2026-11-13 hold numbers but name few run
directories; runs/ (untracked) holds decks for most. Expect 14 to 20 verified, 5 to 11
claimed (M19 certainly: no test named; M24 likely: "every isolated-system run" names no
entry; M01/M02/M05-M07 through the "standalone build" only if that build calls the same
kernels as AthenaK, which it does by construction since it includes nrpic_kernels.hpp, but
the option-of links M05 (NrpicInit reads tolerance) need the AthenaK path), 0 refuted.
Refuted would be: a named test whose record shows the property failing (identity not met,
invariants off the published digits) for the code path of the link.

## L1 search notes and E1 prediction (evidence checks), 23:40 UTC

Search by hand (entries of docs/TESTLOG.md and cosmo/TESTLOG.md, the decks and command lines
of the runs they name under the main checkout's untracked runs/, the source at 47ab19ab).
Draft verdicts: 19 verified, 5 claimed (M18, M19, M20, M24, M25), 1 refuted (M23). Findings
that set verdicts:
- M23: NrpicWriteConservation is the conservation-law diagnostic (residuals of
  nabla_b T^ab = 0, nrpic_io.cpp:643-661), returns on refined meshes (:665) and entered the
  code in f219aded (2026-11-14), a day after the named test (495d451c). The identity of the
  paper (L759-762, sum over leaf cells = particle sums) is dep_sum of NrpicDepositSources
  (nrpic.cpp:1179) written by NrpicWriteHistory (nrpic_io.cpp:289).
- M20: the named test runs/dev/dep_smr uses `refinement = static`: no regrid, so the call of
  NrpicInitializeSources after a regrid (mesh_refinement.cpp:189) never runs in it.
- M18, M25: the named test (problems/tests/mesh_static.athinput) has `<adm> dynamic = false`
  and no `<z4c>` block: neither Z4c::CalcRHS nor Z4c::ADMConstraints runs.
- M13: verified on the static order (run kb-20261121-232013-52c350a) plus the named test
  reaching AssembleTasks; [JUDGEMENT] the named test runs only the particle half.
Script `scripts/link_evidence.py` encodes every locator (entry heading at its line at
47ab19ab, the commit that added it, deck or command-line text, source line at 47ab19ab).
Prediction E1: all 203 locator checks pass (a development pass already passed after the
links athena.log -> athena.<stamp>.log were followed within their directory; this is not
blind) and the nco scan finds no parameter read of `nco` in athenak/src. Refuted if any
check fails in the registered run or a `"nco"` read exists.
