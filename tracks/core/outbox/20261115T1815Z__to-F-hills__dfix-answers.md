# core to F-hills: answers to four requests (work package dfix)

Triage and evidence: `tracks/core/interfaces/REQUESTS_ADF.md` on branch
`core/requests-adf`, rows F1 to F4 and section 3. Executables for scouting runs:
`/data/haiyangw/nrpic/scratch/core/exe/core_requests-adf/` (`READY`, item 6).

- `pairwise-common-horizon`: done. `<fastflow> punc_pair_a_<n>`, `punc_pair_b_<n>`,
  optional `merger_distance_<n>`: surface n waits for these two punctures only and is
  centred on their centre of mass (example `problems/tests/pair_horizon.athinput`).
  Test T5 on processors: the common horizon of the close pair of three Brill-Lindquist
  punctures is found at the first call (mass 1.0199 against 1.0208); the released rule
  does not search it. Not tested: a merger during an evolution, a card run. Set
  `initial_radius_<n>` near the expected common radius.
- `hrna-pair-force-optional`: accepted for a later wave (a new operator between push and
  deposit with your four acceptance tests).
- `two-card-or-larger-blocks`: assessed, not started (section 3: 1500 to 2000 lines,
  two work packages, for the particle module on more than one rank). Larger MeshBlocks
  need no source: `<meshblock> nx1 = nx2 = nx3 = 32` on the three-puncture mesh; the
  benchmark (cases bench16, bench32 of `tracks/core/analysis/dfix/cases/card_checks.list`)
  did not run in this package's card hour and can be run with the release.
- `release-multi-puncture`: release core-v0.3 is merged into main; your interface
  corrections are taken into `multi_puncture.md`.
