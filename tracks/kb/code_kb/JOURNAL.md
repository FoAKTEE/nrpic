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
