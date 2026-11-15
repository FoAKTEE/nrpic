# What G0 of B-emd-gw still lacks

State 2026-11-15, end of wave 2 (lead). Items 1-5 are the gate's own items; 6-16 are open
questions that G0 records and later gates close. Delivered items stay listed with where.

## Owed by the gate itself (charter 9.2, brief 13.3-13.4; CHECKLIST.md items)

1. Working note v0 (C5, C17): DELIVERED, `note/main.pdf` (10 pages; run
   B-20261115-165556-a399d4e). Not yet run: step 4 of the new-paper procedure (reviewer
   agents), which helper sessions cannot start (outbox to orch of the note helper's request).
2. Schematics (C6, C7, C10, C11, C16): DELIVERED, `note/figures/schem_*.png`.
3. Independent verifier (C18): DELIVERED as `stage/G0/VERIFIER.md`; the harness looks for
   `VERIFIER_REPORT.md` (request to orch to accept the name).
4. `nrpic-stage verify` on the committed tip: run in wave 2; its `runs` check fails on
   wave-1 hand-written manifests without code, env and input fields and on run
   B-20261115-164157-40b9f6d, whose outputs were moved into its directory after `finish`
   (`VERIFY_RESULTS.md`). These cannot be repaired without rewriting the record; request to
   orch to rule on them.
5. Knowledge base (C2): the track's statements are claims 171-228 and 619-625 of snapshot
   kb-20261115-44b7406, locators resolved by kb; the seven key references not read in wave 1
   are read at abstract level (EVIDENCE.md, wave-2 section), not yet claims in the kb.

## Scientific items open at G0 (closed at G1-G3)

6. GR reference solution of the plane-symmetric pancake (planar Szekeres class; Track A owns
   the general solution, B the planar reduction and the GW null, A's reply of 18:37Z)
   [TO VERIFY].
7. The gauge-safe pre-shell-crossing reference: CLOSED at second order. The verifier's
   derivation (VERIFIER.md C5: zero shift and Newtonian first-order slicing make the
   second-order TT strain the same as in Poisson gauge) and the measured spatial-gauge piece
   G_tot below 1.1 percent of c_+ for a <= 20 (first_source P5, run
   B-20261115-174722-ba1048d, -180834-c77a132), confirmed by a second spatial gauge (P6,
   rechecked by the lead in run B-20261115-190007-e09a0d2). The slicing piece is bounded by a
   scaling estimate only (P10). Beyond a ~ 20 the gauge piece reaches 10 percent near shell
   crossing: G_tot is reported with every strain.
8. The noise floor after shell crossing: the jittered-lattice null run (jitter option on
   core/requests-b, `problems/cosmo/make_waves.py --jitter`); not run.
9. The late rise of h^TT in the wave-1 cosmology dumps: CLOSED as a question of gauge. It is
   not the second-order spatial-gauge piece (a tenth of the rise, at low k; runs
   B-20261115-164616-a6d9477, -171804-42e975b) and not the slicing (P9, P10); 93-97 percent of
   it lies at |k|L/2pi >= 20 and depends on the deposit there (rechecked, run
   B-20261115-190019-b5f5eb6): unresolved small-scale structure or noise, quasi-static. Open
   part: the resolved band below 20 also grows (deposit-independent), which needs the run
   at 256^3 or more particles to settle.
10. Covariant (York) TT decomposition: not implemented.
11. The literature box comparison of S2: 2212.00425 and 2312.12499 read at abstract level
    only (EVIDENCE.md); their spectra not yet extracted.
12. Baseline discrepancies: the Omega prefactor of 2403.15126 line 1501 missed by 144-392; the
    verifier finds the factor varies as theta^(2/3), i.e. with where the emission redshift is
    taken, and Omega today scales as sigma^(5/2) with the paper's own eq. (result_OmZ) (z_e at
    t_col, line 1061) against the stated sigma^(7/2) (line 1074) [TO VERIFY]; the track uses
    7/2 for the emitted energy only (SCOPE.md section 1).
13. Oblique linear-wave test: generator fixed by core on core/requests-b (not on main);
    the track's own oblique and expanding-box tests are owed (G1). Gauge wave to 1000
    crossings and the robust-stability test per gauge: not run.
14. FLRW and growth rows: particle-number convergence in the production configuration,
    growth rate f(a), a glass or Poisson start (VERIFY.md section 7).
15. Multi-code row (0013): shearing dust of arXiv:2003.08014 and GR against the Newtonian mode
    of the code; not run.
16. Thin periodic boxes: confirmed by core (256 x 256 x 16, through shell crossing equal to the
    cube to 3e-10; core message 20261115T1620Z); not yet used by the track.
