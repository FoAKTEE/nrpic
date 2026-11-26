"""Figure: three-way convergence of the growth (G2 item C2; note v3, g2long/JOURNAL.md entries 25-26).

Draws, with the reader g2long/tools/conv3.py, from the horizon summaries of the registered card runs
(common.RUNS keys fnq, fk, fn4 for the particle number at M/8; ff4, esfl, fl16 for the mesh, with the
own-mesh vacuum controls v1l4, v1l, v1l16): (a) differences of M_AH between N/4, N, 4N; (b) differences
of Delta M = M_AH(t) - M_AH(20 M) between M/4, M/8, M/16, M/4 drawn dashed and labelled outside the
convergent regime (decision 0039 item 4); (c) the same with each own-mesh vacuum control subtracted.
Horizon masses come from runs made without the finder diagnostics (decision 0041 item 4). Writes
fig_g2conv.{pdf,png} and fig_g2conv_numbers.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402

sys.path.insert(0, os.path.join(C.TRACK, "g2long", "tools"))
import conv3  # noqa: E402


def main():
    out = C.out_dir("figures")
    d = C.run_dir
    argv = ["--out", out,
            "--part", f"FNQ={d('fnq')}:esflkq", "--part", f"FK={d('fk')}:esflk", "--part", f"FN4={d('fn4')}:esflk4n",
            "--mesh", f"FF4={d('ff4')}:esfl4:{d('v1l4')}/v1l4.horizon_summary_0.txt:0.25:out",
            "--mesh", f"ES-FL={d('esfl')}:esfl:{d('v1l')}/v1l.horizon_summary_0.txt:0.125:in",
            "--mesh", f"FL16={d('fl16')}:esfl16:{d('v1l16')}/v1l16.horizon_summary_0.txt:0.0625:in"]
    for k, base in (("fnq", "esflkq"), ("fk", "esflk"), ("fn4", "esflk4n"), ("ff4", "esfl4"), ("esfl", "esfl"),
                    ("fl16", "esfl16"), ("v1l4", "v1l4"), ("v1l", "v1l"), ("v1l16", "v1l16")):
        C.run_file(k, base + ".horizon_summary_0.txt")      # sha256 against the run's record
    conv3.main(argv, stem="fig_g2conv")
    C.report_checks("fig_g2conv")


if __name__ == "__main__":
    main()
