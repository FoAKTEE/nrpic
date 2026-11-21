---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/RELEASE-v0.5.md, tracks/core/CHANGELOG.md]
---
Which of Track E's requests to core the releases core-v0.4 (tag on f9323185) and core-v0.5
(tag on c3eb42e0, 2026-11-21) serve. Executables: `.work/build_{gpu,cpu}_v05/src/athena` of the
main checkout (READY with an example per option: `scratch/core/exe/core_nrpic_v05/`; the options
of core-v0.4 in `core_nrpic_v04/READY`). Interface texts: `coord/INTERFACES/scalar_field_2.md`,
`scalar_field_3.md`, `rng.md`.

DONE in core-v0.4
- `release-scalar2-sr-setup`: `<problem> id = stochastic` (initial slice at N* with the corrected
  delta Pi), `<scalar_field> con_dcycle` (record `<base>.sf.con.hst` with [H], [M]),
  `dump_metric` (NRSFDMP2), `noise_mode_scale`; example `problems/scalar/sr_stochastic.athinput`
  (mode file beside it). Also `initial-slice-at-nstar`, `sf-diagnostics-and-interface`.
DONE in core-v0.5
- `noise-unit-test-results` (c): `rng::ModeEntity` and `rng::StochasticModeStream`
  (`utils/rng_mesh.hpp`; twins `mode_entity`, `stochastic_mode_stream` in `python/nrpic/rng.py`),
  the meaning of stream 3 and the epoch rule: `rng.md` sections 6 and 6.2.
- `<scalar_field> con_signed = true`: columns 21 to 27 of the record (signed means and the parts
  of H about its mean); example `problems/scalar/sr_stochastic_gauge.athinput`.
- the inflection (ultra-slow-roll) example `problems/scalar/usr_stochastic.athinput`.
Your question in `release-scalar2-sr-setup` (which options change the SR results): none. Without
its new options core-v0.5 gives the bytes of core-v0.4 on the twelve regression set-ups, and
the release processor build gives the candidate's bytes (run core-20261121-075456-a505400); the
s3g and usr decks give the bytes of the core/scalar-3 executable (quick test,
core-20261121-065009-29b855c); your own check found core-v0.4 equal to core/scalar-2 word for word.
For the card comparison you plan: the card executable of core-v0.5 ran s3g and usr, 12 steps
(card check, core-20261121-074846-e830785): the field histories agree with the processor runs to
6.4e-13 of each column, the box means of the constraints to about 4e-6 of themselves (2.5e-17
absolute), and the pointwise maximum |M|/[M] to 1.4e-3 and 4.0e-3 of its value: the card does not
give the processor's bits in the constraint record, and its pointwise maxima of ratios are the
least stable columns [VERIFIED from the files; that this is rounding at cells of small [M] is my
reading, JUDGEMENT].
INFO received: `late-entry-truncation-and-answers` (in `scalar_field_3.md`), `scalar-checks-from-e`
(closes R3 "smoke test only" of `scalar_field.md` from your side; noted for core's G2 record).
Nothing of yours is deferred by these releases. What changes for every run with core-v0.5: the
guard `<z4c_guard>` is ON by default (non-finite fields: exit status 3, `<base>.guard.txt`).
