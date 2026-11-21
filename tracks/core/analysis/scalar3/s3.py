"""Helpers of the test drivers of the third scalar-field package (tracks/core/
JOURNAL-scalar3.md): the helpers of the second package (paths, running the executable,
figure style), the two test cases of arXiv:2512.14649 in code units, the run directory
of a registered run, and the extraction of the curvature perturbation from a dump."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scalar2"))

import common                                   # noqa: E402
from common import inf, np                      # noqa: E402,F401
from nrpic import scalar_field as sf            # noqa: E402

SEED = 20261115
LENGTH = 2.0*np.pi
SYM = (("gxx", 0, 0), ("gxy", 0, 1), ("gxz", 0, 2), ("gyy", 1, 1), ("gyz", 1, 2),
       ("gzz", 2, 2))


def run_dir(arg=None):
    """Output directory: the argument, or $NRPIC_RUN_DIR of a registered run (nrpic-run
    starts its command without a shell, so the variable is read here)."""
    out = arg or os.environ.get("NRPIC_RUN_DIR")
    if not out or "$" in out:
        raise SystemExit("no output directory: give --out or run under nrpic-run")
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    return out


def case(name, nmax2, kstart=None):
    """The quadratic ("sr") or the inflection ("usr") case in code units."""
    model = inf.quadratic_model() if name == "sr" else inf.inflection_model()
    return inf.code_case(model, nmax2, kstart=kstart)


def dumps(rundir, base):
    """Dumps of a run by cycle."""
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, base + ".sf.?????.dump"))):
        d = sf.read_dump(f)
        d["file"] = f
        out[int(d["cycle"])] = d
    return out


def rnr_of_dump(d, n, n2):
    """Curvature perturbation of every mode of the hemisphere from a dump with the
    metric: R^NR_n = psi_n + (H/Pi_b) delta phi_n with psi_n = (a^2 chi_n - 1)/2 +
    (1/4) n_i n_j (gt_ij - delta_ij)_n/n^2 and the box means H = -<K>/3, Pi_b = <Pi>,
    a^2 = 1/<chi> (journal of the second package, test T8).  Returns (rnr, means)."""
    fl = d["fields"]
    chib = fl["chi"].mean()
    hub = -fl["K"].mean()/3.0
    pib = fl["Pi"].mean()
    psi, _ = sf.analyse(0.5*(fl["chi"]/chib - 1.0), n)
    nn = n.astype(float)
    for name, i, j in SYM:
        c, _ = sf.analyse(fl[name] - (1.0 if i == j else 0.0), n)
        psi = psi + 0.25*(1.0 if i == j else 2.0)*nn[:, i]*nn[:, j]*c/n2
    dphi, _ = sf.analyse(fl["phi"] - fl["phi"].mean(), n)
    means = dict(chi=chib, H=hub, Pi=pib, phi=fl["phi"].mean(),
                 alpha=fl["alpha"].mean())
    return psi + (hub/pib)*dphi, means


def lock_reference(dumpfile, n2, windowed=True):
    """Coarse-grained linear solution L^(-3/2) W R of every mode (without alpha_n) from
    the lockstep record next to a dump, and the header of the record."""
    head, tab = sf.read_modes(dumpfile.replace(".dump", ".modes"))
    sh = tab[:, 0].astype(int)
    idx = np.searchsorted(sh, n2)
    r = (tab[:, 1] + 1j*tab[:, 2])[idx]
    w, _ = inf.window(n2, LENGTH, head["a"], head["H"], head["eps1"])
    if not windowed:
        w = np.ones(n2.size)
    return LENGTH**-1.5*w*r, w, head, tab


def rms(x):
    return float(np.sqrt(np.mean(np.abs(x)**2)))
