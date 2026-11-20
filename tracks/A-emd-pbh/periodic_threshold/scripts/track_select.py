"""Reorder a particle file of make_peak_ic.py so that chosen particles come first and are
tracked by the code (tag = position in the file, `<particles> traj_ntrack`; reader in
athenak/src/particles/nrpic_io.cpp, ih(PTAG,p) = p). Nothing else changes: the same
particles, masses and momenta, in another order (the deposit is a sum over particles).

    python3 track_select.py --data DIR [--out DIR]

DIR holds particles.nrp and id.json of make_peak_ic.py (lattice of one particle per cell
on the cell corners, make_field.lattice_fields with stagger: q = (i + 1) h, shifted by
-L/2, so that the lattice point c = n/2 - 1 sits on the peak at the origin). Tracked: the
particle at the origin, the particles on the six half axes (offsets 1 to 30 lattice
spacings, r0 <= 9.4) and on the eight half diagonals (offsets 1 to 17, r0 <= 9.2): 317
particles. The lattice index of a particle is recovered from its position (Zel'dovich
displacements are below half a spacing; checked). Writes particles_track.nrp and
track.json (traj_ntrack; for each tracked tag: lattice index, direction, offset, initial
position, radius, momentum, mass).
"""
import argparse
import json
import os
import struct

import numpy as np


def read_particles(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRPIC001":
            raise ValueError(f"{path}: not an NRPIC001 file")
        n, = struct.unpack("q", f.read(8))
        rec = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
        sp = np.fromfile(f, dtype=np.int32, count=n)
    return rec, sp


def write_particles(path, rec, sp):
    with open(path, "wb") as f:
        f.write(b"NRPIC001")
        f.write(struct.pack("q", len(rec)))
        np.ascontiguousarray(rec, dtype=np.float64).tofile(f)
        np.ascontiguousarray(sp, dtype=np.int32).tofile(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or a.data
    info = json.load(open(os.path.join(a.data, "id.json")))
    n, L = int(info["n"]), float(info["L"])
    if int(info.get("ppc", 1)) != 1:
        raise ValueError("expects one particle per cell")
    h = L/n
    rec, sp = read_particles(os.path.join(a.data, "particles.nrp"))
    x = rec[:, 0:3]
    off0 = 1.0 if info.get("stagger", True) else 0.5
    q = (x + 0.5*L)/h - off0                   # lattice coordinate (make_field q1)
    idx = np.rint(q).astype(np.int64)
    off = np.abs(q - idx).max()
    if off >= 0.45:
        raise ValueError(f"displacement {off:.3f} spacings: lattice index ambiguous")
    idx = np.mod(idx, n)
    key = (idx[:, 0]*n + idx[:, 1])*n + idx[:, 2]
    if len(np.unique(key)) != len(key):
        raise ValueError("two particles on one lattice site")
    where = np.full(n**3, -1, dtype=np.int64)
    where[key] = np.arange(len(key))
    c = int(round(0.5*L/h - off0))             # lattice index of the origin
    if abs((c + off0)*h - 0.5*L) > 1e-12*L:
        raise ValueError("no lattice point at the origin")
    dirs = [((1, 0, 0), "+x"), ((-1, 0, 0), "-x"), ((0, 1, 0), "+y"), ((0, -1, 0), "-y"),
            ((0, 0, 1), "+z"), ((0, 0, -1), "-z")]
    dirs += [((sx, sy, sz), f"d{'+' if sx > 0 else '-'}{'+' if sy > 0 else '-'}"
              f"{'+' if sz > 0 else '-'}")
             for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]
    chosen, labels, offs = [where[(c*n + c)*n + c]], ["origin"], [0]
    for d, lab in dirs:
        kmax = 30 if sum(abs(v) for v in d) == 1 else 17
        for kk in range(1, kmax + 1):
            ijk = [(c + kk*v) % n for v in d]
            chosen.append(where[(ijk[0]*n + ijk[1])*n + ijk[2]])
            labels.append(lab)
            offs.append(kk)
    chosen = np.array(chosen)
    if np.any(chosen < 0):
        raise ValueError("lattice site without particle")
    rest = np.setdiff1d(np.arange(len(rec)), chosen, assume_unique=False)
    order = np.concatenate([chosen, rest])
    assert len(order) == len(rec) and len(np.unique(order)) == len(rec)
    os.makedirs(out, exist_ok=True)
    write_particles(os.path.join(out, "particles_track.nrp"), rec[order], sp[order])
    xt = rec[chosen, 0:3]
    tr = dict(source=os.path.abspath(os.path.join(a.data, "particles.nrp")),
              traj_ntrack=int(len(chosen)), n=n, L=L, h=h, origin_index=c,
              max_offset_from_lattice_spacings=float(off),
              tracked=[dict(tag=int(t), label=lab, offset=int(o),
                            index=[int(v) for v in idx[p]],
                            x0=[float(v) for v in xt[t]],
                            r0=float(np.sqrt((xt[t]**2).sum())),
                            u0=[float(v) for v in rec[p, 3:6]], m=float(rec[p, 6]))
                       for t, (p, lab, o) in enumerate(zip(chosen, labels, offs))])
    with open(os.path.join(out, "track.json"), "w") as f:
        json.dump(tr, f, indent=1)
    print(f"traj_ntrack: {tr['traj_ntrack']}  largest offset from the lattice: {off:.3f} "
          f"spacings  r0 from {min(t['r0'] for t in tr['tracked']):.4f} to "
          f"{max(t['r0'] for t in tr['tracked']):.4f}")


if __name__ == "__main__":
    main()
