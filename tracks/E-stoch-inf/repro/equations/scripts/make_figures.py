"""Figures of the symbolic checks: a matrix of the results of check_equations.py and
check_code_map.py (green pass / red fail, with the expected outcome marked)."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# entries whose expected outcome is FAIL (misprints or negative controls written as such)
EXPECT_FAIL = (
    'P1:267 as printed', 'Hddot', 'alternative sign', 'prefactor -2)',
    'printed P0:231 exactly', 'delta_ij literally', 'as printed, P0:350',
    'as printed P0:371', '4 pi (printed)', 'as printed (S_i = J_i)',
    'as stated at P0:730', 'as printed solves Friedmann', 'term a^2 H^-1 k^2 R>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eq', required=True)
    ap.add_argument('--code', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    rows = []
    for path in (args.eq, args.code):
        with open(path) as fh:
            d = json.load(fh)
        for kk, v in d.items():
            if kk.startswith('_'):
                continue
            exp_fail = any(t in kk for t in EXPECT_FAIL)
            rows.append((kk, v['pass'], exp_fail))
    n = len(rows)
    fig, ax = plt.subplots(figsize=(7.5, 0.16 * n + 0.6))
    for i, (kk, ok, ef) in enumerate(rows):
        y = n - 1 - i
        col = '#2e8b57' if ok else '#c0392b'
        ax.barh(y, 1.0, color=col, height=0.8)
        mark = 'misprint/control: FAIL expected' if ef else ''
        good = (ok and not ef) or ((not ok) and ef)
        ax.text(1.03, y, ('as predicted' if good else 'NOT as predicted') + ('  ' + mark if mark else ''),
                va='center', fontsize=5)
        ax.text(-0.02, y, kk[:95], va='center', ha='right', fontsize=5)
    ax.set_xlim(0, 2.0)
    ax.set_ylim(-1, n)
    ax.axis('off')
    ax.set_title('sympy checks: green = identity holds, red = it does not', fontsize=8)
    fig.subplots_adjust(left=0.55, right=0.98, top=0.97, bottom=0.01)
    fig.savefig(os.path.join(args.out, 'fig_checks_matrix.png'), dpi=170)
    bad = [r for r in rows if not ((r[1] and not r[2]) or ((not r[1]) and r[2]))]
    print('%d checks, %d not as predicted' % (n, len(bad)))
    for r in bad:
        print('  NOT AS PREDICTED:', r[0])


if __name__ == '__main__':
    main()
