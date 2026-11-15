#!/usr/bin/python3 -I
"""Vendor the figure libraries into harness/style/ (brief section 13.4), or check them.

    python3 -I harness/style/vendor.py --check            compare the vendored files with SHA256SUMS
                                                          and with their sources where readable
    harness/bin/nrpic-env exec -- python harness/style/vendor.py --write
                                                          (main checkout only) regenerate from the sources

Sources:
  czstyle.py             extracted from section 9 of the skill zoom-figure-style (its SKILL.md), with
                         the extraction regex the skill gives
  cyclic_zoom.mplstyle   written by czstyle.write_mplstyle() (needs matplotlib: run --write in a venv)
  paperfig.py            scripts/paperfig.py of the skill sleep-paper-figure-style
  figstyle.py            python/nrpic/figstyle.py of this repository (the project's older module with
                         the same rcParams and palette; kept for the scripts that import it)
The skills are looked up under ~/.claude/skills (synced skills live in ~/.claude/skills/synced/*/).
SHA256SUMS lists the four files; SOURCES.json records where each came from and the source's sha256.
Tracks copy the files unchanged into tracks/<ID>/note/scripts/; nrpic-stage verify compares the
copies with SHA256SUMS. A change goes through a proposal against harness/style/.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.realpath(os.path.join(HERE, "..", ".."))
FILES = ("czstyle.py", "cyclic_zoom.mplstyle", "paperfig.py", "figstyle.py")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def find_skill(name):
    home = os.path.expanduser("~")
    cands = (glob.glob(os.path.join(home, ".claude", "skills", name, "SKILL.md")) +
             glob.glob(os.path.join(home, ".claude", "skills", "synced", "*", name, "SKILL.md")) +
             glob.glob(os.path.join(home, ".claude", "skills", "*", name, "SKILL.md")))
    cands = sorted(set(cands), key=lambda p: os.path.getmtime(p), reverse=True)
    return os.path.dirname(cands[0]) if cands else None


def czstyle_source(skill_dir):
    text = open(os.path.join(skill_dir, "SKILL.md")).read()
    m = re.search(r'```python\n("""czstyle:.*?)```', text, re.S)
    if not m:
        raise SystemExit("czstyle block not found in the zoom-figure-style skill (old one-sentence version?)")
    return m.group(1)


def sources():
    zoom = find_skill("zoom-figure-style")
    sleep = find_skill("sleep-paper-figure-style")
    src = {}
    if zoom:
        src["czstyle.py"] = {"from": os.path.join(zoom, "SKILL.md"), "how": "section 9 code block",
                             "source_sha256": sha(os.path.join(zoom, "SKILL.md"))}
        src["cyclic_zoom.mplstyle"] = {"from": "czstyle.write_mplstyle()", "how": "generated"}
    if sleep and os.path.isfile(os.path.join(sleep, "scripts", "paperfig.py")):
        p = os.path.join(sleep, "scripts", "paperfig.py")
        src["paperfig.py"] = {"from": p, "how": "copied", "source_sha256": sha(p)}
    p = os.path.join(REPO, "python", "nrpic", "figstyle.py")
    if os.path.isfile(p):
        src["figstyle.py"] = {"from": "python/nrpic/figstyle.py", "how": "copied", "source_sha256": sha(p)}
    return zoom, sleep, src


def write():
    zoom, sleep, src = sources()
    missing = [f for f in FILES if f not in src]
    if "czstyle.py" in src:
        open(os.path.join(HERE, "czstyle.py"), "w").write(czstyle_source(zoom))
        sys.path.insert(0, HERE)
        import czstyle                                   # needs matplotlib
        czstyle.write_mplstyle(os.path.join(HERE, "cyclic_zoom.mplstyle"))
    if "paperfig.py" in src:
        shutil.copyfile(src["paperfig.py"]["from"], os.path.join(HERE, "paperfig.py"))
    if "figstyle.py" in src:
        shutil.copyfile(os.path.join(REPO, "python", "nrpic", "figstyle.py"), os.path.join(HERE, "figstyle.py"))
    present = [f for f in FILES if os.path.isfile(os.path.join(HERE, f))]
    with open(os.path.join(HERE, "SHA256SUMS"), "w") as f:
        for fn in present:
            f.write(f"{sha(os.path.join(HERE, fn))}  {fn}\n")
    for k, v in src.items():
        if os.path.isfile(os.path.join(HERE, k)):
            v["sha256"] = sha(os.path.join(HERE, k))
    home = os.path.expanduser("~")
    for v in src.values():
        if v["from"].startswith(home + os.sep):
            v["from"] = "~" + v["from"][len(home):]
    json.dump({"vendored_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "files": src,
               "not_found": missing}, open(os.path.join(HERE, "SOURCES.json"), "w"), indent=2)
    print("vendored: " + ", ".join(present) + (f"; sources not found: {missing}" if missing else ""))


def check():
    bad = []
    sums = {}
    for line in open(os.path.join(HERE, "SHA256SUMS")):
        d, fn = line.split()
        sums[fn] = d
        if sha(os.path.join(HERE, fn)) != d:
            bad.append(f"{fn}: differs from SHA256SUMS")
    zoom, sleep, src = sources()
    if "czstyle.py" in src and czstyle_source(zoom) != open(os.path.join(HERE, "czstyle.py")).read():
        bad.append("czstyle.py: the zoom-figure-style skill has a newer section 9 (re-vendor through a proposal)")
    for fn in ("paperfig.py", "figstyle.py"):
        if fn in src and src[fn]["source_sha256"] != sums.get(fn):
            bad.append(f"{fn}: the source {src[fn]['from']} changed (re-vendor through a proposal)")
    for fn in FILES:
        if fn not in src:
            print(f"note: source of {fn} not readable here; checked against SHA256SUMS only")
    for b in bad:
        print("FAIL " + b)
    if not bad:
        print("PASS vendored figure libraries match SHA256SUMS and their sources")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        write()
    elif "--check" in sys.argv:
        sys.exit(check())
    else:
        print(__doc__)
        sys.exit(2)
