# Re-verification: C-sidm G0

`harness/bin/nrpic-stage verify C-sidm G0` on 2026-11-15T19:49:22Z, clean export of commit `3ba998966392` in `scratch/C-sidm/tmp/stage-verify/C-sidm-G0-3ba9989-20261115T194014Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 3ba998966392 (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G0-3ba9989-20261115T194014Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 10 of 72 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## runs

```
{
 "C-sidm-20261115-120715-38ab057": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-120717-38ab057": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-120722-38ab057": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121400-d463e1a": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121412-d463e1a": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121524-5cebcf5": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121536-5cebcf5": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121748-4e8d6b5": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121811-38da24f": [
  "fields missing: preregistered_in, code, input"
 ],
 "C-sidm-20261115-121859-690ff91": [
  "fields missing: preregistered_in, code, input"
 ]
}
```

## run-notes

```
{
 "C-sidm-20261115-115344-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115344-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-115348-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115348-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-115400-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115400-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-120610-b4592be": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input tracks/C-sidm/equilibria/check_equilibria.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-120703-9b3e868": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-120703-9b3e868/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-120715-38ab057": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/test_tmb.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120717-38ab057": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/paper_tables.py no longer present (not re-verifiable)",
  "input kb-data/raw/arxiv/2108.11967/v2/src/main.tex no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120722-38ab057": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/run_sequence.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120801-38ab057": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/C-sidm/equilibria/check_equilibria.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-121302-313d399": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-121302-313d399/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-121400-d463e1a": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/pulsation_check.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121412-d463e1a": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/timescales.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121524-5cebcf5": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/pulsation_check.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121536-5cebcf5": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/initial_models.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121626-e99907d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-121748-4e8d6b5": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/initial_models.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121811-38da24f": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/make_figures.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121859-690ff91": [
  "input wt/C-sidm/tracks/C-sidm/gravothermal/make_figures.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-122915-cdc395c": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input tracks/C-sidm/equilibria/knudsen.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-125308-54870b9": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-130010-69e27db": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input python/nrpic/io.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-131130-3077a99": [
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-131130-3077a99/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-131135-3077a99": [
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-131135-3077a99/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-132327-eab8e41": [
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-132327-eab8e41/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-132624-13a77db": [
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-132624-13a77db/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ]
}
```

## compare

```
[
 [
  "note/figures/schem_timeline.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_collisions.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_collisions.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_box_step.png",
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
  "note/figures/fig_knudsen.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/schem_timeline.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_box_step.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_sequences.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_knudsen.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_sequences.png",
  "PASS",
  "identical"
 ]
]
```
