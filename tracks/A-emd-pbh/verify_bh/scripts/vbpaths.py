"""Artefact paths of the package verify_bh (read-only inputs)."""
import os

SCR = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
STEM = "expball_tophat_HRb0p7_dc1p5_R10p65_R20p95_rm4p25"
DS3 = os.path.join(SCR, "A-20261119-143524-334e553")          # data set 3: table, lat34/51/68
LAT136 = os.path.join(SCR, "A-20261119-164113-74f0f32")       # lattice h = M/16
TABLE = os.path.join(DS3, STEM + ".tab")
NRP = {34: os.path.join(DS3, "lat34", f"{STEM}_lat34_track.nrp"),
       51: os.path.join(DS3, "lat51", f"{STEM}_lat51_track.nrp"),
       68: os.path.join(DS3, "lat68", f"{STEM}_lat68_track.nrp"),
       136: os.path.join(LAT136, "lat136", f"{STEM}_lat136_track.nrp")}
BH1R = os.path.join(SCR, "A-20261119-164634-f1fe887", "bh_smr")
BH1 = {128: os.path.join(SCR, "A-20261119-144419-13d5601", "bh_n128"),
       192: os.path.join(SCR, "A-20261119-144419-13d5601", "bh_n192"),
       256: os.path.join(SCR, "A-20261119-144419-13d5601", "bh_n256")}
# lattice used by each run (decks and manifests: bh.athinput header, batch arguments)
RUN_LAT = {"bh_smr": 136, "bh_n128": 34, "bh_n192": 51, "bh_n256": 68}
RUN_DX = {"bh_n128": 0.25, "bh_n192": 1.0 / 6.0, "bh_n256": 0.125}
RUN_DIR = {"bh_smr": BH1R, "bh_n128": BH1[128], "bh_n192": BH1[192], "bh_n256": BH1[256]}


def outdir():
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join(SCR, "tmp", "verify_bh", "dev")
    os.makedirs(d, exist_ok=True)
    return d
