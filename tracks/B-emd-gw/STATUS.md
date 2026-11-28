# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2: package complete for the independent gate
             review in the lead's judgement (batch 37; stage/G2/OPEN.md): 20 of 20 items PASS or
             NA; C18 PASS (fresh verifier, stage/G2/VERIFIER.md, coverage as it states); C2 PASS
             for the band strain in mesh and particle number, gauge leg recorded as an identified
             gauge dependence, halo catalogue at one particle per cell FAILED on record. Not signed.
headline:    In the Gamma-driver gauge the band strain |k| <= 8 k_f of the population box is the
             same on 128^3 and 256^3 to 1.1 per cent up to a = 64 and 2.8 per cent up to a = 132
             (B-20261127-232236-7ab7aa2; reproduced by the verifier), and at a fixed eight
             particles per cell the late constraint means fall 1.6-2.3 times (H) and 1.7-2.2 times
             (M, from a = 49) when the spacing halves, against 1.05-1.41 at one per cell
             (B-20261128-030556-5ef9294).
last-result: batch 37 (2026-11-27 18:56-19:40 PST): verifier's findings a-e answered (note v5,
             run_all B-20261128-030805-78634c0; pairing analysis B-20261128-030556-5ef9294; SPEC
             item 5 amended); the 256^3 member at eight per cell fits one card: 42-46 GiB of 80
             (bound 76), about 12 card-h (8-16) (B-20261128-030350-19295a4; E1 holds, E2's 4-7
             card-h refuted); its initial data started.
running:     processor, detached: initial data 256^3 at eight per cell, B-20261128-030420-33ccdca
             (one core, 30-55 h expected, log scratch/B-emd-gw/B-20261128-030420-33ccdca/run.log;
             close with nrpic-run finish). Stage verify of this batch: see HANDOFF.
cards:       nothing queued. The 256^3/8 ppc member is queued (priority 2, chain, release build)
             by the session that checks its initial data (I1-I4).
next:        1. when B-20261128-030420-33ccdca ends: finish, check I1-I4 (meta.json against the
                128^3 data's), then nrpic-queue add the 256^3/8 ppc member (q0060's options,
                new files; HANDOFF has the command)
             2. G2 gate review (orchestrator); answer its findings
             3. G3 scope: population runs at eight particles per cell in the Gamma-driver gauge,
                strain read in that gauge, halo catalogue only at fixed particles per cell
needs:       orch: gate review of G2; answer on the 128^3/8 ppc Gamma-driver partner (outbox
             20261128, request g2-p8-gamma-driver-partner-128).
             core: parameters added at a restart (NEXT_SOURCE item 1).
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); analyze_gr.py --equal-mass;
             compare_legs.py --halo-base; judge_c3.py and pair_ratio.py (constraint histories of
             a mesh pair under several pairings); mem_fit.py (card memory and card time from
             the job logs and restart intervals); shear/scripts/crossing.py; findings R25-R30
budget:      card-hours toward G2: 11.64 used, 28.36 left (nrpic-run budget); none this session
