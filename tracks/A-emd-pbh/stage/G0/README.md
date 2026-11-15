# stage/G0 of A-emd-pbh

The G0 stage package of Track A (decision 0012) and, since wave 2, the independent
verifier's work package.

| File | Written by | What |
|---|---|---|
| `CHECKLIST.md`, `EVIDENCE.md`, `OPEN.md` | lead (wave 1) | gate items, artefacts with run ids, what G0 still lacks |
| `VERIFIER.md` | verifier (wave 2) | independent check of eight claims of the G0/G1 material: verdicts (CONFIRMED, NOT CONFIRMED, WRONG), the three weakest points of the plan, comparison with the track's own review |
| `JOURNAL.md` | verifier | predictions written before each run, outcomes after (including the verifier's own coding errors caught before the registered runs) |
| `scripts/verify_claims.py` | verifier | the independent re-derivations V1-V6 (ball window, amplitude conventions, hoop line by quadrature, H1 timing, own construction of data set 2t with its own constraint check and broken variants, dispersion and particle number); renders two source figures of arXiv:2609.14218 for reading |

Runs of the verifier (manifests under `../../runs/<run id>/manifest.json`, outputs and
figures under `/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/`):
A-20261115-160935-41f721d (first pass), A-20261115-161239-1c41333 (second pass, the numbers of
VERIFIER.md), A-20261115-161253-e506d90 (the track's unit tests).

## Rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create --no-kokkos`):

```text
harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/A-emd-pbh/stage/G0 \
  --cores 4 --purpose "..." -- python3 tracks/A-emd-pbh/stage/G0/scripts/verify_claims.py \
  --Nmax 192 --Ntrack 256                      # 122 s in run A-20261115-161239-1c41333
harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/A-emd-pbh/stage/G0 \
  --cores 4 --purpose "..." -- python3 -B -m pytest -q -p no:cacheprovider \
  --basetemp=/data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/pytest_verifier tracks/A-emd-pbh/expball/tests
```

The script writes only into the run directory (`NRPIC_RUN_DIR`, or `--out`); `--parts V1,...`
selects parts. It reads the data set 2t table and JSON of run A-emd-pbh-20261115-130609-947c898,
the raw store of arXiv:2609.14218 (pdftoppm renders `alpha.pdf` and `thre_p0.pdf` into
`src_render/`, never to be committed), and imports `expball.mesh` and `expball.model` only for
the rerun of the track's own test (part V5, without writing bytecode into the package).

## Requests

- core: when data set 2t first runs in AthenaK (SR-1 or SR-2), report the t = 0 Hamiltonian
  and momentum norms and the sign of d(areal radius)/dt of the tracked shells over the first
  steps: the constraint test of G1 cannot tell the expanding ball from its time reverse
  (VERIFIER.md C5, limit 1), so only the evolution confirms how the code reads KL, KT and betar.
- orch (through the lead): decision 0013 states that the expanding ball holds only amplitudes
  below the comparison amplitudes of arXiv:2609.14218; at q = 2 it holds the particle bracket
  (0.045, 0.05] (VERIFIER.md C1c). The ruling can stand on other grounds (the paper's own data
  in the periodic box); its reason should be corrected.
- Harness: none; `nrpic-run submit --package` worked for all three runs.

For the lead of A-emd-pbh (not another owner; the lead edits these files): correct the H1
timing prediction of `scope/SCOPE.md` section 2 (239 t_H is contradicted by `alpha.pdf`; the
two-stage shape suggests ~250-280 t_H), the label of the finite-duration cutoff in section 3,
the inference in section 4, `RISKS.md` row 4 and the proposal to orch; add the
time-orientation limit to `stage/G1/STATUS.md` T1; consider a risk row for the G2
horizon-mass criterion against what the source paper's own test showed (VERIFIER.md C7).
