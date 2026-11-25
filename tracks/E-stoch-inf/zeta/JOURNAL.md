# JOURNAL of package zeta (Track E, gate G3)

## entry-1 (2026-11-25 07:40 PST, lead of E, batch 19): the 32^3 mirrored pairs for Z0 and Z2, before the run

Four runs (`inputs/pairs32.list`): 32^3 USR deck `usr/inputs/usr_base.athinput` with nmax2 = 64, the deck's
seed, noise_mode_scale = +-1/4, +-1/2, dumps at t = 0 and tlim with the metric, release processor build
`.work/build_cpu_v07/src/athena`, two at a time on two cores.
- P1 (health): all four reach tlim with exit 0 and finite fields; each takes between 2 and 30 minutes.
- P2 (mirror): the box means of phi at tlim of the + and - members differ by less than 1e-3 of the rms of
  their difference field (the mean is even in s; the field's odd part has no k = 0 mode).
Z0-Z2 themselves are judged by the reader against `../g3/JOURNAL.md` entry 4 once it exists.
