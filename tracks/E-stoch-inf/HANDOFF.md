# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0, G1 and G2 (the last two with reservations,
coord/GATES.md). G3 (tail statistics) is scoped in `spec/scope/SCOPE.md` 4d with amendments 4d.9 A1-A14; its card runs
wait in the shared queue (cards held by another partition); the processor side (reference, zeta reader) is built.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- Scope of G3: SCOPE 4d (original), 4d.9 A1-A14 (govern). Predictions: `g3/JOURNAL.md` entries 2 and 4;
  `g3/amend/JOURNAL.md` entries 5-10 (reference); `zeta/JOURNAL.md` entries 1-7 (reader).
- Reference (one-patch delta N, 128 band, `langevin/`): direct 4e6 `results/ref_inflection_n32_4e6.json`
  (E-20261125-152832-c301e92); tilted nu = 4 `results/ref_inflection_n32_tilt.json` (E-20261125-160658-855db8c,
  `scripts/ref_tilt.py`); lattice sigma = 0.1 `results/ref_inflection_n32_s01lat.json` (E-20261125-160722-a6d1f26); direct repeat `results/ref_inflection_n32_4e6rep2.json` (E-20261125-163825-ca2ebaa);
  32^3 band `results/ref_inflection_n8.json` (E-20261125-160705-5f75bb4).
- zeta reader: `zeta/zeta_reader.py` (map RK4 in phi; Z0-Z2; LM; A4 preview), record E-20261125-161456-8d3f43c.
  Its status: Z0, Z2(i), Z2(iii') pass; Z1 along Pi alone and Z2(iii) FAILED as written; ruling asked (outbox).
- Review record: `stage/REVIEW-wave3.md` Part I; open items `stage/G3/OPEN.md`; risks R38-R41 new.

## Runs in flight

| What | Where | Run id | Read by |
|---|---|---|---|
| G3P pilot (10 baseline seeds, 2 kdriver, 2 level 2; 128^3) | queue q0050 (priority 2), waiting | `nrpic-queue show q0050` | g3 reader (to extend with zeta), G3P-1..3, A8 record |
| G3C: seed 0 at s = +-1, +-1/2, +-1/4, 21 dumps | q0051 (priority 2), waiting | idem | own three-amplitude reader (R30) with A6 |
| G3R: seed 0 at s = +-1, +-1/2 on 160^3 | q0052 (priority 2), waiting | idem | Richardson reader with A7 |
| G3B00, G3B01: baseline pairs | q0053, q0054 (priority 5, after G3P) | idem | g3 reader; V and T |

Card runs are closed with `harness/bin/nrpic-run finish <run_id>`. Keep `tracks/E-stoch-inf/g3/` clean while entries
wait (the queue holds entries of a package with uncommitted files).

## Next, in order

1. The orchestrator's ruling on the reader (Z1 along Pi, Z2(iii)) and on A14; if Z1 must pass as written, a map
   along Pi in a form that does not cancel near rounding (series about the attractor, or long double).
2. Cost of the zeta map on 128^3 (R41: about 11 core-minutes per dump at 4000 steps): fewer steps with a
   Richardson check, or a table of the map along the box relation; then extend `g3/read_seed.py` with zeta.
3. When q0050 ends: cost per run into A12 (dated), A8 record of k000/k001, reader on the b and l members; then the
   remaining baseline pairs (at most six entries a session) and level 2 (16 pairs).
4. Coarse-graining bound (R39): paired-noise reference at sigma = 0.01, 0.05, 0.1 (same noise per path).
5. (done in batch 20) The independent direct repeat E-20261125-163825-ca2ebaa (NRPIC_REF_SEEDTAG=_rep2) settled the
   nu = 3 validation: pooled direct and tilted agree on both sides (g3/amend entry 12).

## Traps

- Card runs only through `harness/bin/nrpic-queue add`; production runs need `--preregistered <file>#entry-N`.
- `nrpic-run submit` refuses when its `--package` has uncommitted files (ref_spec.py and ref_tilt.py write into
  `langevin/fig` and `langevin/results`: commit them after each run).
- zeta = -R^NR at first order; a_zeta = a_map - a_R at second order (A14 (b)).
- The map's second independent integrator (DOP853 in N) is off by default: near rounding it takes millions of steps.
- A run with noise_mode_scale = s has a .modes record that already carries s (R32).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification
  suite 834-860, context protocol 957-1004.
