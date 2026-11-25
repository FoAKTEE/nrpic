# Re-verification: D-bh-dress G2

`harness/bin/nrpic-stage verify D-bh-dress G2` on 2026-11-25T16:11:48Z, clean export of commit `69f47d5f2ad8` in `scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G2-69f47d5-20261125T161012Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 69f47d5f2ad8 (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G2-69f47d5-20261125T161012Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 13 figures, each with its script |
| min-figs | PASS | 2 schematics and 11 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 2 of 311 runs have problems; 1 waived |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): D-20261121-165420-5d1c245: superseded: the check run of the G1 gate reviewer; an input under scratch changed after the run; its result stands in the gate review of G1 and no later claim rests on it (decision 0039 item 4) |
| run-notes | WARN | 99 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 13 of 13 scripts and commands ran cleanly in the export |
| compare | PASS | 37 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 26 committed figure files regenerated |

## runs

```
{
 "D-20261124-172725-2f426b6": [
  "status is submitted: not finished (nrpic-run finish)"
 ],
 "D-20261124-172745-72472ed": [
  "status is submitted: not finished (nrpic-run finish)"
 ]
}
```

## runs-waived

```
{
 "D-20261121-165420-5d1c245": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "superseded: the check run of the G1 gate reviewer; an input under scratch changed after the run; its result stands in the gate review of G1 and no later claim rests on it (decision 0039 item 4)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/gate_review_G1/review_checks.py changed since the run (sha256 differs)"
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
  "hand-written (registered_by: hand: tracks/D-bh-dress/secondary_infall/nm_register.py, because harness/bin/nrp)",
  "input tracks/D-bh-dress/secondary_infall/nm_field.py changed since the run (sha256 differs)"
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
 ]
```

## compare

```
[
 [
  "note/figures/fig_q16_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_kerr_seeds_numbers.json",
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
  "note/figures/fig_q16.png",
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
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_esrun.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_kerr_seeds.png",
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
  "note/figures/fig_esf.png",
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
  "note/figures/fig_esf_numbers.json",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_kerr_seeds.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
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
  "note/figures/fig_q16.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_esf.pdf",
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
