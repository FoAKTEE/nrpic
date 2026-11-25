# g3/zeta_verify: independent check of the zeta reader (decision 0041 item 1)

Helper of E-stoch-inf, batch 21 (2026-11-25), processors only, no card time. Verdict and
details: `VERIFY.md`. Predictions and outcomes: `JOURNAL.md` (entries 1-4).

| Path | What |
|---|---|
| `VERIFY.md` | the report and the verdict line |
| `JOURNAL.md` | predictions P1-P7 before each computation, outcomes after |
| `scripts/zv_lib.py` | my own reader: NRSFDMP1/2 dump parser, the deck's potential (and two test potentials), FKG integrator in e-folds (long-double RK4, fixed step, end surface by a Newton-solved last step), first and second variational equations and the end-surface map derivatives, R^NR per cell |
| `scripts/test_closed.py` | P1, P2: closed forms (exponential potential off the attractor; Hamilton-Jacobi attractor) |
| `scripts/analyse_pairs.py` | P3-P7 on the 32^3 mirrored pairs: Z0, Z2, the map along the field, the momentum and the box relation (exact and finite differences), round-off floor, end-surface choice, one-point error |
| `scripts/compare_lead.py` | step 4: my map at the lead's Z1 state against `zeta/zeta_reader.py`'s numbers |
| `results/*.json` | copies of the registered outputs (closed_form, pairs, compare_lead) |
| `fig/*.png` | the figures, each looked at |

Runs (manifests in `../../runs/<id>/`, outputs in `scratch/E-stoch-inf/<id>/`):
E-20261125-170519-fa5ad33 (closed forms), E-20261125-172002-6890cad (pairs, about 9 min on one
core), E-20261125-173127-4dcc4ee (comparison). Input data: the pairs of run
E-20261125-153148-cfad424 (lead's), the deck `usr/inputs/usr_base.athinput`.

How to rerun (from the worktree root, `.venv` present):

    harness/bin/nrpic-run submit --kind scouting --gate G3 --purpose "..." \
      --package tracks/E-stoch-inf/g3/zeta_verify --cores 1 -- \
      python3 tracks/E-stoch-inf/g3/zeta_verify/scripts/test_closed.py '$NRPIC_RUN_DIR'
    ... -- python3 tracks/E-stoch-inf/g3/zeta_verify/scripts/analyse_pairs.py \
      /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261125-153148-cfad424 \
      tracks/E-stoch-inf/usr/inputs/usr_base.athinput '$NRPIC_RUN_DIR'
    ... -- python3 tracks/E-stoch-inf/g3/zeta_verify/scripts/compare_lead.py \
      /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261125-161456-8d3f43c/zeta_tests.json \
      /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261125-172002-6890cad/pairs.json \
      tracks/E-stoch-inf/usr/inputs/usr_base.athinput '$NRPIC_RUN_DIR'

## Requests

To the lead of E-stoch-inf (no other owner is concerned):
1. Record Z1 along the momentum alone as "reference below its precision at eps = box rms"
   rather than as a reader failure, with the variational coefficients of
   `results/pairs.json` (`map`) and `results/compare_lead.json` (`exact_at_lead_state`) as the
   expected values; or rewrite Z1's reference as a long-double or variational one. A float64
   integration of the absolute field in N has a round-off floor of 4-5e-10 in N
   (E-20261125-172002-6890cad), above the 6.7e-10 second-order change it is asked to resolve.
2. Take the expected values of the tests (Z1 state, a_map of Z2(iii), (iii')) at the box's own
   background (the lockstep record at N_f) rather than at the own DOP853 background, which lies
   0.03 e-folds away; a_map differs by 2.1e-4 relative between the two. Not needed for any
   verdict at the present bars.
3. Before the G3 reading: a check of the reader's map at G3 amplitudes (zeta up to about 2.5,
   sigma_lin = 0.494), which this package did not make (the pairs reach zeta 0.17): for example
   the lead's map_rk4 against `zv_lib.efolds_to_surface` on states along the box relation out to
   +-3 e-folds.
