# G1 status of D-bh-dress (2026-11-15, lead session of wave 2)

G1 criteria of the track sheet (charter 9.7, brief line 779; decision 0013 changes nothing
for Track D) and the common G1 evidence (charter 9.2). Verdict of the lead: NOT YET MET.
Met: D-pre-1, D-pre-2, D-pre-4, interface proposals, baseline figures. Open: the
Einstein-Straus analysis pipeline on AthenaK output (ES-1 and V-1 are running), the D-pre-3
profile criterion (wording, proposal to orch), an updated architecture schematic, a
fresh-context verifier of the wave-2 baselines. Checklist: `CHECKLIST.md`; artefacts:
`EVIDENCE.md`; lead's recheck: `../REVIEW-wave2.md`. Paths relative to `tracks/D-bh-dress/`.

## Track-specific criteria

| Criterion | State | Evidence |
|---|---|---|
| Derivation and offline check of D-pre-1 | MET | `einstein_straus/DERIVATION.md`; 48 symbolic identities (D-bh-dress-20261115-042626-f3da881; lead rerun -065141-5fdc744, 48/48); lead's own quadrature gives a = 0.9765922286441, m_p = 1.023968828206 M, equal to `es.json` to 1e-13; offline 1D and 3D residuals fourth order (orders 3.85-4.07 in seven sub-boxes, D-bh-dress-20261115-042704-f3da881); inside AthenaK at t = 0 the residuals fall faster than fourth order in the middle of the curvature transition (box orders 5.88 for H and 5.76 for M; over 4 < r < 30 M 5.3 and 4.7), momentum residual order 3.2 at the inner dust edge, deposited density equals rho to 1.1e-13 (-043002-d51c7f2, -043033-4df1e76, -043406-4df1e76). Release core-v0.3 reproduces the t = 0 check bit for bit (verifier, D-20261115-170224-924d1d9). Data set with the outer dust edge at 60 M checked again at fourth order (D-20261115-170234-f9b7f03). |
| Baseline of D-pre-2 (spike in the probe limit) | MET (one difference to a published curve open) | Schwarzschild, constant f: peak 0.8699e8 GeV/cm^3 at 7.58 Gm, against digitized SFW Fig. 1 to 0.02 per cent at the peak and 0.26 per cent over the curve; exact peak ratio over the Gondolo-Silk spike 2.59, GS edge moved 8 -> 4 Gm raises the peak by 9.2 per cent (D-bh-dress-20261115-123029-4df1e76, lead rerun -145636-5259f48); Hernquist cusp: FdRW Schwarzschild curve to 1.0 per cent. AthenaK probe test a = 0: chi^2/dof median 0.98 over 20000 M, loss-cone probes 1200/1200 inside cross, 0/1200 outside (-123755-25227d4, -125739-a18d74d, -123801-25227d4, -123936-72cd01e). Kerr (wave 2): FdRW constant f at a = 0.5, 0.8 within 0.88 and 0.95 per cent; Hernquist within 1.4-1.5 per cent at a = 0 and on the axis, 4 per cent below FdRW at the a = 0.8 equatorial peak [TO VERIFY, cause open] (D-bh-dress-20261115-171615-8adbbdd); AthenaK stationarity in Kerr a = 0.8, 48000 particles, 20000 M, late/early 0.998-1.003, invariants to 1e-5 (-172611-1e40191, analysis -174954-786ddcc; lead recheck D-20261115-193844-df4523c). Open: inner-range time averages 1-4 per cent below the reference with a common sign (REVIEW-wave2 section 2). |
| Baseline of D-pre-3 (Newtonian secondary infall) | OPEN for the profile criterion; MET for the growth of the dress | Semi-analytic: self-similar solution with a seed, slope of m 0.741 on [1e-4, 1e-3] r_ta, r^(-9/4) only below lambda ~ 1e-4, outermost caustic 0.355 r_ta, mass inside it 0.654 M_ta (-123813-97afeea); dress fraction 0.625 = f_passed of the shells (-125613-248fdaf); eta_ta of 2106.07480 to 1.3e-5 (-122051-bf0d6b1); lead's closed form M_ta 1.52542, 2.62815 at a/a_i = 2, 4 (-145610-5259f48). AthenaK Newtonian mode (wave 2, release core-v0.3, clump stand-in at a cell centre): M_ta and dress agree with the shell reference matched to the measured mesh kernel to 0.1-0.5 per cent; M_ta = 2.597 M, dress 0.797 M at a/a_i = 4 in N128c and N64c; 4.816 M and 2.154 M at a/a_i = 8 (D-20261115-171503-4262f03, -171505-62940f4, -171507-d1058a9; analysis -190541-e27453d; lead recheck D-20261115-193823-88f7f86 within 0.07 per cent). Profile within the bin scatter of the matched shells from 4 dx to r_ta; within 25 per cent of the self-similar profile on lambda = 0.1-0.3 only at a/a_i = 8, flatter inside. The sheet's "reproduce the r^(-9/4) profile" and SCOPE's "slope -9/4 +- 0.05 on [2 dx, r_ta/2]" fail for an exact code (verifier C4): proposal to judge against the self-similar m(lambda) and the matched shells (outbox to orch). |
| Noise floor of D-pre-4 | MET (for an asymptotically flat vacuum puncture) | Card runs M/8 and M/16 to 500 M, 2.18 card-hours (-121313-284ec4f, -121314-284ec4f; analysis -130954-49ed46f; lead -145546-5259f48; verifier D-20261115-171508-94e8cb1): drift 50 -> 490 M +2.95e-4 (M/8), +3.67e-5 (M/16); smallest detectable change at M/16 2.0-2.5e-5 for windows ending before 210 M; excursions of 5e-5 to 1e-4 at the same times at both resolutions (boundary attribution untested, R4); the M/8 run is still in its gauge transient at 50 M (use t0 = 100 M). The floor of the null test is the matched control V-1 (running). |

## Common G1 evidence (charter 9.2)

| Item | State | Evidence |
|---|---|---|
| Baseline results without the coupling | MET for D-pre-1..4 as above | |
| Analysis pipeline validated on them | PARTLY | D-pre-2 binning, invariants and crossing times; D-pre-3 masses (lead's independent implementation, W6); D-pre-4 finder re-search. The Einstein-Straus pipeline (`es_runs/analyse.py`: horizon mass against V-1, tracer areal radius against proper time, crossing times) has run on smoke output only; ES-1 and V-1 are running. |
| Interface proposals submitted | MET | `outbox/20261115T1510Z__to-core__*.md`; core implemented tracer rule, restart dump, accretion diagnostics, analytic-metric excision, Newtonian point mass (`scratch/core/exe/core_requests-adf/READY`, items 1-5); lapse for expanding dust and puncture on the torus open |
| Schematics, working note, verifier | note and schematics MET (G0); architecture to be updated for core's dfix executables; fresh verifier of the wave-2 baselines OPEN | `note/`, `../G0/VERIFIER.md` |

## The first full-relativity run: ES-1 and V-1 (running)

ES-1: the D-pre-1 data set with the outer dust edge at 60 M (run D-20261115-170213-d2c2131:
696688 dust particles, 140 tracers of mass 1e-30, M_tot = 2.73967 M, H = 5.58116e-3/M,
puncture of bare mass m_p = 1.0239688282062387), evolved on the card with release core-v0.3,
1+log and Gamma-driver (the gauge that exists), 344 MeshBlocks of 24^3 cells (root 4 M on
+-192 M, 2 M on +-96 M, 1 M on +-48 M, M/8 on +-6 M), D-pre-4 finder,
`metric_drvts = interpolant`, `ah_exc_factor = 0.8`, 200 M of coordinate time. V-1: the same
slice without dust (vacuum f-slice of one Schwarzschild hole), same mesh, gauge and tracers.
Runs D-20261115-172726-60ba4c2 (Slurm 4472) and D-20261115-172730-c6d151b (Slurm 4473);
predictions copied into `es_runs/JOURNAL.md` entry 2 before submission (wave-1 predictions
1-4 and the helper's A1-A6). Exact references: wall (36^1.5 + 1.5 sqrt(2) tau)^(2/3) M
(46.99, 56.80, 65.84, 74.29 M at tau = 50..200 M), tracer groups R0 = 6, 10 M reach R = 2M at
tau = 14.83 and 34.44 M (not 15.0 and 34.6, the grid points of wave 1); under 1+log the
plateau lapse reaches 10.8 and the dust proper time 1251 M at t = 200 M (homogeneous model).
Finish: `es_runs/tools/finish.sh` from the worktree root, then the outcome under entry 2.
Pass criteria as written: horizon-mass change of ES-1 within 3 times V-1's floor; wall
tracers within 1 per cent of the closed form for tau <= 200 M.
