"""Integrity listing of the run outputs behind the note's ledger (G1 verifier, finding 7).

For every run directory named in tracks/A-emd-pbh/note/scripts/common.py (RUNS), under
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/:
  - without sha256sums.txt (wave-1 runs and hand-run wave-2 runs): write the sha256 of every
    file of the directory, in `sha256sum` format with paths relative to the directory, into
    <out>/<run id>.sha256;
  - with sha256sums.txt: verify every listed file against it and record the result.
The listed directories are opened read-only: the script checks before and after that no
file's size and modification time changed, and hashes every listed file a second time.
Writes <out>/integrity.json and the figure <out>/fig_integrity.{pdf,png}
(style python/nrpic/figstyle.py). Usage: python wave1_sha256.py --out DIR (or under nrpic-run).
"""
import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "note", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "python"))
import common  # noqa: E402  (the note's run table)

SCRATCH = common.SCRATCH


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files_of(rdir):
    out = []
    for base, dirs, files in os.walk(rdir):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(base, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            out.append(os.path.relpath(p, rdir))
    return out


def stat_map(rdir, rels):
    m = {}
    for r in rels:
        st = os.stat(os.path.join(rdir, r))
        m[r] = (st.st_size, st.st_mtime_ns)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    out = ap.parse_args().out
    if not out:
        raise SystemExit("give --out DIR or run under nrpic-run")
    os.makedirs(out, exist_ok=True)
    runs = sorted(set(common.RUNS.values()))
    rows = []
    for run_id in runs:
        rdir = os.path.join(SCRATCH, run_id)
        rels = files_of(rdir)
        before = stat_map(rdir, rels)
        sums = os.path.join(rdir, "sha256sums.txt")
        row = dict(run=run_id, dir=rdir, n_files=len(rels),
                   bytes=sum(v[0] for v in before.values()))
        if os.path.isfile(sums):
            table = {}
            for line in open(sums):
                p = line.split(None, 1)
                if len(p) == 2:
                    table[p[1].strip()] = p[0]
            bad = [r for r, h in table.items() if sha256(os.path.join(rdir, r)) != h]
            unlisted = [r for r in rels if r not in table and r != "sha256sums.txt"
                        and not r.startswith(".nrpic/")]
            row.update(kind="recorded by the run", n_listed=len(table), mismatches=bad,
                       unlisted=unlisted)
        else:
            digests = {r: sha256(os.path.join(rdir, r)) for r in rels}
            again = {r: sha256(os.path.join(rdir, r)) for r in rels}
            with open(os.path.join(out, f"{run_id}.sha256"), "w") as f:
                for r in rels:
                    f.write(f"{digests[r]}  {r}\n")
            row.update(kind="listed now", n_listed=len(rels), mismatches=[],
                       second_pass_equal=digests == again, listing=f"{run_id}.sha256")
        after = stat_map(rdir, rels)
        row["unchanged"] = before == after and files_of(rdir) == rels
        rows.append(row)
        print(f"{run_id}: {row['kind']}, {row['n_files']} files, mismatches {len(row['mismatches'])}, "
              f"unchanged {row['unchanged']}")
    summary = dict(date_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), runs=rows,
                   n_listed_now=sum(r["kind"] == "listed now" for r in rows),
                   n_files_listed_now=sum(r["n_files"] for r in rows if r["kind"] == "listed now"),
                   n_mismatch=sum(len(r["mismatches"]) for r in rows),
                   all_unchanged=all(r["unchanged"] for r in rows))
    with open(os.path.join(out, "integrity.json"), "w") as f:
        json.dump(summary, f, indent=1)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.36, right=0.97, bottom=0.15, top=0.97)
    y = range(len(rows))
    for i, r in enumerate(rows):
        c = fs.PAL["blue"] if r["kind"] == "recorded by the run" else fs.PAL["red"]
        if r["mismatches"] or not r["unchanged"]:
            c = "k"
        ax.barh(i, r["n_files"], color=c)
    ax.set_yticks(list(y))
    ax.set_yticklabels([r["run"] for r in rows], fontsize=7)
    ax.minorticks_off()
    ax.invert_yaxis()
    ax.set_xlabel("files in the run directory")
    ax.text(0.98, 0.10, "blue: verified against the run's own sha256sums.txt\n"
            "red: listed now (no record by the run)\nblack: mismatch or changed",
            transform=ax.transAxes, ha="right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_integrity"))
    print(f"integrity: {summary['n_listed_now']} directories listed now "
          f"({summary['n_files_listed_now']} files), {summary['n_mismatch']} mismatches, "
          f"all unchanged {summary['all_unchanged']}")
    return 1 if summary["n_mismatch"] or not summary["all_unchanged"] else 0


if __name__ == "__main__":
    sys.exit(main())
