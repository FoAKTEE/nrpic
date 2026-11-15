# Re-verification: E-stoch-inf G0

`harness/bin/nrpic-stage verify E-stoch-inf G0` on 2026-11-15T17:36:21Z, clean export of commit `55ab0781f8c0` in `scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G0-55ab078-20261115T173542Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 55ab0781f8c0 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G0-55ab078-20261115T173542Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: spec/scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 7 of 60 runs have problems |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## runs

```
{
 "E-20261115-170645-3b21217": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-170645-3b21217/sha256sums.txt"
 ],
 "E-20261115-170727-d15df12": [
  "status is running: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-170727-d15df12/sha256sums.txt"
 ],
 "E-20261115-172347-a297a96": [
  "status is running: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-172347-a297a96/sha256sums.txt"
 ],
 "E-20261115-172618-f948386": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-172618-f948386/sha256sums.txt"
 ],
 "E-20261115-172625-416fec0": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-172625-416fec0/sha256sums.txt"
 ],
 "E-20261115-172629-312a82c": [
  "status is submitted: not finished (nrpic-run finish)",
  "missing /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-172629-312a82c/sha256sums.txt"
 ],
 "E-20261115-173540-b69c63f": [
  "status is running: not finished (nrpic-run finish)"
 ]
}
```

## run-notes

```
{
 "E-stoch-inf-20261115-122727-a1c2237": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-122727-a1c2237/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-122806-ef0d039": [
  "output directory read from a field other than outputs.dir",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-122806-ef0d039/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-122934-9ac98d8": [
  "output directory read from a field other than outputs.dir",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-122934-9ac98d8/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-123146-82d2fd4": [
  "output directory read from a field other than outputs.dir",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-123146-82d2fd4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-123201-82d2fd4": [
  "output directory read from a field other than outputs.dir",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-123201-82d2fd4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/spec/ref/make_figures.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-123236-2e87364": [
  "output directory read from a field other than outputs.dir",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-123236-2e87364/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-123936-b2ec5c7": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-123936-b2ec5c7/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input /data/haiyangw/nrpic/scratch/E-stoch-inf/E-stoch-inf-20261115-122727-a1c2237/<case>/time.log and athena.log: no sha256 recorded"
 ],
 "E-stoch-inf-20261115-125014-097160b": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125014-097160b/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/scripts/v1_drift_diffusion.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/exact.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125255-fcdcbdc": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125255-fcdcbdc/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125312-dafadc4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125312-dafadc4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/scripts/v1_drift_diffusion.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125316-dafadc4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125316-dafadc4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/scripts/v2_quadratic.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125434-742a681": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125434-742a681/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/count_draws.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125603-39cb4dd": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125603-39cb4dd/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125656-e3eaef3": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125656-e3eaef3/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-125658-e3eaef3": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125658-e3eaef3/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-130137-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-130137-176cdd6/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-130139-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-130139-176cdd6/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-130747-1b9bee4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-130747-1b9bee4/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "E-stoch-inf-20261115-130917-74083ad": [
  "output directory read from a field other than outputs.dir",
  
```

## compare

```
[
 [
  "note/figures/fig_deltan.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_noise.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_background.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_freezing.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_noise.png",
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
  "note/figures/fig_deltan.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_background.png",
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
  "note/figures/fig_freezing.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
