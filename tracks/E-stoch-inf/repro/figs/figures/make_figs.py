"""Make every figure of arXiv:2512.14649 from the outputs of the registered dump passes (runs.py groups).

Usage (inside a registered run):
  make_figs.py OUT --usr256 PASSRUN [--sr256 PASSRUN] [--rsf256 PASSRUN ...] [--ablation PASSRUN]
               [--rungs PASSRUN] [--cl256s PASSRUN] [--al2s PASSRUN]
PASSRUN is the output directory of a registered dump pass; the label subdirectories inside it are
found by name. Figures and their json numbers go to OUT; nothing is read off P1's figures.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(args):
    print(" ".join(args), flush=True)
    subprocess.run([PY] + args, check=True)


def sub(passrun, label):
    p = os.path.join(passrun, label)
    return p if os.path.isdir(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--usr256")
    ap.add_argument("--usr256kt", help="pass of group usr256kt (Fig. 6b with the invariant Kt)")
    ap.add_argument("--sr256", help="pass with P256v6 (all dumps)")
    ap.add_argument("--rsf256", action="append", default=[],
                    help="passes with RSF256 and its continuation (labels RSF256, RSF256c)")
    ap.add_argument("--ablation")
    ap.add_argument("--rungs")
    ap.add_argument("--cl256s", action="append", default=[])
    ap.add_argument("--al2s", action="append", default=[])
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    F = lambda n: os.path.join(HERE, n)  # noqa: E731
    run([F("fig1_meanrolls.py"), out])
    if a.usr256:
        p = sub(a.usr256, "USF256")
        run([F("fig_contrasts.py"), "--pass", p, "--case", "usr", "--name", "fig4_usr_contrast",
             "--out", out, "--title", "Inflection, USF256 (256^3)", "--con", "USF256"])
        run([F("fig_contrasts.py"), "--pass", p, "--case", "usr", "--name",
             "fig4_usr_contrast_hzero", "--out", out, "--hzero",
             "--title", "Inflection, USF256, box mean of H removed"])
        run([F("fig_spectra.py"), "--pass", p, "--case", "usr", "--kind", "R", "--name",
             "fig5_usr_spec", "--out", out, "--title", "Inflection, USF256"])
        pk = sub(a.usr256kt, "USF256") if a.usr256kt else p
        run([F("fig_spectra.py"), "--pass", pk, "--case", "usr", "--kind", "K", "--name",
             "fig6b_usr_Kspec", "--out", out, "--title", "Inflection, USF256"])
    sr_passes = []
    for r in a.rsf256:
        for lab in ("RSF256", "RSF256c"):
            if sub(r, lab):
                sr_passes.append(sub(r, lab))
    if a.sr256 and sub(a.sr256, "P256v6"):
        p = sub(a.sr256, "P256v6")
        run([F("fig_contrasts.py"), "--pass", p, "--case", "sr", "--name",
             "fig2_sr_contrast_P256v6", "--out", out, "--title", "Quadratic, P256v6 (256^3)"])
        run([F("fig_spectra.py"), "--pass", p, "--case", "sr", "--kind", "R", "--name",
             "fig3_sr_spec_P256v6", "--out", out, "--title", "Quadratic, P256v6"])
        run([F("fig_spectra.py"), "--pass", p, "--case", "sr", "--kind", "K", "--name",
             "fig6a_sr_Kspec_P256v6", "--out", out, "--title", "Quadratic, P256v6"])
    if sr_passes:
        args = []
        for p in sr_passes:
            args += ["--pass", p]
        run([F("fig_contrasts.py")] + args + ["--case", "sr", "--name", "fig2_sr_contrast",
                                              "--out", out, "--title", "Quadratic, RSF256 (256^3)",
                                              "--con", "RSF256"])
        run([F("fig_spectra.py")] + args + ["--case", "sr", "--kind", "R", "--name", "fig3_sr_spec",
                                            "--out", out, "--title", "Quadratic, RSF256"])
        run([F("fig_spectra.py")] + args + ["--case", "sr", "--kind", "K", "--name",
                                            "fig6a_sr_Kspec", "--out", out,
                                            "--title", "Quadratic, RSF256"])
    conv = [F("fig_conv.py"), "--out", out]
    if a.rungs:
        for lab in ("C32S", "C64S", "C128S"):
            conv += ["--rung", f"{lab}={sub(a.rungs, lab)}"]
    for r in a.cl256s:
        if sub(r, "CL256Sc"):
            conv += ["--rung", f"CL256S={sub(r, 'CL256Sc')}", "--with256"]
    run(conv)
    if a.ablation:
        npz = []
        for lab in ("AL0S", "AL1S", "AL0U", "AL1U", "AL2U", "RL1", "UL1", "U256ap"):
            if sub(a.ablation, lab):
                npz += ["--npz", f"{lab}={sub(a.ablation, lab)}"]
        if a.sr256 and sub(a.sr256, "P256v6"):
            npz += ["--npz", f"P256v6={sub(a.sr256, 'P256v6')}"]
        for r in a.al2s:
            if sub(r, "AL2Sc"):
                npz += ["--npz", f"AL2S={sub(r, 'AL2Sc')}"]
        run([F("fig_ablation.py"), "--out", out] + npz)


if __name__ == "__main__":
    main()
