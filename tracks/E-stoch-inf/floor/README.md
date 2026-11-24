# Package floor (Track E, G2)

Tests whether the floor of the slow-roll spectral convergence at the lowest injected shells (128 and
256 cells on each other at N_f; `../repro/figs/RESULTS.md` Fig. 7, S19, S22) is the second order of the
field: the 128- and 256-cell convergence runs again at half the noise amplitude
(`scalar_field/noise_mode_scale=0.5`), otherwise identical to C128S and CL256S of `../repro/scope`.

Predictions before submission: `JOURNAL.md` entry 1 (F1-F5). Runs go through the shared card queue
(labels FL128h, FL256h, priority 2); run ids and outcomes are added to `JOURNAL.md` when they have
run. Reading: `../repro/figs/figures/dumppass.py ... --last --scale 0.5 --save-modes` (entry 1).

| Label | s = 1 counterpart | Queue | Run | Card-h |
|---|---|---|---|---|
| FL128h | C128S (E-20261123-020704-2b99463, pass E-20261124-133251-42e8aab) | see HANDOFF.md of E | pending | - |
| FL256h | CL256S (E-20261123-090727-4b6e5a5 + E-20261124-130952-4be980b, pass E-20261124-213029-e937f69) | see HANDOFF.md of E | pending | - |
