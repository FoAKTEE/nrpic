# STATUS of E-stoch-inf

gate:        G0 PASS (signed 2026-11-20, coord/GATES.md). G1 in progress, NOT met and NOT complete
             for review: spectrum, freezing, convergence verified by a fresh verifier; strict A4
             fails (ruling on A4' asked of orch); note products (C8, C9, C13-C15) missing.
headline:    The slow-roll case of arXiv:2512.14649 runs in this AthenaK and passes A1-A3, A5-A7 up
             to 256^3 in two realisations; an independent verifier and the lead reproduce every
             number from the raw dumps; scalar-2 is now in release core-v0.4.
last-result: - Verifier (g1verify, own code): V1-V7 CONFIRMED (A2 1.21e-4 at 256^3, A3 3e-6, odd part
               of H order 5.5-5.96, A6 3.93-4.10, A7 bit-identical on the G1 executable); strict A4
               FAILS, A4' passes with (d) on maxima (stage/G1/VERIFIER.md; runs -030207-fb6f090,
               -031951-82984f8, -030522-c6907b6, -031251-c48670d).
             - Ladder wave 3: time-matched pairing (P256 odd/even 25, not 385); A6 at 64^3 3.82-4.03;
               L5 single kick: no hook defect (H factor 4.0000, projector term = reference to 1.2%);
               second seed of P256 passes (A2 2.12e-4) (E-20261121-025643-02526ff, -032828-fe18c5f).
             - Lead batch 2a: all 38136 numeric leaves of both packages' analyses rerun bit for bit
               (E-20261121-063551-7957a3d); own code confirms seed 2, the 385/25, records, A6 64^3, L5
               (E-20261121-063816-64ac0dc; one sub-prediction failed: K's max-norm order 3.52 at
               t = 0.98); release core-v0.4 = core/scalar-2 bit for bit at 32^3 on processors (E-20261121-064707-77ec326).
next:        1. Orch's ruling on A4' (outbox 20261121T064752Z); then C6 of the G1 checklist.
             2. Finish the cut package `note` (G1 schematics, one script per figure, G1 sections,
                ledger, checker --compile); then nrpic-stage verify/report G1 and call it complete.
             3. Resume `usr` and `window`: analyse the finished card jobs (E-20261120-222621-ba66218,
                -222424-0eb754b), close their manifests; P256 rerun on the release card build (0.5 h).
blockers:    G1: orchestrator (A4 ruling); the note package (needs a session). G2: none from core
             (scalar-2 released; scalar-3, con_signed and the USR example in candidate core-v0.5).
needs:       orch: a4-ruling-with-verifier, resume-cut-packages (outbox 2026-11-21); earlier
             a4-a5-rewording, g1-verifier (now done by the track's own helper). core: info only
             (scalar-checks-from-e, outbox 2026-11-21).
offers:      - SR ladder 32^3-256^3, two seeds, with verdicts: ladder/ (track/E-stoch-inf).
             - Independent verifier tools (reader, Philox, MS, R^NR, odd/even split): g1verify/scripts/.
             - Lead's check code: stage/G1/scripts/lead_check.py, stage/review3/scripts/.
             - Reproduction spec with errata: spec/SPEC.md; MS references: spec/ref/.
             - Stochastic delta-N solvers and reference statistics: langevin/ (to A-emd-pbh).
             - Noise validator A0-A15: noise/ (to core, C-sidm).
budget:      G1 1.96 of 10 card-hours used; G2 0.90 reserved by two finished jobs of cut packages
             (about 0.54 actually run); this session 0 card-hours (processors only).
