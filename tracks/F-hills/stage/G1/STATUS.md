# G1 of F-hills: criterion by criterion (2026-11-21, lead, batch 2a; first written 2026-11-19)

Gate G1 "pre-core baseline" (brief l. 681) and the track criteria (brief l. 818, charter
section 9.9) as amended by decision 0013 (mass ratio four for the convergence study and the first
scan line; q = 10 when the mesh fits; the first clump passage right after the first black-hole
passage). Paths relative to `tracks/F-hills/`; manifests under `runs/<id>/`; predictions and
outcomes in `JOURNAL.md` and the package journals. This file replaces the wave-1 version (which
named P1 at q = 10 and was written before core-v0.3 was released).

Verdict: **G1 not met.** Met: F-pre-1 for 0911.1136 and 1804.02911, the baselines, the
validated pipeline, interface proposals. Not met: KHSR (1201.4794) for F-pre-1; the Kerr part of
F-pre-2; the junk radiation of the three-hole data; a complete vacuum Hills passage (P1's binary
merged at t = 48.8 M before the passage, most likely a resolution effect: not yet a passage the
references can be compared with); the note's G1 text is written but not compiled or checked
(package `note`, paused); no G1 verifier. The G1 schematics exist (`note/figures/schem_architecture`,
`schem_dataflow`, run F-20261120-222908-4ffcfba).

| # | criterion | state | evidence |
|---|---|---|---|
| T1 | F-pre-1 reproduces the restricted three-body curves (0911.1136, 1201.4794, 1804.02911) | **met for 0911.1136 and 1804.02911**; 1201.4794 (KHSR) not reproduced (G0 verifier D8; planned, SCOPING 5) | newton3 P1, P2, P7, P8 (`newton3/README.md`; runs F-hills-20261115-130237-cbfaf6b, -130239-cbfaf6b, -132703-0bfc352, -132942-2f7ad7f; figures `newton3/figures/fig_skr_curves.png`, `fig_bkrs_and_h1.png`, `fig_general_pdis_energy.png`). Lead: newton3 tests 10/10 (V1) and 15/15 after the energy fix (V10, F-20261119-145509-fb91531); independent restricted code agrees within 0.002 in P_dis and 0.4 percent in energy at seven (sense, D) points (V4, V4b; F-hills-20261115-145246-090f5dc, -145544-a314517) and within 0.0023 / 0.0063 in P_dis and 0.4 / 1.2 percent in energy at retrograde D = 0.1 / 0.2 (V4 only; correction of the wave-1 "nine points"). Deviations: retrograde edge 0.41 against SKR's 0.44 (SKR's curve with the H1 counting); SKR's D-uniform retrograde mean energy not matched; KHSR's non-parabolic orbits and BKRS's eccentric binaries not reproduced. Finite mass ratio with the corrected (Jacobi-split) energies: newton3_fix runs F-20261115-175232-d399e83, -180351-440afa2. |
| T2 | F-pre-2 reproduces 2404.16270; for Kerr follows 2402.02178 | **partly**: Schwarzschild yes (verifier K5 confirmed it with its own HRNA, runs F-20261121-032337-9c6d87a, -032325-f58a391), Kerr no (package `kerr`, wave 3, cut before any outcome; files uncommitted) | geodesic_binary: separation fraction within 0.0225 of the paper's figure, mean v_inf within 0.7 percent, 6/6 printed encounters (F-hills-20261115-130405-ce17dcf, analysis -142554-c10b371, -134350-d16b473; `geodesic_binary/figures/s1_sepfrac.png`, `s1_vinf.png`); T1-T4 rerun by the lead (V2). Second check (wave 2): no defect in the drivers; HRNA gives a moving binary a spurious sideways self-acceleration (1.065e-4 at V = 0.28, F-20261115-175620-df20ffe), so HRNA percentages at q = 10 released at 4 r_t are model outputs, not predictions. Kerr: equatorial HRNA exists (S4, -133124-c799a81); 2402.02178's inclined-binary result not reproduced. |
| T3 | constraint residuals and junk radiation of the three-puncture data quantified | **partly**: constraints yes; junk of one member measured (junk_gauge, E/m = 7e-5, range 4e-5 to 2e-4, runs F-20261120-222808-b65001c, -223018-a5c0838, -223121-c921d2d; not yet reviewed by the lead); junk of the three-hole data not measured (J4 predicted) | Constraints (nr_first E2, F-20261115-173547-a02af7d, -181434-b9c8916; `nr_first/figures/fig_c0_constraints.png`): at m/8 the t = 0 Hamiltonian norm is truncation error (4.7e-5); the corrected data's own residual 4.9e-7 = 1/33 of uncorrected, visible from m/16 on; truncation converges at order 7.6-8. The card smoke gives the same H(t = 0) = 4.713e-5 (F-20261115-174602-c6879fe). Junk: the single-puncture runs stopped before the pulse reached 30 m (F-20261115-173601-2fae2dc, slot limit); S2g (F-20261119-143443-f11ebb9, pending) and P1's spheres at 40-90 M will measure it. |
| T4 | one complete vacuum passage | **not met in substance**: the run is nearly complete, the passage is not a Hills passage | P1, run F-20261119-150017-b45ec5f, chain segment 14 (Slurm 4769) running from t = 231.9 M to tlim 280 M. The binary MERGED at t = 48.8 M, before the pericentre (p1 entry 4, runs F-20261120-222808-0e709b6, -223252-ca18a81; confirmed by the lead's own parser, F-20261121-063449-4dcca98: separation < 0.1 M at 48.79 M, common horizon 0.2686 at 48.81 M); the remnant passes the heavy hole at 7.0 M coordinate distance at t = 155 M and recedes. Trackers and horizons are found throughout; the constraint norm to t = 280 M is not yet read. No reference merges (Newton, HRNA, EIH; inspiral time about 3400 M), so the merger is most likely numerical (members at m/8) [JUDGEMENT, TO VERIFY with the isolated binary at m/8 and m/16]. |
| G1 | baseline results without the coupling | **met** | T1, T2 (Newtonian and geodesic references); `nr_first/figures/fig_baselines_p1.png` (both from the P1 state, F-20261115-174102-ffa764f) |
| G2 | analysis pipeline validated on them | **met** | Newtonian and HRNA pipelines against the literature (T1, T2). NR readers `nr_first/scripts/nrread.py`: synthetic full-Newton trajectory in AthenaK formats with restart overlap and planted failed searches 10/10 (F-20261119-143627-1a84aa5); core's run A reproduced (E3a, F-20261115-182100-613c9c6); passage analysis on synthetic files reproduces +1.31187 / -1.62654 units (E9, F-20261115-183737-49f0a7f); on the real S3/S2 and smoke outputs, reproduced from the raw files by the lead's own parser (V8, F-20261119-145434-82c05f2). Tracker files survive chain restarts only through `nr_first/scripts/athena_keep_trackers.sh` (E5). |
| I | interface proposals submitted | **met** | wave 1: `outbox/20261115T1507Z__to-core__*` (input format, pairwise common-horizon trigger, energy diagnostics; core answered `dfix-answers`: pairwise common horizon done, corrections taken into `multi_puncture.md`); wave 2b: `outbox/20261119T*__to-core__*` (tracker files on restart, finder at 4 cells per radius, found flag, three-hole damping) |

## P1, the passage (submitted 2026-11-19; outcome so far in T4 above)

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

## What completes G1 (2026-11-21)

1. The cause of P1's merger: the isolated binary (the two members only, same a_b, momenta and
   gauge) at m/8 and m/16 for about 60 M. If m/8 alone merges, the passage is repeated with finer
   members (m/16 fits one card at q = 4: g2mesh run F-20261120-222810-e408386, 3000 slots at
   78785 MiB) or a wider binary; if both merge, gauge and data are next (E10, `corr`).
2. P1 to t = 280 M: finish, `p1/scripts/run_all.sh` and `nr_first/scripts/p1_analysis.py`, the
   constraint norm, the remnant's flyby, the junk and merger signals at the spheres (J4).
3. KHSR: one result of 1201.4794 with newton3 (SCOPING 5).
4. Kerr: package `kerr` (2402.02178 inclined set-up, or why not).
5. Note: the paused G1 revision (registered rerun, compile, checker, pages), with the lead's
   corrections listed in `note/JOURNAL.md`.
6. A fresh verifier of the G1 material (ledger tables 3-4, P1, junk, eih).
