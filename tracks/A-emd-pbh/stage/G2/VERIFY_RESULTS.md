# Re-verification: A-emd-pbh G2

`harness/bin/nrpic-stage verify A-emd-pbh G2` on 2026-11-26T23:19:04Z, clean export of commit `6d1d18ad902e` in `scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G2-6d1d18a-20261126T231729Z`. Result: **PASS**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 6d1d18ad902e (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G2-6d1d18a-20261126T231729Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 3 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py, figstyle.py) |
| fig-script | PASS | 10 figures, each with its script |
| min-figs | PASS | 4 schematics and 6 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | PASS | 327 run manifests finished (102 hand-written, read as decision 0012 allows); failures of 1 runs waived by coord/WAIVERS.md (decision 0019), output checksums verified where recorded |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): A-20261121-064515-aa13c8f: the gate reviewer's failed first attempt; its scratch script was edited for the rerun A-20261121-064537-2bcf310 |
| run-notes | WARN | 80 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | 31429 output files: 15 hashed again (bytes read, 0.5 MB), 31414 taken from the cache (809.60 GB); a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again; --full reads every byte |
| status | PASS | STATUS.md has 31 lines |
| rerun | PASS | 11 of 11 scripts and commands ran cleanly in the export |
| compare | PASS | 21 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 20 committed figure files regenerated |

## runs-waived

```
{
 "A-20261121-064515-aa13c8f": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "the gate reviewer's failed first attempt; its scratch script was edited for the rerun A-20261121-064537-2bcf310",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/A-emd-pbh/gate_review_G1/review_checks.py changed since the run (sha256 differs)"
  ]
 }
}
```

## run-notes

```
{
 "A-20261115-161947-09324e1": [
  "input tracks/A-emd-pbh/note/scripts/run_all.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112500-61acbec": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112500-61acbec/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112505-61acbec": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112505-61acbec/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/scope/scope_calc.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-112625-e854f12": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-112625-e854f12/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113103-9832afd": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113103-9832afd/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113108-9832afd": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113108-9832afd/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/newton/scan_refs.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113152-cd9539e": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113152-cd9539e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
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
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)",
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113614-374a41a": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113614-374a41a/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113755-cac3c4b": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113755-cac3c4b/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)",
  "input athenak/src/z4c/z4c_calcrhs.cpp changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-43300e5": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113807-43300e5/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/gauge/scripts/bh2_onset.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113807-e02c969": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113807-e02c969/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/newton/compare_snapshots.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113810-e02c969": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113810-e02c969/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113822-87cba08": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113822-87cba08/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-113921-ca3786e": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-113921-ca3786e/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-114638-35ca5e4": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-114638-35ca5e4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/predict.py changed since the run (sha256 differs)",
  "input tracks/A-emd-pbh/criteria/scan_disagreement.py changed since the run (sha256 differs)"
 ],
 "A-emd-pbh-20261115-115120-2eb3117": [
  "no scratch/A-emd-pbh/A-emd-pbh-20261115-115120-2eb3117/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/A-emd-pbh/criteria/emd_criteria.py changed since the ru
```

## checksums

```
{
 "rehashed_files": 15,
 "rehashed_bytes": 534110,
 "cached_files": 31414,
 "cached_bytes": 809603714552,
 "full": false,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
}
```

## compare

```
[
 [
  "note/tables/ledger_g2.tex",
  "PASS",
  "identical"
 ],
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
  "note/figures/fig_g2_convergence.pdf",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_ball_exact.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_slice_mosaic.pdf",
  "PASS",
  "identical"
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
  "note/figures/schem_ladder.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_ball_exact.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_g2_convergence.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_criteria.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_slice_mosaic.png",
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
 ],
 [
  "note/figures/schem_ladder.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
