# core to A-emd-pbh: answer to `newton-mode-and-ball-ic` (work package dfix)

Triage and evidence: `tracks/core/interfaces/REQUESTS_ADF.md` on branch
`core/requests-adf`, rows A1 to A3. Executables for scouting runs:
`/data/haiyangw/nrpic/scratch/core/exe/core_requests-adf/` (`READY`, item 5).

- Isolated boundary values: exist in core-v0.3 (`<gravity> mg_bc = multipole`,
  `problems/newton/isolated.athinput`).
- Background acceleration of the matter era: `<particles> newton_bg_t0 = t0` adds
  -(2/9) x/(t0 + t)^2 (with `newton_expansion = none`); test T4 reproduces
  r = r0 (1 + t)^(2/3) and (1 + t)^(1/3) to 3e-7. A fixed point mass is also available
  (`newton_pm_*`).
- Special-relativistic push, snapshots at chosen times, per-species second moments:
  deferred to the next package of the Newtonian mode.
- Zel'dovich-deformed ball in `problems/ic/make_ic.py`: deferred to the next core
  session after this wave's merge (formulas from your `newton/SCAN.md` section 4).
- The halting tests are your acceptance tests of the mode (decision 0010).
