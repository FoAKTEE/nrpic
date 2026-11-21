# Re-verification: core G2

`harness/bin/nrpic-stage verify core G2` on 2026-11-21T16:21:46Z, clean export of commit `042f70bcd92b` in `scratch/core/tmp/stage-verify/core-G2-042f70b-20261121T161613Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 042f70bcd92b (HEAD) in /data/haiyangw/nrpic/scratch/core/tmp/stage-verify/core-G2-042f70b-20261121T161613Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | FAIL | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); no verifier's report yet (VERIFIER.md, decision 0016) |
| style | PASS | no figure scripts yet |
| fig-script | PASS | 0 figures, each with its script |
| min-figs | WARN | 0 schematics and 0 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 10 of 1405 runs have problems |
| run-notes | WARN | 1147 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 36 lines |
| rerun | PASS | 0 of 0 scripts and commands ran cleanly in the export (none registered) |
| compare | PASS | 0 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 0 committed figure files regenerated |

## runs

```
{
 "core-20261120-220538-eafed07": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
 ],
 "core-20261120-220816-09f6f79": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
 ],
 "core-20261121-025527-eb8e6b7": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
 ],
 "core-20261121-030438-e52cdb3": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-031145-ffc12b3": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-031330-4d924b0": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-031446-5b1fdcd": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-033330-614286b": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-033435-0152dad": [
  "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
 ],
 "core-20261121-154654-d3ec487": [
  "status is submitted: not finished (nrpic-run finish)"
 ]
}
```

## run-notes

```
{
 "core-20261115-031705-b7b431d": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/tests/cf_table_regress.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-032614-45e1779": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-032615-45e1779": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-032617-45e1779": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-032625-45e1779": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-032757-b7b431d": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed"
 ],
 "core-20261115-032826-45e1779": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "input /data/haiyangw/nrpic/runs/os/nocap_sc: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/os/nocap_v4: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/prolate/e09_v8: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0900_v4: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0819_v4: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0605_v5: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0500_v5: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0283_v5: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/migration_yc0500_v4: no sha256 recorded",
  "input /data/haiyangw/nrpic/runs/st/yc0756_unpert: no sha256 recorded"
 ],
 "core-20261115-033115-b7b431d": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/tests/cf_table_regress.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033118-b7b431d": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/tests/cf_table_regress.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033228-b7b431d": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/tests/cf_table_regress.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033408-bac7416": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-033410-bac7416": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed"
 ],
 "core-20261115-033645-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033646-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033647-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033648-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033649-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033650-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033651-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id/problems/ball/ball.athinput changed since the run (sha256 differs)"
 ],
 "core-20261115-033652-408df57": [
  "status None read as completed from exit code 0",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status None read as completed",
  "input /data/haiyangw/nrpic/wt/core-id
```
