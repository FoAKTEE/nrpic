# Re-verification: B-emd-gw G2

`harness/bin/nrpic-stage verify B-emd-gw G2` on 2026-11-25T12:23:30Z, clean export of commit `37439b2f28f6` in `scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G2-37439b2-20261125T121029Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 37439b2f28f6 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G2-37439b2-20261125T121029Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 4 schematics and 8 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 7 of 345 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 46 lines |
| rerun | PASS | 12 of 12 scripts and commands ran cleanly in the export |
| compare | PASS | 23 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 23 committed figure files regenerated |
| new-files | WARN | 1 files written by the scripts are not in the commit |

## runs

```
{
 "B-20261124-172958-73b0662": [
  "status is running: not finished (nrpic-run finish)"
 ],
 "B-20261124-172958-fc4a2cf": [
  "status is running: not finished (nrpic-run finish)"
 ],
 "B-20261124-210431-6bf48af": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "B-20261124-210432-6c4d005": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "B-20261124-223926-33194d9": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "B-20261125-093500-242d3a3": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "B-20261125-115657-91b61ec": [
  "status is running: not finished (nrpic-run finish)"
 ]
}
```

## run-notes

```
{
 "B-emd-gw-20261115-112946-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-112947-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-112948-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113102-bc5e082": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113120-bc5e082": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113148-4e5c33b": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113151-4e5c33b": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113212-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113213-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113214-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113215-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113216-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113217-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113218-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113219-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113220-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113221-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113222-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113223-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113227-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113231-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113232-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113236-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113246-50c684b": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113254-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113304-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113321-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113418-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113517-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113548-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113600-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113615-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed"
 ],
 "B-emd-gw-20261115-113632-2960145": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, 
```

## compare

```
[
 [
  "note/figures/fig_gauge.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_waves.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_baseline.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_scan.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_scan.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_waves.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_dataflow.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_dataflow.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_ladder.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_architecture.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_source.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_pancake.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_gauge.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_baseline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_r2.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_source.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_r2.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_pancake.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```

## new-files

```
[
 "note/figures/schem_ladder.svg"
]
```
