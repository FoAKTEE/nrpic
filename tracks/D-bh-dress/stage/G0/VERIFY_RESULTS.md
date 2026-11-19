# Re-verification: D-bh-dress G0

`harness/bin/nrpic-stage verify D-bh-dress G0` on 2026-11-19T15:44:55Z, clean export of commit `b7777f441e37` in `scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G0-b7777f4-20261119T154350Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of b7777f441e37 (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G0-b7777f4-20261119T154350Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 1 of 153 runs have problems |
| run-notes | WARN | 97 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 8 of 8 scripts and commands ran cleanly in the export |
| compare | PASS | 23 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## runs

```
{
 "D-20261119-142633-6f72922": [
  "status is submitted: not finished (nrpic-run finish)"
 ]
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
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170826-20d5d4a": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170827-ba851f0": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170829-0d86d49": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170831-b379b65": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170834-ac15adf": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170837-af64029": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-170839-187b91b": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171245-a89f225": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171247-cde0674": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171414-93fdf13": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171503-4262f03": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171505-62940f4": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171507-d1058a9": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-171508-94e8cb1": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171532-ba23a99": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171534-ff5b0e9": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171543-d966aba": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171545-d7e01a7": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171733-633d422": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171818-a5aefe8": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-171953-908afff": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-173149-7c6dd72": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/stage/G0/verify/hand_run.py, because harness/bin/nrpic-r)"
 ],
 "D-20261115-174734-a688058": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_analyze.py changed since the run (sha256 differs)"
 ],
 "D-20261115-180251-ffafe32": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_analyze.py changed since the run (sha256 differs)"
 ],
 "D-20261115-185248-9dc7934": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_analyze.py changed since the run (sha256 differs)"
 ],
 "D-20261115-190403-0bdb9b7": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_analyze.py changed since the run (sha256 differs)"
 ],
 "D-20261115-190541-e27453d": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-20261115-190543-783d7be": [
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)"
 ],
 "D-bh-dress-20261115-042626-f3da881": [
  "status N
```

## compare

```
[
 [
  "note/tables/ledger.tex",
  "PASS",
  "identical"
 ],
 [
  "note/tables/claims.json",
  "PASS",
  "identical"
 ],
 [
  "note/tables/parameters.tex",
  "PASS",
  "identical"
 ],
 [
  "note/tables/claims.md",
  "PASS",
  "identical"
 ],
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
 ]
]
```
