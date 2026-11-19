"""The one embedding model of the knowledge base (stage K4, brief 12.6; decision 0015).

The model is BAAI/bge-small-en-v1.5 at a pinned revision, fetched once into the environment
of this worktree (`kb/.venv/models/...`) by `kb embed --fetch-model`, and afterwards loaded
from there with the network off. Choice, licence and source: `kb/EMBEDDING.md`.

Rules this module keeps:
- Requests to huggingface.co go through urllib with a generic client name and no token (the
  user's Hugging Face cache and token are never read); only the files listed in MODEL["files"]
  are fetched, weights only as safetensors (no pickle), every file checked against the hash
  the repository tree lists (sha256 of LFS files, git blob sha1 of the others).
- Loading sets HF_HUB_OFFLINE=1 and HF_HOME inside the environment before any Hugging Face
  import, passes local_files_only=True and trust_remote_code=False: nothing leaves the machine
  and no downloaded Python runs.
- `HashEmbedder` is a deterministic stand-in (numpy only) for the tests.
"""
import hashlib
import json
import os
import re
import shutil
import time
import urllib.request

from .paths import KB_DIR

MODEL = {
    "name": "BAAI/bge-small-en-v1.5",
    "revision": "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a",
    "license": "MIT",
    "source": "https://huggingface.co/BAAI/bge-small-en-v1.5",
    "dim": 384,
    "max_seq_length": 512,
    "pooling": "cls",
    "normalize": True,
    # bge v1.5: the instruction is added to short queries only, never to passages
    "query_prefix": "Represent this sentence for searching relevant passages: ",
    "files": [".gitattributes", "1_Pooling/config.json", "README.md", "config.json",
              "config_sentence_transformers.json", "model.safetensors", "modules.json",
              "sentence_bert_config.json", "special_tokens_map.json", "tokenizer.json",
              "tokenizer_config.json", "vocab.txt"],
}
USER_AGENT = "kb-embed-fetch/0.1 (generic research client)"
HF = "https://huggingface.co"


def model_key(m=MODEL):
    """The value of embeddings.model: name and the first seven characters of the revision."""
    return f"{m['name'].split('/')[-1]}@{m['revision'][:7]}"


def models_root():
    return os.environ.get("KB_EMBED_MODELS") or os.path.join(KB_DIR, ".venv", "models")


def model_dir(m=MODEL):
    return os.path.join(models_root(), m["name"].replace("/", "__"), m["revision"])


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def tree(m=MODEL):
    """{path: {"size", "sha256" or "sha1"}} from the repository tree at the pinned revision."""
    out = {}
    raw = json.loads(_get(f"{HF}/api/models/{m['name']}/tree/{m['revision']}?recursive=1"))
    for e in raw:
        if e.get("type") != "file":
            continue
        rec = {"size": e.get("size")}
        if e.get("lfs"):
            rec["sha256"] = e["lfs"].get("oid") or e["lfs"].get("sha256")
            rec["size"] = e["lfs"].get("size", rec["size"])
        else:
            rec["sha1"] = e.get("oid")
        out[e["path"]] = rec
    return out


def fetch(m=MODEL, log=print):
    """Download the listed files of the pinned revision into a new empty directory, check every
    file against the tree's hash, then move the directory into place. Returns the record."""
    final = model_dir(m)
    if os.path.exists(os.path.join(final, "download.json")):
        log(f"model already present: {final}")
        return json.load(open(os.path.join(final, "download.json")))
    listing = tree(m)
    missing = [f for f in m["files"] if f not in listing]
    if missing:
        raise RuntimeError(f"files not in the tree of {m['name']}@{m['revision']}: {missing}")
    parent = os.path.dirname(final)
    os.makedirs(parent, exist_ok=True)
    tmp = os.path.join(parent, f".fetch-{os.getpid()}-{int(time.time())}")
    os.makedirs(tmp)                                          # new and empty
    rec = {"name": m["name"], "revision": m["revision"], "source": m["source"], "license": m["license"],
           "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "user_agent": USER_AGENT,
           "files": {}}
    for f in m["files"]:
        if f.startswith("/") or ".." in f.split("/"):
            raise RuntimeError(f"refusing path {f}")
        data = _get(f"{HF}/{m['name']}/resolve/{m['revision']}/{f}", timeout=600)
        want = listing[f]
        got = {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if want.get("size") is not None and want["size"] != len(data):
            raise RuntimeError(f"{f}: size {len(data)} != tree size {want['size']}")
        if "sha256" in want and want["sha256"] != got["sha256"]:
            raise RuntimeError(f"{f}: sha256 {got['sha256']} != tree {want['sha256']}")
        if "sha1" in want and want["sha1"] != _git_blob_sha1(data):
            raise RuntimeError(f"{f}: git blob sha1 differs from the tree")
        got["checked_against"] = "lfs sha256" if "sha256" in want else "git blob sha1"
        path = os.path.join(tmp, f)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        os.chmod(path, 0o444)
        rec["files"][f] = got
        log(f"  {f}: {len(data)} bytes, {got['checked_against']} ok")
    with open(os.path.join(tmp, "download.json"), "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    if os.path.exists(final):
        shutil.rmtree(final)                              # an incomplete earlier attempt (no download.json)
    os.replace(tmp, final)
    return rec


def weights_sha256(m=MODEL):
    rec = json.load(open(os.path.join(model_dir(m), "download.json")))
    return rec["files"]["model.safetensors"]["sha256"]


def check_local(m=MODEL):
    """Recompute the sha256 of every stored file against download.json; returns problems."""
    d = model_dir(m)
    p = os.path.join(d, "download.json")
    if not os.path.exists(p):
        return [f"no model at {d} (run: kb embed --fetch-model)"]
    rec = json.load(open(p))
    bad = []
    for f, want in rec["files"].items():
        fp = os.path.join(d, f)
        if not os.path.exists(fp):
            bad.append(f"{f}: missing")
            continue
        h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        if h != want["sha256"]:
            bad.append(f"{f}: sha256 differs")
    return bad


class STEmbedder:
    """bge-small-en-v1.5 through sentence-transformers on the processors, offline."""

    def __init__(self, m=MODEL, threads=8, batch_size=32):
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        os.environ.setdefault("HF_HOME", os.path.join(models_root(), "hf_home"))
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
            os.environ[v] = str(threads)
        bad = check_local(m) if os.environ.get("KB_EMBED_SKIP_CHECK") != "1" else []
        if bad:
            raise RuntimeError("; ".join(bad))
        import torch
        torch.set_num_threads(threads)
        from sentence_transformers import SentenceTransformer
        self.m = m
        self.key = model_key(m)
        self.dim = m["dim"]
        self.batch_size = batch_size
        self.model = SentenceTransformer(model_dir(m), device="cpu", local_files_only=True,
                                         trust_remote_code=False, token=False)
        self.model.max_seq_length = m["max_seq_length"]
        self.tokenizer = self.model.tokenizer

    def n_tokens(self, texts):
        """Word pieces including [CLS] and [SEP], before truncation."""
        enc = self.tokenizer(list(texts), add_special_tokens=True, truncation=False)["input_ids"]
        return [len(e) for e in enc]

    def encode(self, texts, query=False):
        import numpy as np
        texts = [(self.m["query_prefix"] + t) if query else t for t in texts]
        v = self.model.encode(texts, batch_size=self.batch_size, convert_to_numpy=True,
                              normalize_embeddings=self.m["normalize"], show_progress_bar=False)
        return np.asarray(v, dtype=np.float32)


class HashEmbedder:
    """Deterministic bag-of-words vectors (signed feature hashing, unit length); numpy only.
    A stand-in for the tests: similar texts share words, hence directions."""

    def __init__(self, dim=64, key="hash64@test"):
        self.dim = dim
        self.key = key
        self.m = {"name": "test/hash", "revision": "0" * 40, "dim": dim, "max_seq_length": 10 ** 6,
                  "pooling": "none", "normalize": True, "query_prefix": "", "license": "test",
                  "source": "kbtool.embed_model.HashEmbedder"}

    def n_tokens(self, texts):
        return [len(re.findall(r"\w+", t)) for t in texts]

    def encode(self, texts, query=False):
        import numpy as np
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in re.findall(r"\w+", t.lower()):
                h = int.from_bytes(hashlib.md5(w.encode()).digest()[:8], "little")
                out[i, h % self.dim] += 1.0 if (h >> 32) & 1 else -1.0
            n = float(np.linalg.norm(out[i]))
            if n > 0:
                out[i] /= n
        return out
