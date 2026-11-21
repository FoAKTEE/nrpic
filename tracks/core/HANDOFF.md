# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21): release candidate core-v0.4 is complete on `core/nrpic`. The seven
wave-2 source branches are merged (one merge commit each; source commit f9323185, the
last commit that changes `athenak/`, `python/`, `problems/`, `scripts/`); none is left
out. `tracks/core/RELEASE-v0.4.md` has the verdict line, the regression table, the quick
tests, the card check and the known defects; `tracks/core/CHANGELOG.md` section
core-v0.4 has the options and the corrections that act without an option;
`tracks/core/stage/G2/OPEN.md` (first section) the defects. Executables with READY:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-run status core-20261121-025945-54dc669`
(if `RELEASE-v0.4.md`, section "Card check", still says PENDING: close the card job as
described below; otherwise go on to the wave-3a branches for core-v0.5).

Card check of the candidate (run core-20261121-025945-54dc669, Slurm job 4758, eleven
cases of `analysis/release/card_v04.list` with `.work/build_gpu_v04rc/src/athena`). When
the job has ended:
```
harness/bin/nrpic-run finish core-20261121-025945-54dc669
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --parent core-20261121-025945-54dc669 --purpose "card check of core-v0.4 judged against the processor runs" -- python3 tracks/core/analysis/release/card_v04.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-025945-54dc669 --cpu /data/haiyangw/nrpic/scratch/core/core-20261121-025955-bd47414 --out '$NRPIC_RUN_DIR'
```
then look at `fig_card_v04.png`, write the outcome against predictions C and C1 to C5
of `JOURNAL.md` (entries 2026-11-20T22:10Z and 2026-11-21T02:58Z), replace the section
"Card check" of `RELEASE-v0.4.md`, the STATUS paragraph of athena_gpu and item C of
`scratch/core/exe/core_nrpic_v04/READY`, commit, push.

Files to read first: `tracks/core/STATUS.md`; `tracks/core/RELEASE-v0.4.md`;
`tracks/core/stage/G2/OPEN.md`; the last two entries of `tracks/core/JOURNAL.md`; for a
capability its interface document under `tracks/core/interfaces/` and the journal of
its package (`JOURNAL-{bfix,gauge,scalar2,clump,idsolve,dfix,coll2}.md`).

Executables (read-only): candidate `wt/core/.work/build_cpu_v04rc/src/athena`,
`wt/core/.work/build_gpu_v04rc/src/athena` (= the published copies; sha256 in
SHA256SUMS there); release core-v0.3 `/data/haiyangw/nrpic/.work/build_{cpu,gpu}_v03/src/athena`.
Build after a source change: `scripts/build_cpu.sh .work/<dir>`, `scripts/build_gpu.sh
.work/<dir>` in a NEW directory (an incremental card build that overlaps a header
change left stale objects once: `interfaces/collisions.md` 11.5).

How the release checks are run (each a registered run; outputs under scratch/core/<run_id>/):
- byte regression against the previous release, twelve set-ups, about 7 minutes on 3
  cores: `analysis/release/regress_v04.py --base OLD --new NEW --out DIR --cores 3`;
  figure and table: `analysis/release/fig_regress_v04.py RUNDIR --out DIR`
- one example per merged branch against the branch's published executable, about 9
  minutes on 4 cores: `analysis/release/quick_v04.py --new NEW --out DIR --cores 4`
  (`--analyse-only --runs OLDDIR` evaluates and draws again without running)
- card: `harness/bin/nrpic-run submit --launcher batch --list
  tracks/core/analysis/release/card_v04.list --exe <athena_gpu> --gpu-hours 0.2`, then
  `analysis/release/card_v04.py --card RUNDIR --cpu QUICKRUNDIR --out DIR`
For core-v0.5: copy the three drivers, replace the cases of quick and card by the
examples of the nine wave-3a READY files, and take core-v0.4 as the base.

Open with other owners:
- orch/clerk: tag, merge into main, release executables, interface documents to
  `coord/INTERFACES/` (list in RELEASE-v0.4.md, "For the release clerk").
- Track C: four format requests, an ADM-mass diagnostic and collisions on refined
  meshes (outbox 20261120T220741Z__to-C-sidm__collisions-2-card-closed.md lists them).
- Track A: `hmean_tol` and the other findings of package cosmo-amr (its outbox message
  of 2026-11-20 on branch core/cosmo-amr).
- 26 GB of restart files of run core-20261119-143232-4d1e995 and 12 GB of
  core-20261120-220816-09f6f79 may be deleted once nothing reads them (orchestrator).

Traps:
- Byte comparisons against core-v0.3 show two intended classes of difference (36 unset
  restart bytes; `last_time` lines of embedded parameter dumps): the release drivers
  classify them. Against core-v0.4 neither should appear.
- Preparation products (particle files and the generator's json, which holds the
  directory name) are not outputs: `quick_v04.py` lists them before AthenaK starts.
- On a card, runs with deposit and collisional runs are not byte-reproducible against
  another executable: compare counts and bounds (`card_v04.py`).
- AthenaK accepts on the command line only parameters that the input file has.
- `.bin` dumps are single precision unless `double_precision = true`.
- `runs/` in .gitignore also hides `tracks/core/runs/`: nrpic-run adds its manifests
  itself; a hand-written manifest needs `git add -f`.
- The clock: take times from `date -u`; two sessions wrote estimated times into
  journal headings and had to correct them.
- `scratch/core/` is shared by every core session: this session's temporary files are
  in `scratch/core/tmp/lead_v04/` and `scratch/core/tmp/cardtest/`.
