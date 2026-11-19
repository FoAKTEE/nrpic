# flux_tools: horizon mass growth against the particle flux through the horizon (Track D, G2)

Helper package of owner D-bh-dress, wave 3a (2026-11-19). Gate G2 of the track sheet:
"with matter filled in, the mass growth agrees with the integrated particle flux through
the horizon". This directory holds the readers of core's accretion diagnostics and of the
horizon finder, the comparison with its error budget, its tests on core's own output and
on a processor run of test particles into a fixed hole, an application to the wave-2 card
runs ES-1/V-1, and the prepared input and predicted growth law of the first matter run
after the vacuum-bubble benchmark (ES-F: the bubble of ES-1 filled with dust).
Predictions and outcomes: `JOURNAL.md` (entries 1-5). Card-hours used: 0. No result here has been checked by a second agent yet.
Labels [VERIFIED], [JUDGEMENT], [TO VERIFY] as in the charter.

## Contents

| File | What it is |
|---|---|
| `fluxio.py` | readers: `<base>.removed.bin` (20 named fields), `.nrpic.hst` / `.acc.hst` (any `[k]=name` header, last record of each time), `.horizon_summary_N.txt`, `.traj.bin` + `.trajmet.bin` (with E = alpha W - beta^i u_i computed from the metric), snapshots, particle files (read and write). Each checks magic and record length |
| `exact_ks.py` | exact test-particle references in Kerr-Schild Schwarzschild: E, L, capture, Kerr-Schild time of any inward passage, sphere crossings of bound orbits (one-dimensional quadratures; turning points through r = r_t -+ w^2 with the factored E^2 - V) |
| `compare.py` | the comparison (library and command line): dM_AH(t) of the finder against F_rem(t) (sum of m E over particles removed inside the horizon, a lower bound) and F_sph(t) (net inward m E through a sphere outside the horizon, an upper bound for monotone infall); budget sigma = (floor^2 + mass_tol^2)^(1/2), floor = envelope of a vacuum control or a constant; `--energy_by_tag` replaces the code's E by the energy fixed per particle by the initial data |
| `t_core.py` | entry 1: readers and comparison on core's T3 and T7 output |
| `p1.py`, `inputs/p1_fixed_bh.athinput` | entry 2: 3000 test particles into a fixed hole (static mesh metric and analytic metric), exact references, analysis |
| `es_apply.py` | entry 3: ES-1/V-1 through the tools; the code's particle energy against the Killing energy of the bubble tracers |
| `esf_data.py`, `esf_check.py` | entry 4: ES-F data (table, particles, per-tag energies and labels, exact growth law) and its checks (offline constraints against drbar; growth law against the wave-2 shells) |
| `inputs/esf_dx8.athinput`, `inputs/v0_dx8.athinput` | the ES-F run and its vacuum control V-0 (ES-1 mesh, gauge, finder; accretion diagnostics on) |
| `esf_analyse.py` | the analysis of the ES-F run, written before it (bracket with initial-data energies and the sphere content at t0, per-label bound against the lattice sum at the next finder sample, growth law) |
| `t_esf_synth.py` | entry 5: esf_analyse.py on synthetic ES-F runs built from the exact LTB solution (lattice truth, continuum truth, growth x 0.97) |
| `figs/`, `results/` | copies of the figures (each looked at) and JSON of the registered runs |

## Results (run ids; numbers in `JOURNAL.md`)

- Core's T3/T7 output (D-20261119-143610-818e89f): every count, the content identity
  (to 9e-17), the energies (1.15e-5 mesh, 3.5e-6 analytic), the removal step and the
  sphere crossings reproduce my own exact references; the restart case is identical byte
  for byte; the comparison passes a synthetic exact horizon and rejects a 5 per cent
  deficit (828 sigma). [VERIFIED]
- P1, fixed hole (D-20261119-144040-3acb22f, analyses -144246-238a592, -144600-15dcc67):
  2935 captures and 65 bound orbits exactly as predicted; sphere counts exact; sum m E
  through r = 2M to 2.7e-6; the bracket holds at all 1601 times (max 0.011 sigma),
  closure 1.0e-5; a 3 per cent deficit (802 sigma) and a 2 M late horizon (1242 sigma)
  are rejected. Failed predictions: energy errors up to 1.8e-4 for orbits whirling near
  the unstable circular orbit (pusher, dt = 0.05 M), removal up to 0.45 steps early for
  them on the mesh metric, 18 of 8001 horizon-sphere records one particle off. The bracket
  F_sph - F_rem is up to 0.017 M wide during the main infall: the sharp test is the
  closure over windows longer than the lag (0.8-1.5 M here). [VERIFIED]
- ES-1/V-1 (D-20261119-144248-0143469): the code's E of the bubble tracers is 1.03-1.06
  E_K at t = 0, 1.35-2.49 E_K at excision, and tracks the lapse of the bubble region late
  in the run. In this gauge E = alpha W - beta^i u_i is not the Killing energy: the G2
  flux must use the initial-data energy per tag (or a stationary, normalised gauge).
  Null comparison of ES-1 against V-1 (t0 = 100 M): inside 3 sigma at all 200 finder
  times (max 2.6 sigma), not blind (entry 3). [VERIFIED]
- Synthetic ES-F runs (entry 5; final D-20261119-150306-d0e692e after three failed
  predictions, D-20261119-145851-944d6fd, -150029-06e4f7f, -150219-c40d908): the analysis
  passes an exact lattice history with finder-like noise (3.06 sigma max, per label
  -2.7e-5) and rejects a 3 per cent deficit (773 sigma) and the code energies (9017
  sigma). It needs the sphere content at t0 in the upper bound, the lattice sums of m E_K
  (they differ from the continuum m(R0) by up to 3.9e-3 M) and the first finder sample
  after a removal. [VERIFIED on synthetic data only]
- ES-F data (D-20261119-145022-2208a19, checks -145026-2f11618): table residuals of
  fourth order (5e-7 of 16 pi rho0 at drbar = 0.02); lattice rest mass to 4e-7; exact
  growth law below. [VERIFIED]

## ES-F: the first matter run after the vacuum-bubble benchmark

Construction [derivation here; JUDGEMENT until a second agent checks it]. Spherical
dust at rest in the slice (u_i = 0, S_i = 0), K^i_j = diag(KL, KT, KT), areal radius R,
Misner-Sharp mass m(R) = M + D(R), D' = 4 pi R^2 rho. The momentum constraint gives
KL = d(R KT)/dR for any KT; the slicing KT = -f (2m/R^3)^(1/2) gives (dR/dl)^2 = 1 - 2m(1 -
f^2)/R and each shell the LTB energy E = (f^2 - 1) m/R. Choosing f^2 = 1 - M/m(R) gives
E = -M/R0 for every shell (the Newtonian energy of the unperturbed Hubble flow around a
seed, v = H R in the plateau) and (dR/dl)^2 = 1 - 2M/R everywhere: the spatial metric is
Schwarzschild of mass M, psi = 1 + M/(2 rbar) exactly, so the format-2 table has u = 0
and the puncture carries m_p = M = 1. Then KT = -(2D/R^3)^(1/2) and the Hamiltonian
constraint 4 KL KT + 2 KT^2 = 4 D'/R^2 = 16 pi rho holds identically (R_3 = 0). The
parameters are ES-1's: rho0 = 3.71818e-6 (H = 5.58116e-3/M, eps = H M, t_i = 119.45 M),
outer edge smooth over 52-60 M, plus the bubble filled from a smooth inner edge over
3-5 M (vacuum core around the horizon, RUNS.md section 4 of `secondary_infall`).
M_tot = 3.73866 M. Particles: 140 tracers at the ES-1 radii (tags 0-139), then 850584
dust particles on the 1 M lattice with rest mass rho psi^6 h^3.

Predicted growth law [VERIFIED as mathematics in esf_check; physics of the run TO
VERIFY]: without shell crossing before the horizon (tau_H(R0) is monotonic), the apparent
horizon mass equals m(R0) of the shell at the trapping horizon R = 2 m(R0), which that
shell reaches at its proper time tau_H(R0) (cycloid with m(R0), E = -M/R0, starting on
the expanding branch). Each particle carries the conserved energy (1 - 2M/R0)^(1/2) per
unit rest mass, and sum m (1 - 2M/R0)^(1/2) over a shell is its dm.

| tau [M] | 25 | 50 | 100 | 150 | 200 | 250 | 300 | 400 | 600 |
|---|---|---|---|---|---|---|---|---|---|
| M_AH exact (LTB) | 1.0062 | 1.0218 | 1.0655 | 1.1168 | 1.1711 | 1.2263 | 1.2815 | 1.3904 | 1.5990 |
| wave-2 shells (capture at 2M) | 1.0061 | 1.0215 | 1.0650 | 1.1160 | 1.1703 | 1.2250 | 1.2798 | 1.3884 | 1.5965 |

Tracer groups reach the horizon at tau_H = 15.9, 39.6, 156.3, 354.2 M (R0 = 6, 10, 20,
28 M). In ES-1 the dust proper time ran ahead of the coordinate time (lapse above 1 in
the bubble, entry 3), so 200 M of coordinate time should cover tau ~ 250-300 M near the
hole [JUDGEMENT], i.e. growth to about 1.2-1.3 M, four orders of magnitude above the
floor of the null test (V-1 envelope 1.4e-4 at 200 M).

Run (not submitted: this package has no card-hours): `inputs/esf_dx8.athinput` with an
executable that has the accretion diagnostics (`scratch/core/exe/core_requests-adf/athena_gpu`
or the release that merges them), and its control `inputs/v0_dx8.athinput` (the ES-F
slice without dust is the time-symmetric Schwarzschild puncture; V-1 is the alternative
control with ES-1's f-slice). Cost [JUDGEMENT from ES-1, 0.769 card-hours for 200 M with
6.97e5 particles, and V-1, 0.672]: ES-F 0.8-1.0 card-hours (may need a second chain
segment), V-0 about 0.7. Processor smoke runs of both inputs: entry 4 item 4.

    cd /data/haiyangw/nrpic/wt/D-bh-dress
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher chain --gpu-hours 1.97 \
      --package tracks/D-bh-dress/flux_tools --exe /data/haiyangw/nrpic/scratch/core/exe/core_requests-adf/athena_gpu \
      --purpose "ES-F: first matter run" -- tracks/D-bh-dress/flux_tools/inputs/esf_dx8.athinput
    # the same with v0_dx8.athinput and --gpu-hours 0.98; then, partial runs allowed:
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/flux_tools --cores 2 \
      --purpose "ES-F analysis" -- python3 tracks/D-bh-dress/flux_tools/esf_analyse.py \
      --run /data/haiyangw/nrpic/scratch/D-bh-dress/<ES-F run id> \
      --data /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261119-145022-2208a19 \
      --control /data/haiyangw/nrpic/scratch/D-bh-dress/<V-0 run id>/v0.horizon_summary_0.txt

Pass criteria proposed for G2 (to be pre-registered by the lead): (i) the bracket
F_rem(t) - 3 sigma <= dM_AH(t) <= F_sph(t) + 3 sigma at every finder time, F computed
with the initial-data energies and the energy inside the sphere at t0 in F_sph; (ii) at
every removal, M_AH at the next finder sample >= m_disc(R0) - 3 sigma (lattice sum of
m E_K up to the label) and tau_H(R0) <= tau_rem <= tau_0(R0); (iii) M_AH against the
proper time of the shells at the horizon within 1 per cent of the exact LTB curve for
tau <= 250 M (the lattice differs from the continuum by at most 3.9e-3 M). Refuted (the
growth does not follow the flux) if (i) fails by more than 3 sigma over windows longer
than the removal lag.

## How to rerun

From the worktree root, with the package committed (`--package` lets other helpers'
changes in `tracks/D-bh-dress/` be recorded instead of refused):

    P="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/flux_tools"
    S=/data/haiyangw/nrpic/scratch
    $P --cores 1 --purpose "core output" -- python3 tracks/D-bh-dress/flux_tools/t_core.py \
       --t3 $S/core/core-20261115-160245-727e96a --t7 $S/core/core-20261115-163129-a200caf
    $P --cores 1 --purpose "P1 run" -- python3 tracks/D-bh-dress/flux_tools/p1.py run \
       --exe $S/core/exe/core_requests-adf/athena_cpu
    $P --cores 1 --purpose "P1 analysis" -- python3 tracks/D-bh-dress/flux_tools/p1.py analyse --run $S/D-bh-dress/<P1 run id>
    $P --cores 2 --purpose "ES-1/V-1" -- python3 tracks/D-bh-dress/flux_tools/es_apply.py \
       --es $S/D-bh-dress/D-20261115-172726-60ba4c2 --v1 $S/D-bh-dress/D-20261115-172730-c6d151b \
       --data $S/D-bh-dress/D-20261115-170213-d2c2131 --t0 100 --floor 2.8e-5
    $P --cores 4 --purpose "ES-F data" -- python3 tracks/D-bh-dress/flux_tools/esf_data.py --hp 1.0
    $P --cores 2 --purpose "ES-F checks" -- python3 tracks/D-bh-dress/flux_tools/esf_check.py

Wall times: T3/T7 test 1 min; P1 run 95 s on one core (mesh 86 s, analytic 9 s), its
analysis 10 s; ES-1/V-1 30 s; ES-F data 15 s; checks 15 s. Python of the worktree's
`.venv` (numpy 2.2, scipy 1.15, matplotlib 3.10). The comparison alone:
`python3 compare.py --horizon <summary> --removed <removed.bin> --acc <acc.hst>
[--control <summary>] [--energy_by_tag <npy>] --t0 T --out DIR`.

## Requests

To core:
1. Particle energy in an evolving gauge (entry 3, run D-20261119-144248-0143469): the E
   of the removal record and of the flux spheres is -u_t of the code's time vector, which
   in the moving-puncture gauge of ES-1/V-1 is 1.3-2.5 times the Killing energy of the
   same particle. Please state this in `REQUESTS_ADF.md` section 2.3 (it says "use spheres
   where the gauge has settled"; settling is not enough, the normalisation of the lapse at
   large radius enters) and, optionally, add a crossing record (time, tag, sphere,
   direction, the 20 fields of the removal record) so that crossings can be weighted per
   particle with the initial-data energy, as removals already can through the tag.
2. A release that contains the accretion diagnostics of `core/requests-adf` with a card
   executable; the ES-F input needs `removal_record` and `acc_*`.
3. The finder still writes `<base>.horizon_summary_0.txt` into the working directory,
   not into `-d` (the smoke runs here `cd` into the run directory).

To the lead of D-bh-dress:
4. Card time for ES-F (0.8-1.0 card-hours) and V-0 (about 0.7), or ES-F with V-1 as the
   control; the inputs are ready and smoke-tested on processors (entry 4).
5. Pre-register the G2 criteria above (or others) in `stage/` before ES-F runs.
6. For the es_finish helper: any use of the code's particle E in `es_runs/analyse.py`
   inherits the gauge factor of entry 3 (the LTB curves there use exact energies; I have
   not checked every use).
