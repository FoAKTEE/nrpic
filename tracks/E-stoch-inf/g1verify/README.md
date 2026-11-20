# g1verify: independent verifier of Track E's G1 material

Helper package of E-stoch-inf, wave 3 (decision 0016 item 4; item C16 of the G1 checklist).
The verifier did not produce the G1 material: the slow-roll (SR) case of arXiv:2512.14649
in this repository's AthenaK (core/scalar-2 a58e95b executables), ladder 32^3-256^3. It
recomputes every G1 quantity with its own code from the registered raw outputs and writes
the verdicts into `VERIFIER.md` (the lead copies it into `stage/G1/`).

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | the report: verdicts V1-V7, weak points, A4 against A4', comparison with the track |
| `JOURNAL.md` | predictions before each run, outcomes after (failed ones included) |
| `scripts/nrsf.py` | own reader of NRSFDMP2 dumps and the .hst records (sequential reads, no memmap) |
| `scripts/alpha.py` | own Philox-4x64-10 and polar Box-Muller: the frozen amplitudes alpha_n |
| `scripts/ref.py` | own background (P2 potential-position fixing; code units), Bunch-Davies modes, full and deformed (BZ) Mukhanov-Sasaki, window |
| `scripts/rnr.py` | own R^NR extraction (TH appendix.tex:517-520) and mode coefficients |
| `scripts/catalog.py` | run names -> run ids, directories and options from the ladder lists |
| `scripts/check_infra.py` | C0: tools checked against core's reader, numpy's Philox, the inputs, the slice at t = 0 |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `fig/`, `results/` | figures (each looked at) and the JSON summaries copied from the run directories |

The scripts are filled in as the package proceeds; see the runs table of `VERIFIER.md`.

## How to rerun

Every analysis is a registered run (`harness/bin/nrpic-run submit --package
tracks/E-stoch-inf/g1verify --kind scouting --gate G1 --launcher local --cores 4 ...`); the
command of each is in its manifest `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, the
outputs in `scratch/E-stoch-inf/<run_id>/`. Python: the worktree's `.venv`
(`harness/bin/nrpic-env create --no-kokkos`); `OMP_NUM_THREADS=4`.

## Requests

None yet.
