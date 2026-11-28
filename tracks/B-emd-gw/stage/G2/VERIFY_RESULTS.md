# Re-verification: B-emd-gw G2

`harness/bin/nrpic-stage verify B-emd-gw G2` on 2026-11-28T04:13:59Z, clean export of commit `7da01b9cc36e` in `scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G2-7da01b9-20261128T041109Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 7da01b9cc36e (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G2-7da01b9-20261128T041109Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 15 figures, each with its script |
| min-figs | PASS | 6 schematics and 9 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 3 of 416 runs have problems; 1 waived |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): B-20261115-164157-40b9f6d: outputs moved into the run directory after the run finished; data unchanged |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | 14069 output files: 27 hashed again (bytes read, 1.0 MB), 14042 taken from the cache (1166.93 GB); a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again; --full reads every byte |
| status | PASS | STATUS.md has 38 lines |
| rerun | PASS | 15 of 15 scripts and commands ran cleanly in the export |
| compare | PASS | 30 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 30 committed figure files regenerated |

## runs

```
{
 "B-20261128-030420-33ccdca": [
  "status is running: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/B-emd-gw/B-20261128-030420-33ccdca/sha256sums.txt"
 ],
 "B-20261128-034731-640f4f4": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/B-emd-gw/B-20261128-034731-640f4f4/sha256sums.txt"
 ],
 "B-20261128-040950-1404d91": [
  "status is running: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/B-emd-gw/B-20261128-040950-1404d91/sha256sums.txt"
 ]
}
```

## runs-waived

```
{
 "B-20261115-164157-40b9f6d": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "outputs moved into the run directory after the run finished; data unchanged",
  "problems": [
   "output not in sha256sums.txt: reference.png",
   "output not in sha256sums.txt: reference.pdf",
   "output not in sha256sums.txt: reference_g.npz",
   "output not in sha256sums.txt: sha256sums.moved.txt",
   "output not in sha256sums.txt: reference.json"
  ]
 }
}
```

## run-notes

```
{
 "B-emd-gw-20261115-112946-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112946-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-112947-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112947-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-112948-b7b431d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-112948-b7b431d/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113102-bc5e082": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113120-bc5e082": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113148-4e5c33b": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113151-4e5c33b": [
  "hand-written (fields nrpic-run never writes: card_hours, commit, cores, output_dir, package)"
 ],
 "B-emd-gw-20261115-113212-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113212-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113213-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113213-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113214-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113214-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113215-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113215-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113216-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113216-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113217-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113217-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113218-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113218-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113219-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113219-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113220-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113220-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113221-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113221-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113222-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113222-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113223-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113223-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113227-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113227-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113231-0ea0f74": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "no scratch/B-emd-gw/B-emd-gw-20261115-113231-0ea0f74/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "B-emd-gw-20261115-113232-0ea0f74": [
  "status 'done' read as co
```

## checksums

```
{
 "rehashed_files": 27,
 "rehashed_bytes": 962629,
 "cached_files": 14042,
 "cached_bytes": 1166927439192,
 "full": false,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
}
```

## compare

```
[
 [
  "note/figures/fig_gauge.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_waves.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_baseline.pdf",
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
  "note/figures/fig_scan.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_scan.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_waves.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_architecture_g2.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline_g2.svg",
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
  "note/figures/schem_ladder.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_pop_gauge.png",
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
  "note/figures/fig_source.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_pancake.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture_g2.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_gauge.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_ladder.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_baseline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_newton.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_r2.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_source.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_r2.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_timeline_g2.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_pancake.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_pop_gauge.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
