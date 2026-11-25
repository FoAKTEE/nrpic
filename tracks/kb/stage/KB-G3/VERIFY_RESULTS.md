# Re-verification: kb KB-G3

`harness/bin/nrpic-stage verify kb KB-G3` on 2026-11-25T12:50:10Z, clean export of commit `4b5e1895596d` in `scratch/kb/tmp/stage-verify/kb-KB-G3-4b5e189-20261125T124942Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 4b5e1895596d (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G3-4b5e189-20261125T124942Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G3/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G3) |
| runs | PASS | 239 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | WARN | STATUS.md has 40 lines (at most 60, with a `gate:` line) |
| rerun | WARN | re-run skipped (--no-rerun) |

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
