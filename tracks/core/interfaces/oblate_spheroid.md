# Interface text: the oblate spheroid in `nrpic_cf` and in the sampler

Status: PROPOSED by core (branch `core/oblate`, wave 3a, 2026-11-19). For the core lead
(merge into `core/nrpic`), the orchestrator (`coord/INTERFACES/particle_id.md`, rows of
the `spheroid` component) and Track A (row 3 of the verification ladder is shared with
A). Evidence: `tracks/core/JOURNAL-oblate.md` (predictions and outcomes), run manifests
under `tracks/core/runs/`, scripts and figures under `tracks/core/analysis/oblate/`.
Units G = c = 1. Labels: [VERIFIED] measured in a registered run or read from a source
with a locator; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 1. What exists

The component `spheroid` of the problem generator `nrpic_cf` (conformally flat,
time-symmetric data, `gamma_ij = psi^4 delta_ij`, `psi = 1 + sum_c u_c`) now accepts an
equatorial semi-axis `a` larger than or equal to the polar semi-axis `b`: the
homogeneous oblate spheroid, and the homogeneous sphere at `a = b`. Before, `a >= b`
was a fatal error. The construction is the one of the prolate case (Yoo, Harada and
Okawa, arXiv:1611.07906, `asymflat.tex` lines 445-550 [VERIFIED by reading]; neither that
paper nor arXiv:1901.04498 treats an oblate configuration, see the journal, entry 1):

- auxiliary density `rho_N = 3M/(8 pi a^2 b)` inside `(x^2+y^2)/a^2 + z^2/b^2 <= 1`
  (Newtonian source mass M/2), zero outside;
- `u = -Phi_N` with `lap Phi_N = 4 pi rho_N`, so `psi -> 1 + M/(2r)`: ADM mass M;
- energy density `rho_ADM = 2 rho_N psi^-5`; particles at rest with coordinate number
  density proportional to `psi` inside, equal masses `m = M_rest/N`.

Closed form of the potential (`athenak/src/pgen/nrpic/nrpic_cf.cpp`, function
`CFOblateExcess`): with `lam = 0` inside and the positive root of
`R^2/(a^2+lam) + z^2/(b^2+lam) = 1` outside, `w = sqrt(b^2 + lam)`,
`f = sqrt(a^2 - b^2)` (radius of the focal ring), `q = f/w`,

    u   = (3M/8) [ I - R^2 J_a - z^2 J_b ],
    I   = (2/f) atan q,
    J_a = atan(q)/f^3 - w/(f^2 (w^2 + f^2)),
    J_b = (2/f^2) (1/w - atan(q)/f),

the prolate expressions with atanh -> atan and f^2 -> -f^2. For `q < 0.3` (far from the
spheroid, or nearly spherical) the three functions are summed as series in `-q^2`
(twenty terms), which is also the sphere. Rest mass in closed form:
`M_rest = M + (3 M^2/(5 a e)) asin e`, `e = sqrt(1 - b^2/a^2)` (prolate:
`M + (3 M^2/(10 b e)) ln((1+e)/(1-e))`, which is the expression of 1611.07906, line 549,
with `M_N = M/2`).

Python twin and sampler: `python/nrpic/spheroid.py`, class `OblateSpheroid(e, a, M)`
(same interface as `ProlateSpheroid`: `psibar`, `phiN`, `rho_adm`, `coordinate_density`,
`rest_mass`, `rest_mass_closed`, `F_s`, `F_z`, `summary`);
`nrpic.sampling.sample_spheroid(N, seed=..., spheroid=OblateSpheroid(...))` draws the
particles (rejection from the uniform spheroid with weight `psibar`; with `symmetrize`
the sample is invariant under z -> -z and under the half turn about z, N a multiple of
4). Semi-analytic reference for the collapse:
`tracks/core/analysis/oblate/newton_spheroid.py` (Newtonian homogeneous spheroid,
continued through the pancake).

## 2. Options

`<problem>` with `pgen_name = nrpic_cf`; `<c>` is the component index.

| Parameter | Meaning |
|---|---|
| `comp<c>_type = spheroid` | as before |
| `comp<c>_mass` | ADM mass M of the component |
| `comp<c>_a`, `comp<c>_b` | equatorial (x, y) and polar (z) semi-axes, both positive. `a < b`: prolate (unchanged code path). `a >= b`: oblate, new; `a = b`: homogeneous sphere of the same construction (not the Oppenheimer-Snyder ball, whose density is uniform in proper volume: use a table for that) |
| `comp<c>_x1`, `_x2`, `_x3` | centre (default 0); the polar axis is always z |

Nothing else is new in the code: no new input block, no new output. The component
superposes with the other components as before (the superposition solves the
Hamiltonian constraint for the sum of the conformal sources).

`problems/ic/make_ic.py oblate --e E --a A --N N --seed S [--no-symmetrize] --out DIR`
writes `oblate_e<E>_a<A>_N<N>_s<S>.nrp` and `.json`; the JSON holds the spheroid
parameters and, under `athenak`, the `<problem>` block for these particles. `--a` is the
equatorial semi-axis in units of M (default 10), `--e` the eccentricity (default 0.9);
the polar semi-axis is `a sqrt(1 - e^2)`.

Example inputs (one per new use):

| Input | What it is |
|---|---|
| `problems/tests/oblate_cf.athinput` | the oblate component alone, no particles, no step: metric and constraint monitor of the initial slice (test T1) |
| `problems/tests/oblate_id.athinput` | the same with the 10^4 sampled particles on a static mesh, no step (test T1, part c) |
| `problems/tests/oblate_super.athinput` | an oblate component off the origin, superposed with a Gaussian and a puncture, no step (test T1, part d) |
| `problems/oblate/oblate_newton.athinput` | the same particles in AthenaK's Newtonian mode (release code, `pusher = newton`): the Newtonian reference of the collapse (test T4) |
| `problems/oblate/oblate_amr.athinput` | the collapse: `problems/prolate/prolate_amr.athinput` with the axes exchanged (refined box 22 x 22 x 10 M at level 4), to t = 55 M; the runs add `mesh_refinement/num_levels=5` or `6`, `mesh_refinement/max_nmb_per_rank=2000`, `particles/nfilter=4`, `particles/filter_compensate=true` on the command line (`analysis/oblate/make_runs.py` writes the list) |

## 3. Existing behaviour

Unchanged where the new case is absent [VERIFIED, test T2, section 4]: the prolate
branch of `CFExcess` has the same statements in the same order; the parser sets the
new type only for `a >= b`, which was refused before. `make_ic.py prolate`, `os`, `st`
write the same bytes as the script on main (particle files, tables, JSON, printed
summary; `diff -r` over four cases, journal entry 1); the prolate particle file of seed
1 has the sha256 of the file of run `runs/prolate/e09_v8` (dcc80b8d...).

Lines touched in shared files (for the merge with the other wave-3a branches):

| File | Lines of this branch | Change |
|---|---|---|
| `athenak/src/pgen/nrpic/nrpic_cf.cpp` | 23-25 (header comment), 65-66 (enum `CFType`), 137-193 (new function `CFOblateExcess`, placed before `CFExcess`), 215-216 (`else if (c.type == kCFOblate)` in `CFExcess`), 545-550 (parser of the spheroid component) | 70 lines added, 4 replaced |
| `python/nrpic/spheroid.py` | docstring (15 lines added), `__all__`, everything after `ProlateSpheroid` (new `_IJ_oblate`, `OblateSpheroid`) | `ProlateSpheroid` and `_IJ` untouched |
| `python/nrpic/sampling.py` | docstring of `sample_spheroid` (one sentence) | no code |
| `problems/ic/make_ic.py` | docstring, import, `choices`, help of `--sampler`, new argument group, the `else` branch of the model switch, the print branch | prolate path unchanged in effect |
| `tracks/core/interfaces/particle_id.md` | rows `compN_mass` and `compN_a, compN_b` | wording |

## 4. Tests

Predictions were written before each run (`JOURNAL-oblate.md`, entry 1); outcomes in
entries 2 and later.

| Test | Run | Result |
|---|---|---|
| T1a conformal factor against the reference potential (`verify/oblate/oblate_reference.py` of branch core/nrpic; quadrature of the defining integrals; closed form of the sphere), three shapes, every cell of the mesh | core-20261119-143758-09c669d (processors) | psi^4 of the single-precision dump is the correctly rounded reference at every one of 1.4e6 cells (largest difference 0.49997 float32 units); Python twin against the reference 9e-14, against quadrature 5e-14 (relative, in u) |
| T1b Hamiltonian monitor without matter = 32 pi rho_N psi^-5 inside, 0 outside | same | inside to 5e-8, outside 7e-7 of the central value (prolate control 5e-8, 2e-6); mesh integral of R psi^5/(16 pi) = 0.9999995 M |
| T1c sampled particles against psi | same | sum m/psi(x_p) = M (1 + 8.9e-5); mesh integral of E psi^5 equal to that sum to 2e-7; core mean of the monitor 0.4 per cent of the source (prolate control 0.4 per cent) |
| T1d the oblate component off the origin, superposed with a Gaussian and a puncture (`problems/tests/oblate_super.athinput`) | core-20261119-152206-4d292b9 (processors; also reran T1a-c with the same numbers) | psi^4 is the correctly rounded sum of the three references at all 262144 cells (largest difference 0.49999 float32 units, flat histogram) |
| T2 byte regression against the release executable, processors | core-20261119-144947-fb1ccae (first attempt core-20261119-144337-5c02abf stopped) | every output file byte-identical: `regress_cf` (16 files, 2 steps), `cf_table_regress` (8 files, 3 steps), prolate start at M/4 with 10^4 particles (16 files, 2 steps) |
| T3 collapse on a card, finest cells M/4 and M/8, 10^4 particles | SEE SECTION 5 | SEE SECTION 5 |
| T4 the same particles in the Newtonian mode of the release (`problems/oblate/oblate_newton.athinput`), against the homogeneous spheroid | core-20261119-153609-754c44d (processors), analysis core-20261119-161400-72ec4a0 | cells M/2: pancake at 20.0 M (homogeneous, mass sum m: 19.74 M), z_rms down to 0.059 of its initial value, R_rms 0.613 there (0.621), 0.966 of the particles across the plane 1 M later, energy conserved to 4e-4 before the caustic; the crossing is spread over 2 M (10 to 90 per cent), mostly by the scatter of particles that start near the plane; cells M/4: SEE SECTION 5 |

Not tested: axis ratios beyond the four of T1 (e = 0, 0.3, 0.9 and 0.909 off the
origin); a polar axis other than z (there is no option for it); double-precision output of
the C++ function (the dump is single precision; the double-precision statement is the
Python twin's); eccentricities so close to 1 that `b` is not resolved by the mesh.

## 5. State of T3 and T4 (2026-11-19 16:15Z)

T2 holds (section 4). T3, the relativistic collapse at finest cells M/4 and M/8 with the
card executable of this branch, is registered as run core-20261119-144923-1a7c274
(Slurm job 4647, one job of at most 45 minutes: `cf_card`, `oblate_m4`, `oblate_m8`)
and was still waiting in the queue at 16:15Z (fifteen jobs ahead on two cards). Its
predictions are in the journal (entries 1 and 3; P3a to P3d, P3a', P3c'), the commands
that finish it in `tracks/core/analysis/oblate/README.md`. A third resolution (M/16)
does not fit in the card-hour of the package: the prolate M/16 run took 0.48 card-hours
(`runs/prolate/e09_v8`, log footer), and job 4647 may use 0.75.

T4 (the Newtonian reference with the same particles) holds at cells M/2; the run at
M/4 was at t = 4 M of 24 at 16:14Z (journal entry 8).

What the two papers of row 3 report, for the comparison in kind [VERIFIED by reading
the sources fetched with `nrpic-fetch-arxiv`, `kb-data/raw/arxiv/`]: neither evolves an
oblate spheroid (1611.07906 `asymflat.tex`: no occurrence of "oblate", prolate
potential only, lines 496-503; 1901.04498 `main.tex`: "oblate" only for the ringing
horizon, line 259, and "we focus on very prolate cases", line 194). For the prolate
collapse they report a caustic in the matter before any horizon, with a curvature
maximum that grows with resolution, a calculation that continues past the caustic, "a
short time later an apparent horizon ... which envelops all the matter" (1901.04498,
lines 363-366), and a final black hole whose mass is M minus the radiated energy to
better than 0.2 per cent (lines 294-295; E_GW about 0.015 M at most for e = 0.9, line
292). The oblate test of this package asks the same questions of the oblate data: a
caustic (the pancake), its passage, a horizon after it, and the horizon mass against
the ADM mass M = 1 of the data.
