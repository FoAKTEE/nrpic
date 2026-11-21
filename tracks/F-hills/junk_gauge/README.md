# junk_gauge (F-hills, wave 3: round 1, closed in batch 2b)

Helper package of F-hills. It closed S2g and judged E10 (the outcome is appended to
`nr_first/JOURNAL.md`), measured the junk radiation of one member (S2g) and of the three-hole data
(P1's spheres) for G1 T3, and writes a gauge recommendation for the passages after P1.
Predictions and outcomes, the failed ones included: `JOURNAL.md` (J0-J4c). Labels [VERIFIED],
[BACKGROUND], [JUDGEMENT], [TO VERIFY] as in the journal. No card time used (cap 0).

## Results

| Item | Result | Evidence |
|---|---|---|
| S2g closed | run F-20261119-143443-f11ebb9 completed (t = 90 m, 0.524 card-hours), finished in `nrpic-run` | its manifest; `S2g/athena.20261119-082406.log` |
| E10 judged | items 1 (settling), 4 (constraints), 5 (health) met; item 2 met except the drift to t = 90 (0.197 against 0.2-3 percent: the mass settles at 1.00966 from t = 40); item 3 met in its band, failed in its equality across 30-50 m | `nr_first/JOURNAL.md` "E10, outcome"; analyses F-20261120-222403-b8dc28c, F-20261120-222415-137ada9; `figures/e10_*.png`, `results/e10_*.json` |
| Pipeline | FFI, time domain, AthenaK's -2Y_lm, sphere quadrature, momentum coupling formula; synthetic test met except two error bounds | J2; F-20261120-222655-4d3bbc2; `figures/j2_fig_test_junk_lib.png` |
| Junk of one member (S2g, P/m = 0.25, cells m/8) | one outgoing pulse at fixed retarded time (r psi4_20 peak 3.0e-3 at 30, 40, 50 m), 94 percent in (2,0) and (2,+-2); E_junk/m = 7e-5, range 4e-5 to 2e-4 (set by the separation from the hole's near-zone signal, not by noise); P_x 1.2-2.5e-5 m along the boost | J3, J3b, J3c; F-20261120-222808-b65001c, F-20261120-223018-a5c0838, F-20261120-223121-c921d2d; `figures/j3*.png` |
| Where P1 radiates (trackers) | inspiral emission tenfold its early level from t = 28.7 M (r12 = 3.4 M), reaching the nearest point of a sphere at u = 6.5 M; merger at t = 48.8 M, 19.8 M from the origin | J4g; F-20261121-075309-b6996ce; `figures/j4g_fig_p1_geometry.png` |
| Junk of the three-hole data (P1's spheres 40, 48, 70, 90 M) | window u in [-35, 6] M (record cut at u = 14): 2.8, 2.6, 2.5, 2.5 e-6 M (FFI omega_0 = 0.2), the same at fixed retarded time (outgoing radiation); E_inf 2.2-2.8e-6 M (1.5-3.9e-6 over FFI 0.1-0.3); spread evenly over l = 2..8 (67-70 percent in l >= 4) at 0.2-0.5/M; momentum below 1.4e-6 M per radius | J4b, J4c; F-20261121-075600-4480a13, F-20261121-075803-8e1955b; `figures/j4_fig_p1_{waves,energy,extrap}.png`, `figures/j4c_fig_p1_lspec.png` |
| P1 prediction item 4 (junk 1e-6 to 1e-4 M by t = 150 M) | MET (2.2-2.8e-6 M, arriving by t = 106 M at 90 M), as a measurement of what the l <= 8 extraction sees | J4b item 6 |
| J4 as written | refuted: the window [-35, 50] holds P1's merger burst (dE/du peak at u = 25-28), and the radiation before it is the same at 40-90 M (no near zone) | J4 outcome |

What the three-hole number means [JUDGEMENT]: a lower bound in l (E_l is flat to l = 8, the
largest l AthenaK extracts, `athenak/src/z4c/z4c_wave_extr.cpp` line 78, so up to about twice
more would pass in l > 8) and an upper bound for the junk alone (it contains the binary's slow
inspiral before t of about 31 M, about 1e-6 M by my estimate). The members' junk at its own
frequency (about 3/M) does not cross P1's wave zone: its share above 1/M falls from 0.28 at 40 M
(2 M cells) to 0.015 at 90 M (4 M cells). Scaled from S2g, the members radiate 1.8e-5 M of junk
near themselves (1.0e-5 to 5.2e-5; J4 item 2). So the junk of P1's data is between about 1.5e-6 M
(seen) and 5e-5 M (scaled, upper end), at most about 3 percent of the binary's Newtonian binding
energy m1 m2 / 2a = 1.6e-3 M [arithmetic].

## Gauge recommendation for the passages after P1 [JUDGEMENT]

Evidence: E3 (S3: eta m = 2; S2: eta m = 0.25, constant) and E10 (S2g: core's mass-scaled
profile, eta m = 2 at the hole and 0.25 far away), single member at m/8; P1 (constant
`shift_eta = 2`, so eta M = 2 at the heavy hole and eta m = 0.25 at the members) merged its
binary at t = 48.8 M (p1 JOURNAL; cause open, RISKS R15).
1. Use core's mass-scaled shift damping for the next passage: `shift_eta = 2.0`,
   `shift_eta_profile = true`, `shift_eta_mref = 1.0` (the heavy mass), `shift_eta_width = 4.0`
   (core's recommendation, `scratch/core/exe/core_gauge/READY` option 2; in release core-v0.4).
   Why: it gives each member eta m = 2 at its puncture, and S2g shows that this reproduces S3's
   horizon mass (medians within 3.2e-4 of S3 over t = 4-22 m; mass flat at 1.00966 from t = 40 m)
   and constraint norm (4.1-5.3e-5 after t = 10 m), with no missed search after 4 m and no
   non-finite value over 90 m. Its coordinate horizon lies between S3's and S2's: mean radius
   1.03 m at t = 14 m against 1.18 m (S3) and 0.89 m (S2), then 0.99-1.01 m (8 cells) from t = 20 to
   90 m [VERIFIED, column meanradius of `single.horizon_summary_0.txt` in the S3, S2 directories of
   run F-20261115-173601-2fae2dc and in `S2g/` of run F-20261119-143443-f11ebb9]. With constant
   eta = 2/M the members get eta m = 0.25 (S2): the smallest coordinate horizon of the tested
   choices and a horizon mass drifting 1.7 times faster over t = 4-14 m (E3). For members resolved
   by 8 cells per mass, the larger coordinate horizon is the safer side.
   The heavy hole keeps eta M = 2 either way. The damping term stays mild: eta dt = (2/m) x
   3.9e-3 M = 0.06 at a member of P1's grid, the same as at S2g's hole [arithmetic].
2. The cost of the profile: the member's coordinate speed keeps lagging its boost speed (f = 0.86
   at t = 90 m and still rising, lag 5.6 m; S2 settles at f = 0.76 within 4 m). Coordinate tracks
   of the members are then not comparable to a Newtonian or post-Newtonian track over the first
   tens of m; compare gauge-invariant quantities (horizons, energies at the spheres, separation
   only after the members' settling).
3. Before a production passage: (a) the isolated-binary test of the lead's next action 1 should
   carry the profile as a third arm (m/8 constant eta, m/8 profile, m/16 constant), so that the
   cause of P1's merger is separated between resolution and gauge; (b) a 400-cycle card smoke of
   P1's input with the profile (about 0.1 card-hours), checked against P1's smoke (E7): trackers,
   the three finders, constraint norm, no non-finite value.
Still untested: the profile with three holes or a passage (core's READY: "Not tested: more than
two holes, a Hills passage"; F's request outbox 20261119T151429Z is unanswered); width 4 (S2g ran
the default width 2); runs longer than 90 m of a member; the neighbour term (width 4 raises eta at
one member through the other by (M/m - 1)/(1 + D^2/(4 m)^2) = 7/(1 + 100) = 7 percent at D = 5 M,
q = 4 [arithmetic from core's formula]).

## G1 T3 evidence text (constraint residuals and junk radiation of the three-puncture data)

T3 is met in substance for P1's data at m/8, with the limits stated.
- Constraints (nr_first E2, runs F-20261115-173547-a02af7d, F-20261115-181434-b9c8916; card
  smoke F-20261115-174602-c6879fe): at m/8 the t = 0 Hamiltonian norm 4.7e-5 is truncation error;
  the corrected data's own residual is 4.9e-7, 1/33 of the uncorrected data, visible from m/16 on;
  truncation converges at order 7.6-8; the card gives the same 4.713e-5.
- Junk of one member (S2g, run F-20261119-143443-f11ebb9; analyses F-20261120-222808-b65001c,
  F-20261120-223018-a5c0838, F-20261120-223121-c921d2d): E_junk/m = 7e-5 (4e-5 to 2e-4) for
  P/m = 0.25 at m/8, a single outgoing pulse mostly in (2,0) and (2,+-2); within a factor 1.4 of
  core's scaling 1.3e-2 (P/m)^4.
- Junk of the three-hole data (P1, run F-20261119-150017-b45ec5f; analyses
  F-20261121-075309-b6996ce, F-20261121-075600-4480a13, F-20261121-075803-8e1955b): 2.2-2.8e-6 M
  of outgoing radiation in the retarded-time window [-35, 6] M before P1's inspiral and merger
  reach the spheres at 40-90 M (1.5-3.9e-6 over integration choices), a lower bound in l (l <= 8
  extracted, flat in l); the members' high-frequency junk (scaled from S2g: 1.8e-5 M, 1e-5 to
  5e-5) is not carried by P1's wave zone and is quoted from the scaling. P1's prediction item 4
  (1e-6 to 1e-4 M) is met.
- Not reviewed yet by the lead or a second agent.

What remains for round 2 (the full P1 run and after):
- Nothing of T3 needs more of P1's record: the junk window ends at t = 106 M at the 90 M sphere,
  and J4b cuts the record at u = 14 M, so the chain's later segments cannot change it (J4's
  whole-record numbers would move only through the FFI kernel's ends).
- To close the l <= 8 limit: an extraction to higher l or spheres centred on the binary (a core
  change, Requests); or the same window on a run with the members near the centre.
- To measure the members' own junk in a three-hole run: wave-zone cells that carry 3/M (about
  M/4 out to 40 M) or a single-member convergence pair (S1 at m/16 beside S2g).
- P1's merger burst and the remnant's passage (u >= 19 M at the spheres) belong to package p1.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | predictions and outcomes J0-J4c |
| `scripts/junk_lib.py` | FFI, time-domain news, port of AthenaK's -2Y_lm, sphere quadrature, momentum coupling formula, tortoise radius |
| `scripts/test_junk_lib.py` | J2: test of junk_lib on synthetic modes |
| `scripts/single_junk.py` | energy, momentum, noise, mode shares, hf_frac per sphere in a retarded-time window; `--ucut` cuts the record first (J3 on S2g; J4, J4b on P1) |
| `scripts/extrap_junk.py`, `pulse_energy.py` | J3b (waveform extrapolated in 1/R), J3c (energy to the end of the pulse) |
| `scripts/newton_quad.py` | J4a: Newtonian quadrupole luminosity of P1's three bodies |
| `scripts/p1_geometry.py` | J4g: P1's binary from its trackers; earliest retarded arrival |
| `scripts/p1_lspec.py` | J4c: J4b's window by l and frequency band |
| `scripts/fig_*.py` | one script per figure; `figstyle.py` is a copy of `harness/style/figstyle.py` |
| `figures/`, `results/` | copies of the figures and JSON of the runs above (prefix = journal entry) |

## How to rerun

From `/data/haiyangw/nrpic/wt/F-hills`, each through `harness/bin/nrpic-run submit --kind scouting
--gate G1 --package tracks/F-hills/junk_gauge --cores 1 --parent <run> --purpose "..." -- env
OMP_NUM_THREADS=1 bash -c "<commands>"`, with `S=tracks/F-hills/junk_gauge/scripts`,
`G=/data/haiyangw/nrpic/scratch/F-hills/F-20261119-143443-f11ebb9/S2g`,
`P=/data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f` (`-` = the run directory):

    .venv/bin/python $S/test_junk_lib.py -                                   # J2
    .venv/bin/python $S/single_junk.py - $G && .venv/bin/python $S/fig_single_waves.py - \
        && .venv/bin/python $S/fig_single_energy.py -                         # J3
    .venv/bin/python $S/p1_geometry.py - $P && .venv/bin/python $S/fig_p1_geometry.py -   # J4g
    .venv/bin/python $S/single_junk.py - $P --M=1.25 --radii=40,48,70,90 --window=-35,50 --tag=P1w50
    .venv/bin/python $S/single_junk.py - $P --M=1.25 --radii=40,48,70,90 --window=-35,12 --tag=P1w12
    .venv/bin/python $S/single_junk.py - $P --M=1.25 --radii=40,48,70,90 --window=-35,6 --ucut=14 --tag=P1b
    .venv/bin/python $S/fig_p1_waves.py - $P && .venv/bin/python $S/fig_p1_energy.py - \
        && .venv/bin/python $S/fig_p1_extrap.py -                             # J4, J4b (one run)
    .venv/bin/python $S/p1_lspec.py - $P && .venv/bin/python $S/fig_p1_lspec.py -         # J4c

J3b, J3c and J4a: the commands are in the manifests of their runs (`tracks/F-hills/runs/<id>/`).
P1's directory is only read.

## Requests

- core: (1) make the largest extracted l an input parameter (`athenak/src/z4c/z4c_wave_extr.cpp`
  line 78 fixes lmax = 8): the junk of P1's data is flat in l up to 8 (J4c), so energies from a
  source 25 M off the centre are lower bounds; l = 16 would settle it. Alternatively, extraction
  spheres centred on a given point or on a tracker. (2) The answer to outbox
  20261119T151429Z (profile with three holes; card E1/E2 of the gauge package), now with S2g's
  result: the profile at a member's damping behaves as eta m = 2 for 90 m (E10).
- F-hills lead: review J3-J4c (a second agent given the run directories, not this conclusion);
  decide the gauge of the next passage with the recommendation above; carry the profile arm into
  the isolated-binary test.
