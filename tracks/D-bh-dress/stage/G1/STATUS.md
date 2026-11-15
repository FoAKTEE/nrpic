# G1 status of D-bh-dress (2026-11-15, lead session of wave 1)

G1 criteria of the track sheet (charter 9.7, brief line 779) and the common G1 evidence
(charter 9.2). Verdict now: NOT YET MET (four met, two partly met, two open). Checklist:
`CHECKLIST.md`; artefacts: `../G0/EVIDENCE.md`. Paths relative to `tracks/D-bh-dress/`.

## Track-specific criteria

| Criterion | State | Evidence |
|---|---|---|
| Derivation and offline check of D-pre-1 | MET | `einstein_straus/DERIVATION.md`; 48 symbolic identities (D-bh-dress-20261115-042626-f3da881; lead rerun -065141-5fdc744, 48/48); lead's own quadrature gives a = 0.9765922286441, m_p = 1.023968828206 M, equal to `es.json` to 1e-13; offline 1D and 3D residuals fourth order (orders 3.85-4.07 in seven sub-boxes, D-bh-dress-20261115-042704-f3da881); inside AthenaK at t = 0 (format-2 reader of `core/id-extrinsic` 408df57) residuals fall at order 5.8-5.9 in the curvature transition and 3.2 at the inner dust edge, deposited density equals rho to 1.1e-13 (-043002-d51c7f2, -043033-4df1e76, -043406-4df1e76). Disagreements with item 2 of `coord/notes/derivations_to_check.md` recorded (outbox to orch). |
| Baseline of D-pre-2 (spike in the probe limit) | PARTLY MET: Schwarzschild yes, Kerr no | Constant f: peak 0.8699e8 GeV/cm^3 at 7.58 Gm against digitized SFW Fig. 1 to 0.02 per cent; Hernquist cusp, canonical action: FdRW Schwarzschild curve to 1.0 per cent (D-bh-dress-20261115-123029-4df1e76; lead rerun -145636-5259f48 identical). AthenaK geodesics (CPU executable of main, analytic Kerr-Schild a = 0): 48000 particles stationary for 20000 M, chi^2/dof median 0.98 (-123755-25227d4, -125739-a18d74d); loss-cone boundary probes 1200/1200 inside cross, 0/1200 outside, crossing times second order in dt (-123801-25227d4, -123936-72cd01e). Kerr (a = 0.5, 0.8; targets digitized in `spike/README.md`) not started. |
| Baseline of D-pre-3 (Newtonian secondary infall) | PARTLY MET: semi-analytic yes, AthenaK Newtonian mode no | Self-similar solution with a seed: slope of m 0.741 on [1e-4, 1e-3] r_ta, r^(-9/4) only below lambda ~ 1e-4, outermost caustic 0.355 r_ta, dress 0.625 M_ta (-123813-97afeea); printed eta_ta of 2106.07480 to 1.3e-5 and the 0.964 of 1901.08528 reproduced, its 0.999 not (-122051-bf0d6b1); shells: M_ta, absorbed and dress masses, warm-dust capture (-125613-248fdaf); lead's closed form agrees (M_ta 1.52542, 2.62815 at a/a_i = 2, 4; -145610-5259f48); run parameters in `secondary_infall/RUNS.md`. Under decision 0010 the particle version is AthenaK's Newtonian mode (`core/newton`, not on main): not run. |
| Noise floor of D-pre-4 | MET (for an asymptotically flat vacuum puncture) | Card runs M/8 and M/16 to 500 M, 2.18 card-hours (-121313-284ec4f, -121314-284ec4f; analysis -130954-49ed46f; lead re-check from the raw finder output -145546-5259f48): drift 50 -> 490 M +2.95e-4 (M/8), +3.67e-5 (M/16); smallest detectable change at M/16 2.0-2.5e-5 for windows from 50 M ending before 210 M, 5-9e-5 across the outer-boundary excursions (9.3e-5 peak to peak in 220-255 M at both resolutions); spin below 5.7e-9 at M/16. Caveat: the boundary attribution is untested and the Einstein-Straus run needs its own matched control (risk R3). |

## Common G1 evidence (charter 9.2)

| Item | State | Evidence |
|---|---|---|
| Baseline results without the coupling | MET for D-pre-1..4 as above | |
| Analysis pipeline validated on them | PARTLY: the finder re-search and slice masses (D-pre-4) and the spike binning, invariants and crossing times (D-pre-2) are validated; the Einstein-Straus pipeline (tracer areal radius from `trajmet.bin`, AH mass against wall proper time) has not run on AthenaK output beyond t = 0 | |
| Interface proposals submitted | MET | `outbox/20261115T1510Z__to-core__*.md` (format-2 merge, tracer push, lapse for expanding dust, accretion diagnostics, analytic-metric excision, Newtonian point mass, restart dump, puncture on the torus) |
| Schematics, working note, fresh verifier | OPEN | `../G0/OPEN.md` |

## The first full-relativity run after the merge of `core/id-extrinsic`

Run ES-1: the D-pre-1 Einstein-Straus data set evolved in AthenaK (`nrpic_cf`, `ncomp = 2`:
format-2 table + puncture of bare mass m_p = 1.0239688282062387; the data set of run
D-bh-dress-20261115-043445-b782009, regenerated with the outer dust edge at 60 M,
`make_es.py --Rb 56 --w_out 4`, and offline-checked again), dx = M/8 at the puncture,
2 M over the dust (1 M inside 48 M), outer boundary at 180-256 M, 200 M of coordinate
time, `fastflow/metric_drvts = interpolant` with the D-pre-4 production finder,
`particles/ah_exc_factor = 0.8`, lapse as agreed with core (1+log with the Gamma-driver
if nothing else exists, recorded as such). Cost 1.4 card-hours (scoping model, run
D-bh-dress-20261115-145950-23fa1c7). Paired with V-1: the same table without dust (the
f-slice of a single Schwarzschild hole, Painleve-Gullstrand beyond 36 M), same mesh,
gauge and length, about 1.2 card-hours [JUDGEMENT], whose horizon-mass history is the
floor for ES-1. Then both at M/16 (2.9 + about 2.6 card-hours).

Predicted result (to be copied into JOURNAL.md before submission):
1. M_AH(t)/M_AH(t0) - 1 stays within the floor of V-1 for 100 <= t <= 200 M; with the
   D-pre-4 floor as the guide, |M_AH(t)/M_AH(100 M) - 1| <= 3e-5 at M/8 (D-pre-4 gives
   2.8e-5 from t0 = 100 M before 210 M). Exact value: M_AH = M on every spherical slice
   (Birkhoff in the vacuum bubble; the mass inside the comoving wall is constant).
   [JUDGEMENT] The level: M_AH(100 M) - M = +1.5e-3 +- 3e-4 at M/8, the finder offset of
   the bare puncture at this resolution (D-pre-4: +1.50e-3 at 100 M), if the interior
   evolves as a bare puncture.
2. The wall tracers (tags 56-69, areal radius from the metric at the particle against
   their proper time) follow R_w(tau) = (36^(3/2) + (3/2) 2^(1/2) tau)^(2/3) M: 46.99,
   56.80, 65.84, 74.29 M at tau = 50, 100, 150, 200 M (`es_reference.csv`), to 3e-3 at
   dx = 1 M (core test 2 measured 3.3e-3 at dx = 1 M in the conformal-time gauge).
3. The tracer groups at R = 6 M and 10 M (tags 0-27) reach R = 2M at tau = 15.0 M and
   34.6 M and are removed; the group at 20 M turns around at about 27 M and falls in at
   tau = 245 M (after the run); no dust particle enters R < R_w(tau).
4. With 1+log slicing the lapse in the dust plateau rises as 1 + 6 ln a, to about 4.9 by
   tau = 200 M (a = 1.93); a front from the dust edges may reach the hole (core test 2).
Refuted by: a horizon-mass change in ES-1 larger than in V-1 by more than 3 times V-1's
floor (then the dust couples to the hole numerically: through the gauge, the deposit or
the boundary), or a wall tracer off the exact curve by more than 1 per cent (then the
push or the expansion is wrong; compare R1, the tracer finding of D-pre-4).

Before ES-1 can run: `core/id-extrinsic` merged (or a pinned build named), core's
answer on the tracer push of the release card executable (outbox, blocker), and a lapse
choice from core; the regenerated data set and V-1's table (both processor work of this
track).
