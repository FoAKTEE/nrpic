# Re-verification: core G2

`harness/bin/nrpic-stage verify core G2` on 2026-11-23T02:15:39Z, clean export of commit `5e6dc433a688` in `scratch/core/tmp/stage-verify/core-G2-5e6dc43-20261123T020751Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 5e6dc433a688 (HEAD) in /data/haiyangw/nrpic/scratch/core/tmp/stage-verify/core-G2-5e6dc43-20261123T020751Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (paperfig.py, figstyle.py) |
| fig-script | PASS | 5 figures, each with its script |
| min-figs | WARN | 1 schematics and 4 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 6 of 1448 runs have problems; 9 waived |
| runs-waived | WARN | failures of the manifest check waived: 9 runs named in main's coord/WAIVERS.md (decision 0019 item 6): core-20261120-220538-eafed07: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261120-220816-09f6f79: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-025527-eb8e6b7: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-030438-e52cdb3: records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-031145-ffc12b3: records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5) |
| run-notes | WARN | 1147 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | WARN | re-run skipped (--no-rerun) |

## runs

```
{
 "core-20261123-020450-7e42037": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261123-020452-e635a8e": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261123-020454-8fec6b2": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261123-020456-884f550": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261123-020458-dfc38d7": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261123-020500-9b192cd": [
  "status is submitted: not finished (nrpic-run finish)"
 ]
}
```

## runs-waived

```
{
 "core-20261120-220538-eafed07": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261120-220816-09f6f79": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-025527-eb8e6b7": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-030438-e52cdb3": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-031145-ffc12b3": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-031330-4d924b0": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-031446-5b1fdcd": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-033330-614286b": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 },
 "core-20261121-033435-0152dad": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_cpu changed since the run (sha256 differs)"
  ]
 }
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
