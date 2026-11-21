# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met (stage/G1/STATUS.md, batch 5):
             no complete Hills passage yet (P1b running); KHSR; note compile; G1 verifier
headline:    The binary alone gives the same orbit at m/12 and m/16 (within 0.002 M to 21 M), so
             rule P1b-D held and P1b at m/16 is on the cards; but the converged pair shrinks by
             0.2 M in 20 M (RISKS R19), and its extension to 120 M decides whether P1b can work.
last-result: - analysis F-20261121-202021-3c4321e (figures read): Delta s(15) = 0.305 / 0.088 /
               0.0865 M at m/8 / m/12 / m/16; Delta s(20) = 0.577 / 0.197 / 0.196 M; member
               masses at m/16 drift -4e-5 to -6e-5 per M; rms H 6e-4 / 1.4e-4 / 4.5e-5
             - rule P1b-D: D1 holds (p = 12, continuum loss 0.086 M at 15 M); D2 (only without
               R12) would fail (0.196 > 0.10 M); its rationale (merger after 210 M) is refuted:
               stretch fit of R12/R16n to P1's shape gives a merger at 93-97 M
             - R16n (F-20261121-130351-04074e1) and R12 (F-20261121-153707-1eaa5d4) closed
               (completed, 3 + 2 segments, 4.18 card-hours)
             - digitized numbers of 2402.02178 out of git (decision 0023 item 4): copy at
               scratch/F-hills/kerr_2402/
card jobs:   A P1b m/16    F-20261121-203144-b2cf16b  Slurm 4832 (PD), 31 segments, tlim 200
             B R16n ext.   F-20261121-203156-03efdd3  Slurm 4836 (PD), 13 segments, 23.3->120 M
             C P1b m/12    F-20261121-203247-961801d  Slurm 4837 HELD; released by the sequencer
                           (pid in scratch/F-hills/seq/seq.pid) when B ends
             read by: binary_conv/scripts/analyze.py (HANDOFF "Reading the runs")
announced:   (decision 0014, all above eight card-hours) A 25.9 card-hours (G1), B 10.9 (G2),
             C 20.9 (G2); 57.7 in all, over days of queue time
next:        1. Later this week: read B (after about six segments, t ~ 70 M): minimum of s(t)
                or common horizon? Stop A and C if the isolated pair merges before P1b's
                pericentre (criterion: JOURNAL batch 5, run A)
             2. KHSR with newton3 (processor minutes); p1 analysis to 280 M; note close-out
             3. Fresh G1 verifier; then nrpic-stage collect/verify/report F-hills G1
blockers:    none outside the track (queue: about eight jobs of other owners ahead at 12:35 PST)
needs:       orch: an analysis session later this week to read B and apply the stop criterion
             (outbox 20261121T204354Z); harness: chain restart option (20261121T204401Z).
             core: chain stray resubmission (seen again: jobs 4820, 4822 ended at once);
             H-norm2 transient at t = 0.5 in R8; HRNA pair-force spec; wave lmax input
offers:      own readers of trackers/horizons/history/waveforms and 1PN variants
             (stage/review_wave3/review4.py); tracker-keeping and resume chain wrappers
             (binary_conv/scripts/athena_keep_trackers_bc.sh, athena_resume_bc.sh); a sequencer
             that holds a chain behind another (binary_conv/scripts/seq_release.sh)
budget:      G1: 18.42 used + 30.5 reserved (A) of 50. G2: 0.05 used + 37.4 reserved (B, C)
             of 50 (nrpic-run budget). This session: 0 card-hours run, 57.7 queued
