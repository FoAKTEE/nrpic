"""Parse the printed tables of arXiv:2108.11967 (F21) from its LaTeX source.

Standard library only; run with python3 -I (the source is untrusted data, never executed):

    python3 -I paper_tables.py <.../2108.11967/v2/src/main.tex> <out.json>

Table 1 ("table:results", main.tex:479-589): four sub-tables b = 0.1, 0.2, 0.3, 0.5, columns
w(0), E^ = M^, E^_rest, B^, eps, R^, C, Z(0), eps_c(0)/mc^2, rho^(0), p^(0), v(0)/c, <gamma>,
gamma_cr. Table 2 ("tab:finerscan", main.tex:597-624): b, w(0), E^, R^, C, Z(0),
eps_c(0)/mc^2, rho^(0), p^(0), v(0)/c, v(R)/c, <gamma> = gamma_cr.
Every row keeps its line number and which cells carry \\underline (the paper's marks of the
marginally stable configurations).
"""
import json
import re
import sys

COLS1 = ["w0", "E", "Erest", "B", "eps", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "gavg", "gcr"]
COLS2 = ["b", "w0", "E", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "vR", "gavg"]

NUM = re.compile(r"^\s*([-+]?\d*\.?\d+)\s*(?:\\times\s*10\^\{\s*([-+]?\d+)\s*\})?\s*$")


def cell_value(cell):
    under = "\\underline" in cell
    s = cell.replace("\\underline", "").replace("{", " ").replace("}", " ")
    s = s.replace("$", " ").replace("\\\\", " ").replace("[0.5ex]", " ")
    # restore the exponent braces removed above
    s = re.sub(r"\\times\s*10\^\s*([-+]?\d+)", r"\\times10^{\1}", s)
    m = NUM.match(s.strip())
    if not m:
        raise ValueError(f"cannot parse cell {cell!r}")
    v = float(m.group(1))
    if m.group(2) is not None:
        v *= 10.0 ** int(m.group(2))
    return v, under


def parse(path):
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    t1, t2 = [], []
    b_current = None
    table = None
    for i, line in enumerate(lines, start=1):
        if "\\label{table:results}" in line or "\\label{tab:finerscan}" in line:
            table = None
        if "\\subcaption*" in line:
            m = re.search(r"mc\^2\s*=\s*([0-9.]+)", line)
            b_current = float(m.group(1))
            table = 1
            continue
        if "\\topcaption{Properties of marginally stable configurations" in line:
            table = 2
        if table is None or "&" not in line or "\\\\" not in line:
            continue
        cells = [c for c in line.split("&")]
        first = cells[0].strip()
        if first.startswith("$w(0)$") or first.startswith("$b$"):
            continue
        cells[-1] = cells[-1].split("\\\\")[0]
        vals = [cell_value(c) for c in cells]
        if table == 1 and len(vals) == len(COLS1):
            row = {k: v for k, (v, _) in zip(COLS1, vals)}
            row["underlined"] = [k for k, (_, u) in zip(COLS1, vals) if u]
            row["b"] = b_current
            row["line"] = i
            t1.append(row)
        elif table == 2 and len(vals) == len(COLS2):
            row = {k: v for k, (v, _) in zip(COLS2, vals)}
            row["line"] = i
            t2.append(row)
    return dict(source=path, table1=t1, table2=t2)


if __name__ == "__main__":
    out = parse(sys.argv[1])
    with open(sys.argv[2], "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"table1 rows {len(out['table1'])}, table2 rows {len(out['table2'])}")
