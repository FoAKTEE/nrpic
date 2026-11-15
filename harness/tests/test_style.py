#!/usr/bin/python3 -I
"""Self-test of the vendored figure libraries harness/style/ (brief section 13.4).

    python3 -I harness/tests/test_style.py

Checks SHA256SUMS and the sources (vendor.py --check), that the style sheet equals czstyle.RC, and
renders two data figures (czstyle: line plot with band, slice mosaic with zoom boxes) and one
schematic (paperfig: architecture with the status legend) in a scratch worktree's venv; czstyle's
overflow check must print nothing. The PNGs are left in the scratch repository to be looked at.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

RC_CHECK = r'''
import matplotlib as mpl, matplotlib.pyplot as plt
import czstyle
plt.style.use("cyclic_zoom.mplstyle")
bad = [(k, mpl.rcParams[k], v) for k, v in czstyle.RC.items() if mpl.rcParams[k] != mpl.RcParams({k: v})[k]]
print("RCBAD", bad)
'''


def main():
    c = F.Checks("vendored figure libraries")
    r = F.sh(["python3", "-I", os.path.join(F.LIVE, "harness", "style", "vendor.py"), "--check"], check=False)
    c.ok(r.returncode == 0, "vendor.py --check: SHA256SUMS and sources agree", r.stdout + r.stderr)
    fx = F.make_repo("test-style", owners=("A-emd-pbh",))
    A = fx["wt"]["A-emd-pbh"]
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-env"), "create", "--no-kokkos"], check=False, timeout=900)
    c.ok(r.returncode == 0, "venv for the figure scripts", r.stderr[-1000:])
    note = F.seed_note(A, "A-emd-pbh")
    scripts = os.path.join(note, "scripts")
    open(os.path.join(scripts, "rc_check.py"), "w").write(RC_CHECK)
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-env"), "exec", "--cwd", scripts, "--", "python", "rc_check.py"],
             check=False)
    c.ok("RCBAD []" in r.stdout, "cyclic_zoom.mplstyle reproduces czstyle.RC", r.stdout + r.stderr)
    os.remove(os.path.join(scripts, "rc_check.py"))
    res = F.run_note_scripts(A, "A-emd-pbh")
    for fn, rr in res.items():
        c.ok(rr.returncode == 0 and "cut at the figure edge" not in rr.stdout,
             f"{fn} runs and czstyle reports no label cut at the figure edge", rr.stdout + rr.stderr)
    figs = os.path.join(note, "figures")
    for stem, exts in (("fig_style_lines", ("pdf", "png")), ("fig_style_mosaic", ("pdf", "png")),
                       ("schem_architecture", ("png", "svg"))):
        c.ok(all(os.path.isfile(os.path.join(figs, f"{stem}.{e}")) for e in exts), f"{stem}: {' + '.join(exts)} written")
    print("figures to look at:\n  " + "\n  ".join(os.path.join(figs, f) for f in sorted(os.listdir(figs)) if f.endswith(".png")))
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
