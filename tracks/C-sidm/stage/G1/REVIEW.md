# C-sidm G1: the lead's recheck of the helpers

The lead's recheck of the wave-2 helpers (box_tests, models, threshold_scan, note, verifier)
is `../REVIEW-wave2.md`, with the scripts in `../review_wave2/` and the runs
C-20261115-193332-48771b4 and C-20261115-193751-d3872ff. For G1 its sections 1 (box tests:
every recomputed number agrees; T6-T8 not run) and 2 (models: particle invariants and the
fluid onsets confirmed with an independent operator; growth-rate fit failed its own test)
are the relevant ones. The wave-1 review of the specifications and the baseline is
`../G0/REVIEW.md`.

Wave 2b (2026-11-19): sections 6 (box_rerun with `coll_energy = particle`: every recomputed
number agrees, run C-20261119-151502-cb831a8, L13) and 7 (the first collisional cluster
runs: what can and cannot be concluded, the Juttner onset of the King family, the decisive
runs D1-D3; runs C-20261119-151502-cb831a8, C-20261119-151944-08f3220) of
`../REVIEW-wave2.md`; section 8 notes that the wave-3a heat package (T6-T8) is not reviewed
yet.

Wave 3, round 1 (lead of batch 2b, 2026-11-21): `../REVIEW-wave3.md`, scripts in
`../review_wave3/`, runs C-20261121-075336-49f92da (own t_c reader and control fits) and
C-20261121-075535-b35b8fb (T7 rows and extrapolations from the per-seed values; figures of the
models validation). For G1: section 1 (heat, T6-T8: confirmed, C6 met), section 4 (models:
v2 estimator confirmed, rates on runs quoted with their interval; C2 met with that
restriction), sections 5 and 6 (note cut before its G1 text; verifier in progress).
Sections 2 and 3 (decisive, drift) are G2 material.

Wave 3, batch 4a (lead, 2026-11-21): `../REVIEW-wave3.md` sections 9 (verify_g1: VERIFIER.md
checked from the artefacts, items 1 and 2 confirmed by runs C-20261121-155049-ecf8893 and
C-20261121-155116-ba83d16, every WRONG or NOT CONFIRMED item answered), 10 (note v1: checker
--compile rerun and six ledger rows rechecked, run C-20261121-155226-8ea9e47; C16 met) and 11
(drift batch 3, G2 material).
