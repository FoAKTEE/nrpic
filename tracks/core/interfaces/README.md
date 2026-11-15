# core / interfaces: corrections to brief section 2 (C0) and interface documents (C1)

Work package "doc" of core in wave 1 (`coord/digests/wave-1-plan.md`). Everything here
is a proposal: the orchestrator decides what goes into `coord/INTERFACES/` and into the
brief. Written from the paper source and from the code at commit b7b431d of `main`.

## Contents

| File | What it is |
|---|---|
| `SECTION2_CORRECTIONS.md` | Section 2 of the brief checked item by item against `refs/arxiv_2611.12831/src/main.tex` (v1, locators `Lnnn`); answers to the seven [TO VERIFY] items of brief line 134; implementation details the paper states and leaves open; differences between the paper and this repository's code |
| `deposit.md` | definition and mesh centring of the ten sources, clouds, level cap, filter and compensation, density form, conservation identity; options, defaults, tests |
| `pusher.md` | particle state, the two pushers, metric reconstruction, removal and reassignment, time step; options, defaults, tests |
| `particle_id.md` | particle file, problem generators `nrpic_cf`, `nrpic_cosmo`, `nrpic_geodesic`, table and field formats, the particle generators and what each guarantees |
| `diagnostics.md` | every output file with its columns or byte layout, cadence options, restart files, the AthenaK outputs used with the module |
| `cosmo_gauge.md` | lapse and shift options, constraint damping and relaxation, step limit, configurations in use |
| `run_manifest.md` | manifest fields of brief section 11.6 merged with `CLAUDE.md` rule 4, with an example |
| `JOURNAL.md` | predictions and outcomes (test D1) |
| `check/d1_formats.athinput` | input of test D1 (all outputs on, 16^3 periodic dust universe) |
| `check/read_outputs.py` | readers for every output file, written from `diagnostics.md`, and the D1 check and figures |
| `check/manifest_core-20261115-112600-b7b431d.json` | copy of the run manifest (the original under `tracks/core/runs/` is ignored by git, see Requests) |
| `figs/d1_history.png`, `figs/d1_slices.png`, `figs/d1_summary.json` | figures and check results of D1 |

Test coverage of each option is given in the documents as entries of `docs/TESTLOG.md`
and `cosmo/TESTLOG.md` by title.

## How to rerun test D1 (processors, about 10 s)

```
RID=<new run id>; OUT=/data/haiyangw/nrpic/scratch/core/$RID
cd /data/haiyangw/nrpic/wt/core/cosmo/ic && python3 make_lattice.py --n 16 --ppc 1 --L 4 \
    --H0 1 --noise-x 0.01 --noise-u 1e-4 --seed 1 --out $OUT/ic
mkdir -p $OUT/run1 $OUT/run2 && cp $OUT/ic/particles.nrp $OUT/run1/ && \
    cp /data/haiyangw/nrpic/wt/core/tracks/core/interfaces/check/d1_formats.athinput $OUT/run1/
cd $OUT/run1 && /data/haiyangw/nrpic/.work/build_cpu_c1/src/athena -i d1_formats.athinput
cd $OUT/run2 && /data/haiyangw/nrpic/.work/build_cpu_c1/src/athena -r $OUT/run1/rst/flrw.00001.rst
python3 /data/haiyangw/nrpic/wt/core/tracks/core/interfaces/check/read_outputs.py \
    $OUT/run1 $OUT/run2 $OUT/ic/particles.nrp $OUT/figs
```

With the processor executable of 2026-11-14 06:03 PST, 24 of 25 checks pass (the failing
one is the tolerance of my own prediction for the mass sum, see `JOURNAL.md`). With a
current executable `.cstat.hst` has 19 columns and the `cstat` check must be changed to
19.

## What is done and what is not

Done: all seven documents; test D1 (run `core-20261115-112600-b7b431d`) checks the
layouts of every file of the particle module and the exactness of a restart on a
uniform periodic mesh.
Not done or not checked by a run of this package:
- outputs on refined meshes (curvature slices with several cell sizes, the level cap,
  the filter across levels) and the horizon-finder files: described from the source and
  the test logs only;
- columns 17-19 of `.cstat.hst`, `damp_ch_chipow`, `damp_kappa_gam`: not in the
  processor executable, not exercised;
- the Boris pusher's untouched proper time and its handling of null particles: read
  from the source, not tested;
- format 2 of the radial table: only pointed to (branch `core/id-extrinsic`);
- no card time was used.

## Requests

1. **orch**: change the ignore rule `runs/` (`.gitignore` line 12) to `/runs/`; it
   also excludes `tracks/<ID>/runs/`, so no run manifest of any track can be committed
   without `-f` (`run_manifest.md` section 1).
2. **orch / core lead**: rebuild the processor executable
   `.work/build_cpu_c1/src/athena` from current `main`; it predates commits 631cfe3,
   010aace and 0c06525 and silently ignores `damp_ch_chipow` and `damp_kappa_gam`
   (`JOURNAL.md` 11:21). Until then `CLAUDE.md` could say which features each shared
   executable has.
3. **orch (owner of `docs/`)**: bring the outputs table of `docs/FORMATS.md` in line with
   `diagnostics.md` sections 1, 6, 7 and 9 (history columns, `.trajmet.bin` with 17
   values, proper time in snapshots, restart format `NRPRST05`).
4. **kb**: confirm page count, submission date and categories of arXiv:2611.12831 from
   the abstract record (not in the source; `SECTION2_CORRECTIONS.md` 1.1).
5. **orch**: review the six interface documents for `coord/INTERFACES/` and the
   corrections for the brief; the rules marked [JUDGEMENT] in each document (frozen
   particle state and file formats for core-v0.1, a separate operator slot for
   non-gravitational kicks, a conservative filter across levels for core-v0.2) need a
   decision.
6. **Tracks A, B, D**: a shift condition in an expanding background has no passing test
   (`cosmo_gauge.md` section 2); runs with moving black holes in cosmology depend on it.
