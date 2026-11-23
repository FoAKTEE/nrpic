# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package started (batch 10a): C4, C7, C12, C19,
             C20 PASS, C8 NA (0013), the rest OPEN (stage/G2/OPEN.md). G2 not met.
headline:    The particle FLRW run in full GR reaches the sub-percent level and converges in mesh
             (16-128 cells) and particle number (1-27 per cell): growth-rate error 5e-6 at most,
             its plateau 2.8e-8 at 128 cells; floor 2e-6 in the amplitude from the start step
last-result: batch 10a (lead, 2026-11-22): flrw_conv closed with the 128-cell member
             (J3 B-20261121-202335-3e6a898, analysis B-20261123-015452-18d2956): G2 criterion (a)
             met; shear series 1 judged (B-20261123-015919-dec4392): S1-S4 within 1e-5 of linear
             after extrapolation, M1 and L1 inside the paper's bounds, M2 opposite sign to the
             prediction, L2 and the f = 1 leg without result; population: the GR run had never
             been submitted (sequencer waited silently on unconverged 0.028 data, queue in file
             order); corrected, pop_s014_gr on the cards
running:     card: pop_s014_gr = B-20261123-014847-f295ab4 (Slurm 4921, chain, v0.6, 128^3 L = 8
             to a = 143); J4 = B-20261123-015905-7a30278 (Slurm 4922, batch, v0.3, 128-cell step
             test). processors: re-solve of the 0.028 data = B-20261123-014850-7b7d986 (36 outer
             iterations, 2 cores, about 75 min). Behind them in the queue: pop_s028_gr. Sequencer
             pid 2942856 (scratch/B-emd-gw/sequencer/), restarted 17:54 with 'waiting:' log lines.
             stage verify G1 in the background (pid 2996426, log scratch/B-emd-gw/tmp/
             verify_G1_20261122.log); G2 verify stopped (contention), to rerun
next:        1. read pop_s014_gr when it ends: predictions G1-G4 (population/JOURNAL.md), halo
                finder, TT strain from the double dumps, against Newtonian fidL8 and DESIGN.md
             2. read J4 against J4a-c (flrw_conv entry 13); R1-R3 of the 0.028 re-solve
             3. shear: L2 fan (NaN arrival), the f = 1 guard stop, S3 at N_y = 256 (processors)
blockers:    none; G2 needs the population comparison, shear L2, a gauge leg, package products
needs:       orch: nothing to decide (outbox population-run-on-the-cards, info). core:
             insitu-fourier-modes (W18, accepted, no branch; needed for 256^3 runs). kb: claim
             861 recorded (2312.12499 factor 3), used as [TO VERIFY]
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio; gauge G_tot); waves/wlib;
             first_source tools; flrw_conv analysis (analyze_f/b/step); shear summary script;
             cards/sequencer.py (queue with 'waiting:' log lines)
budget:      card-hours toward G2: 2.68 used (J2 0.35, J3 2.00, rest earlier), 3.95 reserved
             (pop_s014_gr ceiling 3, J4 1); G1 1.69; allotment 40 (0014)
