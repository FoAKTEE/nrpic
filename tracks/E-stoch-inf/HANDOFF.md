# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20), G1 (2026-11-21)
and G2 (2026-11-24), the last two with reservations (coord/GATES.md). G3 (tail statistics) is scoped in
`spec/scope/SCOPE.md` 4d, amended by 4d.9 (A1-A13, batch 19) before any production run; its card runs are
in the shared queue; no G3 result yet (`stage/G3/OPEN.md`).

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show && harness/bin/nrpic-queue list --owner E-stoch-inf

## Where things are

- Scope of G3: SCOPE 4d (original text, kept) and 4d.9 (amendments; they govern). Predictions: `g3/JOURNAL.md`
  entry 2 (pilot G3P-1..3, G3-C, G3-R, G3-L2) and entry 4 (amended criteria: Z0-Z2, V, T, A4, A6, A7, A8, A9).
- The independent scope review: `g3/scope_review/SCOPE_REVIEW.md`; the lead's checks of it: `g3/amend/`
  (README, JOURNAL entries 1-5: B1, B2, B3 confirmed; LB2 refuted in part; smoke runs). Review record:
  `stage/REVIEW-wave3.md` Part H.
- Reference (one-patch delta N, 128 band): `langevin/scripts/ref_spec.py` (top bin fixed, variance gate,
  state at N_f for the lattice variant, NRPIC_REF_VARIANTS filter, NRPIC_REF_SUFFIX). Corrected 2e5 pilot:
  `langevin/results/ref_inflection_n32_binfix.json` (E-20261125-151340-743c38c). The old
  `ref_inflection_n32.json` is superseded for the lattice variant.
- Floor (R28): closed (`floor/JOURNAL.md` entry 4); note updated (`repro/note/JOURNAL.md` entry 29).
- Working note of the reproduction: `repro/note/manuscript/main.pdf` (32 pages, 5056005 bytes; hook 5 MiB).

## Runs in flight

| What | Where | Run id | Read by |
|---|---|---|---|
| 4e6 direct reference (s0.01_lattice with state at N_f, s0.1), processors, 4 cores, started 07:28 PST | background on anta | E-20261125-152832-c301e92 | `harness/bin/nrpic-run finish E-20261125-152832-c301e92` (if not yet finished), then commit `langevin/results/ref_inflection_n32_4e6.json` and `langevin/fig/ref_inflection_n32_4e6_*`; judge against g3/amend/JOURNAL.md entry 5 (gate within 0.002, skewness, SM2 within 0.99-1.01, phi skewness at N_f: R35) |
| G3P pilot (10 baseline seeds, 2 kdriver, 2 level 2; 128^3) | queue q0050 (priority 2; re-entry of q0045) | from `nrpic-queue show q0050` | the g3 reader (to write); G3P-1..3 of g3/JOURNAL entry 2; A8 record of k000/k001 |
| G3C: seed 0 at s = +-1, +-1/2, +-1/4, 21 dumps with constraints | q0051 (priority 2) | idem | a three-amplitude reader of the track's own (as g2prod judge_q; risk R30) with A6 |
| G3R: seed 0 at s = +-1, +-1/2 on 160^3 | q0052 (priority 2) | idem | Richardson reader (4d.5 with A7) against the 128^3 runs of G3C |
| G3B00, G3B01: baseline mirrored pairs (minus members of 0-9, pairs 10-18) | q0053, q0054 (priority 5, after G3P) | idem | the g3 reader; V and T of entry 4 |

Card runs are closed with `harness/bin/nrpic-run finish <run_id>` (the queue does not finish them). The
queue entries hold while `tracks/E-stoch-inf/g3/` has uncommitted files: keep that package clean.

## Next, in order

1. The 4e6 run (above). If phi at N_f carries the skewness of delta N (R35), the G3 statement rests on A4
   (box d phi against the one-patch phi at N_f); write that down in g3/JOURNAL before reading the pilot.
2. Importance sampler at nu = 4 (A9): two tilted runs (bias of opposite sign), 1e5-path pilot to fix the
   shift so the tilted median lies in [3.5, 4.5] sigma_lin, validated against direct sampling at nu = 3.
3. zeta reader (4d.1 (ii)) and Z0-Z2 on processors (32^3 USR, nmax2 = 64, `usr/inputs/modes_usr_n64.txt`,
   `.work/build_cpu_v07/src/athena`); the independent homogeneous integrator for Z1; the TO VERIFY of 4d.3
   (HiggsInflection of sdn/models.py against the deck's potential and landmarks within 1e-4 in N).
4. When the pilot has run: cost per run into 4d.9 A12 (dated), then queue the remaining baseline pairs 19-127
   (14 runs a job) and level 2 (16 pairs), at most six entries a session.

## Traps

- Card runs only through `harness/bin/nrpic-queue add`; give `--package`; no own sequencers.
- `nrpic-run submit` refuses when its `--package` has uncommitted files (a run of ref_spec.py writes into
  `langevin/fig` and `langevin/results`: commit them after it, or the next langevin run is refused).
- zeta = -R^NR at first order: F_+ of zeta corresponds to F_- of R^NR (SCOPE 4d.9 A2, A3).
- varpi in `sdn/langevin.py` is dphi/dt (cosmic time), not dphi/dN.
- A run with noise_mode_scale = s has a .modes record that already carries s: read it with --scale 1 (R32).
- In the note the noise amplitude is lambda; s is the window steepness. The program's records call the
  amplitude s.
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686, verification
  suite 834-860, context protocol 957-1004.
