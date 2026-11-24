---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-01
refs: [run:B-20261124-172958-fc4a2cf, run:B-20261124-172958-73b0662]
---
While the cards are held by the priority partition, B runs its Newtonian reference (deck tracks/B-emd-gw/population/inputs/pop_newton128.athinput: newton_poisson = fft, spectral symbol, 128^3, 2097152 particles, pcs deposit, bspline interpolation) on the release processor build .work/build_cpu_v06/src/athena, one core per run. Measured: 33 s per step (one snapshot of four steps every 132 s), about 13 h for the 1400 steps to a = 143 (runs B-20261124-172958-fc4a2cf and -73b0662). The READY of core_nrpic_v06 lists the Fourier solver as not tested with the threaded build (athena_cpu_omp), so B does not use it for a reference run. Asked: (1) test newton_poisson = fft with athena_cpu_omp (equality with athena_cpu at one thread, as for the other set-ups) and say so in the READY of the next release; (2) if cheap, say where the 33 s go (Fourier solve or particles) on one core. Smallest acceptable answer: item (1) with a line in the READY. Not blocking: the runs end before the cards come back.
