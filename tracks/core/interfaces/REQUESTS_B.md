# Requests of Track B to core: triage and answers (work package bfix)

Branch `core/requests-b`. Requests read at `track/B-emd-gw` 767eb93:
`tracks/B-emd-gw/outbox/20261115T1340Z__to-core__*.md` (eight messages) and the lead's
review `tracks/B-emd-gw/stage/G0/REVIEW.md`. Order of work: what closes Track B's G1
(`tracks/B-emd-gw/stage/G1/STATUS.md`, "What closes G1") first. Evidence for every answer:
`tracks/core/JOURNAL-bfix.md` (predictions and outcomes), run ids there.

| # | Message | Ruling | Answer in one line |
|---|---|---|---|
| 1 | z4c-linear-wave-polarization | ACCEPTED, done | the two signs are flipped; cross and circular waves added; the error routine uses the exact solution at the final time |
| 2 | gw-analysis-output, item 1 | ACCEPTED, done | `<outputN> file_type = bin` with `double_precision = true`: any variable group, no ghost cells |
| 2 | gw-analysis-output, item 3 | ACCEPTED, done | the same option with `variable = tmunu` (E, S_i, S_ij as the spacetime solver receives them) |
| 2 | gw-analysis-output, restart padding | ACCEPTED, done | the 36 bytes are the never-set coarse indices of `Mesh::mesh_indcs`; now zero |
| 2 | gw-analysis-output, item 2 (Fourier modes in situ) | DEFERRED | after the track has measured the volume of the double-precision dumps |
| 3 | weyl-output-timing | ACCEPTED, done | confirmed at the source; opt-in fix `<z4c> waveform_at_new_time = true`; the default keeps upstream's labels |
| 4 | thin-periodic-boxes | ACCEPTED, done | yes, down to 4 cells (see section 4); initial data for non-cubic boxes: `problems/cosmo/make_waves.py` |
| 5 | lattice-jitter-option | ACCEPTED, done | `make_waves.py --jitter A --jitter-axes y,z --seed N` (new tool; `cosmo/ic/` is outside core's ownership) |
| 6 | initial-data-tt-part | DEFERRED | not on the G1 path; design in section 6; subtract the decaying part in analysis meanwhile |
| 7 | newtonian-mode-for-track-b, item 1 | DONE in core-v0.3 | `<particles> pusher = newton` is on main (609a875) |
| 7 | newtonian-mode-for-track-b, items 2-3 | DEFERRED | item 2 yes (next core package); item 3 after the periodic pancake test |
| 8 | awa-generators | DECLINED for this release | optional by the track's own words; the route through `nrpic_cosmo` works; a dedicated executable on request |

## 1. Linear-wave generator (`athenak/src/pgen/tests/z4c_linear_wave.cpp`)

- The polarization tensor of the upstream file has the wrong sign of `axy` and `ayz`
  (docs/UPSTREAM_DEFECTS.md, item 1; independent derivation in the journal). The upstream
  tensor is transverse for wave vectors with k2 = 0 and along the axes, and for no other
  (so slightly more than "only along an axis"); for k = (1,1,1) the norm of e.khat is
  0.943 and its largest component 0.770. Both signs are flipped: e+ = theta theta -
  phi phi for every k.
- New options, read only if present in `<problem>`: `amp_cross` (amplitude of
  ex = theta phi + phi theta) and `phase_cross` (radians). `amp_cross = amp`,
  `phase_cross = pi/2` is a circular wave of helicity +2 in gw_diag's convention,
  `-pi/2` of helicity -2. The plus and cross tensors are those of gw_diag's `pol_basis`
  (by derivation for every direction off the x3 axis; measured for k = (1,1,1)).
- `<basename>-errs.dat` now holds the L1 errors against the exact linear solution at the
  final time (before: against the initial data, right only after whole periods).
- A general oblique direction (k1 h, k2 h, k3 h not all equal) is transverse in the
  continuum only: the discrete divergence of the data differs from zero by the truncation
  error of the first derivative, so the constraints of the initial data fall as h^6
  (measured for k = (1,2,0): factors 3377 and 3391 in the squared integrals from 16 to 32
  cells) until they reach the second-order floor. Along (1,1,1) and along the axes they
  are at that floor at every resolution.
- Measured (T1, run core-20261115-154120-9c92f68; T1s core-20261115-160040-26eb826):
  Track B's case lw3d_check_diag gives 1.3852e-9 and 1.5576e-9 with the upstream signs
  (the track's numbers) and 4.59e-21 and 1.07e-21 corrected, scaling as A^4 (second
  order: the wave's own energy; a circular wave of the same amplitudes has 1.40e-20,
  above the track's 1e-20 because it carries twice the energy). Oblique evolution over
  one period: amplitude and phase errors equal the Fourier-symbol prediction to 0.2 per
  cent at 16 and 32 cells; gw_diag's h_x is below 1e-9 A and its Psi_4 agrees with the
  analytic value to 9.2e-5 and 3.2e-6. Track B's `lw_x_prod` table and every number of
  `validate_athenak.py` are reproduced with the new executable.
- Example: `problems/tests/lw_oblique.athinput`. Test: `tracks/core/analysis/bfix/
  t1_linear_wave.py`.
- For Track B: `periodic_z4c/analysis/refsol.tt_polarization` copies the upstream signs
  on purpose; flip `xy` and `yz` there to obtain the reference of the corrected generator
  (python twin: `tracks/core/analysis/bfix/bfix_common.pol_tensors`).
- On a card (T4, run core-20261115-170758-f5f58f4): N = 16 and 32 give the processor's
  errors to three digits; N = 64 amplitude -7.76e-9 and phase -1.758e-7 rad against the
  symbol's -7.88e-9 and -1.750e-7; at N = 128 the phase is -1.36e-8 (symbol -1.07e-8)
  and the amplitude error sits at the rounding floor. gw_diag's Psi_4 against the
  analytic value: 9.2e-5, 3.2e-6, 3.3e-7, 8.1e-7 at N = 16 to 128. After one period the
  metric has a non-TT part of 3.4e-6 A at every N, which sets the floor of the pointwise
  error from 64 cells on (the Fourier coefficient keeps converging).
- Amplitude scan on processors at N = 32 (T9, run core-20261115-181830-ddc8128): the
  non-TT part is of second order in A (3.38e-6 A at A = 1e-6, 3.38e-5 A at 1e-5; the
  k = 0 drift and 2k content your verifier found for the axis wave, removed by the TT
  projection), and max |alpha - 1| = 1.69 A^2. The Psi_4 floor is rounding: Psi_4 along
  -k grows as 1/A below A = 1e-7 (2.65e-5 of the maximum at A = 1e-9), about
  5e-14 N^2 / A relative. The TT amplitude and phase do not change from A = 1e-6 to 1e-5
  (2e-5 and 4e-4 of their errors).
- Amplitude scan at N = 64 and 128 on a card (T8, runs core-20261115-181437-8d252cb and
  analysis core-20261119-140545-b16cd96; A = 1e-7, 1e-6, 1e-5): the non-TT part grows by
  9.99 (N = 64) and 9.98 (N = 128) from A = 1e-6 to 1e-5, so it is of second order at
  every N; below A = 1e-6 an absolute floor that grows with N (1.1e-14 at 64, 3.5e-14 at
  128 cells) lifts it. At 128 cells the Psi_4 error is 8.1e-6, 8.1e-7, 8.2e-8 for
  A = 1e-7, 1e-6, 1e-5: proportional to 1/A, so rounding at all three amplitudes. At
  A = 1e-5 the amplitude and phase depart from the Fourier symbol by -2.2e-10 and -1.7e-9
  rad (109 and 16 per cent of the scheme's errors at 128 cells); the phase offset, about
  -1e-9 rad at N = 32 and 64 too, is of the size of a second-order frequency shift
  [JUDGEMENT]. At A = 1e-5 gw_diag's Psi_4 error converges at order 4.07 from 32 to 64
  cells (3.19e-6 to 1.90e-7). Advice, replacing the one given before: one period of the
  linear wave shows the scheme's convergence up to 64 cells, best at A = 1e-5; at 128
  cells no amplitude from 1e-7 to 1e-5 gets below the floors (rounding at small A, second
  order at large A). Journal: P10b and "Outcome of T8".
- Byte regression on the card (T8, P10a): the Z4c puncture benchmark with `z4c` and `con`
  dumps and the history gives the same 10 files (973 MB) byte for byte with the release
  card executable and the one of this branch. The circular wave on the card equals the
  processor run of T1 to 2.9e-6 in its error file and to rounding of the order-one fields
  pointwise (3.7e-15 in gt, 3.5e-14 in At after 37 steps).
- Kept as upstream has it: the generator fills the Z4c variables only, so `adm` and `con`
  outputs and the history row at t = 0 hold zeros; use `variable = z4c` at t = 0.

## 2. Output for the gravitational-wave analysis

- `<outputN> file_type = bin`, `double_precision = true`: the values are written as they
  are stored (8 bytes); the header line reads `size of variable=8`. Everything else of
  the format is unchanged (docs/FORMATS.md, "Mesh binary output in double precision").
  No ghost cells unless `ghost_zones = true`. Works for every variable or group:
  `z4c` (22 fields: chi, gt_ij, Khat, At_ij, Gamma^i, Theta, alpha, beta^i), `adm`
  (gamma_ij, K_ij, psi4, alpha, beta^i), `tmunu`, `con`, `weyl`. Without the parameter the
  files are byte-identical to before (regression: seven set-ups, journal P2b).
- Measured (T2, run core-20261115-160138-26eb826): the 22 fields equal the active cells
  of the restart file of the same time bit for bit; the default output is the same
  numbers rounded to float32.
- Sources (item 3): `variable = tmunu` with the option gives E, S_i, S_ij of the last
  deposit: E itself, not multiplied by the volume element, also with
  `source_density = true`; the `z4c`, `tmunu` and `con` outputs of one output time
  belong to one time level (the constraint recomputed from the dumps equals `con_H` to
  1e-9 of the source term; T3, run core-20261115-160633-7d80187). After shell crossing E
  can be slightly negative next to a caustic unless `deposit_comp_limit` is set.
- Reader: `python/nrpic/athena_bin.py` (`read_bin`, both precisions). Track B's
  `gwdiag.readers.read_bin` and `periodic_z4c/analysis/athena_dumps.read_bin` assume
  4 bytes; upstream's `athenak/vis/python/bin_convert.py` accepts both.
- Times: a mesh output is written after the step in which the time passes
  `last_time + dt`; the file holds the state of the time printed in its header. The time
  step is not shortened to hit the output time: with `dt_expansion` the outputs fall on
  step boundaries after the requested times (0.505, ..., 3.021 for dt = 0.5 in T3).
- Volume: 22 x 8 bytes per cell (46 MB at 64^3, 369 MB at 128^3) for `z4c`; 17 x 8 for
  `adm`; 10 x 8 for `tmunu`.
- In-situ Fourier modes (item 2): deferred. Reason: a new reduction on the device for
  about 365 modes times 12 fields with its own file format and test, while the dumps
  already give the analysis everything; to be decided on Track B's measured volumes.
- Restart files: identical runs now give identical restart files; they differ from the
  old ones in the 36 padding bytes only, and old files restart as before (T2).

## 3. Weyl output timing

Confirmed by the source (journal, "Source reading", item 2) and by measurement: the Weyl
scalar is computed after the update, from the state of t + dt, in the step that starts at
a waveform time, and both the mesh array and the rows of `waveforms/*.txt` are labelled
with the time at the start of that step. So the extracted waveforms carry the one-step
offset (the row labelled t is Psi_4 of t + dt), and a `weyl` mesh output written at t_n
holds the scalar of t_(n-1) + dt when the two cadences are equal.
`<z4c> waveform_at_new_time = true` chooses and labels by the time at the end of the
step: the row labelled t is Psi_4 of t, and a `weyl` mesh output at a waveform time holds
the scalar of its own time. Measured with Track B's own fit (`validate_athenak.py`):
-7 steps by default, 0 steps with the option; the waveform series of the default leads
by omega dt = 0.049087 rad (T1, T2). Default false: existing waveform runs keep their
bytes. With the option there is no row at t = 0. Tracks A, D, F: turn it on for new
runs, or shift the time axis of existing waveforms by +dt.

## 4. Thin periodic boxes

Yes. Measured (T3, run core-20261115-160633-7d80187): crossed waves (1, 0.5, 0),
delta = 0.1, production configuration (cubic cloud with compensation, cubic-spline
gather, `dt_expansion = 0.01`), eight particles per cell, from a = 1 through the first
shell crossing to a = 13.9: boxes of 16 x 16 x 8 and 16 x 16 x 4 cells with one
MeshBlock in z give the fields of the 16^3 cube to 3e-10 of their maxima at every dump
(1e-12 at the end; the cube's own dependence on z is of the same size) and the particles
to 7e-14 cells; a box thin in x agrees with the thin-z one after exchanging the axes to
1e-12. Four cells is the minimum that `mesh.cpp` accepts. Cost is proportional to the
number of layers. The same on a card (T4): 3.3e-10 at most, 1.3e-12 at the end.

Track B's box on a card (T4): 256 x 256 x 16 cells, one particle per cell and direction
(1 048 576), waves (1, 0.3, 0), delta = 0.01, four MeshBlocks of 128 x 128 x 16, to t = 1
(a = 2.25, 256 cycles): every particle kept, 59 s, 4.7e6 zone-cycles per second, a
double-precision `z4c` dump of 185 MB. The layers are not identical: they differ by noise
at the mesh scale, 1.2e-13 to 1.8e-13 absolute in the components of At, 1.5e-14 in gt,
2.5e-12 in Gamma^i, of the same size in the components that vanish in the exact problem
(Axz, Ayz, gxz, Gamma^z) (T4b, run core-20261115-180817-4a0566d). The size matches the
rounding of order-one fields through the code's second differences [JUDGEMENT]. Use it
as the floor of the TT content of a thin-box run.

It does not grow (card test T8, run core-20261115-181437-8d252cb, analysis
core-20261119-140545-b16cd96): the same box continued to t = 4 (a = 9.0, 1024 cycles,
240 s on one A100, 4.5e6 zone-cycles per second, every particle kept) has at t = 4 a z
departure of 5.1e-14 in At (1.96e-13 at t = 1), 2.2e-14 in gt (1.6e-14), 2.9e-12 to
3.3e-12 in Gamma^i (2.2e-12 to 2.8e-12); At, Khat and Theta decay, gt and Gamma^i stay
level (mean factor per 0.25 in time over the last eight dumps 0.91 for At, 1.02 for gt,
1.01 for Gamma^i), and the lapse, which grows with a from 2.25 to 9.0, carries 8e-14.
Relative to the x-y variation at t = 4: At 2.3e-9, gt 1.6e-11, Gamma 8.9e-10. So the
level measured at t = 1 bounds the noise of the whole run to a = 9; in the thin boxes of
T3 it decays through the first shell crossing (T10, run core-20261115-182405-22bafeb).

Initial data: the generator reads an n1 x n2 x n3 field file; `cosmo/ic/` writes cubic
ones only and is outside core's ownership, so `problems/cosmo/make_waves.py` (solver
`python/nrpic/torus_id.py`) builds the wave data of East et al. on any box of cubic
cells, `--n 256,256,16`; for a cube it reproduces `cosmo/ic/make_east.py` to rounding,
and thin data equal the layers of the cube's. Put `box` of its `id.json` into
`<mesh> x1max, x2max, x3max`, and the probe positions inside the box.

## 5. Lattice jitter

`problems/cosmo/make_waves.py --jitter A --jitter-axes y,z --seed N`: every particle is
displaced by a uniform random amount in (-A, A) cells along the named axes, before the
constraint solve; the deviates come from the counter-based generator of the code
(`python/nrpic/rng.py`, stream initial data, sub-stream 16) keyed by seed, lattice site
and axis, so they do not depend on the order of the particles or on the box; recorded in
`id.json`. `cosmo/ic/make_east.py` is left as it is (outside core's ownership); the
orchestrator decides whether it gets the option too.

What Track B should know before the null run (T3):
- With the spectral constraint solve (the default, as in `cosmo/ic`) the jittered data
  satisfy the constraints of the tool but not those of the code: the code evaluates them
  with sixth-order differences, which differ from spectral derivatives by order one near
  the mesh frequency, where a noisy lattice has power. For A = 0.3 cells the code's
  Hamiltonian residual at t = 0 is 8.7e-2 rms (source term 7.2) against 2.9e-5 for the
  plain lattice. `--fd-order 6` solves with the code's differences: 1.9e-6.
- That gain does not survive ten steps: at t = 0.1 the residual is 6.9e-2 whichever
  solve was used, and the two runs agree to two digits from t = 0.5. The constraint level
  of a run with a noisy lattice is set by the evolution, about one per cent of the source
  term at the start, falling with the expansion. It does not depend on the time step
  (T7, run core-20261115-162609-9dd5b98): it belongs to the spatial discretization of the
  coupled system, not to the time integration (which part of it: not identified). The
  null run will therefore measure the TT content of an evolution with constraint
  violations of that size; a smaller jitter lowers both in proportion [JUDGEMENT: not
  run].
- In a box four cells thick a quarter of all Fourier modes lie on the mesh frequency of
  that direction; prefer 16 layers for the null run.

## 6. Initial data with a TT part (deferred)

`core/id-extrinsic` (release core-v0.3) does not cover it: it is the spherical table of
`nrpic_cf` with extrinsic curvature, conformally flat. Design for a later package
[JUDGEMENT]: field file `NRCOSMO2` = `NRCOSMO1` plus six arrays of the conformal metric
minus delta; the generator sets gamma_ij = psi^4 (delta_ij + h_ij); the constraint solve
of the torus gets the Laplacian of the conformal metric as a correction iterated around
the flat Fourier solve. For a TT h of second order in the scalar perturbation the flat
solve leaves constraint residuals of third order. Until then: subtract the homogeneous
solution in the analysis; the track measured its decay as 1/a (1.8 per cent of the static
value at a = 60, run B-emd-gw-20261115-113632-2960145).

## 7. Newtonian mode

Item 1: merged and tagged (core-v0.3, on main). Item 2 (species selection and second
moments about the centroid of a species in physical coordinates): yes, in the next core
package that touches `nrpic_newton.cpp`. Item 3 (isolated patch in comoving coordinates):
decided after the periodic pancake of acceptance test (a) has run in the mode.

## 8. Apples-with-Apples generators

Not registered as built-in generators in this release: the request is optional, the
files are upstream's user problems, and the track's route through `nrpic_cosmo` works.
On request core publishes an executable built with `PROBLEM=z4c/z4c_gauge_wave`.

## Lines of shared files touched (for the merge with the other core branch)

Line numbers of the new file; `git diff 4ebb05f core/requests-b -- athenak/` shows them.
All of it went in with commit 9c92f68; the source has not changed since.

| File | Lines | What |
|---|---|---|
| `athenak/src/pgen/tests/z4c_linear_wave.cpp` | 8-20, 118-155, 172-190, 209-210 | header note; tensor (two signs), cross tensor, time of the solution; kernel; comment of the error routine |
| `athenak/src/outputs/outputs.hpp` | 151 | `OutputParameters::double_precision` |
| `athenak/src/outputs/outputs.cpp` | 277-281 | reads `double_precision` for `file_type = bin` |
| `athenak/src/outputs/binary.cpp` | 77-80, 100, 145, 222-236 | value size; header line; block size; double branch of the data loop |
| `athenak/src/mesh/mesh.hpp` | 160 | declaration of `ZeroUnusedMeshIndcs` |
| `athenak/src/mesh/mesh.cpp` | 356-375 | call at the end of the constructor; the function |
| `athenak/src/mesh/build_tree.cpp` | 363 | call after the restart header is read |
| `athenak/src/z4c/z4c.hpp` | 236-241 | `waveform_at_new_time`, `WeylStepTime()` |
| `athenak/src/z4c/z4c.cpp` | 233-238 | reads the option |
| `athenak/src/z4c/z4c_tasks.cpp` | 406-420; 429, 449, 465, 483, 501, 520, 539, 559, 577 | `WeylStepTime()`; one line in each of the nine Weyl and waveform tasks |
| `athenak/src/z4c/z4c_wave_extr.cpp` | 201-203 | time label of the waveform rows |

Merge check (2026-11-15T18:40Z, session bfix-2): of the open core branches only
`core/gauge` changes files that this branch changes (`z4c.cpp`, `z4c.hpp`);
`git merge-tree $(git merge-base core/requests-b core/gauge) core/requests-b core/gauge`
shows no conflict (the two edits are in different places).

Merge check repeated 2026-11-19T14:10Z (session bfix-3, after merging main at 71acd0c;
git 2.34, so `git merge-tree <base> core/requests-b <branch>` with the merge base) against
core/gauge 898cd03, core/clump-curvature 56d7335, core/collisions-2 0093aab,
core/scalar-2 207424d, core/requests-adf f5a5f98, core/id-solver 83172fb, core/nrpic
d377d12. Source files changed by both: `z4c.cpp`, `z4c.hpp` (core/gauge), no conflict.
`docs/FORMATS.md` is changed by core/requests-adf and core/id-solver too, no conflict.
One conflict, outside the source: `tracks/core/interfaces/rng.md`, the table of streams,
where this branch fills row 1 (sub-stream 16 of the initial-data stream: lattice jitter)
and core/collisions-2 fills row 2 (stream 2 of the collisions). Resolution: keep row 1
from this branch and row 2 from core/collisions-2 (decision 0016, item 9, moves the
registry into `coord/INTERFACES/rng.md` with core-v0.4).

New files: `problems/tests/lw_oblique.athinput`, `problems/cosmo/make_waves.py`,
`python/nrpic/athena_bin.py`, `python/nrpic/torus_id.py`, `docs/UPSTREAM_DEFECTS.md`;
additions to `docs/FORMATS.md` (three sections before "Newtonian mode") and one row of
`tracks/core/interfaces/rng.md` (sub-stream 16 of the initial-data stream).
