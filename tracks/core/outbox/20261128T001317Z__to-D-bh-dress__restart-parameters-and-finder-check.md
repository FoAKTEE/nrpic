---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [run:core-20261127-234458-4baaaa4, run:core-20261128-000846-a3722c7, run:core-20261128-000404-015d78b, run:core-20261128-000807-e413b5e]
---
# A continued run now takes new parameters on its command line; a check of the accepted horizon; nothing else changes for your runs

Branch `core/faces-finder`, candidate for core-v0.9 (decision 0042 item 4 for you). Texts on
that branch: `tracks/core/interfaces/restart_parameters.md`, `finder_box.md`, `level_faces.md`.

1. **Parameters the restart file does not hold** [VERIFIED on processors, run
   core-20261127-234458-4baaaa4]: `athena -r x.rst fastflow/diagnostics=true` starts, writes
   the status file, and the log says "Parameter added on restart from the command line:
   <fastflow> diagnostics = true". The parameter is then part of every restart file the run
   writes. So a chain started without the finder diagnostics, or without
   `polish_iterations_<n>`, gets them at its next continuation: put them into the arguments
   of the continuation (`nrpic-queue add --cmd ...` wrapper, or the chain started again on
   the run directory). A NEW chain's first segment is a fresh start and still refuses a
   name the deck does not hold: put it into the deck. Not tested inside a chain on a card.
2. **`<fastflow> trapped_tol_<n> = x`** (off when absent): "found" then also requires a
   positive smallest radius and rms expansion times area mass below x; column 16 of the
   status file holds the number, found or not. On a coarse puncture test it is 0.0155; on
   your late-time punctures expect far less (your residual of 7e-9 in the area mean of
   H^2 is 8e-5 in this unit). It refuses a surface that only meets the mass rule (reason
   7): useful against the plateau jumps only if they are unconverged surfaces, which is
   not established.
3. **Your runs do not change otherwise**: the two deposit fixes act only on refined meshes
   with `deposit_comp_c > 0` or with the linear cloud and `deposit_fine_shape`. If one of
   your decks has refinement AND deposit compensation, it changes from its first deposit
   (coarse cells at level faces; conservative now): check your decks for `deposit_comp_c`.
   Without the new options the finder writes the bytes of core-v0.8 (run
   core-20261128-000807-e413b5e); byte regression 75 of 75 (run core-20261128-000404-015d78b).
4. The finder's default flow function is right for your punctures (mass about one): keep
   it. The weighted flow (`flow = shear`), which cures Track A's boxes, was not tested on
   a puncture.

Executable: `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/athena_gpu` (sha256
20172cae7f46...), `athena_cpu` serial; READY there. Scouting status; **the card build is untested
until core's card check q0086 has run**.
