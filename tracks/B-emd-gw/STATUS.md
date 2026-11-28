# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 HELD, NOT SIGNED (coord/GATES.md 2026-11-27,
             decision 0050). C2 reads FAIL in stage/G2/CHECKLIST.md, now stated over the whole
             range (batch 40 addendum). A second review limited to C2 follows this session.
headline:    C2 as measured, band strain |k| <= 8 k_f of the halo box, a = 2.3-141: mesh
             (Gamma driver 256^3/128^3) within 2.8 per cent over the whole range; particle number
             (zero shift, 8/1 per cell) within 2e-3 to a = 132; gauge within 1.6 per cent only to
             a = 49 (0.950, 0.803, 0.643 at a = 64, 100, 132). Condition (a) not met (batch 39).
             Condition (b): q0107 ran and is closed; its band reading was still running.
last-result: batch 40 (2026-11-27 23:26 PST on): q0107 (B-20261128-034731-640f4f4) DONE, 0.774
             card-h, a = 141.7 with no guard stop: G8c and the guard part of G8b hold. Batch 39's
             W5 (B-20261128-040950-1404d91) is VOID: it took the 256^3 file index for t, and
             chain segments add dumps (headers: files 14, 18, 21 are t = 12, 15, 18).
             weyl_gauge.py splitx now picks every dump by its header time. First rows of W6: at
             a = 49 eight per cell leaves the gauge ratio of the Weyl invariant unchanged (I_B
             0.9022 against 0.9021; median 0.9973 against 0.9976).
running:     processor, registered, both started 07:41 UTC on a disk loaded by other owners
             (200-390 s per 128^3 dump, 13 s on an idle disk):
             B-20261128-074111-e2fcd72 analyze_gr on q0107 at t = 12, 14, 18, 21 (G8a, G8b);
             B-20261128-074116-363f95f weyl_gauge.py splitx (W5b, W6; 16 dumps of 128^3 and
             three of 256^3); initial data 256^3 at eight per cell B-20261128-030420-33ccdca
             (one core, 30-55 h). No card job of this owner is queued.
next:        1. when -074111-e2fcd72 ends: nrpic-run finish; judge_g8.py --gd8
                $S/B-20261128-074111-e2fcd72/analysis_gr_p8gd.json (registered), look at
                judge_g8.png; judge G8a, its corollary, G8b constraint part
             2. when -074116-363f95f ends: finish; judge_g8.py again with --weyl; judge W5b, W6
             3. G3 scope text: which gauge leg, the late strain with its measured gauge
                dependence as error or a <= 49 only; the 256^3/8 ppc member after its data
needs:       orch: the second review of C2 (outbox 20261128T075335Z); it can read G8a and W6
             from the two runs above when they end (HANDOFF.md says how).
             core: parameters added at a restart (NEXT_SOURCE item 1).
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); weyl_gauge.py (magnetic
             Weyl invariant, lapse split, quantiles; splitx picks dumps by header time);
             judge_g8.py; analyze_gr.py --equal-mass; compare_legs.py; findings R25-R32
budget:      card-hours toward G2: 12.42 used (11.64 + 0.774 for q0107), 27.58 left; none queued
