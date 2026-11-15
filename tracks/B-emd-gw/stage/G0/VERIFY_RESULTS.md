# Re-verification: B-emd-gw G0

`harness/bin/nrpic-stage verify B-emd-gw G0` on 2026-11-15T19:24:43Z, clean export of commit `20350efd1394` in `scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G0-20350ef-20261115T191231Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 20350efd1394 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G0-20350ef-20261115T191231Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 9 of 132 runs have problems |
| run-notes | WARN | 70 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 34 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## runs

```
{
 "B-20261115-164157-40b9f6d": [
  "output not in sha256sums.txt: reference.png",
  "output not in sha256sums.txt: reference.pdf",
  "output not in sha256sums.txt: reference_g.npz",
  "output not in sha256sums.txt: sha256sums.moved.txt",
  "output not in sha256sums.txt: reference.json"
 ],
 "B-emd-gw-20261115-113102-bc5e082": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-113120-bc5e082": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-113148-4e5c33b": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-113151-4e5c33b": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-113246-50c684b": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-113632-2960145": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-115529-58c7f50": [
  "fields missing: code, env, input"
 ],
 "B-emd-gw-20261115-115752-840e994": [
  "fields missing: code, env, input"
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
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112946-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-112947-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112947-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-112948-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112948-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113212-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113212-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113213-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113213-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113214-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113214-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113215-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113215-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113216-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113216-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113217-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113217-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113218-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113218-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113219-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113219-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113220-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113220-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113221-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113221-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113222-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113222-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113223-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113223-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113227-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113227-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113231-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113231-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113232-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113232-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113236-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113236-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)
```

## compare

```
[
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
  "note/figures/fig_waves.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
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
  "note/figures/fig_baseline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_source.png",
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
