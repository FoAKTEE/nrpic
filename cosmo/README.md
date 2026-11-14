# Cosmological structure formation with the NRPIC code

Extension of the numerical-relativity particle-in-cell code of this repository to an
expanding, periodic universe. Three source papers are redone: East, Wojtak & Pretorius
(arXiv:1908.05683), Daverio, Dirian & Mitsou (arXiv:1904.07841), Barrera-Hinojosa & Li
(arXiv:2001.07968).

| File | Content |
|---|---|
| `PLAN.md` | plan, milestones C0 to C6, method tracks T1 and T2, state and revisions |
| `TESTLOG.md` | every test: prediction written before the run, outcome, corrections |
| `paper/main.pdf` | working paper (text, figures, ledger of numbers) |
| `ic/` | initial data: constraint solve on the torus, lattices, random fields, light rays |
| `newton/` | Newtonian particle-mesh reference with the same clouds |
| `analysis/` | analysis scripts and their figures (`analysis/figs/`) |
| `notes/` | specifications read from the source papers, report of the C6 tests |
| `../problems/cosmo/*.athinput` | inputs of the runs |

## Units and gauge

G = c = 1; initial Hubble rate 1 at scale factor 1; lapse condition
`d_t alpha = -(1/3) alpha^2 K` with zero shift, so the time coordinate is conformal time
and `a = (1 + t/2)^2` for matter domination.

## Options added to the code for cosmology (`<particles>` unless stated)

| Option | Meaning |
|---|---|
| `source_density`, `source_extrap` | sources handed to the spacetime solver as densities, converted with the volume element of every stage and extrapolated to the middle of the step |
| `deposit_shape = cic, tsc, pcs` | linear, quadratic, cubic cloud |
| `deposit_comp_c`, `deposit_comp_c2` | compensation of the cloud on the deposited density, before the division by the volume element (1/12, 1/8, 1/6 and 8/45, 37/120, 7/15 for the three clouds) |
| `deposit_comp_limit` | that pass in flux form with a limiter (keeps the energy density positive) |
| `interp = hermite, bspline` | metric at the particles: Catmull-Rom of the method, or the cubic spline through the cell values |
| `dt_expansion` | step limited to this fraction of the expansion time |
| `<z4c> damp_kappa1_over_alpha` | constraint damping at a fixed rate per unit of conformal time |
| `<z4c> lapse_harmonic`, `lapse_kdriver`, `lapse_volume` | lapse conditions |
| `cstat_dcycle` | constraint statistics, absolute and relative (`.cstat.hst`) |
| `cons_dcycle` | conservation of the deposited matter on the mesh (`.cons.hst`) |
| `field_time1..16`, `field_constraints` | dumps of the energy density and conformal factor, optionally with the constraint fields |
| `traj_ntrack`, `traj_dcycle`, `line_dcycle`, `nprobe` | observers, light rays, line records, probes |

Production configuration for lattice starts: `deposit_shape = pcs`,
`deposit_comp_c = 0.1666666666666667`, `deposit_comp_c2 = 0.4666666666666667`,
`interp = bspline`, `dt_expansion = 0.01`, damping rate 0.5 with
`damp_kappa1_over_alpha = true`. Resolve the shortest wave of the initial data with
twenty cells. Give the box size in the input with all its digits (take it from
`meta.json` or `id.json` of the initial data).

## A run from start to finish (random field, larger box, 64 cells)

```
scripts/build_gpu.sh .work/build_gpu_c3
cd cosmo/ic
python3 make_daverio_c.py --box 704 --cut 220 --n 64 --ppc 2 --seed 1 --shape pcs \
    --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
    --out ../../runs/cosmo/dav_c704_n64_pcs4bt
cd ../..
cat > .work/example.list <<EOF
runs/cosmo/dav_c704_n64_pcs4bt problems/cosmo/daverio_field.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 particles/deposit_shape=pcs particles/deposit_comp_c=0.16666666666666666 particles/deposit_comp_c2=0.4666666666666667 particles/interp=bspline particles/dt_expansion=0.01 particles/cons_dcycle=16
EOF
ATHENA_EXE=.work/build_gpu_c3/src/athena scripts/gpu_batch.sh .work/example.list
python3 cosmo/analysis/daverio_c.py --box 704 --cut 220 --cases dav_c704_n64_pcs4bt
```

Runs longer than the one-hour job limit go through `scripts/submit_chain.sh` with
`problems/cosmo/daverio_field_rst.athinput`; restarts are exact.

## Working paper

```
cd cosmo/paper/scripts && python3 make_data_daverio_c.py && python3 fig_daverio_c.py
cd .. && latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```
