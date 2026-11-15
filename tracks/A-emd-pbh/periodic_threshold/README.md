# periodic_threshold: the threshold line in the periodic box (Track A, wave 2)

Helper package of A-emd-pbh (decision 0013: the threshold line of S1 is built in the
periodic box). Design of the set-up and the first scouting runs. Everything here is
analysis, reference arithmetic, drivers of the repository's own tools, inputs and run
manifests; no simulation code (decision 0010).

| File | Content |
|---|---|
| `DESIGN.md` | the design: initial data, gauge, mesh, horizon finder, collapse definition, scan grid and cost, the scouting runs, requests |
| `JOURNAL.md` | predictions written before each test, outcomes after (including the refuted ones and one bug of my own driver) |
| `scripts/design_numbers.py` | P0: epochs, box size in Hubble radii, Zel'dovich and top-hat collapse times (arithmetic) |
| `scripts/make_peak_ic.py` | driver: the peak of arXiv:2609.14218 through `cosmo/ic/make_field.py` (unchanged) into the files of `nrpic_cosmo`; also evaluates the gradient-expansion data of the paper on the same mesh for comparison |
| `scripts/t1_sweep.py` | T1: the solve change c of make_field against amplitude, start epoch, resolution, filter |
| `scripts/t2t3_cpu.py` | T2/T3: static and adaptive mesh in the periodic box; the horizon finder in a periodic mesh (processor executable) |
| `scripts/build_scouting_ic.sh` | data of the scouting runs S1 (mu = 0.5) and S2 (mu = 0.03) |
| `scripts/analyse_scouting.py` | S1/S2: histories, lapse and density along the axes, finder output, figures |
| `scripts/register_run.py`, `scripts/card_run.py` | registration by hand of processor and card runs (see Requests) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `inputs/peak_amr.athinput` | the periodic peak with adaptive refinement (Lohner) |
| `inputs/peak_smr.athinput` | processor test mesh: 32^3 root, two static levels |
| `inputs/peak_smr4.athinput` | the periodic peak with four static levels (scouting) |
| `inputs/punc_box16.athinput` | vacuum puncture in a 32 M box for the finder test |
| `figures/` | copies of the figures that DESIGN.md cites (made by the scripts in the run directories) |

Run directories: `/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/`, manifests under
`tracks/A-emd-pbh/runs/<run_id>/manifest.json`. Run ids are listed in DESIGN.md and
JOURNAL.md next to every number.

## How to rerun

From the worktree root, with the worktree environment `.venv` (numpy, scipy, matplotlib):

```
P=tracks/A-emd-pbh/periodic_threshold/scripts
.venv/bin/python -I $P/register_run.py --purpose "P0" -- .venv/bin/python -I $P/design_numbers.py --out {OUT}
.venv/bin/python -I $P/register_run.py --purpose "T1" --cores 4 -- .venv/bin/python -I $P/t1_sweep.py --out {OUT}
.venv/bin/python -I $P/register_run.py --purpose "T2/T3" --cores 3 -- .venv/bin/python -I $P/t2t3_cpu.py --out {OUT} --jobs 3
.venv/bin/python -I $P/register_run.py --purpose "S data" --cores 2 -- $P/build_scouting_ic.sh {OUT}
# card runs (data directory D from the previous line):
.venv/bin/python -I $P/card_run.py submit --purpose "S1" --wall 00:40:00 \
    --athinput tracks/A-emd-pbh/periodic_threshold/inputs/peak_smr4.athinput \
    --input D/S_mu0.5/fields.bin --input D/S_mu0.5/particles.nrp -- \
    problem/id_file=D/S_mu0.5/fields.bin particles/particle_file=D/S_mu0.5/particles.nrp time/tlim=14
.venv/bin/python -I $P/card_run.py finish <run_id>
.venv/bin/python -I $P/analyse_scouting.py --run <S1 run dir> --run <S2 run dir> --out <dir>
```

The exact command of every run is in its manifest.

## Pending at the time of writing

The card runs S2 (A-emd-pbh-20261115-155754-8422a4a, Slurm job 4448) and S1
(A-emd-pbh-20261115-160349-9d232d2, job 4451) were queued behind about ten jobs. When
`scratch/A-emd-pbh/<run_id>/batch.list.status` exists, close and analyse them:

```
.venv/bin/python -I tracks/A-emd-pbh/periodic_threshold/scripts/card_run.py finish A-emd-pbh-20261115-155754-8422a4a
.venv/bin/python -I tracks/A-emd-pbh/periodic_threshold/scripts/card_run.py finish A-emd-pbh-20261115-160349-9d232d2
S=/data/haiyangw/nrpic/scratch/A-emd-pbh
.venv/bin/python -I tracks/A-emd-pbh/periodic_threshold/scripts/register_run.py --purpose "S1/S2 analysis" -- \
  .venv/bin/python -I tracks/A-emd-pbh/periodic_threshold/scripts/analyse_scouting.py \
  --run S1=$S/A-emd-pbh-20261115-160349-9d232d2/run --run S2=$S/A-emd-pbh-20261115-155754-8422a4a/run --out {OUT}
```

then compare with the predictions S1/S2 in JOURNAL.md and fill DESIGN.md section 7.

## Requests

To core (details and reasons in DESIGN.md, section 8):
1. Phase-1 generator on a constant-mean-curvature slice (K = -3H), with the particle
   masses and momenta carrying E and J of the gradient-expansion data of
   arXiv:2609.14218 (MDPBH.tex:515-547), solved on the torus with the deposit of the run;
   a field-file format that carries the conformal metric (NRCOSMO1 holds psi only).
2. The constraint solve on the refined mesh (wave-2 item `idsolve`) for the periodic
   generator, or at least the clouds and the metric of refined blocks made consistent
   at t = 0.
3. The crash of adaptive refinement with periodic particles and `nrpic_cosmo` (T2c),
   if it is reproduced in the repeat.
4. The horizon finder: map surface points into the periodic box (T3c).
5. Output on refined meshes: the field dumps of the particle module (`field_time*`)
   return on multilevel meshes; a proper-volume mean of K and alpha in a history file
   (for the background time of the collapse definition).
6. A lapse for collapse in an expanding box (wave-2 item `gauge`); the candidate list is
   in DESIGN.md section 3.

To orch: `harness/bin/nrpic-run` refuses the shared worktree while other helpers hold
untracked files; every run of this package was therefore registered by hand with
`scripts/register_run.py` or `scripts/card_run.py` (fields of the manifest template plus
command, cwd, commit, inputs with sha256, output directory, wall time, cores or
card-hours). A per-path cleanliness check (the package directory and the inputs) would
let helpers use it.
