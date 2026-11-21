# Re-verification: A-emd-pbh G1

`harness/bin/nrpic-stage verify A-emd-pbh G1` on 2026-11-21T03:22:02Z, clean export of commit `72ac63ceae80` in `scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G1-72ac63c-20261121T032034Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 4 uncommitted paths: commit them first (tracks/A-emd-pbh/periodic_threshold/JOURNAL.md, tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput, tracks/A-emd-pbh/periodic_threshold/scripts/ltb_reference.py, tracks/A-emd-pbh/periodic_threshold/scripts/ltbref.py) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 72ac63ceae80 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G1-72ac63c-20261121T032034Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 3 schematics and 4 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 4 of 167 runs have problems |
| run-notes | WARN | 45 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 9 of 9 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## runs

```
{
 "A-20261119-164634-f1fe887": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "A-20261120-223123-f436c39": [
  "status is running: not finished (nrpic-run finish)"
 ],
 "A-20261120-223310-a9ce31a": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "A-20261120-223422-8cc4241": [
  "status is running: not finished (nrpic-run finish)"
 ]
}
```

## run-notes

```
{
 "A-emd-pbh-20261115-112500-61acbec": [
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112505-61acbec": [
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113108-9832afd": [
  "input tracks/A-emd-pbh/newton/scan_refs.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113223-5581665": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113244-8e0363b": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113446-024989f": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113608-374a41a": [
  "input tracks/A-emd-pbh/gauge/scripts/vonneumann.py changed since the run (sha256 differs)",
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113755-cac3c4b": [
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-43300e5": [
  "input tracks/A-emd-pbh/gauge/scripts/bh2_onset.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-e02c969": [
  "input tracks/A-emd-pbh/newton/compare_snapshots.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-114638-35ca5e4": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115120-2eb3117": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115122-2eb3117": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115232-bee5b2e": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-120425-80492f8": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-125932-574c747": [
  "status 'failed (exit 1)' read as failed",
  "status 'failed (exit 1)' read as failed"
 ],
 "A-emd-pbh-20261115-125932-779f753": [
  "status 'failed (exit 1)' read as failed",
  "status 'failed (exit 1)' read as failed"
 ],
 "A-emd-pbh-20261115-130256-a7374a4": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-153409-dc27b98": [
  "no gate"
 ],
 "A-emd-pbh-20261115-153415-dc27b98": [
  "no gate"
 ],
 "A-emd-pbh-20261115-153424-dc27b98": [
  "no gate"
 ],
 "A-emd-pbh-20261115-153437-dc27b98": [
  "no gate"
 ],
 "A-emd-pbh-20261115-153719-91b03d1": [
  "input tracks/A-emd-pbh/runs_ball/prep.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-154250-527a6d1": [
  "input /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_smr.athinput changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_amr.athinput changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-154740-69e8f8b": [
  "input /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_smr.athinput changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_amr.athinput changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161253-b8c1dc9": [
  "no gate",
  "input tracks/A-emd-pbh/newton/analyze_newton.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161309-9d3703a": [
  "no gate",
  "input tracks/A-emd-pbh/newton/analyze_newton.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161537-aa788d9": [
  "no gate",
  "input tracks/A-emd-pbh/newton/analyze_newton.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161542-36e461d": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161543-36e461d": [
  "input tracks/A-emd-pbh/criteria/check_criteria2.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161813-6c820fb": [
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-161829-dba94f6": [
  "input /data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_smr4.athinput changed since th
```

## compare

```
[
 [
  "note/figures/fig_landscape.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_criteria.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_constraints.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_ball_exact.pdf",
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
  "note/figures/fig_landscape.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_constraints.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_ball_exact.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_criteria.png",
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
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
