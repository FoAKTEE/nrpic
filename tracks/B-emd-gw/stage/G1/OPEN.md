# What G1 of B-emd-gw still lacks

State 2026-11-21, batch 4a (lead). Items 1-2 are owed before the lead would call the
package complete; 3-7 are open science and wording items that G1 records (none blocks a
criterion). Done since batch 2a: verifier_c18 (stage/G1/VERIFIER-C18.md); the waves README
wordings of verifier3 and the analysis of F2 and XS (waves round 1); the first_source README
wordings of verifier2, P12, P13, the (1 + eps^2) test and the run without a wave (round 3);
G_tot and the double-precision reader in gw_diag (old items 3-8). Core answered old items 9
and 10 in release core-v0.6 (Fourier Poisson solver with the spectral symbol, second moments
of particle groups; core messages of 2026-11-21 08:19Z and 08:53Z).

## Owed by the gate

1. C18, the rest of the ledger recomputed by an independent agent: ledger lines 34-36 (junk
   TT envelope and slope, 34 in part by the G0 verifier; omega_vir; card-hour estimates),
   49-63 (wave-1 pancake through shell crossing, run B-emd-gw-20261115-123852-ea4475c, and
   the homogeneous background, -115414-7ffbde1), 70-71 (independent quadrature of the
   ellipsoid energy, second-order lapse of a closed box), 124 (magnetic Weyl part across the
   two gauges), 199 (constraint residuals of the jittered data, recompute rather than read),
   217 (second-reading bookkeeping); and, not required but useful, P16'(v) and the per-shell
   fractions of round 3. One fresh package (verifier_c18b): processors only, artefacts only,
   report `stage/G1/VERIFIER-C18b.md`. Alternative: a ruling of the orchestrator that the
   wave-1 scouting rows 34-36 and 49-63 move to G2, where the pancake is run again
   (outbox 20261121T*__to-orch__c18-remaining-rows.md).
2. Note v3 wording (C17 stays PASS; these are corrections): ledger row 168 "forward
   combination"; row 101 maxima over the double-precision dumps (0.00882 over all dumps for
   eps = 1) with the driven-shift value 0.018; rows 118-119 define s and add the direct
   zero-shift-to-driven map; row 125 says that 5.48e-5 is the initial slice (evolved dumps
   3.8e-3 to 0.0408); row 197 quotes the floor as about 1e-12; the (1 + eps^2) sentence
   carries its range (0.6-3.6 per cent for a = 30-60 at delta = 0.0025; fails at a = 20);
   then `nrpic-stage report` again.

## Recorded at G1 (open, not blocking)

3. waves: the small-step spectral-Weyl vs TT residual of X (6e-11, spikes 2.8e-10 at t = 2 and
   6) is not explained; an x10 run of F2 at N = 64 would test the Gamma floor of F2-4.
4. first_source: whether the extra grid-scale TT that the wave adds by a = 12 is leakage of a
   wave-modulated noise field or a response (P16' cannot separate them); particle
   convergence at 128^3 (8 per cell not run, decision accepted by the lead).
5. N2 (embedded ellipsoid in a periodic box): core ran it with the group moments of
   core-v0.6 (+2.56, +1.09, +0.42, -0.14 per cent at 64^3-256^3 against the ODE crossing;
   the short axes sit 0.02 R_L below the ODE before the crossing at every resolution). The
   track's own check and the reading of that offset are G2 work.
6. The Newtonian mode's force error: the spectral symbol of core-v0.6 removes the (kh)^2/12
   of the seven-point Laplacian; new GR-Newton comparisons use it or quote the error.
7. G0 reservation still [TO VERIFY]: Omega today sigma^(7/2) (2403.15126:1074) against
   sigma^(5/2) from its eq. (result_OmZ); criterion 2 is judged on the emitted energy. The
   factor 3 between lines 324 and 581 of 2312.12499 waits for kb's claims package.
