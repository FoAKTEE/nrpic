# E-pre-1: reproduction specification for stochastic inflation in NR

Package of Track E (owner E-stoch-inf), work package E-pre-1 of the brief (lines 785-802).
Target: the slow-roll and ultra-slow-roll test cases of arXiv:2512.14649, rebuilt in this
repository's AthenaK (decision 0010).

## Contents

| Path | What |
|---|---|
| `SPEC.md` | the specification: equations and sources with locators, window, gauge, initial data, random draw, the two test cases, acceptance quantities, freezing criterion, unstated items, errata, costs, requests to core |
| `scope/SCOPE.md` | problem statement, exit criteria (G0, G1, G2, downgrade trigger) and risk list of the feasibility gate |
| `JOURNAL.md` | predictions before each test and the outcomes, including the failed ones |
| `ref/ms_reference.py` | background and Mukhanov-Sasaki (full and deformed) reference for both test cases on the N = 256 lattice modes (tests T1, T2, T2c) |
| `ref/norm_test.py` | normalisation of the Gaussian random draw (test T3) |
| `ref/ic_constraint_check.py` | symbolic check of the geodesic-gauge initial data against the linear constraints (test T4) |
| `ref/make_figures.py` | figures and the drift check T2d |
| `fig/*.png` | figures of run E-stoch-inf-20261115-123236-2e87364 (looked at): background against the published Fig. 1, freezing, spectra, drift, normalisation |

Sources read (fetched with `harness/bin/nrpic-fetch-arxiv`, never committed): 2512.14649 v2,
2401.08530 v2, 2502.06783 v3, 2610.32592 v1 (thesis), 2606.14853 v2.

## Runs (manifests in `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, outputs in `scratch/E-stoch-inf/<run_id>/`)

| Run id | Test | Cost |
|---|---|---|
| E-stoch-inf-20261115-122806-ef0d039 | T1, T2, T2c | 202 s, 1 core |
| E-stoch-inf-20261115-122934-9ac98d8 | T3 | 1 s, 4 threads |
| E-stoch-inf-20261115-123146-82d2fd4 | T4 | 1 s, 1 core |
| E-stoch-inf-20261115-123201-82d2fd4 | figures, T2d (superseded only in a figure margin) | 5 s |
| E-stoch-inf-20261115-123236-2e87364 | figures, T2d | 4 s |

No card time used.

## How to rerun

From the worktree root, with NumPy, SciPy, SymPy and Matplotlib (the system Python of `anta`
has them; run without `-I`, the scripts read no downloaded data):

    export OMP_NUM_THREADS=1
    python3 tracks/E-stoch-inf/spec/ref/ms_reference.py --out scratch/E-stoch-inf/<run_id>      # about 3.5 min
    python3 tracks/E-stoch-inf/spec/ref/norm_test.py --out scratch/E-stoch-inf/<run_id2> --n 64 --seeds 8
    python3 tracks/E-stoch-inf/spec/ref/ic_constraint_check.py --out scratch/E-stoch-inf/<run_id3>
    python3 tracks/E-stoch-inf/spec/ref/make_figures.py --ms scratch/E-stoch-inf/<run_id> \
        --norm scratch/E-stoch-inf/<run_id2> --out scratch/E-stoch-inf/<run_id4>

Register each run (`harness/bin/nrpic-run` or a manifest by hand) before quoting a number.
The JSON files of the outputs hold every number quoted in SPEC.md.

## Requests

To **core** (decision 0010: the capability goes into `athenak/src/`; details in SPEC section 10):

1. A minimally coupled scalar field (phi, Pi) coupled to Z4c through `tmunu`, with the quadratic
   and the Higgs-inflection potentials of SPEC section 6, usable with `use_z4c = false`, no
   damping, geodesic slicing and zero shift (parameters in SPEC 2.5).
2. Langevin sources on the right-hand sides of K-hat, At_ij and Pi (SPEC 2.1-2.2), evaluated at
   the stage time of each stage of AthenaK's RK4()4[2S] (the Z4c right-hand side currently
   reads `pmesh->time` for every stage, `z4c_calcrhs.cpp:44`).
3. A GPU FFT (single card at 256^3 is enough for the reproduction), the white noise from the
   `core/rng` generator, per-wave-vector amplitudes R_k, dot R_k evolved with level-0
   coefficients (level 2 later), and per stage the inverse transforms of S_R and
   k_i k_j / k^2 S_R.
4. Initial data at N* from the background and mode tables this track supplies, with the
   corrected delta Pi of SPEC 5.3, and a test that the generated slice satisfies the linearised
   constraints to round-off at first order.
5. Diagnostics: box means, the relative constraint magnitudes [H], [M] of P1, R^NR of SPEC
   7.1 P-c, shell spectra, and per-mode Fourier amplitudes for the check A2.

To the **owner** of Track E (for the G0 stage package): fix the acceptance thresholds of SPEC
7.2-7.3 and the downgrade threshold of SCOPE section 2, choose the Courant factor (SPEC 11.2),
and decide whether the reproduction uses level-0 or level-2 backreaction first.

To **kb**: register the five sources above in the knowledge base with the locators used here.

To **Track C** (E-pre-4 partner): the noise of Track E draws one white-noise field per run at
step 0 (cell entity, one stream), then transforms; it needs no per-step draws.

## Not done in this package

- No AthenaK run: the scalar field and the sources do not exist yet (Request 1-3).
- The tables of R_k(N*), dot R_k(N*) and the background in the input format of core's initial
  data generator are not written; the format does not exist yet (Request 4).
- The 2401.08530 derivation was read for the source terms, gauge families and the BSSN form
  only (lines 585-704, 972-1031), not re-derived.
- The thesis chapters on initial data (`chap_ICNR.tex`, `chap_ICsim.tex`) and on scalar-tensor
  theories (`chap_SIbeyondGR.tex`) were only searched for parameters and costs.
