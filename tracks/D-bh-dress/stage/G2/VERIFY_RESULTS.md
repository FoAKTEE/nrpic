# Re-verification: D-bh-dress G2

`harness/bin/nrpic-stage verify D-bh-dress G2` on 2026-11-27T23:53:31Z, clean export of commit `226a0d645e6b` in `scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G2-226a0d6-20261127T234733Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 226a0d645e6b (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G2-226a0d6-20261127T234733Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md, scope/SCOPE_G3.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 14 figures, each with its script |
| min-figs | PASS | 2 schematics and 12 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 1 of 336 runs have problems; 4 waived |
| runs-waived | WARN | failures of the manifest check waived: 4 runs named in main's coord/WAIVERS.md (decision 0019 item 6): D-20261115-170002-8cefc3e: outputs moved into the run directory after the run finished; data unchanged (decision 0021); D-20261115-170326-dfb2a02: outputs moved into the run directory after the run finished; data unchanged (decision 0021); D-20261115-193755-3a53b08: outputs moved into the run directory after the run finished; data unchanged (decision 0021); D-20261121-165420-5d1c245: superseded: the check run of the G1 gate reviewer; an input under scratch changed after the run; its result stands in the gate review of G1 and no later claim rests on it (decision 0039 item 4) |
| run-notes | WARN | 106 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | 15841 output files: 15 hashed again (bytes read, 2.70 GB), 15826 taken from the cache (704.27 GB); a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again; --full reads every byte |
| status | PASS | STATUS.md has 43 lines |
| rerun | PASS | 14 of 14 scripts and commands ran cleanly in the export |
| compare | PASS | 40 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 28 committed figure files regenerated |

## runs

```
{
 "D-20261127-233719-db5be88": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261127-233719-db5be88/sha256sums.txt"
 ]
}
```

## runs-waived

```
{
 "D-20261115-170002-8cefc3e": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
   "output not in sha256sums.txt: v1_es_slice.pdf",
   "output not in sha256sums.txt: v1_es_slice.json",
   "output not in sha256sums.txt: v1_es_slice.png"
  ]
 },
 "D-20261115-170326-dfb2a02": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
   "output not in sha256sums.txt: es.horizon_summary_0.txt.from_cwd"
  ]
 },
 "D-20261115-193755-3a53b08": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged (decision 0021)",
  "problems": [
   "output not in sha256sums.txt: misplaced_out/es_check.png",
   "output not in sha256sums.txt: misplaced_out/es_check.json",
   "output not in sha256sums.txt: misplaced_out/es_check.pdf"
  ]
 },
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
 "D-202
```

## checksums

```
{
 "rehashed_files": 15,
 "rehashed_bytes": 2698935893,
 "cached_files": 15826,
 "cached_bytes": 704266553118,
 "full": false,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
}
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
  "note/figures/fig_g2conv_numbers.json",
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
  "note/figures/fig_g2conv.png",
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
  "note/figures/fig_g2conv.pdf",
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
