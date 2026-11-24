# After 2026-11-21: what runs unattended, and the analysis round (batch 10)

State on 2026-11-21 15:40 PST. Batches 3 to 9 of wave 3 ran today (run ids in
`scratch/orch/batch<N>_result.json`; specs in `harness/workflows/batch-<N>.json`).
Gates signed today: G1 of A, B, C, D and E; KB-G0 and KB-G2. Release core-v0.6 is on main.

Unattended until the analysis round: the card chains of decision 0026 item 1 (about 190
card-hours asked, about half expected), each owner with a sequencer under
`scratch/<ID>/`; Track A's corrected periodic job is in its queue (decision 0027 item 2).

Usage of the account: weekly window 82 per cent at 15:38 PST; reset Friday 2026-11-27
15:00 PST; pause flag at 95 per cent. A session on Opus costs about half a per cent per
hour, a source session on Fable about three.

The analysis round is prepared as `harness/workflows/batch-10.json` (seven sessions on
Opus, about five per cent): leads of tracks A to F and one session of core read the runs
with the commands of their HANDOFF.md, judge them against the predictions written before
the runs, queue what follows, and bring the stage packages of the next gates up to date.
To start it from the main checkout:

    python3 scratch/orch/make_batch.py harness/workflows/batch-10.json scratch/orch/nrpic-batch-10.js
    (then the Workflow tool with that script; `harness/bin/nrpic-usage watch` beside it)

It is due when most chains have ended (`squeue -u $USER`; expected Monday evening or
Tuesday 2026-11-24). After the reset of the weekly window: source work of core on Fable
(release v0.7: the mitigation of the relaxed lapse, a step limit that counts the gauge
speeds, boosted clumps, the oblate component; then the cure of the relaxed lapse), the
requests to the harness (decision 0026 item 7), the G2 verifiers of the tracks and the
G1 verifier of Track F.
