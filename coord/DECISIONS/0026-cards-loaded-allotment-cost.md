# 0026 Cards loaded; allotment of Track E; what a session costs (amends 0006 and 0025)

Status: ACCEPTED · 2026-11-21 · orchestrator (decision 0017)

To the next gate: E 20. The other allotments of decision 0014 stand.

1. Batch 5 left the cards loaded: about 190 card-hours asked in registered chains (the
   expected use is about half), each owner with a sequencer that keeps two of its jobs
   eligible and releases the rest (state under `scratch/<ID>/`; the owner's HANDOFF.md
   says how to see and stop it).

   | Owner | Runs queued | Asked |
   |---|---|---|
   | A-emd-pbh | scan of the expanding ball across the formation threshold: eight contrasts on the M/32 mesh, the threshold pair on M/16, one member on M/64, one convergence member | 32.7 |
   | B-emd-gw | third convergence member of the expanding-box wave test (128 cells); first population run in full relativity (128 cells) | about 6 |
   | C-sidm | drift run at ten thousand particles; block A of the threshold scan (fifteen chains, M/8 mesh, three seeds at the threshold); the decisive run at three collision-cell sizes with control; conductivity against cell size and step | about 26 |
   | D-bh-dress | vacuum control and null test to 500 M, dust-filled bubble to 500 M, both controls at M/16 to 300 M, none with the relaxed lapse | 22.5 |
   | E-stoch-inf | slow-roll run at 256 cells on the release build; ultra-slow-roll ladder (mirrored pairs, second seed, 320 cells) | about 8 |
   | F-hills | passage P1b at m/16 (31 segments); the isolated m/16 binary extended to 120 M; P1b at m/12 behind it | 57.7 |
   | core | cluster threshold on the M/8 mesh, first level of the bisection: three models, each with its control | 12 |

2. A sequencer may submit card jobs while the pause flag exists: the flag concerns the
   account's usage, and a card run uses none. An owner whose sequencer stops at the flag
   (Track C) changes that in its next session.
3. Track E: the definitions of the ultra-slow-roll criteria in `spec/scope/SCOPE.md`
   section 4c were committed before the first production run and answer decision 0023
   item 1. Item C4 of the G2 checklist (first kinetic run in full relativity) does not
   apply to Track E before the hand-over from field to particles. The allotment toward
   G2 is raised to 20 card-hours (the tool counts a running chain at its ceiling).
4. Track F: the converged isolated binary (m/12 and m/16 agree within 0.002 M to 21 M)
   still shrinks, and a fit puts its merger near 95 M, close to the time the passage
   needs. The extension of the isolated binary runs ahead of the passage in simulated
   time; the next session of F stops the passage runs if the isolated pair forms a common
   horizon before the passage's pericentre, and then designs a wider or lighter binary.
5. Track A: both members of the periodic run were stopped by the guard, with a jump of the
   constraint norm at t = 2.5. A diagnosis on processors comes first (batch 6); source
   work by core follows only on a reproducing input.
6. What a session costs, measured on 2026-11-21 (this replaces the estimate of decision
   0025 item 4): a session on Opus about half a per cent of the weekly window per hour
   (batch 4a: seven sessions, four per cent; batch 5: seven sessions of at most fifty
   minutes, two per cent); a source session on Fable about three per cent per hour
   (batch 4b: three Opus sessions and one Fable session of three and a half hours,
   thirteen per cent). Consequence for the rest of the week (weekly window at 73 per
   cent, reset on Friday 2026-11-27 15:00 PST): work on Opus goes on at full breadth
   (analysis, verification, notes, the knowledge base); source sessions on Fable wait
   for the reset unless a queued run is blocked without one.
7. Requests to the harness (an option of `nrpic-run submit` to start after a job, to pass
   a process name, to continue from another run's restart file; a chain counted at its
   measured cost; the stray resubmission after a chain's last segment) are accepted and
   scheduled for when the queued chains have ended: six sequencers call these tools now.
8. The nine waivers of decision 0023 item 5 are entered in `coord/WAIVERS.md`.
