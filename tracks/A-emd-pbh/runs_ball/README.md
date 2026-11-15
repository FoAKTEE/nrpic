# runs_ball: first full-relativity runs of Track A (SR-1, SR-2)

Helper package of A-emd-pbh, wave 2 (2026-11-15). The expanding dust ball of data set 2t
(expball smoothed top-hat core, Delta = 1 inside R1 = 2.4 M, compensated at 6 M, inside an
Einstein-de Sitter ball with H R_b = 0.5 and a C^4 taper; run
A-emd-pbh-20261115-130609-947c898) evolved with the release executables of core-v0.3 and
compared with the exact solution (`expball/exact.py`) in invariants only. Specification:
`stage/G1/STATUS.md` section 3. Predictions and outcomes: `JOURNAL.md`.

## What is here

| file | content |
|---|---|
| `common.py` | model of data set 2t, readers of trajectories, histories, formatted-table lines, horizon summaries, snapshots; areal radius and Misner-Sharp mass in spherical symmetry |
| `prep.py` | reorders the lattice particles so that the tracked ones come first (tag = position); exact references per tracked particle and global (turnaround, trapping, crunch, horizon mass on slices of constant proper time m_AH(tau), central a(tau) and rho_c(tau)); step plan of SR-1 from the exact coordinate speed of light |
| `compare.py` | the comparison: areal radius against proper time per particle, turnaround, trapping (R = 2m) and crunch times, Misner-Sharp mass on the x axis, trapped cells, finder mass against the exact horizon mass of the same slice, central lapse and density, constraints, gauge maps; numbers JSON and five figures per run |
| `sr1.athinput`, `sr2.athinput` | input decks (dx = M/2; dx = M by command-line overrides) |
| `run_cpu.sh` | processor driver: SR-1 with its restart segments, or SR-2, at one resolution |
| `figs/` | copies of the PNG figures (each looked at; see JOURNAL) |

## How to rerun

    cd /data/haiyangw/nrpic/wt/A-emd-pbh
    harness/bin/nrpic-run submit --kind scouting --gate G2 --purpose "..." --cores 4 -- \
        .venv/bin/python tracks/A-emd-pbh/runs_ball/prep.py --out '$NRPIC_RUN_DIR'
    # processors, dx = M:
    tracks/A-emd-pbh/runs_ball/run_cpu.sh sr1 <prep dir> <n_track> 128 32 <out dir>
    # cards, dx = M/2: a batch list with lines
    #   sr1 tracks/A-emd-pbh/runs_ball/sr1.athinput particles/particle_file=<prep>/..._track.nrp particles/traj_ntrack=<n>
    # then restarts from <run dir>/sr1/rst/ball.00001.rst with time/cfl_number and time/tlim (README section below)
    .venv/bin/python tracks/A-emd-pbh/runs_ball/compare.py --prep <prep dir> --seg <dir> [--seg <dir>] \
        --gauge sr1 --dx 0.5 --label <name> --out <dir> --figdir tracks/A-emd-pbh/runs_ball/figs

Run ids, outcomes and what is open: `JOURNAL.md`; the summary below is filled in at the
end of the session.

## Requests

(filled in at the end of the session)
