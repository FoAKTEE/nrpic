# Re-verification: F-hills G1

`harness/bin/nrpic-stage verify F-hills G1` on 2026-11-28T01:45:50Z, clean export of commit `ec55f2a882d4` in `scratch/F-hills/tmp/stage-verify/F-hills-G1-ec55f2a-20261128T013108Z`. Result: **PASS**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of ec55f2a882d4 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G1-ec55f2a-20261128T013108Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: novelty/scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 15 figures, each with its script |
| min-figs | PASS | 3 schematics and 12 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | PASS | 280 run manifests finished (78 hand-written, read as decision 0012 allows); failures of 3 runs waived by coord/WAIVERS.md (decision 0019), output checksums verified where recorded |
| runs-waived | WARN | failures of the manifest check waived: 3 runs named in main's coord/WAIVERS.md (decision 0019 item 6): F-20261115-173719-923135a: outputs moved into the run directory after the run finished; data unchanged (decision 0021); F-20261115-181805-f9c3473: outputs moved into the run directory after the run finished; data unchanged (decision 0021); F-20261115-182100-613c9c6: outputs moved into the run directory after the run finished; data unchanged (decision 0021) |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | 3761 output files: 1509 hashed again (bytes read, 110.28 GB), 2252 taken from the cache (1850.89 GB); a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again; --full reads every byte |
| status | PASS | STATUS.md has 41 lines |
| rerun | PASS | 15 of 15 scripts and commands ran cleanly in the export |
| compare | PASS | 42 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 30 committed figure files regenerated |

## runs-waived

```
{
 "F-20261115-173719-923135a": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
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
  ]
 },
 "F-20261115-181805-f9c3473": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
   "output not in sha256sums.txt: test_nrread_three.json"
  ]
 },
 "F-20261115-182100-613c9c6": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
   "output not in sha256sums.txt: out/single_analysis.json",
   "output not in sha256sums.txt: out/fig_single_gauge.pdf",
   "output not in sha256sums.txt: out/fig_single_junk.png",
   "output not in sha256sums.txt: out/fig_single_junk.pdf",
   "output not in sha256sums.txt: out/fig_single_gauge.png"
  ]
 }
}
```

## run-notes

```
{
 "F-hills-20261115-045124-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045124-ae6bca8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045332-ae6bca8": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045332-ae6bca8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "F-hills-20261115-045407-bf52f4e": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/F-hills/F-hills-20261115-045407-bf52f4e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/F-hills/novelty/scripts/scale_estimate.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
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
  "no scratch/F-hills/F-hills-20261115-045435-f62d553/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
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
  "input /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/newton3/tes
```

## checksums

```
{
 "rehashed_files": 1509,
 "rehashed_bytes": 110282582070,
 "cached_files": 2252,
 "cached_bytes": 1850887438652,
 "full": false,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
}
```

## compare

```
[
 [
  "note/figures/fig_binary.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_passage.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_single.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_passage.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_binary.pdf",
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
  "note/figures/fig_constraints.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_binary_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_rp_scan.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_elliptic.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_newton_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_single.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_dataflow.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_geodesic_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_dataflow.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_constraints_numbers.json",
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
  "note/figures/fig_constraints.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_tree.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_p1_end_numbers.json",
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
  "note/figures/fig_p1_end.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_tree.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_smoke.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_p1_end.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_elliptic.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_elliptic_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_smoke.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_smoke_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_tree_numbers.json",
  "PASS",
  "identical"
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
 ],
 [
  "note/figures/fig_single_numbers.json",
  "PASS",
  "identical"
 ]
]
```
