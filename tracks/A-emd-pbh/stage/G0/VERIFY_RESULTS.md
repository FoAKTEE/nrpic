# Re-verification: A-emd-pbh G0

`harness/bin/nrpic-stage verify A-emd-pbh G0` on 2026-11-15T18:49:04Z, clean export of commit `8737de9b04e1` in `scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G0-8737de9-20261115T183831Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 8737de9b04e1 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G0-8737de9-20261115T183831Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 1 of 130 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## runs

```
{
 "A-20261115-182329-ad14d95": [
  "output not in sha256sums.txt: misplaced_output/fig_scouting_histories.pdf",
  "output not in sha256sums.txt: misplaced_output/fig_scouting_profiles_S2.png",
  "output not in sha256sums.txt: misplaced_output/scouting_summary.json",
  "output not in sha256sums.txt: misplaced_output/fig_scouting_histories.png",
  "output not in sha256sums.txt: misplaced_output/fig_scouting_profiles_S2.pdf",
  "output not in sha256sums.txt: misplaced_output/fig_scouting_profiles_S1.pdf",
  "output not in sha256sums.txt: misplaced_output/fig_scouting_profiles_S1.png"
 ]
}
```

## run-notes

```
{
 "A-emd-pbh-20261115-112500-61acbec": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112500-61acbec/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112505-61acbec": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112505-61acbec/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112625-e854f12": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112625-e854f12/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113103-9832afd": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113103-9832afd/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113108-9832afd": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113108-9832afd/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/newton/scan_refs.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113152-cd9539e": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113152-cd9539e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113223-5581665": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113223-5581665/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113244-8e0363b": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113244-8e0363b/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113446-024989f": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113446-024989f/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113608-374a41a": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113608-374a41a/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/gauge/scripts/vonneumann.py changed since the run (sha256 differs)",
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113614-374a41a": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113614-374a41a/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113755-cac3c4b": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113755-cac3c4b/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-43300e5": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113807-43300e5/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/gauge/scripts/bh2_onset.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-e02c969": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113807-e02c969/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/newton/compare_snapshots.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113810-e02c969": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113810-e02c969/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113822-87cba08": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113822-87cba08/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-113921-ca3786e": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113921-ca3786e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "A-emd-pbh-20261115-114638-35ca5e4": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-114638-35ca5e4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115120-2eb3117": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-115120-2eb3117/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/check_criteria.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115122-2eb3117": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-115122-2eb3117/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115232-bee5b2e": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-115232-bee5b2e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115339-044312f": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-115339-044312f/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
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
