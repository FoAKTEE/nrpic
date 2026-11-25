# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-24; coord/GATES.md, decision 0038). U-A4'(a) stays FAILED as
             written. G3: scope SCOPE 4d amended by 4d.9 (A1-A13, batch 19) before any production
             run; card runs queued; no G3 result yet (stage/G3/OPEN.md).
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf (32 pages).
last-result: Lead batch 19 (2026-11-25 07:04-08:00 PST):
             - Scope review (g3/scope_review) checked from its artefacts: B1 CONFIRMED by own code
               (variant/lattice 0.97786 as binned, 1.00002 fixed; E-20261125-151230-a4f4059), B2
               CONFIRMED by own arithmetic (E-20261125-151429-83a040c), B3 CONFIRMED from the
               formulas (zeta = -R^NR at first order). ref_spec.py fixed; corrected 128-band pilot
               passes the variance gate 0.9993 +- 0.0032 (E-20261125-151340-743c38c).
             - SCOPE 4d.9: variance and tail shape judged apart; reader tests Z0-Z2; reference state
               at N_f; mirrored pairs; >= 4 judged dumps for G3-C; Richardson model test; nu = 4 only
               with a 2 per cent importance-sampled reference; seeds with reference size; gauge leg
               withdrawn (decision 0040), limitation stated. Predictions g3/JOURNAL.md entry 4.
             - Floor (R28) CLOSED: FL256h halves the floor at 256^3 (1.997, 2.000, no sign flip;
               E-20261125-151222-d5a5f2f); note sentences updated (no new number).
             - Reference state at N_f implemented (A4); smoke run E-20261125-152619-d917a14: phi at
               N_f already skewed by 0.023 (2e4) [TO VERIFY at 4e6; R35].
             - Failed: prediction LB2 in part; run E-20261125-152419-40200ec (figure code), fixed.
card plan:   q0050 G3P (pilot, re-entry of q0045, priority 2); q0051 G3C, q0052 G3R (priority 2);
             q0053 G3B00, q0054 G3B01 (baseline pairs 0-18, priority 5, after G3P).
runs pending: E-20261125-152832-c301e92 (processors, 4e6 reference, background; read and finish it);
             q0050-q0054 (cards; readers: g3 reader to write, judge_q-type three-amplitude reader).
next:        1. Finish and read the 4e6 run (gate, skewness, state at N_f: R35); importance sampler
                at nu = 4 (A9).
             2. zeta reader with Z0-Z2 on processors (32^3, build_cpu_v07).
             3. Read the pilot when it runs: cost per run into 4d.9 A12, then the rest of the
                baseline (98 pairs) and level 2 (16 pairs).
blockers:    none (cards held by another partition: R37).
needs:       core: a field-dependent lapse condition, for later (outbox 2026-11-25), not for G3.
             orch: nothing blocking; info post on the amended scope.
offers:      - repro/: reproduction of both papers (scripts, readers, ledger, verifiers).
             - g2prod/, floor/: release ladder and judges; half-amplitude reader.
             - langevin/: stochastic delta-N statistics with the corrected lattice factor
               (results/ref_inflection_n32_binfix.json; 4e6 file to come) (to A).
budget:      G2 allotment closed at 19.6 card-hours of 30 (+0.44 FL256h, a G2-gate run). G3
             allotment 60: 0 card-hours used; queued at most 0.95 + 0.6 + 0.6 + 0.95 + 0.95.
             This session: processors only, at most 4 cores.
