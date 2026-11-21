# STATUS of B-emd-gw

gate:        G0 PASS (signed 2026-11-19, tag stage/B-emd-gw/G0-pass-20261119). G1 package
             complete for the independent review in the lead's judgement (batch 5): criteria 1
             and 2 met, 3 struck (0013), C18 PASS after verifier_c18b, note v3 corrections made;
             verify FAILs only on four G2 runs in flight (STAGE_REPORT.md, lead's assessment)
headline:    Both GW diagnostics recover oblique flat waves and a tensor mode of the expanding
             matter-era box with the errors the code's stencils predict; the first source follows
             its second-order strain and converges before shell crossing; every ledger number is
             now recomputed by an agent that did not produce it
last-result: lead batch 5: verifier_c18b checked from the artefacts (line 59: 0.00751 and
             0.00254 over all records, the printed values are the five-dump maxima; run
             B-20261121-203426-ea1e945); ledger rows 34, 56, 59, 63, 101, 118, 125, 168, 197
             reworded and a (1 + eps^2) row added (ledger run B-20261121-203254-928275f);
             shear smoke run met (Delta = -6.3e-5 at S1, N_y = 32; B-20261121-202359-d12511c)
running:     card: flrw_conv J3 = B-20261121-202335-3e6a898 (Slurm 4825 running since 12:44,
             chain, 128^3 to a = 1001, v0.3 exe). Done: J2 = B-20261121-202304-dc3020e (0.35
             card-h, exit 0, closed); shear series 1 = -202830-417af0c (closed, 26 of 27 cases
             ran; the f = 1 lapse leg stopped). processors: population initial data sigma1 =
             0.028 = B-20261121-202946-ec4a156 (outer iteration 9 at 12:56). The sequencer (pid
             in scratch/B-emd-gw/sequencer/pid) then submits the population GR chains
next:        1. analyse flrw_conv J1, P1, J2, J3 against PF1-PF6, PB1-PB5 (G2 criterion a)
             2. shear: summary script (Richardson per case, figures), outcomes P4-P12; the f = 1
                lapse leg stopped at t = 0.578 (guard, non-finite Khat): find the cause
             3. population: read the first full-GR box (predictions G1-G4 of its journal)
blockers:    none for G1; G2 legs wait on their runs
needs:       orch: independent review of G1 (outbox 20261121T*__to-orch__g1-package-complete);
             core: insitu-fourier-modes (accepted as W18, no branch; needed for 256^3 science
             runs); kb: claim-2312-12499-delta-factor (waits for kb's claims package)
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio single and double
             precision; gauge G_tot); waves/wlib (exact oblique flat wave and matter-era tensor
             mode); first_source tools; cards/sequencer.py (a queue that keeps at most two card
             jobs of an owner eligible and closes ended runs); all on track/B-emd-gw
budget:      card-hours 2.51 of 40 before this session; this session 0.35 (J2) so far;
             queued about 4 more against G2 (J3 2.4-3.1, population 0.2-0.6 each, two
             amplitudes); announced here, below the 8 card-h note of decision 0014
