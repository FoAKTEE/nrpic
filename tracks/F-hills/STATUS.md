# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1: package complete for an independent
             review in the lead's judgement (batch 34; not passed by the lead): C8 met; C18
             PARTIAL until the fresh verifier reruns its readers on the completed passage
headline:    The m/16 Hills passage P1b (A + A2) is complete to 186.0 M: the binary is disrupted
             between 120 and 133 M, m1 is captured by the heavy hole (common horizon from 137.5 M,
             area mass 1.0053 -> 1.1137), m2 keeps its horizon and recedes after an 8.73-M
             pericentre on a marginal orbit. Newton from the same deck ejects m1 and binds m2.
last-result: - horizons from the status files 133-186 M (F-20261127-232657-163727d,
               fig_b34_horizons, fig_b34_f1 read): finder 2 found at every search; m1's own
               horizon to about 141 M; finder 0's later "found" surfaces are not horizons
               (|mean expansion| up to 24: question to core); m2's mass 0.12954 within 6.4e-4
             - A2 state to 186.0 M (F-20261127-232849-14345be): no gap, overlaps <= 1.25e-9 M,
               waveforms to 186 M, rms H <= 6.19e-5, MeshBlocks <= 2584, memory peak 78789 MiB
             - passage vs Newton (F-20261127-232940-3f652bf): Newton m1 out (39.4 M at 186 M),
               m2 bound (5.78-M pericentre); NR m2 at 17.5 M, energy +0.12 (pre-merger M) or
               about -0.04 units (remnant): fate undecided; coordinate energies (R6)
             - F1 decided in part: the status file cannot separate the heavy hole's branches (both
               found, equal mean expansion; median 6 flow iterations); test = polished searches on
               A2's restart files (G2 list)
             - failed predictions: A2-3, A2-4, D34-1; parts of C25-1, C25-3, D34-2 (JOURNAL b34)
             - A2 and C2 ended by a Slurm submission I/O error (04:17 PST 2026-11-27); B2 DONE
decision:    judge C8 met; G1 package handed to orch for the verifier rerun and review
card jobs:   none queued or running. Closed this session (nrpic-run finish, checksum passes
             started in the background): A2 F-20261124-210400-902c650 (stopped, 186.0 M),
             B2 F-20261126-052133-10f9a5f (DONE, 140 M), C2 F-20261126-131751-89eaff8
             (stopped, 106.69 M; G2; continue from rst/hills.00072.rst)
next:        1. G1 verifier rerun on the completed passage (stage/G1/OPEN.md item 2), then the
                independent review; answer its findings
             2. F1 test: polished finder searches on 2-3 of A2's restart files (87-133 M), after
                core's answer on reading core-v0.5 restarts with core-v0.8 (outbox b34)
             3. Note v3: the passage to 186 M (horizons vs coordinates, reverse fates), HRNA and
                EIH overlays of P1b, the junk at P1b's spheres; then G2: C2's continuation, B2
readers:     `stage/review_wave3/b34_horizons.py` reads the status files (rows end with "# words")
blockers:    none for G1; the cards are shared (R20); Slurm submission I/O errors (once)
needs:       orch: retention of A2's 724 GB of restart files (outbox b34); core: finder
             found flag and v0.5 restarts (outbox b34)
offers:      continue_chain.sh, nrread.py, b21_a2_state.py, b11_passage.py, b34_horizons.py
budget:      A2 19.70 card-hours in all (11.15 + 8.55 of the continuation; A2's 19.5 plus 0.2
             within G1's 19.8); B2 3.52, C2 9.37 (G2); this session 0 card-hours (processors only)
