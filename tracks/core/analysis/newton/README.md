# Figures and numbers of the tests of the Newtonian mode

Made by the scripts of `problems/newton/` from the registered runs named below; the
numbers of each figure are in the JSON file of the same name. Interface note:
`tracks/core/interfaces/newtonian_mode.md`, section 5. Style: `python/nrpic/figstyle.py`.

| File | Test | Runs | What it shows |
|---|---|---|---|
| `field_point.png` | T1 | core-20261115-115136/-115145/-115155-9d84282 | Left: radial force of a unit mass times r^2 on 2000 tracers against distance in cells, three resolutions. Centre: relative force error, with (dx/r)^2. Right: rms force error beyond r = 0.5 and potential error at the probes against the cell size, with a second-order line |
| `field_ball.png` | T2 | core-20261115-115137/-115146/-115203-9d84282 | Left: radial force of the homogeneous ball at N = 128 on the exact curve. Centre: force error against radius, three resolutions (peak at the surface). Right: errors against the cell size; reference: the ball that the lattice samples |
| `field_ball_ideal_radius.png` | T2 | the same | The same analysis against the nominal radius: interior error proportional to r at every resolution (the floor of the first analysis) |
| `field_point_smr.json` | T9 | core-20261115-121732-dc623d1 | Point mass on a mesh with one static level: force errors by region (no figure) |
| `collapse.png` | T3 | core-20261115-115448-fee90ca (N = 64), core-20261115-120028-fee90ca (N = 128, card) | Top: r/r_0 against the cycloid; deviation of the mean, of the inner and of the outer particles; energy. Bottom: second moment and its three derivatives on the exact curves; their deviations; V cycles per step |
| `spin_N64.png` | T6 | core-20261115-120641-6bef558 | Top: drift of the centre of mass from uniform motion, change of momentum and angular momentum, energy. Bottom: trace-free quadrupole and its second and third derivatives, six components |
| `wave.png` | T4 | core-20261115-115706-fee90ca (N = 32), core-20261115-115708-fee90ca (N = 64) | Top: phase space at four scale factors with the Zel'dovich curve; error against Zel'dovich; difference from `cosmo/newton/pm.py`. Bottom: difference from the numpy scheme (rounding level); Layzer-Irvine constant; energies. Grey line: shell crossing |
| `wave_ppc8.json` | T4c | core-20261115-122313-dc623d1 | The plane wave on the N = 32 mesh with 64^3 particles: errors per snapshot (no figure kept) |
| `wave_filter.json` | T4b | core-20261115-121455-c061b12 | The plane wave with the triangular cloud, cloud compensation and the compensated binomial filter (no figure kept) |
