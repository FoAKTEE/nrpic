"""Step 3 of the KB-G2 verifier: run `kb search` on the frozen snapshot for a question set.

For each question and each mode (text, hybrid, rerank) this calls the kb command exactly as
a reader would:
    kb/.venv/bin/python -I kb/bin/kb search QUERY --db SNAPSHOT -k 10 --json [--text-only|--hybrid|--rerank]
                        --threads N
and stores the raw JSON in $NRPIC_RUN_DIR/raw/<set>/<qid>.<mode>.json, with the wall time and
exit code in $NRPIC_RUN_DIR/calls.<set>.jsonl. Scoring is separate (score_search.py).

Question sets: the verifier's heldout.yaml (key `questions`, field `question`) or the golden
file kb/golden/questions.yaml (structure read by load_questions below).
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vg2common as C  # noqa: E402

import yaml  # kb/.venv

WT = "/data/haiyangw/nrpic/wt/kb"
MODES = {"text": ["--text-only"], "hybrid": ["--hybrid"], "rerank": ["--rerank"]}


def load_questions(path):
    with open(path) as f:
        d = yaml.safe_load(f)
    qs = d["questions"] if isinstance(d, dict) else d
    out = []
    for q in qs:
        qid = str(q.get("id") or q.get("qid"))
        text = q.get("question") or q.get("query") or q.get("q")
        out.append((qid, text))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, help="name of the set (heldout or golden)")
    ap.add_argument("--questions", required=True)
    ap.add_argument("--modes", default="text,hybrid,rerank")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--db", default=C.SNAP)
    a = ap.parse_args()
    rd = C.run_dir()
    raw = os.path.join(rd, "raw", a.set)
    os.makedirs(raw, exist_ok=True)
    qs = load_questions(a.questions)
    log = open(os.path.join(rd, f"calls.{a.set}.jsonl"), "a")
    env = dict(os.environ, OMP_NUM_THREADS=str(a.threads), MKL_NUM_THREADS=str(a.threads),
               OPENBLAS_NUM_THREADS=str(a.threads), TOKENIZERS_PARALLELISM="false")
    print(f"set {a.set}: {len(qs)} questions; modes {a.modes}; db {a.db}", flush=True)
    for mode in a.modes.split(","):
        for qid, text in qs:
            cmd = [os.path.join(WT, "kb/.venv/bin/python"), "-I", os.path.join(WT, "kb/bin/kb"), "search", text,
                   "--db", a.db, "-k", "10", "--json", "--threads", str(a.threads)] + MODES[mode]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True)
            dt = time.time() - t0
            with open(os.path.join(raw, f"{qid}.{mode}.json"), "w") as f:
                f.write(p.stdout)
            rec = dict(set=a.set, qid=qid, mode=mode, rc=p.returncode, wall_s=round(dt, 2),
                       stderr=p.stderr[-400:], cmd=cmd[3:])
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(f"{mode:6s} {qid:>8s} rc={p.returncode} {dt:6.1f}s", flush=True)
    log.close()


if __name__ == "__main__":
    main()
