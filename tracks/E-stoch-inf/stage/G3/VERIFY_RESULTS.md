# Re-verification: E-stoch-inf G3

`harness/bin/nrpic-stage verify E-stoch-inf G3` on 2026-11-26T16:29:50Z, clean export of commit `4d9d223b5169` in `scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G3-4d9d223-20261126T120759Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 1 uncommitted paths: commit them first (tracks/E-stoch-inf/stage/REVIEW-wave3.md) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 4d9d223b5169 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G3-4d9d223-20261126T120759Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | WARN | stage/G3/ lacks EVIDENCE.md (decision 0012; STAGE_REPORT.md comes from `report`); scoping text: spec/scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 3 schematics and 9 data figures (brief 13.4 asks at least 1 and 1 at G3) |
| runs | PASS | 337 run manifests finished (30 hand-written, read as decision 0012 allows); failures of 7 runs waived by coord/WAIVERS.md (decision 0019), output checksums verified where recorded |
| runs-waived | WARN | failures of the manifest check waived: 7 runs named in main's coord/WAIVERS.md (decision 0019 item 6): E-20261123-035724-b661081: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-152119-38957ba: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153146-d965002: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153347-18e7c21: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-164235-49b0945: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1) |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | 17621 output files: 16911 hashed again (bytes read, 2838.00 GB), 710 taken from the cache (145.51 GB); a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again; --full reads every byte |
| status | PASS | STATUS.md has 31 lines |
| rerun | PASS | 12 of 12 scripts and commands ran cleanly in the export |
| compare | PASS | 24 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 24 committed figure files regenerated |

## runs-waived

```
{
 "E-20261123-035724-b661081": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-152119-38957ba": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-153146-d965002": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-153347-18e7c21": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-164235-49b0945": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-183822-4abbcae": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 },
 "E-20261123-192948-348e2e5": {
  "waived_by": "coord/WAIVERS.md",
  "reason": "records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1)",
  "problems": [
   "input /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu changed since the run (sha256 differs)"
  ]
 }
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
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125656-e3eaef3/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125658-e3eaef3": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-125658-e3eaef3/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130137-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-130137-176cdd6/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input tracks/E-stoch-inf/langevin/scripts/ref_spec.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130139-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/E-stoch-inf/E-stoch-inf-20261115-130139-176cdd6/sha256sums.txt (hand-written manifest; outputs no
```

## checksums

```
{
 "rehashed_files": 16911,
 "rehashed_bytes": 2838002813143,
 "cached_files": 710,
 "cached_bytes": 145508796604,
 "full": false,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
}
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
  "note/figures/fig_sr_order.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_sr_order.pdf",
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
  "note/figures/fig_cost.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_sr_freezing.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_cost.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_sr_freezing.png",
  "PASS",
  "identical"
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
 ],
 [
  "note/figures/fig_sr_modes.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_sr_modes.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_sr_constraints.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_sr_constraints.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ]
]
```
