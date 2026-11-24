# 0031 Level 2 of the stochastic backreaction is on a branch; ablation runs; allotment of Track E (amends 0006)

Status: ACCEPTED · 2026-11-22 · orchestrator (decision 0017)

To the next gate: E 30. The other allotments stand.

1. `<scalar_field> noise_level = 2` is written on branch `core/noise-level2` (Opus,
   decision 0029 item 2) and tested on processors; its card executable had run no step
   on a card when the session ended. With it came `noise_mode_eq = mesh`, which puts
   levels 0 and 1 on the mesh too: the released levels use per-shell mode functions with
   the continuum wavenumber, which differ from the mesh equation at first order by the
   stencil and would swamp the effect of one part in ten thousand that the paper's
   ablation shows. The ablation of the reproduction therefore compares level 2 and
   level 1 with level 0, all three with the mode equation on the mesh.
2. Choices where the paper is silent are judgements of the implementer and are named as
   such in `tracks/core/interfaces/noise_level2.md` on that branch (the background of
   the window at level 2, the reading of two symbols of the paper's equation). The
   working note repeats them where it shows the ablation.
3. Track E runs the card smoke test of the branch executable and the six ablation runs
   at 256 cells (three levels, two scenarios) through its sequencer; for these runs the
   branch executable is allowed in a production-labelled reproduction because no release
   has the option (decision 0013 limits branch executables to scouting; this is the
   stated exception, and the note says which executable each run used).
4. The review of the branch's diff on Fable, before any release, stays as decision 0029
   item 2 says.
5. Exception to the queue rule (decision 0025 item 5), for the reproduction only: Track
   E's sequencer keeps up to six card jobs in the queue until the runs of the
   reproduction have ended (restarted by the orchestrator on 2026-11-22 19:57 PST with
   `MAXJ=6`; state in `scratch/E-stoch-inf/repro_scope_seq/`). With two eligible jobs
   per round behind six other owners the sixteen runs would have taken about two days.
   No other user's job was queued when this was done; the rule of two returns when that
   queue is empty.
