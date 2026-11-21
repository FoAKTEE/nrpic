# periodic_threshold: the threshold line in the periodic box (Track A, waves 2 and 3)

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
| `scripts/analyse_scouting.py` | S1/S2: histories, lapse and density along the axes, finder output, figures (`--gauge leak` for the wave-3 runs) |
| `scripts/build_p0l.sh`, `scripts/track_select.py` | wave 3: data of P0L (spherical peak, mu = 0.3) and the ordering of 317 tracked particles on the axes and diagonals |
| `scripts/ltbref.py`, `scripts/ltb_reference.py` | wave 3, R1: exact LTB references, A (the paper's profile) and B (the exact spherical future of the code's own initial slice, per tracked shell); the relaxed-lapse background; periodic-image estimates |
| `scripts/smoke_leak.sh` | wave 3, K: processor smoke test of the relaxed-lapse deck on both data sets |
| `scripts/compare_ltb.py` | wave 3: P0L against reference B in invariants (areal radius against own proper time, turnaround, trapping, finder mass against the expected mass, background lapse, constraints) |
| `inputs/peak_leak.athinput` | wave 3: the S1 mesh with the relaxed 1+log lapse, Gamma-driver, guard, finder status, light-speed step limit (release core-v0.5) |
| `lists/job1.list` | wave 3: card job 1 (P0L, S1L) |
| `scripts/register_run.py`, `scripts/card_run.py` | registration by hand of the wave-2 runs (no longer used: from wave 2b every run goes through `harness/bin/nrpic-run`) |
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

Wave 3 (2026-11-21), from the worktree root (every run through `harness/bin/nrpic-run`;
`--package tracks/A-emd-pbh/periodic_threshold`, the package committed first):

```
P=tracks/A-emd-pbh/periodic_threshold/scripts
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/periodic_threshold"
$R --purpose "P0L data" --launcher local --cores 2 -- bash -c "$P/build_p0l.sh \"\$NRPIC_RUN_DIR\""
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
$R --purpose "R1" --launcher local --cores 1 -- bash -c \
   'python -I '$P'/ltb_reference.py --data '$D' --mu 0.3 --rate 20 --out "$NRPIC_RUN_DIR"'
$R --purpose "K" --launcher local --cores 2 -- bash -c "$P/smoke_leak.sh \"\$NRPIC_RUN_DIR\" 4"
$R --purpose "card job 1" --launcher batch --exe /data/haiyangw/nrpic/.work/build_gpu_v05/src/athena \
   --list tracks/A-emd-pbh/periodic_threshold/lists/job1.list --wall 00:58:00
harness/bin/nrpic-run finish <run_id>
# analysis of card job 1 (run directory J = scratch/A-emd-pbh/<run_id>):
$R --purpose "P0L vs LTB" --launcher local --cores 1 -- bash -c \
   'python -I '$P'/compare_ltb.py --run J/P0L --ref /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-130103-e007f42 --out "$NRPIC_RUN_DIR"'
$R --purpose "S1L" --launcher local --cores 1 -- bash -c \
   'python -I '$P'/analyse_scouting.py --gauge leak --run S1L=J/S1L --out "$NRPIC_RUN_DIR"'
```

## Scouting runs

S2 (A-emd-pbh-20261115-155754-8422a4a) and S1 (A-emd-pbh-20261115-160349-9d232d2) ran
and are closed (`scripts/card_run.py finish`); analysis A-emd-pbh-20261115-171930-878a114.
Results: DESIGN.md section 7, JOURNAL.md. Their "no horizon" is not evidence: the decks had
`hmean_tol_0 = 100`, which stops every search in a cosmological box at once (core-v0.5).

## Wave 3 results (DESIGN.md section 7.1; JOURNAL.md from "Wave 3")

| Item | Run | Result |
|---|---|---|
| P0L data (mu = 0.3, e = p = 0) | A-20261120-223123-f436c39 | solve converged (residual 9e-12, c = 0.088); 317 tracked particles |
| R1 exact reference | A-20261121-130103-e007f42 (first pass A-20261121-125808-7366ccd) | paper profile: central crunch 8.82 t_H, apparent horizon born there and growing outward, no shell crossing; the code's own slice: the same structure 1.5 times faster (central crunch 5.87 t_H; turnaround, trapping, crunch 16-17 per cent earlier at equal mass), central shells 13 per cent young; images negligible |
| K smoke test | A-20261121-130655-0e84f0d | both decks run on the release core-v0.5 processor build; S1L repeats S1 at t = 0; first step 0.34 dx (light-speed limit) |
| reader check | A-20261121-131819-ed01cef | code areal radius of the tracked particles equals reference B at t = 0 to 2.4e-5 |
| card job 1 (P0L, S1L) | A-20261121-131600-02b5d41, Slurm 4799 | see JOURNAL.md (pending at the time this table was written) |

## Requests

### Wave 3 (2026-11-21)

To the lead, a draft message to B-emd-gw (the lead sends it; B accepted the spherical
periodic test as the gauge leg of its G2, outbox 20261115T191110Z):

> From A-emd-pbh to B-emd-gw, info. The spherical periodic test is set up at mu = 0.3, not
> 0.5: make_field does not solve mu >= 0.5 at eps_i = 1 (periodic_threshold/JOURNAL.md,
> T1b). Files: deck `tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput`
> (64^3 root over [-10,10]^3, four static levels to k dx = 0.0195, relaxed 1+log lapse
> with lapse_leak = 20, Gamma-driver, guard, finder status, release core-v0.5); data
> `scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3/{fields.bin,particles_track.nrp}`
> (traj_ntrack = 317); exact reference `scratch/A-emd-pbh/A-20261121-130103-e007f42/
> ltb_reference.{json,npz}`: for every tracked shell M, E, age and the proper times of
> turnaround, R = 2M and crunch (reference B, the exact spherical future of the code's
> own t = 0 slice; reference A is the paper's profile, which the code's data do NOT
> reproduce: they collapse 1.5 times earlier). The TT part and Psi_4 of the run must
> vanish up to the box harmonics and the lattice's cubic anisotropy (axes against
> diagonals: 4.7e-3 in M at equal r0). Card run A-20261121-131600-02b5d41 (Slurm 4799)
> holds P0L; its outcome is in periodic_threshold/JOURNAL.md.

To core:
- W1 (confirmation) `cfl_number = 1.0` with `dt_lightspeed = 0.25` is used here so that
  the step grows to dx once the expansion has slowed the coordinate light speed; the
  Courant number of light stays at 0.25, but the 1+log gauge speed sqrt(2 alpha chi)
  exceeds the light speed by sqrt(2/alpha) where the lapse has collapsed. Is this a
  combination core supports, and could the limit optionally include the gauge speeds?
- W2 (request 1, sharpened by R1) the data of make_field at eps_i = 1 carry a bang-time
  (decaying) mode: the central shells are 13 per cent younger than the background and the
  spherical peak at mu = 0.3 collapses 1.5 times earlier than the paper's mu = 0.3
  (A-20261121-130103-e007f42). A generator of the paper's slice (gradient-expansion data
  at eps_i << 1, solved on the torus) is needed before the code's threshold can be set
  against arXiv:2609.14218.
- W3 (minor) `<mesh_refinement> max_nmb_per_rank` prints "not used by the code" on a
  static mesh while the READY of core-v0.5 says the particle restart file is sized by it:
  which holds for static meshes?

### Wave 2

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

To orch (wave 2, served since by `nrpic-run --package`): `harness/bin/nrpic-run` refused
the shared worktree while other helpers held untracked files; the wave-2 runs of this
package were therefore registered by hand with `scripts/register_run.py` or
`scripts/card_run.py`.
