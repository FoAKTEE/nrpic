# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met (stage/G1, batch 11): the
             complete vacuum passage (C8: continuation A2 on the cards) and the G1 verifier (C18)
headline:    The isolated m/16 binary does not merge: it turns at 3.12 M at t = 73.9 M and opens
             again (eccentric start), so the passage P1b can test the Hills mechanism; P1b reached
             61.8 M with its members unmerged before preemptions cut it; it continues as A2.
last-result: - analysis F-20261124-130009-33bef4d (figures read): binary alone at m/16 (R16n + B)
               s = 4.952 -> 3.120 M (t = 73.9) -> 4.585 M (107.85); no common horizon; masses
               -1e-5 to -5.5e-5 per M. P1b m/16 (A): s = 2.74 M at 61.86 M, A1 A2 A4 A5 met;
               A - B = -0.53 M at 60 M. P1b m/12 (C) = A within 0.0023 M to 22 M; C's masses
               drift 1.2-1.7e-4 per M (A4 fails for C)
             - N1/N1m F-20261124-132934-375a163: Newtonian tide plus the members' 1.5 percent
               heavier horizon masses in M's conformal factor give A - B's size at 40-60 M, not
               its early part; no cause named (RISKS R21)
             - KHSR reproduced (khsr_note); lead's rerun identical (1268 values,
               F-20261124-133112-db7d6b8); K1, K2 rederived by hand; risk R14 retired
             - note v2 (24 pages) carried into note/ (figure run F-20261121-214141-256f945)
             - A, B, C closed as stopped (preempted: restart interval 5 M, no restart on
               SIGTERM; RISKS R20); 25.31 card-hours used by them (A 11.77, B 9.28, C 4.26)
card jobs:   A2 P1b m/16  F-20261124-141118-fbc6419  Slurm 5172 (PD), 61.8 -> 200 M, G1 19.5 h
             B2 alone m/16 F-20261124-135408-1e6db58 Slurm 5171 (PD), 107.85 -> 140 M, G2 5 h
             C2 P1b m/12  F-20261124-141842-d5263e9  Slurm 5173 HELD until B2 ends, 20 -> 200 M,
                          G2 24 h
             sequencer seq_b11.sh pid 604718 (scratch/F-hills/seq/seq_b11.log): holds C2,
             continues a chain cut by its segment cap within its registered card-hours
             read by: stage/review_wave3/b11_cards.py (joins A+A2, R16n+B+B2, C+C2)
announced:   (decision 0014) A2 19.5 card-hours (G1), C2 24 (G2); B2 5 (G2)
next:        1. When A2 passes ~130 M: run b11_cards.py (registered), judge A2-1 to A2-5;
                when B2 ends, its apocentre against the Peters prediction
             2. A2 to the separation (>= 170 M), then a fresh G1 verifier (OPEN.md item 2)
             3. Note v3 with the passage; junk at P1b's spheres (T3 reservation)
blockers:    another user's priority jobs preempt the cards for whole nights (R20); G1 has
             0.3 card-hours left beyond A2 (request to orch)
needs:       orch: allotment for A2's tail, chain cap by card time (outbox 20261124T135319Z);
             core: restart on SIGTERM (outbox 20261124T135319Z); earlier: HRNA pair-force spec,
             wave extraction beyond l = 8, H-norm2 transient in R8
offers:      readers of trackers/horizons/history/waveforms (nr_first/scripts/nrread.py), the
             card reader b11_cards.py, the Newtonian tide/mass-offset reference b11_n1_tide.py;
             chain wrappers athena_keep_trackers_bc.sh, athena_resume_bc.sh; sequencer
             seq_b11.sh (hold-behind and in-place continuation within a card-hour ceiling)
budget:      G1: 30.19 used + 18.68 reserved (A2) of 50, 1.13 left. G2: 4.31 used + 41.30
             reserved (B at its ceiling until its finish lands, B2, C2), 4.39 left (nrpic-run
             budget, 06:25 PST). This session: 0 card-hours run; 48.5 registered (A2, B2, C2)
