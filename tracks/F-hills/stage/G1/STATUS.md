# G1 of F-hills: criterion by criterion (2026-11-15, lead)

Gate G1 "pre-core baseline" (brief l. 681) plus the track criteria (brief l. 818, charter
section 9.9). Evidence paths relative to `tracks/F-hills/`; run ids under `runs/`; outcomes
and predictions in `JOURNAL.md`. Verdict: **G1 not met** (two of four track criteria met, one
partly, one not started); nothing is missing on F's side except runs that need
`core/multi-puncture`, named below so that they can start in the next wave.

| # | criterion | state | evidence |
|---|---|---|---|
| T1 | F-pre-1 reproduces the curves of the literature (0911.1136, 1201.4794, 1804.02911) | **met**, with two stated deviations | newton3 P1, P2, P7, P8 (`newton3/README.md`; runs F-hills-20261115-130237-cbfaf6b, -130239-cbfaf6b, -132703-0bfc352, -132942-2f7ad7f; figures `newton3/figures/fig_skr_curves.png`, `fig_bkrs_and_h1.png`, `fig_general_pdis_energy.png`). Lead: tests 10/10 (V1, F-hills-20261115-144857-b5b0bce); independent code agrees at nine (sense, D) points within 0.002 in P_dis and 0.4 percent in energy (V4b, F-hills-20261115-145544-a314517). Deviations: the retrograde edge is 0.41 against SKR's 0.44 with the bound-inside-Hill criterion (SKR's curve is matched when bound binaries wider than 3.5 a count as disrupted, H1); SKR's D-uniform retrograde mean energy not matched (definition unstated). KHSR's non-parabolic orbits and BKRS's eccentric binaries not reproduced. |
| T2 | F-pre-2 reproduces 2404.16270; for Kerr follows 2402.02178 | **partly met**: Schwarzschild yes, Kerr comparison no | geodesic_binary: separation fraction within 0.0225 of the paper's figure, mean v_inf within 0.7 percent, 6/6 printed encounters (runs F-hills-20261115-130405-ce17dcf, analysis -142554-c10b371, -134350-d16b473; figures `geodesic_binary/figures/s1_sepfrac.png`, `s1_vinf.png`); T1-T4 re-run by the lead (V2, runs F-hills-20261115-144919- to -144935-b5b0bce). Equatorial Kerr HRNA exists (S4, -133124-c799a81) but 2402.02178's claim (inclined binaries, main.tex:592-597 per the helper) is not reproduced; 1PN law not implemented. |
| T3 | constraint residuals and junk radiation of the three-puncture data quantified | **not met** (estimates only) | Estimates: three_punctures PLAN section 5 (run F-hills-20261115-131605-634fb86 on core's single-hole runs: correction lowers <H^2> 23 times in RMS, junk unchanged; member junk 4e-6 to 1e-4 M from two estimates that differ by ten); core's t = 0 residuals for its own triple (interface section 8, test 3). Needed: runs R0 and R2 below. |
| T4 | one complete vacuum passage | **not met** (not started; needs `core/multi-puncture`) | named run P1 below |
| G | analysis pipeline validated on the baseline | **partly met** | Newtonian and HRNA pipelines validated (T1, T2). For NR output only the radiated-energy integral exists (`three_punctures/scripts/junk_energy.py`, used on core's runs); tracker and horizon readers and the binding-energy analysis are planned (PLAN section 6), not written. |
| I | interface proposals submitted | **met this session** | outbox files `outbox/20261115T1507Z__*` to core (release, input format, pairwise common-horizon trigger, energy diagnostics) and to orch |

## The runs that complete G1 (to start as soon as `core/multi-puncture` is released)

Executables until the release: processors `/data/haiyangw/nrpic/wt/core-mp/.work/build_cpu/src/athena`,
card `/data/haiyangw/nrpic/wt/core-mp/.work/build_gpu_final/src/athena` (both built from
`core/multi-puncture`, read only); after the release, the executables of `main`. Each run is
registered (`tracks/F-hills/runs/<run_id>/manifest.json`), output under
`scratch/F-hills/<run_id>/`. Inputs (sha256):
`three_punctures/inputs/hills_q10_m8.athinput` 1423a3bf589994a46f51c0675143c765a2d600e9b4629cf4e325de6dda005046,
`three_punctures/inputs/junk_single_P028.athinput` e0de4c1107beff958cb51699bd877d3407a0d7133e19513d2114e712e767c04a,
`three_punctures/inputs/hills_q4_m8.athinput` af35dbe8a8d02655fdcd3185e608eda2870a474a731ca25d2ba6166e10ee7949.

| run | command | cost | prediction (refuted if) |
|---|---|---|---|
| R0 | `athena -i hills_q10_m8.athinput -d <rundir> time/nlim=0`; again with `problem/comp0_corr=none problem/comp1_corr=none problem/comp2_corr=none`; again with `problem/corr_background=false` | processors, minutes each, about 70 GB host memory | 1800 MeshBlocks; code-norm <H^2> ratio none/approx between 3 and 30 (three_punctures PLAN section 7; refuted outside) |
| R2 | `junk_single_P028.athinput` and the variant `problem/comp0_corr=none` on a card | about 1 card-hour each | radiated energy through R = 40, 60, 80 m equal within 20 percent; between 1e-5 and 1e-3 of m; none and approx within 20 percent |
| R4 | `junk_single_P028.athinput` with `z4c/shift_eta=0.1` (eta m of the members) | about 1 card-hour | tracker speed ratio f(t) of the members differs from core's eta m = 2 curve (0.48-0.61 of P/M_ADM) |
| **P1, the passage** | `ATHENA_EXE=<card exe> scripts/submit_chain.sh scratch/F-hills/<run_id> tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput time/tlim=200` | 32-36 card-hours (38.9 for 240 M on the Newtonian trees, runs F-hills-20261115-131348-634fb86; +11 percent if AMR adds blocks), about two days of one card; restarts every 5 M, so it can be extended to t = 250 | see below |

Parameters of P1 (`hills_q10_m8.athinput`): M = 1, m1 = m2 = 0.05 (bare), no spins;
positions M (0.8959, 2.1729, 0), m1 (-7.6709, -20.9806, 0), m2 (-10.2465, -22.4765, 0);
momenta M (-0.022037, -0.014755, 0), m1 (0.008611, 0.011325, 0), m2 (0.013426, 0.003430, 0)
(Newtonian state of newton3 integrated from 10 r_t and read at 4 r_t = 25.85 M, run
F-hills-20261115-130755-982aba0); binary a = 3.036, e = 0.029; centre-of-mass conic
r_p = 7.9965 M, e = 1.00006 (lead V5, F-hills-20261115-145251-090f5dc); coplanar prograde,
effective phase 130 deg; `corr = approx`, `corr_background = true`, `lapse = precollapsed`,
`puncture_setup = true`, `puncture_radius = 1.8`; 11 levels, members at cells 0.00625 (m/8),
heavy hole at 0.1; domain +-204.8 with 64^3 root cells; wave spheres 40, 48, 70, 90;
`shift_eta = 2` (eta M = 2, eta m = 0.1); `max_nmb_per_rank = 2700`; RK4, cfl 0.25.

Predictions for P1 (written before the run; [VERIFIED] model outputs, [JUDGEMENT] the reading):

1. Both baselines separate the binary: full Newton in 0.88 of the phases at this r_p, HRNA in
   1.00 (V7, F-hills-20261115-145915-71abf93). Refuted if the binary is still bound at t = 200.
2. Newtonian baseline (full three-body, from the same state; V5, V5b): m1 ejected with +1.613
   units = +2.90e-3 M (barycentric energy, constant to 3e-5 units after t = 300), m2 bound to
   M with a = 7.55, e = 0.247, pericentre 5.68 M, first pericentre of m2 near t = 95; no member
   inside 4 M.
3. Geodesic baseline (HRNA, hole fixed, the same positions and velocities relative to M; V6):
   m1 reaches r = 2.5 M at t = 97 (its first pericentre) and is captured; m2 is ejected with
   +1.16 units (+0.69 in the 2404 construction at the same r_p, start radius and binary
   orientation). Over 180 phases a member crosses 2.5 M in 94 percent.
4. Lead's expectation [JUDGEMENT]: one member merges with the heavy hole between t = 80 and
   120 (coordinate time, trackers lagging by a few M), the other leaves with an energy between
   the two baselines' values; the heavy hole's horizon mass grows by about the member's mass
   (0.05) and the member's finder stops finding it. If instead no member comes within the
   heavy hole's horizon by t = 200 and one stays bound, the Newtonian baseline describes the
   outcome and the geodesic reference fails at q = 10 (fixed hole) - an equally useful result.
5. Run health (three_punctures PLAN section 7): 1800 MeshBlocks at the start and below 2700
   throughout; 2000-2300 MeshBlock-cycles per second; three horizons from the first search,
   members 0.0515-0.0525, heavy 1.002 +- 0.005; binary separation 3.0 +- 0.3 to t = 40; no
   non-finite values. A member merger at m/8 is the main numerical risk.

Budget: R2 + R4 + P1 = 34-38 card-hours of the 40 of decision 0006 (no margin). Cheaper
fallback if the allotment is not raised: the q = 4 passage `hills_q4_m8.athinput`
(15.2 card-hours for 270 M; full Newton: m1 ejected with +1.312 units, m2 bound; HRNA from the
same state: m1 bound with first pericentre 7.3 M and falling through 5.2 M when the model
stopped at t = 987, m2 ejected with +0.97; 93 percent of phases plunge a member; V5b, V6, V7).

Diagnostics needed before P1 ends (F's work, next wave): a reader of `co_<n>.txt` and
`horizon_summary_<n>.txt`; member energies relative to M and to the barycentre of M and the
captured member (the definition of V5b); radiated energy from `rpsi4` at 40-90 M with
`junk_energy.py`; the HRNA and Newtonian references restarted from the NR state at t = 60.
