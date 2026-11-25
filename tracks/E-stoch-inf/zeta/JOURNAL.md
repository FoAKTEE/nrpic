# JOURNAL of package zeta (Track E, gate G3)

## entry-1 (2026-11-25 07:40 PST, lead of E, batch 19): the 32^3 mirrored pairs for Z0 and Z2, before the run

Four runs (`inputs/pairs32.list`): 32^3 USR deck `usr/inputs/usr_base.athinput` with nmax2 = 64, the deck's
seed, noise_mode_scale = +-1/4, +-1/2, dumps at t = 0 and tlim with the metric, release processor build
`.work/build_cpu_v07/src/athena`, two at a time on two cores.
- P1 (health): all four reach tlim with exit 0 and finite fields; each takes between 2 and 30 minutes.
- P2 (mirror): the box means of phi at tlim of the + and - members differ by less than 1e-3 of the rms of
  their difference field (the mean is even in s; the field's odd part has no k = 0 mode).
Z0-Z2 themselves are judged by the reader against `../g3/JOURNAL.md` entry 4 once it exists.

## entry-2 (2026-11-25 07:50 PST): predictions for `pairs_check.py`, written while the pairs run, before any reading

`pairs_check.py` reads the last dump of each member: P2 as in entry 1, and a preview of the second order of
the linear variable R_lin = (H/Pi) dphi (not a criterion; Z0-Z2 judge zeta once the reader exists).
- P3: the local quadratic coefficient a of the even part on O^2 - <O^2> agrees between s = 1/4 and 1/2
  (a(1/2)/a(1/4) in [0.8, 1.25]); refuted outside: then the even part of R_lin holds a part that is not a
  local quadratic of the odd part (as the per-run part of G2's constraints), and Z2's 2 per cent bar needs
  the same split for zeta.
- P4: skewness of the odd part below 0.01 in magnitude at both amplitudes (32^3 box, 32768 cells: one-box
  noise about 0.014, so only a gross error shows).

## entry-3 (2026-11-25 07:52 PST): outcomes of entries 1-2

Runs E-20261125-153148-cfad424 (four 32^3 runs, 544-552 s each on one core) and reading
E-20261125-155027-a9037d9 (`pairs_check.json`, `fig_pairs_check.png` looked at; the s = 1/4 points lie
under the s = 1/2 points in both panels).
- P1 HOLDS: all four reach tlim = 10.4375 with exit 0 and finite fields.
- P2 HOLDS: |<phi>(+) - <phi>(-)| / rms(difference) = 7.3e-10 (s = 1/4) and 0 (s = 1/2).
- P3 HOLDS: a = 1.83848e-4 (s = 1/4) and 1.83856e-4 (s = 1/2), ratio 1.00004; the residual of the even part
  about a (O^2 - <O^2>) is 0.7797 of its rms at both amplitudes. The even part of R_lin scales exactly as the
  square of the odd part (no part that does not scale, at this level), but only about 40 per cent of its
  variance is the LOCAL quadratic of O; the rest is non-local (products of modes at other positions).
- P4 HOLDS: skewness of O 0.00746 at both amplitudes (the same realisation, scaled).
Reading [JUDGEMENT]: a sigma_O = 6.2e-6 at s = 1/2 means a local-quadratic skewness of R_lin of about 6 a
sigma = 4e-5 in this 32^3 box; the 128^3 box gave a_R = 2.8e-4 (review run E-20261125-131002-ceefa2f)
against 0.0078 for one-patch delta N. With R35 (one-patch phi at N_f already skewed), Z2 for zeta and A4's
direct comparison will tell whether NR's d phi lacks the one-patch non-Gaussianity. Inputs for Z0 and Z2
exist now (the pairs); the reader with the map is the next step.
