# 0011 Interface documents accepted

Status: ACCEPTED · 2026-11-15 · orchestrator

The twelve interface documents that core proposed after wave 1 are accepted as the state
of release `core-v0.3` and copied to `coord/INTERFACES/`: collisions, cosmo_gauge,
deposit, diagnostics, multi_puncture, newtonian_mode, particle_id, pusher, rng,
run_manifest, scalar_field, spherical_id_format2 (the refined format replaces the
orchestrator's provisional text). Core keeps the working copies under
`tracks/core/interfaces/`; a change is proposed there and reaches `coord/INTERFACES/`
with the release that implements it. `docs/**` is added to core's OWNERSHIP: the format
and option documents are part of the source tree.
