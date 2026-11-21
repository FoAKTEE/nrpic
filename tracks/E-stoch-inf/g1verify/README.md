# g1verify: independent verifier of Track E's G1 material

Helper package of E-stoch-inf, wave 3 (decision 0016 item 4; item C16 of the G1 checklist).
The verifier did not produce the G1 material: the slow-roll (SR) case of arXiv:2512.14649
in this repository's AthenaK (core/scalar-2 a58e95b executables), ladder 32^3-256^3. It
recomputed every G1 quantity with its own code from the registered raw outputs and wrote the
verdicts into `VERIFIER.md` (the lead copies it into `stage/G1/`). Status: complete
(2026-11-20/21); V1-V7 CONFIRMED, strict A4 FAILS, A4' passes with (d) read on the maxima.

## Contents

| Path | What |
|---|---|
| `VERIFIER.md` | the report: runs, verdicts V1-V7, summary against the G1 criterion, weak points, A4 against A4', comparison with the track |
| `JOURNAL.md` | predictions before each run, outcomes after (failed ones included), entries 0-7 |
| `scripts/nrsf.py` | own reader of NRSFDMP2 and NRSFDMP1 dumps and of the .hst records (sequential reads, no memmap) |
| `scripts/alpha.py` | own Philox-4x64-10 and polar Box-Muller: the frozen amplitudes alpha_n |
| `scripts/ref.py` | own background (potential-position fixing; code units), Bunch-Davies modes, full and deformed (BZ) Mukhanov-Sasaki, window, crossing times |
| `scripts/rnr.py` | own R^NR extraction (TH appendix.tex:517-520) and mode coefficients |
| `scripts/catalog.py` | run names -> run ids, directories and options from the ladder lists |
| `scripts/check_infra.py` | C0: tools checked against core's reader, numpy's Philox, core's alpha twin, the deck, the mode files; slice at t = 0 |
| `scripts/permode.py` | passes over the p-run dumps: R^NR per mode and box means, sha256 of each dump |
| `scripts/v123.py` | V1 (background), V2 (per mode, spectrum), V3 (freezing) |
| `scripts/constraints.py`, `v45.py`, `v45_addendum.py` | V4/V5: odd/even parts of H and M_i, bands, halving, controls, records, strict A4 and A4', orders, floor |
| `scripts/v6.py` | V6: Richardson orders from the Courant runs |
| `scripts/v7.py`, `a7_layout_restart.sh`, `v7_g1exe.py` | V7: bit-identity of the noise unit test; the G1 executable rerun with 8 MeshBlocks and from a restart, compared bit for bit; cost |
| `scripts/fig_v1.py` ... `fig_v7.py`, `make_figs.sh` | one script per figure; the driver |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `fig/fig_v*.png, .pdf` | the figures (each looked at) |
| `results/*.json` | the JSON outputs copied from the run directories (sha256 in each run's `sha256sums.txt`) |

## How to rerun

Every step is a registered run (`harness/bin/nrpic-run submit --package
tracks/E-stoch-inf/g1verify --kind scouting --gate G1 --launcher local --cores N -- bash -c
'... "$NRPIC_RUN_DIR" ...'`); the exact command of each is in its manifest
`tracks/E-stoch-inf/runs/<run_id>/manifest.json`, the outputs in
`scratch/E-stoch-inf/<run_id>/`. Python: the worktree's `.venv` (`harness/bin/nrpic-env
create --no-kokkos`). Order and inputs:

1. `check_infra.py OUT` (E-20261120-222844-dbca87f)
2. `permode.py OUT P256 L256p` (E-20261120-223154-d42de1a, 31 min, ~45 GB read) and
   `permode.py OUT L32p L64p L128p Q64p Q128p L64p_proc` (E-20261121-025750-d1b6139)
3. `v123.py OUT <dir of 2a> <dir of 2b>` (E-20261121-030207-fb6f090)
4. `constraints.py OUT --verified E-20261115-172618-f948386` (E-20261121-030657-c1afe38, 12 min,
   ~60 GB read), then `v45.py OUT <dir of 4>` (E-20261121-031951-82984f8)
5. `v6.py OUT` (E-20261121-030522-c6907b6); `v7.py OUT` (E-20261121-030520-5a23d64)
6. `bash a7_layout_restart.sh <core_scalar-2 athena_cpu> OUT` (E-20261121-031049-27cdc06, 1 core,
   98 s), then `v7_g1exe.py OUT <dir of 6>` (E-20261121-031251-c48670d)
7. `make_figs.sh OUT` (E-20261121-032413-0672bf9): figures and the V4/V5 addendum; copy
   `fig_v*` into `fig/`.

## Requests

- To the lead of E-stoch-inf: correct `stage/G1/STATUS.md` where it quotes numbers of
  `ladder/results/final/` that come from time-mismatched dumps (P256 odd/even 385 -> 25 from
  `final2`; halving entries 16.0, 9.0 at the last dump) and its A1 maxima (phi 2.0e-12, K
  3.6e-12, not 1.1e-12 and 2.0e-12); say that the "4e4-1.5e5" separation of the negative
  control is the best case (minimum 89-179 at the end of the entry). Details: `VERIFIER.md`,
  last section.
- To the orchestrator: the ruling on A4' (paragraph "For the orchestrator's ruling" of
  `VERIFIER.md`): rule A4' in with (d) read on the maxima over the entry and the floor named
  as the part that does not scale with s; keep the strict A4 on record as failed.
- To core: layout and restart invariance of the G1 executable is now checked on processors
  at 32^3 (V7c); the card build and the rank count are not. A release of scalar-2 would remove
  the scouting caveat.
- Open [TO VERIFY]: why the absolute constraint levels are 40-100 times below P1's
  statements (~1e-10, ~1e-5) while the control/proper ratio matches.
