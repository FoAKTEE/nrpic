# G1 of F-hills: criterion by criterion (2026-11-21, lead, batch 4a; first written 2026-11-19)

Gate G1 "pre-core baseline" (brief l. 681) and the track criteria (brief l. 818, charter
section 9.9) as amended by decision 0013 (mass ratio four for the convergence study and the first
scan line; q = 10 when the mesh fits; the first clump passage right after the first black-hole
passage). Paths relative to `tracks/F-hills/`; manifests under `runs/<id>/`; predictions and
outcomes in `JOURNAL.md` and the package journals. G0 is signed (coord/GATES.md, 2026-11-20).

Verdict: **G1 not met.** Met: F-pre-1 for 0911.1136 and 1804.02911; F-pre-2 for 2404.16270
and, in part, for 2402.02178 (Kerr); constraint residuals and junk radiation quantified (with
reservations); the baselines, the validated pipeline, interface proposals. Not met: KHSR
(1201.4794) for F-pre-1; a complete vacuum Hills passage (P1's binary merged at t = 48.8 M,
a resolution effect of the m/8 members; P1b at m/16 waits for rule P1b-D, JOURNAL batch 4a);
the note's G1 text compiled and checked (package `note`, paused); a G1 verifier.

| # | criterion | state | evidence |
|---|---|---|---|
| T1 | F-pre-1 reproduces the restricted three-body curves (0911.1136, 1201.4794, 1804.02911) | **met for 0911.1136 and 1804.02911**; 1201.4794 (KHSR) not reproduced (G0 verifier D8; planned, SCOPING 5) | newton3 P1, P2, P7, P8 (`newton3/README.md`; runs F-hills-20261115-130237-cbfaf6b, -130239-cbfaf6b, -132703-0bfc352, -132942-2f7ad7f; figures `newton3/figures/fig_skr_curves.png`, `fig_bkrs_and_h1.png`, `fig_general_pdis_energy.png`). Lead: newton3 tests 10/10 (V1) and 15/15 after the energy fix (V10, F-20261119-145509-fb91531); independent restricted code agrees within 0.002 in P_dis and 0.4 percent in energy at seven (sense, D) points (V4, V4b; F-hills-20261115-145246-090f5dc, -145544-a314517). Deviations: retrograde edge 0.41 against SKR's 0.44; SKR's D-uniform retrograde mean energy not matched; KHSR's non-parabolic orbits and BKRS's eccentric binaries not reproduced. |
| T2 | F-pre-2 reproduces 2404.16270; for Kerr follows 2402.02178 | **met for Schwarzschild; in part for Kerr** | Schwarzschild: geodesic_binary (separation fraction within 0.0225 of the paper's figure, mean v_inf within 0.7 percent, 6/6 printed encounters; F-hills-20261115-130405-ce17dcf, -142554-c10b371, -134350-d16b473); verifier K5 with its own HRNA (F-20261121-032337-9c6d87a, -032325-f58a391). Kerr (package `kerr`, batch 3; reviewed batch 4a): HRNA run in a static slicing ('sch', new chart 'bks') reproduces Fig. InclD of 2402.02178 within the paper's pi/6 grid for s = 0 (15/15 pericentres), s = 0.9 L_z < 0 and L_z = 0 (15/15), the figure behind the K2 claim (its text refuted), the retrograde half of Fig. afin (survival 0.953 vs 0.995); NOT the L_z > 0 boundary at beta = 0.52-0.68 (HRNA 1-3 steps more stable) nor the empty prograde half of Fig. afin (0.48 vs 0.13). Runs F-20261121-132131-326dfd1 (scan), -132817-eacfe46 (analysis; repeated exactly by the lead, F-20261121-155614-7997653), -132821-5610cdb; tests -131507-d9da8f1, -131516-34d8c26, -132010-a654642, -132028-86ae5d0 (T8 repeated exactly, F-20261121-155605-7d21f63). HRNA in the Kerr-Schild slicing ('cks') pumps moving binaries at first order in M/r: not to be used at 2402's binary frequency (geodesic_binary S4 in 'cks' to be rerun in 'bks'). |
| T3 | constraint residuals and junk radiation of the three-puncture data quantified | **met with reservations** [JUDGEMENT] | Constraints (nr_first E2, F-20261115-173547-a02af7d, -181434-b9c8916; `nr_first/figures/fig_c0_constraints.png`): at m/8 the t = 0 Hamiltonian norm is truncation error (4.7e-5); the corrected data's own residual 4.9e-7 = 1/33 of uncorrected; truncation converges at order 7.6-8; card smoke H(t = 0) = 4.713e-5 (F-20261115-174602-c6879fe). Junk of one member (S2g, eta m = 2): E/m = 7e-5 (4e-5 to 2e-4; F-20261120-222808-b65001c, -223018-a5c0838, -223121-c921d2d). Three-hole junk at P1's spheres (junk_gauge J4b, F-20261121-075600-4480a13; lead L5, L5b, F-20261121-155457-5f36517, -155549-4359678): a burst of 0.40-0.63e-6 M arriving at u of about -33 M at 40-90 M, then a steady outgoing emission of 5.0-5.4e-8 M per M; the window u in [-35, 6] M holds 2.3-2.8e-6 M (E_inf 2.2-2.8e-6). Reservations: extraction only to l = 8 with E_l flat in l (lower bound in l); measured with the m/8 binary that spirals in numerically (the steady part is not identified); to be repeated at P1b's spheres. |
| T4 | one complete vacuum passage | **not met** | P1 (run F-20261119-150017-b45ec5f; chain DONE at t = 280 M, 12.58 card-hours by sacct over 16 jobs; finished in nrpic-run on 2026-11-21): the binary merged at t = 48.8 M before the pericentre (lead L1, F-20261121-063449-4dcca98). Cause: the members' resolution (binary_conv: the binary alone at m/8 decays like P1, at m/16 it does not decay over 0-7.7 M; F-20261121-130358-6cf186a, -130351-04074e1; decision 0022 item 4). The order of convergence is not yet established (lead review: the 1PN references spread by more than the deviations judged). P1b at m/16 (`binary_conv/inputs/p1b_R16n.athinput`) is submitted when rule P1b-D holds (JOURNAL, batch 4a): R16n segments 2-3 (Slurm 4807 and successor) and R12 (Slurm 4809) decide. |
| G1 | baseline results without the coupling | **met** | T1, T2 (Newtonian and geodesic references); `nr_first/figures/fig_baselines_p1.png` (both from the P1 state, F-20261115-174102-ffa764f) |
| G2 | analysis pipeline validated on them | **met** | Newtonian and HRNA pipelines against the literature (T1, T2). NR readers `nr_first/scripts/nrread.py`: synthetic full-Newton trajectory in AthenaK formats with restart overlap and planted failed searches 10/10 (F-20261119-143627-1a84aa5); core's run A reproduced (E3a, F-20261115-182100-613c9c6); passage analysis on synthetic files reproduces +1.31187 / -1.62654 units (E9, F-20261115-183737-49f0a7f); on the real S3/S2 and smoke outputs, reproduced from the raw files by the lead's own parser (V8, F-20261119-145434-82c05f2). Tracker files survive chain restarts only through `nr_first/scripts/athena_keep_trackers.sh` (E5). |
| I | interface proposals submitted | **met** | wave 1: `outbox/20261115T1507Z__to-core__*` (input format, pairwise common-horizon trigger, energy diagnostics; core answered `dfix-answers`: pairwise common horizon done, corrections taken into `multi_puncture.md`); wave 2b: `outbox/20261119T*__to-core__*` (tracker files on restart, finder at 4 cells per radius, found flag, three-hole damping) |

## P1, the passage (submitted 2026-11-19, ended 2026-11-21 at t = 280 M; outcome in T4 above)

Input `nr_first/inputs/p1_q4.athinput` (sha256 in the run's manifest): M = 1, m1 = m2 = 0.125
(bare), a_b = 5.11, e_b = 0.033, centre-of-mass Newtonian conic e = 1.0002, r_p = 9.81 M, start
at 31.75 M (4 r_t), coplanar prograde, effective phase 127 deg (inside the clean window 109-144
deg of newton3_fix); members at cells m/8 (0.015625), heavy hole at M/8; `corr = approx` with the
background factor; 1+log lapse and Gamma-driver with constant `shift_eta = 2` (eta M = 2, eta m =
0.25); spheres 40, 48, 70, 90 M; restart files every 5 M; tlim 280 M; max_nmb_per_rank 2700.
GR reading of the start state (lead V9, F-20261119-145449-245e984): centre-of-mass turning point
r_S = 9.25 M in the hole frame (E = 1.0042, L = 4.95 M); at the capture boundary with the hole at
rest or with the total mass.
Executable: release core-v0.3 card build behind the tracker wrapper. Cost from the smoke: 17-20
card-hours, 21-25 segments of 50 min; restart files 4.2 GB each.

Predictions (written before submission: `JOURNAL.md`, lead wave 2b, "P1: decision ... and
prediction"): the binary is separated by t = 200 M; Newton ejects m1 with +1.3119 units
(4.96e-3 M per unit) and binds m2 (a = 7.75, e = 0.250, pericentre 5.81 M at t = 122; newton3_fix
F-20261115-180351-b8eb386), HRNA ejects m2 with +0.970 and binds m1 (pericentre 7.26 M at t = 121;
E6); no common horizon of a member with the heavy hole; tree below 2700 MeshBlocks; member horizon
masses growing by 10-18 percent by t = 200 M if the single-puncture drift persists.

Read with `nr_first/scripts/p1_analysis.py <rundir> --baselines=nr_first/results/baselines_p1.json`
after `harness/bin/nrpic-run finish F-20261119-150017-b45ec5f`; member energies against the
barycentre of the heavy hole and the captured member (newton3_fix).

## What completes G1 (2026-11-21, batch 4a)

1. A complete vacuum passage (T4): P1b at m/16 under rule P1b-D (about 27 card-hours, 32
   segments, to 170-205 M), then its analysis against Newton, HRNA and EIH; the three-hole junk
   remeasured at its spheres (T3 reservation).
2. P1's analysis to t = 280 M (package p1: `p1/README.md`, "Commands for the next session"):
   the remnant's flyby and the constraint norm; it no longer decides the gate.
3. KHSR: one result of 1201.4794 with newton3 (SCOPING 5).
4. Note: the paused G1 revision (registered rerun, compile, checker, pages) with the lead's
   corrections (`note/JOURNAL.md`), the Kerr row, the merger of P1 and its cause.
5. A fresh verifier of the G1 material (ledger tables 3-4, P1, junk, eih, binary_conv, kerr).
