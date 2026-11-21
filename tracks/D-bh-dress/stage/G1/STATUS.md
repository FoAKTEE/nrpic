# G1 status of D-bh-dress (2026-11-21, lead session of batch 2a)

G1 criteria of the track sheet (charter 9.7, brief line 779; decisions 0013, 0016 and 0017
change nothing in them for Track D) and the common G1 evidence (charter 9.2). Verdict of the
lead: NOT MET. Met: D-pre-1, D-pre-2 (equatorial; confirmed by the fresh verifier), D-pre-4,
the growth part of D-pre-3, the analysis pipeline (Einstein-Straus pipeline on AthenaK output
of ES-1, V-1 and ES-1G), interface proposals, baseline figures, the redrawn architecture
schematic (C9) and the fresh-context verifier (C17, `VERIFIER.md`). Open: the D-pre-3 profile
criterion (C7; ruling `d-pre-3-criterion` at orch since 2026-11-15, or the run to a/a_i = 30)
and the rebuilt working note (C16; v1 text committed, PDF and checker not rerun). The package
is therefore not complete for the orchestrator's review. Checklist: `CHECKLIST.md`;
artefacts: `EVIDENCE.md`; lead's rechecks: `../REVIEW-wave2.md`, `../REVIEW-wave3.md`. Paths
relative to `tracks/D-bh-dress/`. Corrections of 2026-11-21 after the verifier: the dress at
a/a_i = 2 (V2), the profile bound (V2), the a = 0.8 Hernquist gap and the hole mass (V3).

## Track-specific criteria

| Criterion | State | Evidence |
|---|---|---|
| Derivation and offline check of D-pre-1 | MET | `einstein_straus/DERIVATION.md`; 48 symbolic identities (D-bh-dress-20261115-042626-f3da881; lead rerun -065141-5fdc744, 48/48); lead's own quadrature gives a = 0.9765922286441, m_p = 1.023968828206 M, equal to `es.json` to 1e-13; offline 1D and 3D residuals fourth order (orders 3.85-4.07 in seven sub-boxes, D-bh-dress-20261115-042704-f3da881); inside AthenaK at t = 0 the residuals fall faster than fourth order in the middle of the curvature transition (box orders 5.88 for H and 5.76 for M; over 4 < r < 30 M 5.3 and 4.7), momentum residual order 3.2 at the inner dust edge, deposited density equals rho to 1.1e-13 (-043002-d51c7f2, -043033-4df1e76, -043406-4df1e76). Release core-v0.3 reproduces the t = 0 check bit for bit (verifier, D-20261115-170224-924d1d9). Data set with the outer dust edge at 60 M checked again at fourth order (D-20261115-170234-f9b7f03). |
| Baseline of D-pre-2 (spike in the probe limit) | MET (one difference to a published curve open) | Schwarzschild, constant f: peak 0.8699e8 GeV/cm^3 at 7.58 Gm, against digitized SFW Fig. 1 to 0.02 per cent at the peak and 0.26 per cent over the curve; exact peak ratio over the Gondolo-Silk spike 2.59, GS edge moved 8 -> 4 Gm raises the peak by 9.2 per cent (D-bh-dress-20261115-123029-4df1e76, lead rerun -145636-5259f48); Hernquist cusp: FdRW Schwarzschild curve to 1.0 per cent. AthenaK probe test a = 0: chi^2/dof median 0.98 over 20000 M, loss-cone probes 1200/1200 inside cross, 0/1200 outside (-123755-25227d4, -125739-a18d74d, -123801-25227d4, -123936-72cd01e). Kerr (wave 2): FdRW constant f at a = 0.5, 0.8 within 0.88 and 0.95 per cent; Hernquist within 1.4-1.5 per cent at a = 0 and on the axis, 4 per cent below FdRW at the a = 0.8 equatorial peak (D-bh-dress-20261115-171615-8adbbdd). Fresh verifier (VERIFIER.md V3, run D-20261121-033209-9c0bd44, own code): constant f within 0.85 and 0.88 per cent, Hernquist a = 0 within 1.67 per cent for r >= 5 Gm, a = 0.8 peak 4.5 per cent below FdRW and 0.6 per cent from ours; [JUDGEMENT, verifier's reasons: grows with spin, FdRW's a = 0.8 curve has a narrow bump at its maximum, two implementations agree] the gap lies in FdRW's curve; the axis curve NOT CONFIRMED (not computed). Hole mass 4e6 Msun: FdRW give only M_BH >~ 4e6 Msun (`kerrdm.tex:127`); 4e6 is the track's choice [JUDGEMENT], consistent with the a = 0 curve to 0.55 per cent; AthenaK stationarity in Kerr a = 0.8, 48000 particles, 20000 M, late/early 0.998-1.003, invariants to 1e-5 (-172611-1e40191, analysis -174954-786ddcc; lead recheck D-20261115-193844-df4523c). Inner-range time averages 3.1, 1.8, 0.9 per cent below the reference with a common sign, each within 1-2 sigma (verifier V4, D-20261121-040826-9d5051a; REVIEW-wave2 section 2); a second sampler seed would decide a bias (G2 item). |
| Baseline of D-pre-3 (Newtonian secondary infall) | OPEN for the profile criterion; MET for the growth of the dress | Semi-analytic: self-similar solution with a seed, slope of m 0.741 on [1e-4, 1e-3] r_ta, r^(-9/4) only below lambda ~ 1e-4, outermost caustic 0.355 r_ta, mass inside it 0.654 M_ta (-123813-97afeea); dress fraction 0.625 = f_passed of the shells (-125613-248fdaf); eta_ta of 2106.07480 to 1.3e-5 (-122051-bf0d6b1); lead's closed form M_ta 1.52542, 2.62815 at a/a_i = 2, 4 (-145610-5259f48). AthenaK Newtonian mode (wave 2, release core-v0.3, clump stand-in at a cell centre): M_ta agrees with the shell reference matched to the measured mesh kernel within 0.3 per cent at a/a_i = 2, 4, 8, the dress within 1.1 per cent from a/a_i = 3 on and within 0.5-3.3 per cent at a/a_i = 2, where it is small and depends on the central force law (corrected after the verifier's V2, D-20261121-031711-0d79cb3; lead Z4, D-20261121-063617-3f2036f; the earlier wording "0.1-0.5 per cent" for both was WRONG at a/a_i = 2); M_ta = 2.597 M, dress 0.797 M at a/a_i = 4 in N128c and N64c; 4.816 M and 2.154 M at a/a_i = 8 (D-20261115-171503-4262f03, -171505-62940f4, -171507-d1058a9; analysis -190541-e27453d; lead recheck D-20261115-193823-88f7f86 within 0.07 per cent). Profile within the bin scatter of the matched shells from 4 dx to r_ta; about 25 per cent from the self-similar profile on lambda = 0.1-0.3 at a/a_i = 8 (verifier: 25.9 per cent against its seedless solution, 33-35 per cent with r_ta moved by 3 per cent: sensitive to r_ta), flatter inside. The sheet's "reproduce the r^(-9/4) profile" and SCOPE's "slope -9/4 +- 0.05 on [2 dx, r_ta/2]" fail for an exact code (verifier C4): proposal to judge against the self-similar m(lambda) and the matched shells (outbox to orch). |
| Noise floor of D-pre-4 | MET (for an asymptotically flat vacuum puncture) | Card runs M/8 and M/16 to 500 M, 2.18 card-hours (-121313-284ec4f, -121314-284ec4f; analysis -130954-49ed46f; lead -145546-5259f48; verifier D-20261115-171508-94e8cb1): drift 50 -> 490 M +2.95e-4 (M/8), +3.67e-5 (M/16); smallest detectable change at M/16 2.0-2.5e-5 for windows ending before 210 M; excursions of 5e-5 to 1e-4 at the same times at both resolutions (boundary attribution untested, R4); the M/8 run is still in its gauge transient at 50 M (use t0 = 100 M). The floor of the null test is the matched control V-1 on the ES mesh (wave 2b: 4.2e-5 over 100-165 M, 1.4e-4 over 100-200 M with a late drift of open cause), not this floor. |

## Common G1 evidence (charter 9.2)

| Item | State | Evidence |
|---|---|---|
| Baseline results without the coupling | MET for D-pre-1..4 as above | |
| Analysis pipeline validated on them | MET | D-pre-2 binning, invariants and crossing times; D-pre-3 masses (lead's independent implementation, W6); D-pre-4 finder re-search; Einstein-Straus pipeline on ES-1/V-1: wall tracers within 2.2e-3 of the exact curve for tau <= 200 M, crossings of R = 2M within 6e-4 and 5.6e-3 M of the exact proper times (D-20261119-141839-8686bd7), reproduced by the lead's own code (D-20261119-151039-b2ce968). |
| Interface proposals submitted | MET | `outbox/20261115T1510Z__to-core__*.md`; core implemented tracer rule, restart dump, accretion diagnostics, analytic-metric excision, Newtonian point mass (`scratch/core/exe/core_requests-adf/READY`, items 1-5); lapse for expanding dust and puncture on the torus open |
| Schematics, working note, verifier | architecture schematic redrawn (MET, run D-20261120-222429-026731f); working note v1 text committed, PDF not rebuilt (OPEN); fresh verifier MET (`VERIFIER.md`) | `note/`, `VERIFIER.md`, `../REVIEW-wave3.md` section 2 |

## The first full-relativity runs (G2 material; for G1 they validate the pipeline)

ES-1 and V-1 (1+log, faces at +-192 M, M/8 at the hole; D-20261115-172726-60ba4c2,
-172730-c6d151b): wall and crossings held; the 3e-5 drift prediction failed (3.40e-4 and
1.37e-4 over 100-200 M); the 1+log slicing leaves the dust (es_runs entries 4, 6-8).
ES-1G (core's lapse_leak, D-20261119-142633-6f72922, 0.794 card-hours; es_runs entry 9;
lead Z1-Z2): the dust is sliced on its exact curve (wall within 1.7e-4 to tau = 206 M, proper
time of R0 = 48 M 205.3 M at t = 200 M), but the horizon mass grows by +6.96e-3 over
100-199.5 M while the hole shrinks to 0.78 M in coordinates; the growth is in the slice, not
the finder, and the exterior mass is lost from the outer faces inward (K1-K2).
V-1B (V-1 with the faces at +-384 M, D-20261120-222625-63abd72, 0.778 card-hours; lead Z3):
the late drift of V-1 is gone: |drift| <= 4.8e-5 over 100-200 M, D(199.5 M) = -9.2e-6; V-1B
and V-1 separate only after t ~ 90 M (1e-6 at 133 M). The late drift of V-1 was the outer
boundary [VERIFIED at M/8 in vacuum]; for ES-1 and ES-1G the same cause is likely
[JUDGEMENT], not tested. Next: ES-1G and V-1G with the faces at +-384 M (`../HANDOFF.md`).
