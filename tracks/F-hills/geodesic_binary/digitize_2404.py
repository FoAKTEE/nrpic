"""Read the data curves of a matplotlib-made vector figure of arXiv:2404.16270 (untrusted data:
the file is only parsed, never executed).  Output: JSON with each stroked polyline of more
than `min_pts` points in data coordinates, its stroke colour and line width, calibrated on the
tick marks and tick labels of each axes found in the content stream.

    python3 -I digitize_2404.py <figure.pdf> <out.json>

Only the first page content stream is read.  Supports the operators matplotlib 2.2 writes
(m, l, c, h, S, B, f, RG, w, cm, q/Q, BT/Td/Tj/ET).  The digitized curves are kept in scratch
(numbers read from a third-party figure, regenerable) and used only for comparison plots.
"""
import json
import re
import sys
import zlib


def content(path):
    b = open(path, "rb").read()
    s = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S)[0]
    return zlib.decompress(s).decode("latin1")


def parse(d, min_pts=20):
    toks = re.findall(r"\((?:\\.|[^\\)])*\)|\[[^\]]*\]|/[^\s/\[\]()]+|[^\s\[\]()/]+", d)
    stack, paths, cur = [], [], []
    color, width = (0, 0, 0), 1.0
    texts, tpos = [], (0, 0)
    ticks = []
    for t in toks:
        if t in ("m", "l"):
            y, x = float(stack.pop()), float(stack.pop())
            if t == "m":
                if len(cur) > 1:
                    paths.append((cur, color, width, "open"))
                cur = [(x, y)]
            else:
                cur.append((x, y))
            stack = []
        elif t == "c":
            pts = [float(v) for v in stack[-6:]]
            cur.append((pts[4], pts[5]))
            stack = []
        elif t in ("S", "B", "f", "n", "h"):
            if t in ("S", "B") and len(cur) == 2:
                ticks.append(tuple(cur))
            if t in ("S", "B", "f", "n") and len(cur) > 1:
                paths.append((cur, color, width, t))
                cur = []
            stack = []
        elif t == "RG":
            color = tuple(float(v) for v in stack[-3:])
            stack = []
        elif t == "G":
            g = float(stack[-1])
            color = (g, g, g)
            stack = []
        elif t == "w":
            width = float(stack[-1])
            stack = []
        elif t == "Td":
            tpos = (float(stack[-2]), float(stack[-1]))
            stack = []
        elif t == "Tj":
            texts.append((tpos, stack[-1][1:-1] if stack else ""))
            stack = []
        elif re.fullmatch(r"[A-Za-z\*']+", t) or t.startswith("/"):
            if not t.startswith("/"):
                stack = []
        else:
            stack.append(t)
    curves = [dict(points=p, color=c, width=w, op=o) for p, c, w, o in paths if len(p) >= min_pts]
    return curves, ticks, texts


def main(pdf, out):
    d = content(pdf)
    curves, ticks, texts = parse(d)
    with open(out, "w") as fh:
        json.dump(dict(curves=curves, ticks=ticks, texts=texts), fh)
    print(len(curves), "curves;", len(ticks), "tick-like segments;", len(texts), "texts")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
