"""P0: run the unit tests as a registered run; the pytest log goes to the run directory.

Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 scripts/run_tests.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runlib  # noqa: E402

PKG = os.path.dirname(HERE)
run = runlib.start_run("P0: unit tests of the newton3 package (integrator, restricted equations, "
                       "driver initial data, conservation, SciPy cross-checks)", cores=1,
                       extra_inputs=[os.path.join(PKG, "tests", "test_hills3.py")],
                       preregistered="tracks/F-hills/newton3/JOURNAL.md#P0")
p = subprocess.run([sys.executable, "-m", "pytest", "-v", "-p", "no:cacheprovider", "tests"],
                   cwd=PKG, capture_output=True, text=True)
with open(os.path.join(run["dir"], "pytest.log"), "w") as fh:
    fh.write(p.stdout + p.stderr)
print(p.stdout[-2000:])
runlib.finish_run(run, status="completed" if p.returncode == 0 else "failed", exit_code=p.returncode,
                  results={"pytest_summary": p.stdout.strip().splitlines()[-1] if p.stdout else ""})
