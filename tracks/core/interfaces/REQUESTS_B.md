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
| 4 | thin-periodic-boxes | ACCEPTED, in work | yes, down to 4 cells (see section 4); initial data for non-cubic boxes: `problems/cosmo/make_waves.py` |
| 5 | lattice-jitter-option | ACCEPTED, in work | `make_waves.py --jitter A --jitter-axes y,z --seed N` (new tool; `cosmo/ic/` is outside core's ownership) |
| 6 | initial-data-tt-part | DEFERRED | not on the G1 path; design in section 6; subtract the decaying part in analysis meanwhile |
| 7 | newtonian-mode-for-track-b, item 1 | DONE in core-v0.3 | `<particles> pusher = newton` is on main (609a875) |
| 7 | newtonian-mode-for-track-b, items 2-3 | DEFERRED | item 2 yes (next core package); item 3 after the periodic pancake test |
| 8 | awa-generators | DECLINED for this release | optional by the track's own words; the route through `nrpic_cosmo` works; a dedicated executable on request |

## 1. Linear-wave generator (`athenak/src/pgen/tests/z4c_linear_wave.cpp`)

- The polarization tensor of the upstream file has the wrong sign of `axy` and `ayz`
  (docs/UPSTREAM_DEFECTS.md, item 1; independent derivation in the journal). The upstream
  tensor is transverse for wave vectors with k2 = 0 and along the axes, and for no other.
  Both signs are flipped: e+ = theta theta - phi phi for every k.
- New options, read only if present in `<problem>`: `amp_cross` (amplitude of
  ex = theta phi + phi theta) and `phase_cross` (radians). `amp_cross = amp`,
  `phase_cross = pi/2` is a circular wave of helicity +2 in gw_diag's convention,
  `-pi/2` of helicity -2.
- `<basename>-errs.dat` now holds the L1 errors against the exact linear solution at the
  final time (before: against the initial data, right only after whole periods).
- A general oblique direction (k1 h, k2 h, k3 h not all equal) is transverse in the
  continuum only: the discrete divergence of the data differs from zero by the truncation
  error of the first derivative, so the constraints of the initial data fall as h^6
  instead of vanishing. Along (1,1,1) and along the axes they vanish to second order in
  the amplitude at every resolution.
- Example: `problems/tests/lw_oblique.athinput`. Test: `tracks/core/analysis/bfix/
  t1_linear_wave.py` (it runs Track B's own cases `lw3d_check`, `lw_x_prod`,
  `lw3d_dump_N32` and its `validate_athenak.py` on the new executable).
- For Track B: `periodic_z4c/analysis/refsol.tt_polarization` copies the upstream signs
  on purpose; flip `xy` and `yz` there to obtain the reference of the corrected generator.

## 2. Output for the gravitational-wave analysis

- `<outputN> file_type = bin`, `double_precision = true`: the values are written as they
  are stored (8 bytes); the header line reads `size of variable=8`. Everything else of
  the format is unchanged (docs/FORMATS.md, "Mesh binary output in double precision").
  No ghost cells unless `ghost_zones = true`. Works for every variable or group:
  `z4c` (22 fields: chi, gt_ij, Khat, At_ij, Gamma^i, Theta, alpha, beta^i), `adm`
  (gamma_ij, K_ij, psi4, alpha, beta^i), `tmunu`, `con`, `weyl`. Without the parameter the
  files are byte-identical to before.
- Reader: `python/nrpic/athena_bin.py` (`read_bin`, both precisions). Track B's
  `gwdiag.readers.read_bin` and `periodic_z4c/analysis/athena_dumps.read_bin` assume
  4 bytes; upstream's `athenak/vis/python/bin_convert.py` accepts both.
- Times: a mesh output is written after the step in which the time passes
  `last_time + dt`; the file holds the state of the time printed in its header (the
  Z4c state, the ADM variables and, with depositing particles, the sources of that time
  level). The time step is not shortened to hit the output time: with `dt_expansion`
  the outputs fall on step boundaries after the requested times.
- Volume: 22 x 8 bytes per cell (46 MB at 64^3, 369 MB at 128^3) for `z4c`; 17 x 8 for
  `adm`.
- In-situ Fourier modes (item 2): deferred. Reason: a new reduction on the device for
  about 365 modes times 12 fields with its own file format and test, while the dumps
  already give the analysis everything; to be decided on Track B's measured volumes.
- Restart files: identical runs now give identical restart files (section "padding" of
  the journal); files written before the fix restart as before.

## 3. Weyl output timing

Confirmed by the source (journal, "Source reading", item 2): the Weyl scalar is computed
after the update, from the state of t + dt, in the step that starts at a waveform time,
and both the mesh array and the rows of `waveforms/*.txt` are labelled with the time at
the start of that step. So the extracted waveforms carry the one-step offset (the row
labelled t is Psi_4 of t + dt), and a `weyl` mesh output written at t_n holds the scalar
of t_(n-1) + dt when the two cadences are equal. `<z4c> waveform_at_new_time = true`
chooses and labels by the time at the end of the step: the row labelled t is Psi_4 of t,
and a `weyl` mesh output at a waveform time holds the scalar of its own time. Default
false: existing waveform runs keep their bytes. Tracks A, D, F: turn it on for new runs,
or shift the time axis of existing waveforms by +dt.

## 4. Thin periodic boxes

See the journal entry P3 for the measured statement. Nothing in `nrpic_cosmo`, the
deposit (clouds, filter, compensation), the gather or the Z4c exchange is tied to a
cubic mesh; `mesh.cpp` asks for at least 4 cells per direction. Initial data: the
generator reads an n1 x n2 x n3 field file; `cosmo/ic/` writes cubic ones only, so
`problems/cosmo/make_waves.py` (solver `python/nrpic/torus_id.py`) builds the wave data
of East et al. on any box with cubic cells.

## 5. Lattice jitter

`problems/cosmo/make_waves.py --jitter A --jitter-axes y,z --seed N`: every particle is
displaced by a uniform random amount in (-A, A) cells along the named axes, before the
constraint solve; the deviates come from the counter-based generator of the code
(`python/nrpic/rng.py`) keyed by seed, lattice index and axis, so they do not depend on
the order of the particles or on the box; recorded in `id.json`. `cosmo/ic/make_east.py`
is left as it is (outside core's ownership); the orchestrator decides whether it gets the
option too.

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

Listed in `tracks/core/JOURNAL-bfix.md`, section "Files and lines".
