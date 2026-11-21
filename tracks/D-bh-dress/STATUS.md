# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20, stage/D-bh-dress/G0-pass-20261120). G1 NOT met and not
             complete for review: C7 (D-pre-3 profile criterion; ruling d-pre-3-criterion at orch
             since 2026-11-15) and C16 (working note v1 not compiled) open; C9 (schematic) and C17
             (fresh verifier, stage/G1/VERIFIER.md) met in wave 3 (stage/G1/STATUS.md, OPEN.md)
headline:    The late horizon-mass drift of the Einstein-Straus vacuum control was the outer boundary:
             with the faces at +-384 M (V-1B) the drift stays within 4.8e-5 over 100-200 M at M/8
             (was -1.37e-4). core's lapse_leak slices the expanding dust on its exact curve (ES-1G,
             wall within 1.7e-4) but the hole shrinks to 0.78 M and its mass grows by 7e-3 while the
             exterior mass leaks through the +-192 M faces; that run with the faces moved is next.
last-result: V-1B D-20261120-222625-63abd72 (0.778 card-hours): drift [-4.8e-5, +2.0e-5], D(199.5 M)
             = -9.2e-6; ES-1G D-20261119-142633-6f72922 judged (es_runs entry 9: G1, G3-G5, G7 held;
             G2 failed; G6, J5, K1, K2 refuted); fresh verifier of G1 (verifier_g1, 10 runs): no ledger
             row WRONG, dress at a/a_i = 2 WRONG as worded (corrected); lead recheck Z1-Z5 held
             (D-20261121-063617-3f2036f; stage/REVIEW-wave3.md); ES-F construction confirmed by a
             second agent (D-20261120-222651-3180e07)
next:        1. Card (two jobs at most): ES-1GB = es_runs/inputs/es1g_dx8 with the root level of
                drift_controls/inputs/v1b_bnd384 (faces at +-384 M), prediction first (~0.95 card-h);
                then V-1GB (V-1B with lapse_leak); then ES-F as pre-registered (flux_tools entry 7)
             2. Processors: secondary_infall's run to a/a_i = 30 (192^3 isolated box, 0.4-0.8 h on six
                threads) and its analysis with R8; drift_controls' Pb3-Pb4 on V-1B and its README
             3. Note v1: P11 outcome, compile, check_manuscript --compile, read pages, the verifier's
                wording corrections (closes C16); then G1 is complete if orch rules on C7
blockers:    orch: ruling d-pre-3-criterion (third request 2026-11-21); core: a lapse-excision criterion
             not resting on alpha_exc (R14), the faces option benchmarked on V-1 (R13)
needs:       orch: d-pre-3-criterion-third, g1-numbers-errata-reminder; core: boundary-benchmark-v1b,
             es1g-outcome-for-gauge-ready, lapse-excision-criterion, particle-energy-and-crossing-record,
             finder-summary-outdir, trajmet-format-doc, newton-selfforce-doc, spike-mass-refinement,
             accretion-diagnostics item 3, newtonian-mode-point-mass (all in outbox/)
offers:      boundary benchmark of the Painleve-Gullstrand exterior: V-1 (faces +-192 M) against V-1B
             (+-384 M), inputs es_runs/inputs/v1_dx8.athinput, drift_controls/inputs/v1b_bnd384.athinput,
             outputs of the two runs; ES-1G as the long lapse_leak test with dust; ES-F data (bubble
             filled with dust, exact LTB growth law, flux_tools/esf_data.py, data run
             D-20261119-145022-2208a19); Einstein-Straus data and exact references
             (es_runs/make_data.py); Kerr spike reference (spike/kerr_lib.py); Newtonian-mode infall
             references (secondary_infall/nm_shells.py)
budget:      5.19 card-hours used (G1 4.41, G2 0.78), nothing reserved, 29.22 left toward G2 (30 per
             gate, decision 0014); no job queued (nrpic-run budget, 2026-11-21)
