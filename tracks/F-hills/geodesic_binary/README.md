# geodesic_binary: relativistic baseline F-pre-2 (HRNA of arXiv:2404.16270)

Work package F-pre-2 of track F-hills (helper package). It implements the "exact
Schwarzschild (or Kerr) acceleration of each member plus Newtonian attraction between the
members" model of Manzaneda, Navarrete & Tejeda (arXiv:2404.16270, the Hybrid
Relativistic-Newtonian Approximation, HRNA). It validates the model, reproduces the paper's
printed results, and extends the scans to pericentres of a few gravitational radii and to a
spinning hole. Results, predictions and outcomes are in `JOURNAL.md`, with run ids.

Decision 0010 [JUDGEMENT]: the HRNA is an ordinary-differential-equation reference solution
(two point masses on an analytic background), allowed outside `athenak/src/`. No outside code
(the paper used REBOUND) is used. The integrator is a DOP853 written here; numba is the only
added package.

## Contents

| file | what |
|---|---|
| `hrna.py` | the model: closed-form metrics (Schwarzschild in Cartesian form, Cartesian Kerr-Schild with spin), Eq. (CoordtEqs) of 2404 (`article.tex:246-256`) for each member, Newtonian (or Hooke) pair force, Newtonian law for comparison, DOP853 with on-the-fly diagnostics, initial data of 2404 appendix B, the driver `run_encounter` |
| `scan.py` | phase scans over (law or spin, sense, beta, phase), parallel |
| `examples.py` | the single encounters printed in 2404 (Figs. 1, 3-5) with figures |
| `analysis_s1.py` | reproduction of 2404 Sec. IV against curves read from the paper's vector figures |
| `analysis_strong.py` | separation fraction, ejection speed and captures from r_p = 1000 to 4 r_g |
| `analysis_kerr.py` | coordinate dependence of HRNA (Kerr-Schild vs Schwarzschild) and Kerr spin |
| `digitize_2404.py` | reads the stroked curves of a matplotlib vector figure (parsed as data only) |
| `register.py` | registers a run (manifest in `tracks/F-hills/runs/<run_id>/`, outputs in `scratch/F-hills/<run_id>/`) |
| `tests/t1_metric_checks.py` | T1: metric identities, derivatives against differences, CKS metric against `python/nrpic/kerr.py`, flat-space binary |
| `tests/t2_geodesic_limit.py` | T2: single-body limit against `python/nrpic/geodesic.py` (Schwarzschild and Kerr a = 0.9) |
| `tests/t3_time_dilation.py` | T3: the time-dilation test of 2404 appendix B (free-falling oscillator) |
| `figures/` | copies of the figures the journal relies on (made by the scripts above, from the runs named in each caption line of JOURNAL.md) |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/F-hills
uv venv /data/haiyangw/nrpic/scratch/F-hills/venv-gb      # once; then:
VIRTUAL_ENV=/data/haiyangw/nrpic/scratch/F-hills/venv-gb uv pip install numba numpy scipy matplotlib mpmath
PY=/data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python
G=tracks/F-hills/geodesic_binary
python3 -I $G/register.py --purpose "T2" -- $PY -I $G/tests/t2_geodesic_limit.py {out}
python3 -I $G/register.py --cores 8 --purpose "S1" -- $PY -I $G/scan.py --out {out}/s1.npz --betas 0.1:10:100 --workers 8
$PY -I $G/analysis_s1.py <s1.npz> <dir with digitized json> <outdir>
```

The digitized curves are produced (into scratch, never committed) with
`python3 -I $G/digitize_2404.py kb-data/raw/arxiv/2404.16270/v1/src/Figures/<name>.pdf <out.json>`
for `sep_fraction`, `v8-asymp` and `frac-surv-Rgr-2`. The fetch of the paper's source is
`python3 -I harness/bin/nrpic-fetch-arxiv 2404.16270 2402.02178`.

## Driver interface (shared with the Newtonian baseline `tracks/F-hills/newton3`)

Units G = c = M = 1 (lengths r_g, times GM/c^3, speeds c). One encounter:
`hrna.run_encounter(**params)`.

| name | meaning | 2404 value | newton3 name |
|---|---|---|---|
| `law` | `"newton"` or `"hrna"` | both | (Newtonian only) |
| `coords` | HRNA coordinates: `"sch"` Schwarzschild (Cartesian form) or `"cks"` Cartesian Kerr-Schild | `"sch"` | - |
| `spin` | a/M, with `coords="cks"`; positive: CM orbit co-rotating with the hole | 0 | - |
| `mb`, `q12` | total binary mass (in M) and m2/m1 | 1e-6, 1 | `m1`, `m2` (aliases accepted) |
| `a0` | initial separation of the circular binary | 1.013 | `a` (alias accepted) |
| `beta` or `rp` | r_t/r_p with r_t = (M/mb)^(1/3) a0, or r_p in r_g | 0.1 to 10 | `D` = 1/beta (alias accepted) |
| `phase` | binary phase at release, from the x axis (2404 convention) | [0, pi) | newton3's `phase` is the effective phase at pericentre: different |
| `sense` | +1 prograde, -1 retrograde (coplanar only) | both | `varphi` = +pi/2 / -pi/2 with `theta` = pi/2 (aliases accepted) |
| `r0_rt`, `rf_rt` | release radius and stop radius of the CM, in r_t | 50, 150 | - |
| `rtol` | DOP853 tolerance (default 1e-12) | - | `rtol` |

Returned keys: `outcome` (newton3 codes 0 survived, 1 m1 bound/m2 free, 2 m2 bound/m1 free,
3 both bound, 4 both free; 6 a member captured by the hole), `E1_u`, `E2_u` (energies in
newton3's unit (m1 m2/a)(M/mb)^(1/3)), `separated`, `Eb_end`, `eb_end`, `ab_end`, `eps1`,
`eps2` (E - 1 per unit mass, E = -u_t), `L1`, `L2`, `eps_cm`, `L_cm`, `vinf` =
sqrt(2 max eps) (2404 definition), `vinf_exact` = sqrt(1 - 1/E^2), `t_peri`, `r_peri`, `t_s`
(in T0, from pericentre), `rcm_ts`, `a_min` (in a0), `alpha_max` (a/R while E_b < 0),
`alpha_all` (a/R at any time), `plunged`, `status`, `nsteps`, `rt`, `rp`, `r0`, `T0`.

Stopping rule: the CM radius exceeds `rf_rt` r_t moving outwards (2404 protocol), or the CM turns
around after pericentre beyond 10 r_t (bound CM; 2404 does not say how it treats these), or a
member crosses r < 2.5 r_g (Schwarzschild) / r_+ + 0.05 r_g (Kerr-Schild) moving inwards
(captured; that member is then frozen and the pair force switched off).

## Results

See the end of `JOURNAL.md` ("Summary") for the numbers with run ids.

## Requests

(see the end of this file after the summary is written)
