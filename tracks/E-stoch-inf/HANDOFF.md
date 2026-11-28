# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0, G1 and G2 (the last two with reservations,
coord/GATES.md). G3 (tail statistics of zeta, SCOPE 4d with amendments 4d.9 A1-A14) is read on 71 of 128 mirrored pairs:
the tail shape agrees with one-patch delta N, the variance differs (+0.28 +- 0.07 per cent, (V) failed as written).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- Scope of G3: `spec/scope/SCOPE.md` 4d and 4d.9 (A13: what "G3 met" means: 128 pairs, (V), (T), A4, level 2 reported,
  fresh verifier).
- Predictions and outcomes: `g3/JOURNAL.md` entries 2, 4 (criteria), 14-18 (this batch: preemptions, the 71-pair reading).
- Readers: `g3/read_pilot.py` (per box; `--map table --msteps 4000 --save-fields`), `g3/pairs_g3.py` (pairs against the
  reference; figures), `g3/check_lists.py` (run on every list), `g3/inputs/gen_lists.py` (lists base07-11, l2_01-02).
- Note: `repro/note/manuscript/main.tex` section V (G3), scripts `fig_g3_mosaic.py`, `schem_ladder_g3.py`, G3 rows in
  `ledger.py`, step 3b in `run_all.py` (constants G3READ, G3PAIRS at its top: change G3PAIRS to the new pair run).
- Review record: `stage/REVIEW-wave3.md` part L; open items `stage/G3/OPEN.md`; checklist `stage/G3/CHECKLIST.md`.

## Card jobs of this owner (shared queue, priority 2; all on .work/build_gpu_v07 as SCOPE 4d fixes)

| Entry | What | State at 16:40 PST | Read by |
|---|---|---|---|
| q0079 G3B07b | m071 + pairs 72-81 | running (job 5537) | read_pilot.py --save-fields |
| q0080-q0082 G3B08b-G3B10b | pairs 82-92, 93-103, 104-114 | pending in Slurm (5538, 5540, 5541) | idem |
| q0083 G3B11b | pairs 115-125 | waiting | idem |
| q0084 G3L00b | level-2 pairs 0-4 + k000/k001 | waiting | idem (C6-2, C6-4, A8) |
| q0087 G3L01b, q0088 G3L02b | level-2 pairs 5-10; 11-15 + baseline 126-127 | waiting | idem |

Preemption is frequent (another user's partition "priority"): a job cut early is closed with `nrpic-run finish <id>
--status stopped`, its finished members are kept, the rest re-listed with the same seeds (entry 14) and queued again.

## Next, in order

1. As jobs end: `nrpic-run finish <run_id>`; read with `nrpic-run submit --kind production --gate G3 --preregistered
   tracks/E-stoch-inf/g3/JOURNAL.md#entry-15 --package tracks/E-stoch-inf/g3 --launcher local --cores 3 -- python3
   tracks/E-stoch-inf/g3/read_pilot.py '$NRPIC_RUN_DIR' --run <card run dir> --deck tracks/E-stoch-inf/g2prod/inputs/
   usr_prod.athinput --lead-json <scratch>/E-20261125-161456-8d3f43c/zeta_tests.json --members <labels> --procs 3 --map
   table --msteps 4000 --save-fields`; then `pairs_g3.py` with every reading run and `--pairs 0-127` (prediction entry
   first: entry 4 stands; write the expected variance excess and what would change it).
2. Level 2 against level 0 on the same pairs (a small addition to pairs_g3.py: paired differences of F, skewness, kurtosis);
   A4 from the saved fields (variance and skewness of d phi, d Pi at N_f against the reference's state_Nf columns).
3. The variance difference: sigma-paired reference at sigma = 0.01, 0.05, 0.1 (R39) and, if cards allow, a 160^3 subset.
   Then the fresh verifier and `harness/bin/nrpic-stage verify E-stoch-inf G3 --full` (detached).

## Traps

- AthenaK takes command-line overrides only for lines the deck has: run check_lists.py on every list.
- Bars below about 1e-9 against map_rk4 fail on round-off (R43); P5-3 fails that way on every box.
- `nrpic-run submit` refuses a dirty package: commit before a registered run (the note build uses --package repro/note).
- The note PDF is near the 5 MB hook limit; it was passed through ghostscript (/prepress) this batch.
- zeta = -R^NR at first order; F_+ of zeta corresponds to F_- of R^NR (A2).
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification suite
  834-860, context protocol 957-1004.
