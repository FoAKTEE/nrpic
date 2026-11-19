"""Print 'line: excerpt' for lines of a text file matching a regex (case-insensitive).
Usage: python3 -I lgrep.py FILE REGEX [width] [lo] [hi]"""
import re, sys
f, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
w = int(sys.argv[3]) if len(sys.argv) > 3 else 200
lo = int(sys.argv[4]) if len(sys.argv) > 4 else 1
hi = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
for i, l in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
    if lo <= i <= hi:
        m = pat.search(l)
        if m:
            s = max(0, m.start() - w // 2)
            print(f"{i}: {l[s:s + w].rstrip()}")
