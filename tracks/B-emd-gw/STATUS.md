# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 HELD, NOT SIGNED (coord/GATES.md 2026-11-27,
             decision 0050): the convergence item C2 is met for the band strain only to a = 49;
             after that the gauges differ by 5, 20, 36 per cent at a = 64, 100, 132 and the
             particle-number leg exists only with zero shift. C2 reads FAIL in CHECKLIST.md.
             Signed only after a second review limited to C2, when (a) a gauge-invariant measure
             agrees between the gauges or (b) the particle leg converges in the driven gauge.
headline:    Condition (a) measured and NOT met by the proper-volume magnetic Weyl invariant: on
             the same slices (volume, <K>, <alpha> agree to 3e-4) the invariant ratios Gamma
             driver/zero shift at a = 100, 132 are median 0.936, 0.821, larger-lapse half 0.957,
             0.883, mean 0.837, 0.841 (B-20261128-040834-8e1587d). In amplitude far less than
             the band strain's 0.80, 0.64: most of the gauge dependence is coordinate, not all.
last-result: batch 39 (2026-11-27 19:31-20:45 PST): reader of the invariant tested on analytic
             waves under three coordinate maps (B-20261128-034232-f589717: invariant to 2e-5; my
             claim that the maps move the TT band by >10 per cent refuted); W1 holds, W2 fails, W4
             refuted (population/JOURNAL batch 39); figure population/figs/weyl_gauge.png looked
             at; gate review corrections made (C1 pancake row, C2 zero-shift leg, gauge ratio
             against a, stream-crossing cause open again, note Sec. VII, ladder, EVIDENCE,
             REPRODUCE); scope amended with dates (decision 0050 item 3); note v6 compiled.
running:     card: q0107 (128^3, eight per cell, Gamma driver; run B-20261128-034731-640f4f4,
             Slurm job 5585, pending at 20:12 PST; predictions G8a-G8c, population/JOURNAL
             2026-11-27 19:36). Processor: W5 mesh scale of the invariant, background run
             B-20261128-040950-1404d91 (256^3 Gamma driver, 3 cores, about an hour); initial data
             256^3 at eight per cell, B-20261128-030420-33ccdca (one core, about two days).
next:        1. when q0107 ends: nrpic-run finish, judge G8a-G8c (band strain 8/1 per cell in the
                driven gauge at a = 64, 100, 132; K1 guard and constraints), and run the Weyl
                statistics on it and on q0006's zero-shift member (8 per cell in both gauges)
             2. when B-20261128-040950-1404d91 ends: finish, judge W5 (mesh scale against the
                gauge difference); then outbox one line for the second review of C2
             3. G3 scope text (lapse leg, gauge-qualified late strain, eight per cell) before any
                production; the 256^3/8 ppc member after its initial data (I1-I4)
needs:       orch: the second review of C2 after q0107 and W5 are read (outbox 20261128T041156Z).
             core: parameters added at a restart (NEXT_SOURCE item 1).
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); population/scripts/
             weyl_gauge.py (proper-volume magnetic Weyl invariant, lapse split, quantiles, tested
             under coordinate maps); analyze_gr.py --equal-mass; compare_legs.py; pair_ratio.py;
             mem_fit.py; findings R25-R31
budget:      card-hours toward G2: 11.64 used before this batch, 28.36 left; q0107 adds about
             0.85 when it runs (none used in this session)
