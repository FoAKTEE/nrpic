# Reproducible random numbers

`athenak/src/utils/rng.hpp` gives every kernel random numbers that are a pure function of
a key (seed, stream, entity, step, draw): no generator state, the same bits on processors,
on a card and in Python (`python/nrpic/rng.py`). The contract (key layout, registry of
streams, rules, what is verified, cost) is `coord/INTERFACES/rng.md` (proposal:
`tracks/core/interfaces/rng.md`). This file says how to use it and how to rerun its tests.

## Use

Input file: the seed of the run is `<job> rng_seed` (default 0).

    #include "utils/rng.hpp"
    const std::uint64_t seed = rng::RunSeed(pin);                 // once, on the host
    const std::uint64_t stream = rng::Stream(rng::kStreamTests, 16);
    const std::uint64_t step = static_cast<std::uint64_t>(pmesh->ncycle);
    // inside a kernel, for particle p
    const rng::Key key{seed, stream, static_cast<std::uint64_t>(pi(PTAG,p)), step};
    double z[2];
    rng::Normal2(key, 0, z);                    // draw 0
    const double u = rng::Uniform(key, 1);      // draw 1

Functions: `Bits`, `Bits4`, `Uniform`, `Uniform4`, `Index`, `Normal`, `Normal2`,
`Direction`; `CellEntity`, and in `utils/rng_mesh.hpp` `CellOffsets`, `WrapIndex` for
draws keyed by cells. The same names in lower case in `nrpic.rng`, with keyword arguments
`seed, stream, entity, step, draw, entity_hi` that broadcast over arrays.

The five rules that matter most: the entity is the particle tag or the global cell index,
never an array or MeshBlock index; the step is the cycle number; every variate has its own
draw index; every purpose has its own stream from the registry; one seed per run.

A complete example is the test kick, `athenak/src/particles/nrpic_kick.cpp`
(`<particles> test_kick = true`, options at the top of the file; off and without any
effect on a run unless the parameter is present).

## Tests (drivers in `tracks/core/analysis/rng/`)

| Test | Command (register with `runreg.py`) |
|---|---|
| table of draws, sums, cost inside the code | `make_keys.py keys.bin`; `athena -i problems/tests/rng_test.athinput problem/key_file=keys.bin problem/nstat=2e8 problem/ntime=2e7` (processor) or `nstat=1e10 ntime=4e9` (card) |
| agreement of all implementations | `run_agreement.py --keys keys.bin <tables>` (compiles `standalone_table.cpp` with five option sets; `compare_table.py`: Python twin and `numpy.random.Philox`) |
| statistics and figures | `stat_tests.py --n 20000000 --stat label=<basename>.rng_stat.txt ...` |
| logarithm of the normal draw | `accuracy_log.py` |
| words of one call | `run_words_corr.py` |
| draws keyed by cells | `run_cell_check.py --exe athena` |
| kick in the particle module: divisions into MeshBlocks, restart, controls, Python twin | `run_kick_demo.py --exe athena --case analytic` and `--case mesh`; figure `plot_kick_demo.py` |
| existing behaviour unchanged | `run_regression.py --base <old athena> --new <new athena>` |
| all card runs in one allocation | `sbatch ... gpu_job.sh` (arguments at the top of the script) |

Files written by `pgen_name = rng_test` (`athenak/src/pgen/unit_tests/rng_test.cpp`):

| File | Content |
|---|---|
| key file (input) | 8 bytes `NRRNGKY1`, int64 N, N records of 6 uint64: seed, stream, entity, entity_hi, step, draw |
| `rng_table.bin` | 8 bytes `NRRNGTB1`, int64 N, the N key records, N records of 6 uint64 (four words, `Index` with n = 1000003, upper half of the product of the first two words), N records of 9 float64 (`Uniform4`, `Normal2`, `Direction`) |
| `<base>.rng_stat.txt` | `name value` lines: sums of powers and products of the draws for `nstat` keys; `hist_*` lines: histograms |
| `<base>.rng_time.txt` | per function: seconds, ns per call, calls per second, checksum |
| `<base>.rng_cells.txt` | per refinement level: number of cells, checksum of the draws keyed by cells |
| `<base>.kick.txt` (test kick) | per cycle: cycle, time after the step, particles, particles kicked, checksum of the deviates, step used in the key |
