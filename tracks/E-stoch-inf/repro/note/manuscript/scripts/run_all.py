"""Make every figure and table of the working note in one registered run.

Usage: run_all.py OUT
1. make_figs.py OUT/lattice: the figures of the lattice paper from the registered dump passes
   and records (the same arguments as the figure run E-20261124-230839-0e1e13a: the continued
   runs, 256^3 rung and SR level 2 at N_f from pass E-20261124-213029-e937f69, joined records of
   join check E-20261124-212343-7e9c4b2 through runs.py; the SR run with dumps to its end from
   pass E-20261124-225826-0bf3842, joined in E-20261124-225720-444aecc);
2. analyse.py SIM OUT/langevin: the one-patch figures from simulation E-20261123-021043-d00a314;
3. schem_pipeline.py, schem_ladder.py: the schematics;
3a. the G2 figures into OUT/g2: fig_g2_halving.py (judge E-20261123-024359-5dc3213, quarter pair
   E-20261125-033450-4c4a31c, the verifier's E-20261125-023427-6fb6400), fig_g2_resolution.py (the
   same judge), fig_g2_mosaic.py (last dump of the release run E-20261121-211214-0377aab);
4. ledger.py OUT: the ledger tables;
5. copies of the figures under the manuscript's names into OUT/figures;
6. checks: the lattice jsons against the committed jsons of the figure package and the
   one-patch numbers against the committed langevin.json (OUT/checks.json).
Then copy OUT/figures/* to manuscript/figures/ and OUT/tables/* to manuscript/tables/.
"""
import filecmp
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
TRACK = os.path.abspath(os.path.join(HERE, *[".."] * 4))
S = "/data/haiyangw/nrpic/scratch/E-stoch-inf/"
SIM = S + "E-20261123-021043-d00a314"
LATTICE_ARGS = [
    "--usr256", S + "E-20261124-130628-6790851",
    "--usr256kt", S + "E-20261124-141807-8352509",
    "--usr256kt", S + "E-20261124-172949-8b2255b",
    "--sr256", S + "E-20261124-133251-42e8aab",
    "--ablation", S + "E-20261124-133251-42e8aab",
    "--rungs", S + "E-20261124-133251-42e8aab",
    "--ablation75", S + "E-20261124-141807-8352509",
    "--cl256s", S + "E-20261124-213029-e937f69",
    "--al2s", S + "E-20261124-213029-e937f69",
    "--rsf256", S + "E-20261124-225826-0bf3842",
]
FIGS = {  # manuscript name: source (without extension)
    "fig_pipeline": "figures_raw/schem_pipeline",
    "fig_background": "lattice/fig1_meanrolls",
    "fig_spec_sr": "lattice/fig3_sr_spec_P256v6",
    "fig_spec_usr": "lattice/fig5_usr_spec",
    "fig_contrast_sr": "lattice/fig2_sr_contrast",   # all six rows, from the SR run with dumps to N_f
    "fig_contrast_usr": "lattice/fig4_usr_contrast",
    "fig_kspec_sr": "lattice/fig6a_sr_Kspec_P256v6",
    "fig_kspec_usr": "lattice/fig6b_usr_Kspec",
    "fig_specconv": "lattice/fig7_specconv",
    "fig_constraints": "lattice/fig8_convergence",
    "fig_ablation": "lattice/fig9_ablation",
    "fig_ablation_sr": "lattice/fig9_ablation_sr_t75",
    "fig_signflip": "lattice/fig_signflip",
    "fig_ladder": "figures_raw/schem_ladder",
    "fig_g2_mosaic": "g2/fig_g2_mosaic",
    "fig_g2_resolution": "g2/fig_g2_resolution",
    "fig_g2_halving": "g2/fig_g2_halving",
    "fig_lv_background": "langevin/fig/fig_background",
    "fig_lv_step": "langevin/fig/fig_step_seed",
    "fig_lv_paths": "langevin/fig/fig1_paths_ito_naive",
    "fig_lv_scheme": "langevin/fig/fig_scheme",
    "fig_lv_pdfs": "langevin/fig/fig3_pdfs_ito_naive",
    "fig_lv_logpdfs": "langevin/fig/fig4_logpdfs_ito_naive",
}


def run(args):
    print(" ".join(args), flush=True)
    subprocess.run([PY] + args, check=True)


def strip(d):
    if isinstance(d, dict):
        return {k: strip(v) for k, v in d.items() if k != "simdir"}
    if isinstance(d, list):
        return [strip(v) for v in d]
    return d


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    run([os.path.join(HERE, "make_figs.py"), os.path.join(out, "lattice")] + LATTICE_ARGS)
    run([os.path.join(HERE, "analyse.py"), SIM, os.path.join(out, "langevin")])
    run([os.path.join(HERE, "schem_pipeline.py"), "--out", os.path.join(out, "figures_raw")])
    run([os.path.join(HERE, "schem_ladder.py"), "--out", os.path.join(out, "figures_raw")])
    for script in ("fig_g2_halving.py", "fig_g2_resolution.py", "fig_g2_mosaic.py"):
        run([os.path.join(HERE, script), os.path.join(out, "g2")])
    run([os.path.join(HERE, "ledger.py"), out])
    fdir = os.path.join(out, "figures")
    os.makedirs(fdir, exist_ok=True)
    for name, src in FIGS.items():
        done = False
        for ext in (".pdf", ".png"):
            p = os.path.join(out, src + ext)
            if os.path.exists(p):
                shutil.copy(p, os.path.join(fdir, name + ext))
                done = True
        if not done:
            sys.exit(f"missing figure {src}")
    # checks (journal entry 1, P1 and P2)
    checks = {"lattice_json_equal": {}, "langevin_equal": None}
    ref = os.path.join(TRACK, "repro", "figs", "fig")
    for fn in sorted(os.listdir(ref)):
        if fn.endswith(".json"):
            p = os.path.join(out, "lattice", fn)
            checks["lattice_json_equal"][fn] = (os.path.exists(p)
                                                and filecmp.cmp(p, os.path.join(ref, fn), shallow=False))
    a = strip(json.load(open(os.path.join(out, "langevin", "langevin.json"))))
    b = strip(json.load(open(os.path.join(TRACK, "repro", "langevin", "results", "langevin.json"))))
    checks["langevin_equal"] = a == b
    with open(os.path.join(out, "checks.json"), "w") as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks, indent=1))


if __name__ == "__main__":
    main()
