# Re-verification: core G2

`harness/bin/nrpic-stage verify core G2` on 2026-11-24T14:18:24Z, clean export of commit `c4a041dc0dcf` in `scratch/core/tmp/stage-verify/core-G2-c4a041d-20261124T135913Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of c4a041dc0dcf (HEAD) in /data/haiyangw/nrpic/scratch/core/tmp/stage-verify/core-G2-c4a041d-20261124T135913Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (paperfig.py, figstyle.py) |
| fig-script | PASS | 5 figures, each with its script |
| min-figs | WARN | 1 schematics and 4 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 6 of 1457 runs have problems; 9 waived |
| runs-waived | WARN | failures of the manifest check waived: 9 runs named in main's coord/WAIVERS.md (decision 0019 item 6): core-20261120-220538-eafed07: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261120-220816-09f6f79: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-025527-eb8e6b7: records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-030438-e52cdb3: records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5); core-20261121-031145-ffc12b3: records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5) |
| run-notes | WARN | 1147 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 42 lines |
| rerun | PASS | 5 of 5 scripts and commands ran cleanly in the export |
| compare | PASS | 10 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 10 committed figure files regenerated |
| new-files | WARN | 4 files written by the scripts are not in the commit |

## runs

```
{
 "core-20261124-130310-597d9ca": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261124-130321-ed96d4d": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261124-130340-31cf5e8": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261124-130347-7d6a10d": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261124-130356-d9d09bf": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "core-20261124-130406-09319a0": [
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

## compare

```
[
 [
  "note/figures/fig_row4_m8.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_collapse.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_geodesic.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_clusters.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_architecture.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_geodesic.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_row4_m8.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_clusters.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_collapse.png",
  "PASS",
  "identical"
 ]
]
```

## new-files

```
[
 "note/numbers_clusters.json",
 "note/numbers_collapse.json",
 "note/numbers_geodesic.json",
 "note/numbers_row4m8.json"
]
```
