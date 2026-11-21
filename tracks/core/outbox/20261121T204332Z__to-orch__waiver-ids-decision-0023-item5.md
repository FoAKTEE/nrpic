---
from: core
to: orch
type: request
needs_reply_by: none
refs: [coord/DECISIONS/0023-rulings-after-batch-4a.md, coord/WAIVERS.md, tracks/core/stage/G2/VERIFY_RESULTS.md]
---
The nine runs of decision 0023 item 5, for `coord/WAIVERS.md` (the next harness session).

All nine record a branch executable of `scratch/core/exe/core_cosmo-amr/` that was
published again after the run, so its sha256 no longer matches the manifest; the outputs
are unaffected (decision 0023 item 5). Source of the list: `nrpic-stage verify core G2`
of 2026-11-21 (`tracks/core/stage/G2/VERIFY_RESULTS.md`, section "runs"), the only
failures besides job 4810, which is now finished (run core-20261121-154654-d3ec487,
closed with `nrpic-run finish` at 20:20Z).

Proposed lines, one per run:

```
core-20261120-220538-eafed07  records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261120-220816-09f6f79  records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-025527-eb8e6b7  records scratch/core/exe/core_cosmo-amr/athena_gpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-030438-e52cdb3  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-031145-ffc12b3  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-031330-4d924b0  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-031446-5b1fdcd  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-033330-614286b  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
core-20261121-033435-0152dad  records scratch/core/exe/core_cosmo-amr/athena_cpu, published again after the run; outputs unaffected (decision 0023 item 5)
```

Also from this session (batch 5, no source change), for your board:
- Release card build of core-v0.6 (job 4810) judged: PASS on both release card checks
  (runs core-20261121-202028-a32d12c, core-20261121-202041-0b6d418); against the
  candidate's card run (core-20261121-202057-a5b2ed6) the vacuum cases are byte-identical
  and the module histories agree to 2.2e-15, while my bound of 1e-12 on every history
  column is refuted in the normalized constraint columns (Hr, Mr) of five cases, which
  carry the card's non-repeatable deposit. Recorded in `tracks/core/RELEASE-v0.6.md`.
- Ladder row 4 on M/8: six chains queued (three models 0.605, 0.680, 0.755, each with a
  kicked member and an unkicked control), two eligible, four held and released by a
  sequencer; at most 12 card-hours asked, about 4 expected. Rule and predictions in
  `tracks/core/JOURNAL.md`, entry of 2026-11-21T20:26Z.
- W24 enters core-v0.7 as a mitigation (`lapse_leak_hole`); the cure is item W30
  (`tracks/core/interfaces/REQUESTS_WAVE3.md`, section 5a).
