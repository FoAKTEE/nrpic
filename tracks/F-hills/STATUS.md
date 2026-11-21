# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met (stage/G1/STATUS.md, batch 4a):
             no complete Hills passage (P1's binary merged at m/8); KHSR; note compile; verifier
headline:    P1's early merger is a resolution effect of its m/8 members (the binary alone at
             m/8 decays like P1; at m/16 it holds its separation over 0-7.7 M). The passage P1b
             at m/16 waits for the m/16 and m/12 binaries to show the time it needs.
last-result: - lead review batch 4a (stage/REVIEW-wave3.md): binary_conv separations and analysis
               repeat exactly (F-20261121-155018-620fe7f, -155442-5f15a25); BUT three 1PN
               references of the binary differ by 0.019 M at 7.5 M and 0.158 M at 20 M
               (F-20261121-155353-e4d3354), so "m/16 follows EIH" fixes no convergence order
             - three-hole junk at P1's spheres: burst 0.4-0.6e-6 M, then a steady emission
               5.0-5.4e-8 M per M (window total 2.3-2.8e-6 M; F-20261121-155457-5f36517,
               -155549-4359678; junk_gauge J4b repeated within 8 percent)
             - Kerr part of F-pre-2: 2402.02178 reproduced in part in a static slicing (kerr;
               T8 and the analysis repeated exactly, F-20261121-155605-7d21f63, -155614-7997653);
               HRNA in Kerr-Schild slicing pumps moving binaries (RISKS R18)
             - P1 (F-20261119-150017-b45ec5f) ended at t = 280 M, 12.58 card-hours; finished
next:        1. When R16n segment 3 and R12 segment 2 have ended: binary_conv analysis, rule
                P1b-D (JOURNAL batch 4a), close both runs, cancel stray resubmissions; submit
                P1b if the rule holds
             2. KHSR with newton3 (processor minutes); p1 analysis to 280 M; note close-out
             3. Fresh G1 verifier; then nrpic-stage collect/verify/report F-hills G1
card jobs:   R16n F-20261121-130351-04074e1 segment 2 = Slurm 4807 (PD), then segment 3;
             R12 F-20261121-153707-1eaa5d4 = Slurm 4809 (PD), 2 segments. Read by binary_conv
             (README "Analysis") and rule P1b-D
announced:   P1b at m/16 (decision 0014): --gpu-hours 32 = 32 segments of 50 min, about 26.7
             card-hours, to 170-205 M; input binary_conv/inputs/p1b_R16n.athinput; submitted
             ONLY under rule P1b-D (G1 total then about 45 of 50)
blockers:    none outside the track (the queue: two F-hills jobs pending since 07:05/07:37 PST)
needs:       orch: a session to read R16n/R12 and apply P1b-D when they end (outbox batch 4a);
             awareness of kerr's digitized numbers (rule 9). core: chain stray resubmission;
             H-norm2 transient at t = 0.5 in R8; HRNA pair-force spec (T8 d); wave lmax input
offers:      own readers of trackers/horizons/history/waveforms and 1PN variants
             (stage/review_wave3/review4.py); tracker-keeping chain wrappers; MeshBlock tree model
             (g2mesh/scripts/tree3.py); Newton three-body (newton3), HRNA with static Kerr chart
             'bks' (kerr/hrna_bks.py), 1PN three-body (eih)
budget:      G1: about 15.1 card-hours used (P1 12.58 by sacct over 16 jobs, S2g 0.52, wave 2
             0.30, binary_conv 1.67) + 3.3 queued of 50 (0014); P1b would add about 26.7.
             G2: 0.05 (g2mesh) of 120 (0016). This session: 0 card-hours
