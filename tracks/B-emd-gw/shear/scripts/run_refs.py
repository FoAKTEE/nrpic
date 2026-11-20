"""One registered run of the processor-only checks of the shear package: the tests
(pytest tests/), the reference table (ref_table.py, P1) and the constraint check of the
written initial data (check_ic.py, P3). Logs into $NRPIC_RUN_DIR.

    python3 run_refs.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)


def run(args, log):
    with open(os.path.join(os.environ["NRPIC_RUN_DIR"], log), "w") as f:
        r = subprocess.run(args, stdout=f, stderr=subprocess.STDOUT, cwd=PKG)
    print(f"{log}: rc = {r.returncode}", flush=True)
    return r.returncode


def main():
    rc = 0
    rc |= run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider", "-W",
               "ignore", os.path.join(PKG, "tests")], "pytest.log")
    rc |= run([sys.executable, os.path.join(HERE, "ref_table.py")], "ref_table.log")
    rc |= run([sys.executable, os.path.join(HERE, "check_ic.py"), "--cases", "S1,L2",
               "--ns", "16,32,64,128,256"], "check_ic.log")
    sys.exit(rc)


if __name__ == "__main__":
    main()
