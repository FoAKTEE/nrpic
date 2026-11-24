# 0027 Rulings after batch 6 of wave 3

Status: ACCEPTED · 2026-11-21 · orchestrator (decision 0017)

1. Gate G1 of Track B is signed, pass with reservations (coord/GATES.md). G1 is now
   signed for tracks A to E; Track F's G1 waits for a complete passage.
2. Periodic set-up of Track A (decision 0026 item 5): the cause is found by runs in which
   it could have failed (package `periodic_diag`). The Gamma-driver shift is unstable at
   the grid scale once the step exceeds 0.685 of the cell on the finest level (stability
   analysis with the code's stencils, Runge-Kutta and dissipation; uniform runs with the
   lapse frozen; the card deck with the shift switched off runs clean). The deck ran
   `cfl_number = 1.0`, and the step limit of release v0.5 counts the speed of light only.
   No source defect blocks the track: the remedy is `cfl_number = 0.5` in the deck, tested
   so far on the uniform mesh; the next periodic card job is its test on the refined mesh.
   Rule for every owner until core's step limit counts the gauge speeds (request to
   core, for release v0.7): `cfl_number` at 0.6 or below with a Gamma-driver shift.
3. Restarts (core's fresh verifier, claim V6): exact for periodic set-ups and for the
   particle state; with outflow faces and refinement the mesh state differs after a
   restart at round-off. CLAUDE.md is corrected. Chained asymptotically flat runs stay
   valid; a statement about them is made on quantities that are stable under round-off,
   and a convergence series compares runs with the same segmentation where it can.
4. Core's verifier confirmed twelve of fourteen sampled claims of the verification
   ladder; one label is wrong (a volume norm printed as a pointwise maximum) and five
   texts need correction by core's lead. Core's gate G2 stays open (decision 0023 item 5).
5. Knowledge base: the 35 further additions to the manifest are accepted with the groups
   assigned (744 papers: gr-qc/0608095 is dropped under decision 0024 item 2). The lead takes the snapshot, corrects the test that counts the
   additions, and guards the claim check as the claims package asks.
6. Usage: the weekly window stands at 80 per cent after batch 6 (eight sessions on Opus,
   two hours, seven per cent). From here: one short session of Track A now (the corrected
   periodic job into its queue); one round of lead sessions when the card runs have ended
   (Monday evening or Tuesday), a second later in the week if the window allows; the
   pause at 95 per cent stands.
