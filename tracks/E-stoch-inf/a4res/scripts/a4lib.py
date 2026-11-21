"""Shared definitions of package a4res (Track E): the set-ups of the pre-registered test,
the dump schedule of the code, core's linear twin (extracted from a branch into a run
directory), the even-part model of the prediction.

Set-ups (JOURNAL entry 3): SR case, input ../../ladder/inputs/sr_base.athinput, one mode
file ../../ladder/inputs/modes_n4096.txt for all, seed 20261115, four members each
(noise_mode_scale = +1, -1, +1/2, -1/2), tlim = 4.5, dump_dt = 0.125, dump_constraints =
true, dump_metric = false.  Cells per shortest source wavelength = N/sqrt(nmax2).
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
TRACK = os.path.abspath(os.path.join(PKG, ".."))
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "ladder", "scripts"))
import ladder_lib as LL  # noqa: E402

SETUPS = [
    dict(name="N64q16", N=64, nmax2=16),
    dict(name="N64q25", N=64, nmax2=25),
    dict(name="N64q36", N=64, nmax2=36),
    dict(name="N64q64", N=64, nmax2=64),
    dict(name="N128q100", N=128, nmax2=100),
    dict(name="N128q64", N=128, nmax2=64),
]
MEMBERS = [("p", 1.0), ("m", -1.0), ("ph", 0.5), ("mh", -0.5)]
TLIM = 4.5
DUMP_DT = 0.125
CFL = 0.25
L_BOX = 2.0*np.pi
BASE_INPUT = "tracks/E-stoch-inf/ladder/inputs/sr_base.athinput"
MODE_FILE = os.path.join(TRACK, "ladder", "inputs", "modes_n4096.txt")
CORE_BRANCH = "core/scalar-3"
TWIN_FILES = ["__init__.py", "rng.py", "scalar_field.py", "sf_lattice.py"]
# core's scan (git show core/scalar-3:tracks/core/interfaces/scalar_field_3.md, section 4)
CORE_SCAN = {4: 692.0, 5: 213.0, 6: 77.0, 8: 14.9, 10: 4.0, 12: 1.38, 16: 0.25}
CORE_CROSS = dict(one=12.7, tenth=18.7)


def cells(s):
    return s["N"]/np.sqrt(s["nmax2"])


def run_name(s, mem):
    return f"{s['name']}_{mem}"


# ------------------------------------------------------------------ schedule of the code
def step_times(nroot, tlim=TLIM):
    """Times of the steps of a run: dt = cfl h, the last step shortened to tlim (the
    driver of AthenaK; checked against the ladder's runs, JOURNAL entry 2)."""
    dt = CFL*L_BOX/nroot
    nfull = int(np.floor(tlim/dt*(1.0 + 1e-14)))
    t = dt*np.arange(nfull + 1)
    if tlim - t[-1] > 1e-12*tlim:
        t = np.append(t, tlim)
    return t


def dump_cycles(times, dump_dt=DUMP_DT):
    """Cycles at which <scalar_field> dump_dt writes a dump (scalar_field.cpp:381-384 at
    a58e95b): cycle 0, then the first cycle with time >= next - 1e-12 next."""
    out = [0]
    nxt = times[0] + dump_dt
    for c in range(1, times.size):
        t = times[c]
        if t >= nxt - 1e-12*abs(nxt):
            out.append(c)
            while nxt <= t*(1.0 + 1e-12):
                nxt += dump_dt
    return out


# ------------------------------------------------------------------ core's twin
def extract_twin(dest, branch=CORE_BRANCH):
    """git show the twin modules of `branch` into dest/nrpic/; returns provenance."""
    commit = subprocess.check_output(["git", "-C", REPO, "rev-parse", branch],
                                     text=True).strip()
    pkg = os.path.join(dest, "nrpic")
    os.makedirs(pkg, exist_ok=True)
    blobs = {}
    for f in TWIN_FILES:
        spec = f"{commit}:python/nrpic/{f}"
        txt = subprocess.check_output(["git", "-C", REPO, "show", spec])
        with open(os.path.join(pkg, f), "wb") as fp:
            fp.write(txt)
        blobs[f] = subprocess.check_output(["git", "-C", REPO, "rev-parse", spec],
                                           text=True).strip()
    return dict(branch=branch, commit=commit, blobs=blobs, dir=pkg)


def import_twin(dest):
    sys.path.insert(0, dest)
    for k in [k for k in sys.modules if k == "nrpic" or k.startswith("nrpic.")]:
        del sys.modules[k]
    import nrpic.sf_lattice as sl
    import nrpic.scalar_field as sf
    if not os.path.abspath(sl.__file__).startswith(os.path.abspath(dest)):
        raise RuntimeError(f"twin imported from {sl.__file__}, not from {dest}")
    return sl, sf


def potential_fns():
    m2 = LL.MASS**2
    return (lambda x: 0.5*m2*x*x, lambda x: m2*x, lambda x: m2 + 0.0*x)


class TwinSetup:
    """Core's twin (Twin and CodeTwin of nrpic.sf_lattice) for one set-up, with Track E's
    own wave vectors and amplitudes (ladder_lib.Modes, noise/ref/philox_ref.py)."""

    def __init__(self, sl, sf, s, modefile=MODE_FILE):
        self.sl, self.s = sl, s
        modes = LL.Modes(s["N"], s["nmax2"])
        self.n = modes.n
        self.alpha = modes.alpha()
        a_core = sf.mode_alpha(LL.SEED, 0, 0, self.n)
        self.alpha_core_maxdiff = float(np.abs(a_core - self.alpha).max())
        self.nc, self.inv = sl.canonical(self.n)
        self.n2f, self.r0f, self.dr0f = LL.read_modefile(modefile)
        self.v, self.dv, self.d2v = potential_fns()

    def _args(self, nroot):
        return (self.nc, nroot, L_BOX, self.v, self.dv, self.d2v, LL.PHI0, LL.PI0,
                self.n2f, self.r0f, self.dr0f)

    def rms(self, dg, it):
        hh = dg["dH"][it][self.inv]*self.alpha
        mm = dg["dM"][it][self.inv]*self.alpha[:, None]
        return (float(np.sqrt(2.0*(np.abs(hh)**2).sum())),
                float(np.sqrt(2.0*(np.abs(mm)**2).sum())))

    def code_twin(self, times, cycles):
        """CodeTwin at the steps `times` of a run; rms of the first-order H and |M| at the
        cycles, scale s = 1."""
        tw = self.sl.CodeTwin(*self._args(self.s["N"]))
        sol = tw.integrate_steps(times, cycles)
        dg = tw.diagnostics(sol)
        rows = []
        for it, c in enumerate(sol["cycle"]):
            h, m = self.rms(dg, it)
            rows.append(dict(cycle=int(c), time=float(sol["time"][it]), H=h, M=m,
                             efolds=float(sol["ln_a"][it]), hubble=float(sol["H"][it]),
                             H0_twin=float(sol["H0"][it])))
        return rows

    def twin(self, t_eval):
        """Twin (exact time integration) at the times t_eval, scale s = 1."""
        tw = self.sl.Twin(*self._args(self.s["N"]))
        sol = tw.integrate(np.asarray(t_eval, float))
        dg = tw.diagnostics(sol)
        rows = []
        for it, t in enumerate(sol["time"]):
            h, m = self.rms(dg, it)
            rows.append(dict(time=float(t), H=h, M=m, efolds=float(sol["ln_a"][it])))
        return rows


# ------------------------------------------------------------------ even-part model
def _ladder_pair(name):
    p = os.path.join(TRACK, "ladder", "results", "final", f"pair_{name}.json")
    rows = json.load(open(p))["rows"]
    rows = [r for r in rows if r["time"] <= 8.5]
    t = np.array([r["time"] for r in rows])
    he = np.array([r["H_even"]*r["Hmag"] for r in rows])
    me = np.array([r["M_even"]*r["Mmag"] for r in rows])
    hmag = np.array([r["Hmag"] for r in rows])
    return t, he, me, hmag


def _loginterp(t, tt, yy):
    t = np.clip(t, tt[0], tt[-1])
    return np.exp(np.interp(t, tt, np.log(yy)))


class EvenModel:
    """[JUDGEMENT] Prediction of the even (second-order) part, box mean removed, absolute
    rms, from the ladder's measured pairs (another mode file, same seed): while shells
    still enter, the even part is that of Q64 (k_max = 16); after the top shell K has
    entered it follows L64's (K = 8) curve shifted in time by ln(K/8):
        E(t; K) = min(E_Q64(t), E_L64(t - ln(K/8))).
    Uncertainty: a factor 2 (mode file, the time sampling of 0.5 of the ladder)."""

    def __init__(self):
        # the last dump of Q64p/Q64m and L64 pairs at t ~ 4.5 is time-mismatched in the
        # ladder (JOURNAL entry 9): drop dumps whose partner had another tlim
        self.tq, self.hq, self.mq, _ = _ladder_pair("Q64p_Q64m")
        self.tl, self.hl, self.ml, self.hmag = _ladder_pair("L64p_L64m")
        keep = self.tq < 4.4
        self.tq, self.hq, self.mq = self.tq[keep], self.hq[keep], self.mq[keep]

    def H(self, t, K):
        sh = np.log(K/8.0)
        return np.minimum(_loginterp(t, self.tq, self.hq), _loginterp(t - sh, self.tl, self.hl))

    def M(self, t, K):
        sh = np.log(K/8.0)
        return np.minimum(_loginterp(t, self.tq, self.mq), _loginterp(t - sh, self.tl, self.ml))

    def Hmag(self, t):
        return np.interp(t, self.tl, self.hmag)


class FloorModel:
    """The rounding floor of the odd parts of the ladder (floor analysis
    E-20261119-142713-32c883a, ../../ladder/results/floor/floor.json): model
    F(N, t) = odd_256(t) (N/256)^q relative to <[H]> (H) or <[M]> (M) at the dumps
    t = 0.54-3.53; extrapolated in time with the slope of its last two points."""

    def __init__(self):
        d = json.load(open(os.path.join(TRACK, "ladder", "results", "floor", "floor.json")))
        self.t = np.array(d["times"])
        self.fl = d["floor"]

    def rel(self, key, nroot, t):
        y = np.array(self.fl[key]["model"][str(nroot)])
        lt, ly = self.t, np.log(y)
        t = np.asarray(t, float)
        out = np.interp(t, lt, ly)
        lo = (ly[1] - ly[0])/(lt[1] - lt[0])
        hi = (ly[-1] - ly[-2])/(lt[-1] - lt[-2])
        out = np.where(t < lt[0], ly[0] + lo*(t - lt[0]), out)
        out = np.where(t > lt[-1], ly[-1] + hi*(t - lt[-1]), out)
        return np.exp(out)


def window(efolds, hubble, k, sharp=5.0, sigma=1.0):
    """W = (1 + tanh[s ln(sigma a H/k)])/2 of SPEC (scalar_field.md 7.3)."""
    return 0.5*(1.0 + np.tanh(sharp*np.log(sigma*np.exp(efolds)*hubble/k)))


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.bool_):
            return bool(o)
        raise TypeError(type(o))
    with open(path, "w") as fp:
        json.dump(obj, fp, indent=1, default=conv)
