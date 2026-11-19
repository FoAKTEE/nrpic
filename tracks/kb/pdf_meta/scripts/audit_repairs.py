"""Draw repairs of the PDF reader at random for reading by a person (test P1, repair precision).

    python -I audit_repairs.py <out_dir> [--n 30] [--seed 20261119] <paper_id> ...

Reads kb-data/build/tex/<key>/pdf_edits.json and pdf_raw.txt (written by kbtool.pdf_ingest),
keeps the word repairs (ligature-dropped, ligature-split, ot1-ligature, dehyphen), draws n of
them with a fixed seed and writes <out_dir>/repair_sample.tsv with 40 characters of context on
either side (paper text: stays in scratch, never in git) and <out_dir>/repair_counts.json.
The verdict column is filled by the reader by hand.
"""
import json
import os
import random
import sys

KINDS = ("ligature-dropped", "ligature-split", "ot1-ligature", "dehyphen")
DATA = "/data/haiyangw/nrpic/kb-data/build/tex"


def main(argv):
    out = argv[0]
    n, seed, ids = 30, 20261119, []
    i = 1
    while i < len(argv):
        if argv[i] == "--n":
            n, i = int(argv[i + 1]), i + 2
        elif argv[i] == "--seed":
            seed, i = int(argv[i + 1]), i + 2
        else:
            ids.append(argv[i])
            i += 1
    pool, counts = [], {}
    for pid in ids:
        key = pid.replace("/", "_")
        ed = json.load(open(os.path.join(DATA, key, "pdf_edits.json"), encoding="utf-8"))
        counts[pid] = {}
        # step-2 edits are offsets in the text after step 1; rebuild that text for context
        raw = open(os.path.join(DATA, key, "pdf_raw.txt"), encoding="utf-8").read()
        parts, pos = [], 0
        for a, b, old, new, kind in sorted(ed["step1_on_raw"], key=lambda e: e[0]):
            parts += [raw[pos:a], new]
            pos = b
        parts.append(raw[pos:])
        t1 = "".join(parts)
        for step, text in (("step1_on_raw", raw), ("step2_on_step1", t1)):
            for a, b, old, new, kind in ed[step]:
                counts[pid][kind] = counts[pid].get(kind, 0) + 1
                if kind in KINDS:
                    ctx = (text[max(0, a - 40):a] + "[[" + old + "=>" + new + "]]" + text[b:b + 40]).replace("\n", " ")
                    pool.append((pid, kind, old, new, ctx.replace("\t", " ")))
    rng = random.Random(seed)
    sample = rng.sample(pool, min(n, len(pool)))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "repair_sample.tsv"), "w", encoding="utf-8") as f:
        f.write("k\tpaper\tkind\told\tnew\tcontext\tverdict\n")
        for k, (pid, kind, old, new, ctx) in enumerate(sample, 1):
            f.write(f"{k}\t{pid}\t{kind}\t{old!r}\t{new!r}\t{ctx}\t\n")
    with open(os.path.join(out, "repair_counts.json"), "w") as f:
        json.dump({"counts": counts, "pool": len(pool), "sample": len(sample), "seed": seed}, f, indent=1)
    print(json.dumps({"pool": len(pool), "sample": len(sample), "counts": counts}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
