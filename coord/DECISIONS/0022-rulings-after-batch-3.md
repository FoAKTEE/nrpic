# 0022 Rulings after batch 3 of wave 3

Status: ACCEPTED · 2026-11-21 · orchestrator (decision 0017)

1. Release core-v0.6 is on main (Fourier Poisson solver and group moments of the
   Newtonian mode, extended outer faces of the spacetime solver, second pass of the
   initial-data solver). Its merged card executable had not run on a card at the tag
   (Slurm job 4800); core closes that check. Not in the release: boosted equilibrium
   clumps (still testing) and the oblate component.
2. Track E, criteria U-A2 and U-A4 of the ultra-slow-roll case. The reworded forms
   proposed by the lead after the data (U-A2 at 256 cells judged on the odd part of a
   mirrored pair; U-A4 as A4' of decision 0021) are accepted for the gate; the strict
   forms stay on record as failed, and the note says that the rewording came after the
   data.
3. Track D. The relaxed lapse (`lapse_leak`) makes the horizon mass of a black hole
   grow late in a run even in vacuum (run V-1GB: drift up to +1.3e-3 over 100-200 M with
   the faces far away, against 5e-5 without the option). The null test of gate G2 is
   therefore made without that option, or with a corrected one: core takes the defect
   as its first item for release v0.7 (the relaxation must act only where matter
   expands, or switch off around a tracked black hole).
4. Track F. The merger of the first passage's binary came from the resolution of its
   members (binary alone at m/8 decays like the passage run; at m/16 the member horizons
   are found in every search with flat masses). The next passage (P1b) uses m/16; the
   lead submits it when the isolated m/16 binary has reached the time the passage needs.
5. Gates KB-G0 and KB-G2 of the knowledge base are signed on the independent verifier's
   report and the lead's recount (coord/GATES.md). The four packages of the knowledge
   base that were cut on 2026-11-20 are scheduled after the tracks' gate work.
6. Budget. The weekly usage window stands at 54 per cent on 2026-11-21 07:45 PST after
   about fifty sessions since its reset. One more batch of about fifteen sessions runs
   today; the remainder is kept for the sessions that read the card runs now queued or
   running, and for the gate packages that depend on them.
