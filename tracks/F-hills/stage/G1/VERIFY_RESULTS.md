# Re-verification: F-hills G1

`harness/bin/nrpic-stage verify F-hills G1` on 2026-11-19T15:22:08Z, clean export of commit `b95903f4e876` in `scratch/F-hills/tmp/stage-verify/F-hills-G1-b95903f-20261119T152147Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of b95903f4e876 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G1-b95903f-20261119T152147Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 2 of 158 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 49 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 19 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## runs

```
{
 "F-20261119-143443-f11ebb9": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "F-20261119-150017-b45ec5f": [
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

## compare

```
[
 [
  "note/figures/fig_passage.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_passage.pdf",
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
  "note/figures/fig_cost_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_geodesic.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_rp_scan.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_geodesic_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_cost.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_cost.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_rp_scan.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_passage_numbers.json",
  "PASS",
  "identical"
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
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_rp_scan_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton.png",
  "PASS",
  "identical"
 ]
]
```
