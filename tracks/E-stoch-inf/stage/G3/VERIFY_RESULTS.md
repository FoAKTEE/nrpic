# Re-verification: E-stoch-inf G3

`harness/bin/nrpic-stage verify E-stoch-inf G3` on 2026-11-25T16:35:18Z, clean export of commit `21cd418fcb82` in `scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G3-21cd418-20261125T163310Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 2 uncommitted paths: commit them first (tracks/E-stoch-inf/RISKS.md, tracks/E-stoch-inf/stage/REVIEW-wave3.md) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 21cd418fcb82 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G3-21cd418-20261125T163310Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | WARN | stage/G3/ lacks EVIDENCE.md (decision 0012; STAGE_REPORT.md comes from `report`); scoping text: spec/scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 3 schematics and 9 data figures (brief 13.4 asks at least 1 and 1 at G3) |
| runs | FAIL | 1 of 317 runs have problems; 7 waived |
| runs-waived | WARN | failures of the manifest check waived: 7 runs named in main's coord/WAIVERS.md (decision 0019 item 6): E-20261123-035724-b661081: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-152119-38957ba: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153146-d965002: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-153347-18e7c21: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1); E-20261123-164235-49b0945: records scratch/core/exe/core_noise-level2/athena_gpu (sha256 468109496c82...), replaced in place on 2026-11-24; the file that ran is kept unchanged as scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (tracks/core/EXE_PROVENANCE.md on core/nrpic); outputs unaffected (decision 0039 item 1) |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 45 lines |
| rerun | WARN | re-run skipped (--no-rerun) |

## runs

```
{
 "E-20261125-160658-855db8c": [
  "status is running: not finished (nrpic-run finish)"
 ]
}
```

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
  "no gate"
 ],
 "E-stoch-inf-20261115-122806-ef0d039": [
  "output directory read from a field other than outputs.dir"
 ],
 "E-stoch-inf-20261115-122934-9ac98d8": [
  "output directory read from a field other than outputs.dir"
 ],
 "E-stoch-inf-20261115-123146-82d2fd4": [
  "output directory read from a field other than outputs.dir"
 ],
 "E-stoch-inf-20261115-123201-82d2fd4": [
  "output directory read from a field other than outputs.dir",
  "input tracks/E-stoch-inf/spec/ref/make_figures.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-123236-2e87364": [
  "output directory read from a field other than outputs.dir"
 ],
 "E-stoch-inf-20261115-123936-b2ec5c7": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/scratch/E-stoch-inf/E-stoch-inf-20261115-122727-a1c2237/<case>/time.log and athena.log: no sha256 recorded"
 ],
 "E-stoch-inf-20261115-125014-097160b": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/v1_drift_diffusion.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/exact.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125255-fcdcbdc": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125312-dafadc4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/v1_drift_diffusion.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125316-dafadc4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/v2_quadratic.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125434-742a681": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/count_draws.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125603-39cb4dd": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125656-e3eaef3": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-125658-e3eaef3": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130137-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/ref_spec.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130139-176cdd6": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/ref_spec.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130747-1b9bee4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130917-74083ad": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/ref_plot.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-130919-74083ad": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/scripts/ref_plot.py changed since the run (sha256 differs)",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-131031-ec74943": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/validate/validate_noise.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/validate/athenak_io.py changed since the run (sha256 differs)",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/ref/noise_ref.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-131126-8eb199a": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input /data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/noise/validate/athenak_io.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-131133-02047c4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/sdn/langevin.py changed since the run (sha256 differs)"
 ],
 "E-stoch-inf-20261115-131232-02047c4": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/E-stoch-inf/langevin/sdn/lange
```
