#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-env in a scratch repository (brief 11.4, rows [venv] [env] [build]).

    python3 -I harness/tests/test_nrpic_env.py

Covers: create installs uv.lock into <worktree>/.venv for two worktrees, as copies (no shared
inodes); Kokkos (a stand-in submodule) checked out with --reference to the main checkout; exec
gives the worktree's interpreter and ignores the caller's variables; --set, --threads and the
protected variables; the environment hash is the same for identical branch content and changes
with the machine file; check flags a symbolic link out of the worktree; build refuses a linked
build directory.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402


def env_cmd(wt, args, env=None, cwd=None, timeout=900):
    return F.sh([os.path.join(wt, "harness", "bin", "nrpic-env")] + args, cwd=cwd or wt, env=env,
                check=False, timeout=timeout)


def main():
    fx = F.make_repo("test-env")
    A, B = fx["wt"]["A-emd-pbh"], fx["wt"]["B-emd-gw"]
    c = F.Checks(f"nrpic-env (scratch repo {fx['repo']})")

    for name, wt in (("A", A), ("B", B)):
        r = env_cmd(wt, ["create"])
        c.ok(r.returncode == 0 and os.path.isdir(os.path.join(wt, ".venv")), f"create in worktree {name}",
             r.stdout[-1500:] + r.stderr[-1500:])
    r = env_cmd(A, ["exec", "--", "python", "-c", "import sys, numpy, matplotlib; "
                    "print(sys.prefix); print(numpy.__version__, matplotlib.__version__)"])
    lines = r.stdout.split()
    c.ok(r.returncode == 0 and lines[0] == os.path.join(A, ".venv") and lines[1] == "2.2.6",
         "exec runs the worktree's own interpreter with the locked numpy", r.stdout + r.stderr)
    fa = os.path.join(A, ".venv", "lib", "python3.10", "site-packages", "numpy", "__init__.py")
    fb = os.path.join(B, ".venv", "lib", "python3.10", "site-packages", "numpy", "__init__.py")
    sa, sb = os.stat(fa), os.stat(fb)
    c.ok(sa.st_ino != sb.st_ino and sa.st_nlink == 1 and sb.st_nlink == 1,
         "the two venvs share no file (copies, link count 1)")
    c.ok(F.sh(["git", "-C", A, "status", "--porcelain"]).stdout.strip() == "",
         ".venv leaves the worktree clean (uv's own .gitignore)")
    k = os.path.join(A, "athenak", "kokkos")
    alt = F.sh(["git", "-C", k, "rev-parse", "--git-path", "objects/info/alternates"]).stdout.strip()
    altp = alt if os.path.isabs(alt) else os.path.join(k, alt)
    c.ok(os.path.isfile(os.path.join(k, "CMakeLists.txt")) and os.path.isfile(altp)
         and os.path.join(fx["repo"], ".git", "modules") in open(altp).read(),
         "Kokkos checked out with --reference to the main checkout (alternates)", altp)

    polluted = dict(F.H.boot_env(), FOO="ambient", CUDA_HOME="/wrong", PYTHONPATH="/x", OMP_NUM_THREADS="64")
    r = env_cmd(A, ["exec", "--set", "BAR=given", "--threads", "3", "--", "bash", "-c",
                    'echo "${FOO:-unset} $BAR $CUDA_HOME ${PYTHONPATH:-unset} $OMP_NUM_THREADS $NRPIC_TRACK"'],
                env=polluted)
    c.ok(r.stdout.split() == ["unset", "given", "/usr/local/cuda-12.6", "unset", "3", "A-emd-pbh"],
         "exec ignores the caller's variables; --set and --threads apply", r.stdout + r.stderr)
    r = env_cmd(A, ["exec", "--set", "PATH=/evil", "--", "true"])
    c.ok(r.returncode == 1 and "fixed by nrpic-env" in r.stderr, "--set of a protected variable refused", r.stderr)
    r = env_cmd(A, ["exec", "--threads", "17", "--", "true"])
    c.ok(r.returncode == 1 and "16 cores" in r.stderr, "--threads above the allotment refused", r.stderr)

    ha = env_cmd(A, ["hash"]).stdout.strip()
    hb = env_cmd(B, ["hash"]).stdout.strip()
    c.ok(len(ha) == 64 and ha == hb, "same environment hash for identical branch content")
    mf = os.path.join("harness", "env", "machines", F.H.host() + ".sh")
    F.commit_file(B, mf, open(os.path.join(B, mf)).read() + "# changed\n", "change machine file")
    hb2 = env_cmd(B, ["hash"]).stdout.strip()
    c.ok(hb2 != hb, "the hash changes with the machine file")

    r = env_cmd(A, ["check"])
    c.ok(r.returncode == 0 and "FAIL" not in r.stdout, "check passes in a fresh worktree", r.stdout + r.stderr)
    link = os.path.join(A, "tracks", "A-emd-pbh", "outside")
    os.symlink(B, link)
    r = env_cmd(A, ["check"])
    c.ok(r.returncode == 1 and "[links  ] FAIL" in r.stdout, "check flags a link out of the worktree", r.stdout)
    os.remove(link)
    other = os.path.join(fx["root"], "elsewhere")
    os.makedirs(other)
    os.symlink(other, os.path.join(A, "build"))
    r = env_cmd(A, ["build", "cpu"])
    c.ok(r.returncode == 1 and "symbolic link" in r.stderr, "build refuses a linked build directory", r.stderr)
    os.remove(os.path.join(A, "build"))
    r = env_cmd(A, ["vars", "--export"])
    c.ok(r.returncode == 0 and f"export NRPIC_WT={A}" in r.stdout and "NRPIC_SCRATCH=" in r.stdout,
         "vars --export prints the identity variables", r.stdout)
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
