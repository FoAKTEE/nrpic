# Re-verification: F-hills G1

`harness/bin/nrpic-stage verify F-hills G1` on 2026-11-21T21:06:22Z, clean export of commit `1c4fe7fe003c` in `scratch/F-hills/tmp/stage-verify/F-hills-G1-1c4fe7f-20261121T210421Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 1 uncommitted paths: commit them first (tracks/F-hills/g2mesh/scripts/card_analysis.py) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 1c4fe7fe003c (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G1-1c4fe7f-20261121T210421Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | WARN | note/main.pdf is older than the last change of its .tex files |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 3 schematics and 9 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 3 of 238 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 40 lines |
| rerun | WARN | re-run skipped (--no-rerun) |

## runs

```
{
 "F-20261121-203144-b2cf16b": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "F-20261121-203156-03efdd3": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "F-20261121-203247-961801d": [
  "status is submitted: not finished (nrpic-run finish)"
 ]
}
```

## run-notes

```
{
 "F-hills-20261115-045124-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045332-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045407-bf52f4e": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045410-bf52f4e": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/F-hills/novelty/scripts/compute_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045435-f62d553": [
  "output directory read from a field other than outputs.dir",
  "no gate"
 ],
 "F-hills-20261115-045438-f62d553": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/F-hills/novelty/scripts/compute_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045918-e7d0a66": [
  "output directory read from a field other than outputs.dir",
  "no gate"
 ],
 "F-hills-20261115-125858-0232c4c": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t1_metric_checks.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-125915-9518508": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t1_metric_checks.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-125918-9518508": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130007-80eb1b9": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130058-00c6bf4": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t3_time_dilation.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130124-76059c5": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130237-cbfaf6b": [
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/compare_full.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/runlib.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_coplanar.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_general.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130239-cbfaf6b": [
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/compare_full.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/runlib.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_coplanar.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_general.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130253-6fc800e": [
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/compare_full.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/runlib.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_coplanar.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_general.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/newton3/tests/test_hills3.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130319-7f2c45b": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/scan.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130342-0471114": [
  "no gate",
  "input tracks/F-hills/three_punctures/scripts/newton_start.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130405-ce17dcf": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/scan.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130630-c1d003c": [
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/analyze.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/compare_full.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/runlib.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_coplanar.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/scripts/scan_general.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130724-982aba0": [
  "no gate",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/examples.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130755-982aba0": [
  "no gate",
  "input tracks/F-hills/three_punctures/scripts/newton_start.py changed since the run (sha256 differs)",
  "input tracks/F-hills/newton3/hills3/threebody.py changed since the run (sha256 differs)"
 ],
 "F-hills-2
```
