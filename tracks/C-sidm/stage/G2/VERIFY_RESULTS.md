# Re-verification: C-sidm G2

`harness/bin/nrpic-stage verify C-sidm G2` on 2026-11-27T10:40:35Z, clean export of commit `6764898fa3f4` in `scratch/C-sidm/tmp/stage-verify/C-sidm-G2-6764898-20261127T085337Z`. Result: **FAIL**.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 6764898fa3f4 (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G2-6764898-20261127T085337Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 14 figures, each with its script |
| min-figs | PASS | 4 schematics and 10 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 2 of 263 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | PASS | 9199 output files: 9199 hashed again (bytes read, 1184.70 GB), 0 taken from the cache (0.0 MB) (--full); every byte read again (none taken from the cache, where a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again) |
| status | PASS | STATUS.md has 32 lines |
| rerun | PASS | 14 of 14 scripts and commands ran cleanly in the export |
| compare | PASS | 28 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 28 committed figure files regenerated |

## runs

```
{
 "C-20261121-210524-36a658e": [
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00001.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00002.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00003.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00004.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00005.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00006.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00007.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00008.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00009.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00010.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00011.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00012.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00013.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00014.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.05_p0.1_dx0.125/heat.part.00015.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00001.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00002.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00003.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00004.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00005.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00006.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00007.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00008.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00009.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00010.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00011.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00012.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00013.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00014.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.125/heat.part.00015.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00001.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00002.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00003.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00004.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00005.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00006.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00007.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00008.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00009.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00010.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00011.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00012.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00013.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00014.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.25/heat.part.00015.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00001.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00002.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00003.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00004.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00005.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00006.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00007.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00008.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00009.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00010.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00011.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00012.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00013.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00014.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s6_dt0.1_p0.1_dx0.5/heat.part.00015.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00001.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00002.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00003.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00004.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00005.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00006.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00007.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00008.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00009.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00010.bin",
  "missing output TC_th0.003_kl0.2_e0.2_s7_dt0.05_p0.1_dx0.125/heat.part.00011.bin",
  "missing output TC_
```

## run-notes

```
{
 "C-sidm-20261115-115344-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115344-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-115348-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115348-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-115400-eb8b752": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-115400-eb8b752/sha256sums.txt (hand-written manifest; outputs not re-verifiable)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-120610-b4592be": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input tracks/C-sidm/equilibria/check_equilibria.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-120703-9b3e868": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-120703-9b3e868/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-120715-38ab057": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/test_tmb.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120717-38ab057": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/paper_tables.py no longer present (not re-verifiable)",
  "input kb-data/raw/arxiv/2108.11967/v2/src/main.tex no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120722-38ab057": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/run_sequence.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-120801-38ab057": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "input tracks/C-sidm/equilibria/check_equilibria.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-121302-313d399": [
  "output directory read from a field other than outputs.dir",
  "no gate",
  "no scratch/C-sidm/C-sidm-20261115-121302-313d399/sha256sums.txt (hand-written manifest; outputs not re-verifiable)"
 ],
 "C-sidm-20261115-121400-d463e1a": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/pulsation_check.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121412-d463e1a": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/timescales.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121524-5cebcf5": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/pulsation_check.py no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121536-5cebcf5": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/initial_models.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121626-e99907d": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input python/nrpic/io.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-121748-4e8d6b5": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/initial_models.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120722-38ab057/criteria.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121811-38da24f": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/make_figures.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-121859-690ff91": [
  "hand-written (launcher 'local (tracks/C-sidm/gravothermal/register.py)')",
  "input wt/C-sidm/tracks/C-sidm/gravothermal/make_figures.py no longer present (not re-verifiable)",
  "input scratch/C-sidm/C-sidm-20261115-120717-38ab057/f21_tables.json no longer present (not re-verifiable)"
 ],
 "C-sidm-20261115-122915-cdc395c": [
  "status 'done' read as completed",
  "output directory read from a field other than outputs.dir",
  "no gate",
  "status 'done' read as completed",
  "input tracks/C-sidm/equilibria/knudsen.py changed since the run (sha256 differs)",
  "input python/nrpic/io.py changed since the run (sha256 differs)",
  "input python/nrpic/figstyle.py changed since the run (sha256 differs)"
 ],
 "C-sidm-20261115-125308-54870b9": [
  "status 'done' read as completed",
  "output directory rea
```

## checksums

```
{
 "rehashed_files": 9199,
 "rehashed_bytes": 1184696052959,
 "cached_files": 0,
 "cached_bytes": 0,
 "full": true,
 "meaning_of_a_cached_entry": "a checksum taken from the cache proves unchanged size and modification time since it was hashed, not bytes read again",
 "notes": []
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
  "note/figures/fig_g2_threshold.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_box_summary.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_collisions.png",
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
  "note/figures/fig_box_step.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_cluster.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_g2_threshold.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_cluster.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_ladder.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_heat.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_box_summary.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_heat.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_g2_mosaic.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/schem_architecture.png",
  "PASS",
  "identical"
 ],
 [
  "note/figures/fig_onsets.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
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
  "note/figures/schem_ladder.svg",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_g2_mosaic.pdf",
  "PASS",
  "regenerated (vector files carry dates; the PNG preview is compared)"
 ],
 [
  "note/figures/fig_onsets.png",
  "PASS",
  "identical"
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
