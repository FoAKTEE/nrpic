# JOURNAL of box_tests (helper of C-sidm, wave 2)

Box tests of the collision operator of release core-v0.3 with the release executables
(`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`, serial Kokkos, no MPI;
`.../build_gpu_v03/src/athena`, one A100), against `../collide/TESTS.md` (criteria fixed in
wave 1; not changed here; a new criterion would be a new test) and the option names of
`coord/INTERFACES/collisions.md`. Entries are appended; predictions are written before the
run they concern, outcomes after it, failed predictions included.

## 2026-11-15 S0 smoke run (formats only)

Purpose: learn the header of `box.coll.hst`, the dump layout and the snapshot names of the
release executable on a 1e4-particle box (theta = 0.1, sigma = 10, 4^3 cells, 20 steps,
dump at cycle 5). No criterion. Expectation: the run ends with rc 0; the dump parses with
the layout of collisions.md section 5 (18 doubles and 7 int32 per particle, file length
exact); lapse 1, gamma = identity, proper volume 1/64 in every record.
