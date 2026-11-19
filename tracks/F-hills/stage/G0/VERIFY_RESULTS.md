# Re-verification: F-hills G0

`harness/bin/nrpic-stage verify F-hills G0` on 2026-11-19T15:20:29Z, clean export of commit `7a24d7eca748` in `scratch/F-hills/tmp/stage-verify/F-hills-G0-7a24d7e-20261119T150132Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 7a24d7eca748 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G0-7a24d7e-20261119T150132Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/G0/SCOPING.md, novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 6 of 153 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 49 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 19 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## runs

```
{
 "F-20261115-173719-923135a": [
  "output not in sha256sums.txt: out/fig_test_nrread_synthetic.pdf",
  "output not in sha256sums.txt: out/fig_test_nrread_synthetic.png",
  "output not in sha256sums.txt: out/test_nrread_synthetic.json",
  "output not in sha256sums.txt: out/run/hills.horizon_summary_0.txt",
  "output not in sha256sums.txt: out/run/hills.co_0.txt",
  "output not in sha256sums.txt: out/run/hills.horizon_summary_1.txt",
  "output not in sha256sums.txt: out/run/hills.co_1.txt",
  "output not in sha256sums.txt: out/run/hills.co_2.txt",
  "output not in sha256sums.txt: out/run/hills.horizon_summary_2.txt",
  "output not in sha256sums.txt: out/run/trk_keep/seg1/hills.co_0.txt",
  "output not in sha256sums.txt: out/run/trk_keep/seg1/hills.co_1.txt",
  "output not in sha256sums.txt: out/run/trk_keep/seg1/hills.co_2.txt"
 ],
 "F-20261115-181805-f9c3473": [
  "output not in sha256sums.txt: test_nrread_three.json"
 ],
 "F-20261115-182100-613c9c6": [
  "output not in sha256sums.txt: out/single_analysis.json",
  "output not in sha256sums.txt: out/fig_single_gauge.pdf",
  "output not in sha256sums.txt: out/fig_single_junk.png",
  "output not in sha256sums.txt: out/fig_single_junk.pdf",
  "output not in sha256sums.txt: out/fig_single_gauge.png"
 ],
 "F-20261119-143443-f11ebb9": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/F-hills/F-20261119-143443-f11ebb9/sha256sums.txt"
 ],
 "F-20261119-145920-d7af935": [
  "status is running: not finished (nrpic-run finish)"
 ],
 "F-20261119-150017-b45ec5f": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f/sha256sums.txt"
 ]
}
```

## run-notes

```
{
 "F-hills-20261115-045124-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045124-ae6bca8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045332-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045332-ae6bca8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045407-bf52f4e": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045407-bf52f4e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045410-bf52f4e": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045410-bf52f4e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/compute_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045435-f62d553": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045435-f62d553/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "F-hills-20261115-045438-f62d553": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045438-f62d553/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/compute_estimate.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045918-e7d0a66": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045918-e7d0a66/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "F-hills-20261115-125858-0232c4c": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-125858-0232c4c/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t1_metric_checks.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-125915-9518508": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-125915-9518508/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t1_metric_checks.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-125918-9518508": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-125918-9518508/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130007-80eb1b9": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-130007-80eb1b9/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130058-00c6bf4": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-130058-00c6bf4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the run (sha256 differs)",
  "input tracks/F-hills/geodesic_binary/tests/t3_time_dilation.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-130124-76059c5": [
  "no gate",
  "no scratch/F-hills/F-hills-20261115-130124-76059c5/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
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
  "no scratch/F-hills/F-hills-20261115-130319-7f2c45b/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/geodesic_binary/hrna.py changed since the
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
