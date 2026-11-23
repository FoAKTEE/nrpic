"""Check S0 of repro/scope (JOURNAL entry 0): NRSFDMP2 header and variables of each dump under
<out>/{sr,usr}, Hmag > 0, and the number of record lines.  Standard library only (python3 -I).
Layout (coord/INTERFACES/scalar_field_2.md section 4): 8 bytes 'NRSFDMP2'; int64 nmb, nx1, nx2,
nx3, nvar, cycle, nnoise; double time; nvar names of 16 bytes; per MeshBlock int64 level, lx1, lx2,
lx3; double x1min..x3max; nvar arrays of nx3*nx2*nx1 doubles."""
import glob
import json
import os
import struct
import sys

WANT = ["phi", "Pi", "chi", "K", "alpha", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Axx", "Axy",
        "Axz", "Ayy", "Ayz", "Azz", "H", "Mx", "My", "Mz", "E", "Hmag", "Mmag", "MBx", "MBy", "MBz"]


def read_header(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        (time,) = struct.unpack("<d", f.read(8))
        names = [f.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        out = dict(magic=magic.decode(errors="replace"), nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar,
                   cycle=cycle, time=time, names=names)
        ncell = nx1 * nx2 * nx3
        if "Hmag" in names and nmb == 1:
            f.read(4 * 8 + 6 * 8)
            k = names.index("Hmag")
            f.seek(k * ncell * 8, 1)
            vals = struct.unpack("<%dd" % ncell, f.read(ncell * 8))
            out["Hmag_min"] = min(vals)
            out["Hmag_max"] = max(vals)
        return out


def main(root):
    res = {}
    ok = True
    for case in ("sr", "usr"):
        d = os.path.join(root, case)
        dumps = sorted(glob.glob(os.path.join(d, "*.dump")))
        hdrs = [read_header(p) for p in dumps]
        con = glob.glob(os.path.join(d, "*.sf.con.hst"))
        nrec = 0
        if con:
            with open(con[0]) as f:
                nrec = sum(1 for line in f if line.strip() and not line.startswith("#"))
        missing = sorted(set(WANT) - set(hdrs[0]["names"])) if hdrs else WANT
        c_ok = (len(dumps) >= 2 and all(h["magic"] == "NRSFDMP2" for h in hdrs) and not missing
                and all(h.get("Hmag_min", 0) > 0 for h in hdrs) and nrec >= 9)
        ok = ok and c_ok
        res[case] = dict(dumps=[os.path.basename(p) for p in dumps],
                         times=[h["time"] for h in hdrs], cycles=[h["cycle"] for h in hdrs],
                         nvar=[h["nvar"] for h in hdrs], missing=missing,
                         Hmag_min=[h.get("Hmag_min") for h in hdrs], record_lines=nrec, pass_=c_ok)
    res["S0"] = "PASS" if ok else "FAIL"
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
