# Re-verification: D-bh-dress G1

`harness/bin/nrpic-stage verify D-bh-dress G1` on 2026-11-21T07:07:14Z, clean export of commit `9182d4dddadd` in `scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G1-9182d4d-20261121T064019Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 3 uncommitted paths: commit them first (tracks/D-bh-dress/drift_controls/tools/compare_runs.py, tracks/D-bh-dress/drift_controls/tools/count_blocks.py, tracks/D-bh-dress/drift_controls/tools/slice_profiles.py) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 9182d4dddadd (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G1-9182d4d-20261121T064019Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | WARN | note/main.pdf is older than the last change of its .tex files |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 10 figures, each with its script |
| min-figs | PASS | 2 schematics and 8 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 3 of 188 runs have problems; 3 waived |
| runs-waived | WARN | failures of the manifest check waived: 3 hand-written manifests of waves 1 and 2 listed in EVIDENCE.md (decision 0016 item 3) |
| run-notes | WARN | 100 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 10 of 10 scripts and commands ran cleanly in the export |
| compare | FAIL | 28 regenerated files compared with the committed ones; 1 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 20 committed figure files regenerated |

## runs

```
{
 "D-20261115-170002-8cefc3e": [
  "output not in sha256sums.txt: v1_es_slice.pdf",
  "output not in sha256sums.txt: v1_es_slice.json",
  "output not in sha256sums.txt: v1_es_slice.png"
 ],
 "D-20261115-170326-dfb2a02": [
  "output not in sha256sums.txt: es.horizon_summary_0.txt.from_cwd"
 ],
 "D-20261115-193755-3a53b08": [
  "output not in sha256sums.txt: misplaced_out/es_check.png",
  "output not in sha256sums.txt: misplaced_out/es_check.json",
  "output not in sha256sums.txt: misplaced_out/es_check.pdf"
 ]
}
```

## runs-waived

```
{
 "D-bh-dress-20261115-121313-284ec4f": {
  "listed_in": "stage/G0/EVIDENCE.md",
  "problems": [
   "production run without preregistered_in"
  ]
 },
 "D-bh-dress-20261115-121314-284ec4f": {
  "listed_in": "stage/G0/EVIDENCE.md",
  "problems": [
   "production run without preregistered_in"
  ]
 },
 "D-bh-dress-20261115-130954-49ed46f": {
  "listed_in": "stage/G0/EVIDENCE.md",
  "problems": [
   "production run without preregistered_in"
  ]
 }
}
```

## run-notes

```
{
 "D-20261115-170700-b2c6d6e": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_ic.py changed since the run (sha256 differs)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170703-46ddffa": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_ic.py changed since the run (sha256 differs)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170706-71431c6": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_ic.py changed since the run (sha256 differs)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170803-d988f59": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170824-788678f": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170826-20d5d4a": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170827-ba851f0": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170829-0d86d49": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170831-b379b65": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170834-ac15adf": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170837-af64029": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-170839-187b91b": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_shells.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171245-a89f225": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171247-cde0674": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171414-93fdf13": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171503-4262f03": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171505-62940f4": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171507-d1058a9": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_run.py changed since the run (sha256 differs)"
 ],
 "D-20261115-171508-94e8cb1": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)",
  "no scratch/D-bh-dress/D-20261115-171508-94e8cb1/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "D-20261115-171532-ba23a99": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)",
  "no scratch/D-bh-dress/D-20261115-171532-ba23a99/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "D-20261115-171534-ff5b0e9": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)",
  "no scratch/D-bh-dress/D-20261115-171534-ff5b0e9/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "D-20261115-171543-d966aba": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)",
  "no scratch/D-bh-dress/D-20261115-171543-d966aba/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "D-20261115-171545-d7e01a7": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)",
  "no scratch/D-bh-dress/D-20261115-171545-d7e01a7/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "D-20261115-171733-633d422": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/
```

## compare

```
[
 [
  "note/figures/fig_infall.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_floor_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_infall_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_kerr.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_es.pdf",
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
  "note/figures/fig_kerr.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_es_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_constraints.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_kerr_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_esrun.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_floor.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_floor.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_spike_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton_numbers.json",
  "FAIL",
  "text differs (not only numbers)"
 ],
 [
  "note/figures/fig_esrun.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_constraints_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_spike.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_esrun_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_constraints.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_spike.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_infall.png",
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
  "note/figures/fig_es.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_newton.png",
  "PASS",
  "identical"
 ]
]
```
