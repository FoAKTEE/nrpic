# Batches 3, 4a and 4b of wave 3 (2026-11-21)

Batch 3 (04:52 to 07:43 PST, run wf_16ad2a5e-18f): sixteen sessions, all returned.
Release core-v0.6 merged, tagged and built. Gates KB-G0 and KB-G2 signed. Rulings:
decision 0022.

Batch 4a (07:50 to 08:47 PST, run wf_44088022-3dd): seven sessions, all returned.
Gate G1 of Track E signed. Tracks C and D call their G1 packages complete. Core closed
release v0.6 (card check PASS, job 4800; release processor build identical with the
candidate, 75 of 75) and brought its G2 package up to date (not met: ten of eighteen
items). Rulings: decision 0023.

Batch 4b (from 08:52 PST, run wf_a71b9fca-d0a, spec `harness/workflows/batch-4b.json`):

| Owner | Session |
|---|---|
| C-sidm | independent review of gate G1 |
| D-bh-dress | independent review of gate G1 |
| B-emd-gw | second verifier for item C18 of G1 (rows the first left without an independent value) |
| core | the relaxed-lapse defect (decision 0022 item 3), in the spare worktree `wt/core-s1`, branch `core/gauge-2` |

Usage of the account: weekly window 58 per cent at 08:48 PST after about 58 sessions since
its reset (0.9 to 1.1 per cent a session). After batch 4b about 62 per cent.

Card runs queued or running, to be read by later sessions:

| Owner | Run | What |
|---|---|---|
| A-emd-pbh | A-20261121-131600-02b5d41 (job 4799) | periodic set-up with the relaxed lapse against the exact spherical solution |
| C-sidm | drift run (v), not yet submitted | controls at ten thousand particles on the M/4 mesh: does the contraction scale with particle number |
| D-bh-dress | D-20261121-144631-aa7ce9b (job 4806) | growth of the horizon against the dust flux |
| F-hills | F-20261121-130351-04074e1 (m/16), F-20261121-153707-1eaa5d4 (m/12) | isolated binary; decides the passage P1b (about 27 card-hours) |
| core | core-20261121-154654-d3ec487 (job 4810) | release card build of core-v0.6 on the fifteen cases |

Next, in this order, within what the week allows (the weekly window resets on Friday
2026-11-27 15:00 PST): sign G1 of C and D on the reviews; a lead session of B once the
second verifier has returned, then its gate review; a session of F to apply its rule to
the binary runs and submit P1b; a session of A for the periodic run and the open
question on the horizon mass at first detection; core: release v0.7 (lapse fix, boosted
clumps, oblate component), then the cluster threshold on the finer mesh; the four
packages of the knowledge base that were cut on 2026-11-20.
