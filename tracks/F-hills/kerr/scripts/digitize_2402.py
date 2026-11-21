"""Read the vector content of a matplotlib-made figure of arXiv:2402.02178 (untrusted data: the
PDF is only parsed as text, never executed or rendered by this script).

    python3 -I digitize_2402.py <figure.pdf> <out.json>

Output (raw PDF user-space coordinates, no calibration; the analysis scripts calibrate on the
tick marks listed here):
  fills    : closed filled paths  [{"pts": [[x, y], ...], "rgb": [r, g, b]}]
  strokes  : stroked paths        [{"pts": ..., "rgb": ..., "width": w, "dash": "[..] p"}]
  markers  : marker placements    [{"xobj": "/M0", "x": x, "y": y, "rgb_fill": ..., "rgb_stroke": ...}]
  texts    : text strings         [{"x": x, "y": y, "s": "..."}]  (position of the first Td/Tm)
Only the first content stream (the page) is read; operators handled: m l c h re f f* B S n
rg RG g G w d cm q Q Do BT ET Td Tm Tj TJ.  Marker positions follow the cumulative
translations matplotlib writes ("1 0 0 1 dx dy cm /M0 Do") inside one q ... Q block.
"""
import json
import re
import sys
import zlib


def content(path):
    b = open(path, "rb").read()
    s = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", b, re.S)[0]
    return zlib.decompress(s).decode("latin1")


TOK = re.compile(r"\((?:\\.|[^\\)])*\)|\[[^\]]*\]|/[^\s/\[\]()]+|[^\s\[\]()/]+")


def parse(d):
    toks = TOK.findall(d)
    stack = []
    cur = []                       # current subpath list of points
    sub = []                       # list of subpaths of the current path
    fill, stroke, width, dash = (0, 0, 0), (0, 0, 0), 1.0, "[] 0"
    ctm_stack = []
    tx, ty = 0.0, 0.0              # cumulative translation inside q ... Q (marker placements)
    fills, strokes, markers, texts = [], [], [], []
    in_text, text_pos, text_buf = False, None, []
    for t in toks:
        if t in ("m", "l"):
            y, x = float(stack[-1]), float(stack[-2])
            if t == "m":
                if len(cur) > 0:
                    sub.append(cur)
                cur = [(x, y)]
            else:
                cur.append((x, y))
            stack = []
        elif t == "c":
            v = [float(s) for s in stack[-6:]]
            cur.append((v[4], v[5]))
            stack = []
        elif t == "re":
            x, y, w, h = (float(s) for s in stack[-4:])
            if cur:
                sub.append(cur)
            cur = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
            stack = []
        elif t == "h":
            stack = []
        elif t in ("f", "f*", "B", "B*", "S", "n", "b"):
            if cur:
                sub.append(cur)
            for p in sub:
                if len(p) < 2:
                    continue
                if t in ("f", "f*", "B", "B*", "b"):
                    fills.append(dict(pts=p, rgb=fill))
                if t in ("S", "B", "B*", "b"):
                    strokes.append(dict(pts=p, rgb=stroke, width=width, dash=dash))
            cur, sub = [], []
            stack = []
        elif t == "rg":
            fill = tuple(float(v) for v in stack[-3:])
            stack = []
        elif t == "RG":
            stroke = tuple(float(v) for v in stack[-3:])
            stack = []
        elif t == "g":
            g = float(stack[-1])
            fill = (g, g, g)
            stack = []
        elif t == "G":
            g = float(stack[-1])
            stroke = (g, g, g)
            stack = []
        elif t == "w":
            width = float(stack[-1])
            stack = []
        elif t == "d":
            dash = " ".join(stack[-2:])
            stack = []
        elif t == "q":
            ctm_stack.append((tx, ty))
            stack = []
        elif t == "Q":
            tx, ty = ctm_stack.pop() if ctm_stack else (0.0, 0.0)
            stack = []
        elif t == "cm":
            v = [float(s) for s in stack[-6:]]
            if not in_text:
                tx, ty = tx + v[4], ty + v[5]
            stack = []
        elif t == "Do":
            markers.append(dict(xobj=stack[-1] if stack else None, x=tx, y=ty,
                                rgb_fill=fill, rgb_stroke=stroke))
            stack = []
        elif t == "BT":
            in_text, text_pos, text_buf = True, None, []
            stack = []
        elif t in ("Td", "Tm"):
            if text_pos is None:
                text_pos = (float(stack[-2]), float(stack[-1]))
            stack = []
        elif t in ("Tj", "TJ"):
            text_buf.append(stack[-1] if stack else "")
            stack = []
        elif t == "ET":
            if text_pos is not None:
                texts.append(dict(x=text_pos[0], y=text_pos[1], s=" ".join(text_buf)))
            in_text = False
            stack = []
        else:
            stack.append(t)
    return dict(fills=fills, strokes=strokes, markers=markers, texts=texts)


def main(pdf, out):
    res = parse(content(pdf))
    res["source"] = pdf
    with open(out, "w") as fh:
        json.dump(res, fh)
    print(out, {k: len(v) for k, v in res.items() if isinstance(v, list)})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
