"""Run tests P, C, K and Q of the KB-G1 verifier into one output directory.

Usage (registered): harness/bin/nrpic-run submit ... -- python3 -I tracks/kb/stage/KB-G1/verifier/run_all.py
The output directory is $NRPIC_RUN_DIR (or the first argument).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    for script in ("check_papers.py", "fig_papers.py", "check_claims.py", "check_params.py",
                   "check_answers.py", "fig_summary.py"):
        print(f"== {script}", flush=True)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, script), out])
        if r.returncode != 0:
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
