# STATUS of C-sidm

gate:        G0 package complete for review (stage/G0/, 2026-11-19; decision 0016 item 4);
             G1 NOT MET (heat-conduction tests T6-T8 of C-pre-1 still running)
headline:    the collision operator passes every box test run so far, now also with the
             energy taken at each particle's metric and in a static curved metric (T12);
             first collisional King clusters collapse at Kn = 10 and 1, the contraction is
             not started by the release operator's energy defect, and whether CC2's
             collapse is physical or numerical (mesh) is open
last-result: wave-2b review (runs C-20261119-151502-cb831a8, C-20261119-151944-08f3220):
             box_rerun confirmed from its outputs (option absent byte-identical; T0b, T1,
             T2, T10 counts identical to the release; T12 rate = alpha0 psi0^6 x flat twin
             exactly, analytic within 1e-4); King-family fluid onset (Juttner Gamma_1)
             y0 = 0.32143 between CC2 (0.314) and CC1 (0.334); relative core contraction
             starts at 44-46 M (Kn = 10) when the defect has injected 1.3-1.6 percent of
             the binding margin; collisions-2 particle mode leaves +1.7-2.0e-21 of the
             canonical energy per collision (box_rerun runs C-20261119-141431-a351ac7 ...)
next:        1. decisive cluster runs D1 (coll_energy = particle at Kn = 10, seeds 1, 2,
                plus a cell-mode seed; ~1.5 card-h) once core states the collisions-2
                card executable usable and a card slot of the owner is free; then D2
                (finer mesh) and D3 (King y0 = 0.25-0.28) (stage/REVIEW-wave2.md sec. 7)
             2. review the heat package (T6-T8) from its artefacts when the helper ends;
                close G1 criterion C6
             3. G1 remainder: growth-rate fit fix validated on runs, G1 schematics and
                data-flow diagram, note G1 sections, a verifier of the G1 material
blockers:    collisions-2 card executable has FAIL lines in CARD_TESTS.log (core);
             two-card-job limit held by the heat helper's queued jobs (until they run)
needs:       core: card-tests-collisions-2, format-findings, adm-energy-diagnostic,
             refined-mesh-and-nonfinite-stop (outbox 20261119T1517*); orch: core share
             for a lead (outbox 20261119T15*__to-orch__lead-core-share)
offers:      collision tests and references: tracks/C-sidm/collide/ (SPEC, TESTS, 62
             reference tests); box-test drivers incl. coll_energy, T12 twin and King defect:
             tracks/C-sidm/box_tests/scripts/; static Einstein-Vlasov solver and samplers:
             tracks/C-sidm/equilibria/; F21/King pulsation onsets with Juttner Gamma_1:
             tracks/C-sidm/models/fluid_onset.py, stage/review_wave2/rv_king_onset.py;
             King and F21 b = 0.1 particle models at N = 1e4, 1e5
             (scratch/C-sidm/C-sidm-20261115-120610-b4592be, C-20261115-170742-84990ed);
             answer to F-hills on clump models (outbox 20261119T151728Z)
budget:      card-hours G1 0.01, G2 1.73 used + 1.84 reserved (heat card jobs), 41.4 left
             of 45 (decisions 0006, 0014); processors otherwise
