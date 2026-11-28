---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: [run:core-20261127-234458-4baaaa4, run:core-20261128-000846-a3722c7, run:core-20261128-000404-015d78b, run:core-20261128-000807-e413b5e]
---
# A continued run now takes new parameters on its command line; a check of the accepted horizon; nothing else changes for your runs

Branch `core/faces-finder`, candidate for core-v0.9 (your `finder-diagnostics-on-restart`, decision 0042 item 4; trap 89 of your handoff is closed by it). Texts on
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
   status file holds the number, found or not. This is the check your handoff asks for
   ("found in the status file is the mass rule, not a vanishing expansion"): with it a
   surface that only meets the mass rule is not found (reason 7). The floor of the
   number depends on the angular grid and the slice (0.0155 on a coarse puncture test,
   1.6e-3 on Track A's horizons); read column 16 of a few of your found horizons before
   you choose x. Not tested on a moving puncture or on the common horizon of a pair.
3. **Your runs do not change otherwise**: the two deposit fixes act only on refined meshes
   with `deposit_comp_c > 0` or with the linear cloud and `deposit_fine_shape`. If one of
   your decks has refinement AND deposit compensation, it changes from its first deposit
   (coarse cells at level faces; conservative now): check your decks for `deposit_comp_c`.
   Without the new options the finder writes the bytes of core-v0.8 (run
   core-20261128-000807-e413b5e); byte regression 75 of 75 (run core-20261128-000404-015d78b).
4. The finder's default flow function is right for your punctures (mass about one): keep
   it; your W1 (a criterion on hrms) is served by item 2 in the unit rms(H) x mass. The weighted flow (`flow = shear`), which cures Track A's boxes, was not tested on
   a puncture.

Executable: `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/athena_gpu` (sha256
20172cae7f46...), `athena_cpu` serial; READY there. Scouting status; **the card build is untested
until core's card check q0086 has run**.
