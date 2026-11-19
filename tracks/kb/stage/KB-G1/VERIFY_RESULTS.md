# Re-verification: kb KB-G1

`harness/bin/nrpic-stage verify kb KB-G1` on 2026-11-19T16:33:14Z, clean export of commit `78282d393e8d` in `scratch/kb/tmp/stage-verify/kb-KB-G1-78282d3-20261119T163032Z`. Result: **PASS**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 78282d393e8d (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G1-78282d3-20261119T163032Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G1/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G1) |
| runs | PASS | 117 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 38 lines |
| rerun | PASS | 5 of 5 scripts and commands ran cleanly in the export |
| compare | PASS | 6 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 6 committed figure files regenerated |

## run-notes

```
{
 "kb-20261115-112414-6bb2b7d": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-112414-6bb2b7d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-112522-3ac74c2": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-112522-3ac74c2/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-112823-3ac74c2": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-112823-3ac74c2/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-124340-9048b83": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-124340-9048b83/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-130232-ac33aa1": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-130232-ac33aa1/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-130931-c0e0ec8": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-130931-c0e0ec8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input /data/haiyangw/nrpic/wt/kb/kb/kbtool/code_params.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/kb/kb/kbtool/code_symbols.py changed since the run (sha256 differs)"
 ],
 "kb-20261115-131150-7350d70": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131150-7350d70/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-131158-7350d70": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131158-7350d70/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-131207-7350d70": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131207-7350d70/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-131627-7350d70": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131627-7350d70/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-131730-b603113": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131730-b603113/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-131809-f7f36ac": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-131809-f7f36ac/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132028-f7f36ac": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132028-f7f36ac/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132114-932c894": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132114-932c894/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132730-a51e26e": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132730-a51e26e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132750-bb3da03": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132750-bb3da03/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132754-bb3da03": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132754-bb3da03/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-132806-013c452": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-132806-013c452/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "kb-20261115-133232-3f7f25a": [
  "status 'finished' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'finished' read as completed",
  "no scratch/kb/kb-20261115-133232-3f7f25a/sha256sums.txt (hand-written manifest; outputs not
```

## compare

```
[
 [
  "note/figures/fig_w2b_review.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_kbg2.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_kbg2.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_w2_review.png",
  "PASS",
  "pixel rms 0.0"
 ],
 [
  "note/figures/fig_w2b_review.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_w2_review.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
