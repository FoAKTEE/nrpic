"""Where the registered card outputs of the members are, and which table each used (read
from the batch list or the chain configuration of the run itself)."""
import os
import re

S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"

CONV = {  # conv_ball (README "Runs and results")
    "A": S + "/A-20261121-075926-d10c2c1/A",
    "B": S + "/A-20261121-075926-d10c2c1/B",
    "A-L32": S + "/A-20261121-075926-d10c2c1/A-L32",
    "A-R1.25": S + "/A-20261121-075926-d10c2c1/A-R1.25",
    "A-R1.35": S + "/A-20261121-075926-d10c2c1/A-R1.35",
    "A-N8": S + "/A-20261121-075926-d10c2c1/A-N8",
    "C": S + "/A-20261121-083336-6a82131",
    "B-N8": S + "/A-20261121-091934-ac62f5f/B-N8",
    "A-N64": S + "/A-20261121-091934-ac62f5f/A-N64",
    "B-R1.25": S + "/A-20261121-110017-471b0ae/B-R1.25",
    "B-R1.35": S + "/A-20261121-110017-471b0ae/B-R1.35",
    "B-L32": S + "/A-20261121-110017-471b0ae/B-L32",
}

THRESH = {  # threshold_ball (card runs named by the members' manifests / queue)
    "B-d1.00": S + "/A-20261122-054155-4b3d92e",
    "B-d0.70": S + "/A-20261122-100756-829dcf9",
    "B-d0.50": S + "/A-20261122-051554-7662f22",
    "B-d0.45": S + "/A-20261122-003952-552f805",
    "B-d0.42": S + "/A-20261121-204149-c48bd33",
    "B-d0.40": S + "/A-20261121-204250-0bf45c7",
    "B-d0.35": S + "/A-20261122-101357-9a73701",
    "B-d0.20": S + "/A-20261122-132959-dfba903",
    "A-d0.42": S + "/A-20261121-235851-d2200d7/A-d0.42",
    "A-d0.40": S + "/A-20261121-235851-d2200d7/A-d0.40",
    "C-R1.25": S + "/A-20261122-141100-f00cfc2",
    "C-d0.42": S + "/A-20261122-173202-f98c79f",
}


def member_args(d):
    """Command-line options of a member: from chain/config.sh or the parent's batch.list."""
    cfg = os.path.join(d, "chain", "config.sh")
    text = None
    if os.path.exists(cfg):
        text = open(cfg).read()
    else:
        bl = os.path.join(os.path.dirname(d), "batch.list")
        for line in open(bl):
            if line.split() and line.split()[0].rstrip("/") == d.rstrip("/"):
                text = line
    if text is None:
        raise FileNotFoundError("no configuration for %s" % d)
    args = dict(re.findall(r"([a-z_0-9]+/[a-z_0-9]+)=(\S+)", text))
    return {k: v.rstrip(")") for k, v in args.items()}


def table_of(d):
    return member_args(d)["problem/comp0_file"]
