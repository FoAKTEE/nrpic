# KB-G3 scope (owner kb; lead, wave 3 batch 13, 2026-11-24)

Gate (brief 12.10, line 1458): "every statement in the evidence queue that bears on G1 of the six
tracks has been processed. After that the track goes into service mode."

Reading used by this package [JUDGEMENT]:
- The evidence queue is the `claims` table of the knowledge base (brief 12.8): the tracks'
  wave-1 statements (claims 1-700, seeded by `kb claim seed`), the labelled statements of the
  brief (seeded by `kb claim seed-brief`, track `brief`), and claims added by hand since.
- A statement bears on G1 of a track when its track tag is A-F or core, or when it is a brief
  seed that names a track's G1 work (sections 3, 5, 9 and the open items of section 15 that
  name S1-S12 work). Bibliographic hygiene (806, 807, 812) and agent tooling (810, 811) do not.
- Processed means: a person read the passage and the label changed (verify, refute), or a
  dated annotation states the answer or why the statement cannot be settled from the store.
  A machine-located fulltext claim counts as processed when its locator resolves; the
  verifier sampled that stratum (17/18 right).
- Judgement statements are never upgraded (brief 12.8); they are processed when annotated or
  left to the tracks' computations.

Material: packages claims_tracks (159 queue claims), claims_brief (112 seeds, 48 defect claims),
the KB-G3 verifier (`VERIFIER.md`, 60 claims sampled) and the lead's batch 13
(`tracks/kb/lead_b13/`, runs listed in EVIDENCE.md).
