"""Where things are: the main checkout ($NRPIC_HOME), the data root and the package.

$NRPIC_HOME is taken from the environment variable NRPIC_HOME when set, otherwise from the
git common directory of the checkout that holds this file (the same rule as
harness/bin/nrpic-fetch-arxiv), so that a linked worktree and the main checkout agree.
The data root is $NRPIC_HOME/kb-data unless KB_DATA_ROOT is set, and the writer lock is
$NRPIC_HOME/locks/kb-writer.lock unless KB_LOCK is set (tests set both).
"""
import os
import subprocess
from dataclasses import dataclass
from functools import lru_cache

PKG_DIR = os.path.dirname(os.path.abspath(__file__))     # .../kb/kbtool
KB_DIR = os.path.dirname(PKG_DIR)                         # .../kb
CHECKOUT = os.path.dirname(KB_DIR)                        # worktree or checkout holding kb/


@lru_cache(maxsize=1)
def nrpic_home():
    env = os.environ.get("NRPIC_HOME")
    if env:
        return os.path.abspath(env)
    try:
        common = subprocess.run(
            ["git", "-C", PKG_DIR, "rev-parse", "--path-format=absolute", "--git-common-dir"],
            check=True, capture_output=True, text=True, timeout=30).stdout.strip()
        return os.path.dirname(common)
    except Exception:                                     # not in git: fall back to the layout
        return CHECKOUT


@dataclass(frozen=True)
class Layout:
    home: str
    data: str
    lock: str

    @property
    def raw_arxiv(self):
        return os.path.join(self.data, "raw", "arxiv")

    @property
    def raw_github(self):
        return os.path.join(self.data, "raw", "github")

    @property
    def meta_arxiv(self):
        return os.path.join(self.data, "meta", "arxiv")

    @property
    def meta_github(self):
        return os.path.join(self.data, "meta", "github")

    @property
    def db_dir(self):
        return os.path.join(self.data, "db")

    @property
    def db_work(self):
        return os.path.join(self.db_dir, "kb.sqlite")

    @property
    def db_current(self):
        return os.path.join(self.db_dir, "current")

    @property
    def manifests(self):
        return os.path.join(self.data, "manifests")

    @property
    def logs(self):
        return os.path.join(self.data, "logs")

    @property
    def build(self):
        return os.path.join(self.data, "build")

    @property
    def legacy_refs(self):
        """Older copies of paper sources made before the store existed (not part of the store)."""
        return os.path.join(self.home, "refs")

    def dirs(self):
        """Directories of brief section 12.2 that K0 creates."""
        return [os.path.join(self.data, "raw", "arxiv"), os.path.join(self.data, "raw", "github"),
                self.meta_arxiv, self.meta_github,
                os.path.join(self.build, "tex"), os.path.join(self.build, "code"),
                self.db_dir, self.manifests, self.logs]


def layout(data_root=None):
    home = nrpic_home()
    data = data_root or os.environ.get("KB_DATA_ROOT") or os.path.join(home, "kb-data")
    lock = os.environ.get("KB_LOCK") or os.path.join(home, "locks", "kb-writer.lock")
    return Layout(home=home, data=os.path.abspath(data), lock=os.path.abspath(lock))


def kb_manifest_dir():
    """The manifests extracted from the brief, kept in git."""
    return os.path.join(KB_DIR, "manifests")


def schema_path():
    return os.path.join(KB_DIR, "schema.sql")


def migrations_dir():
    return os.path.join(KB_DIR, "migrations")


def fetch_command():
    """The one arXiv download command of the machine (CLAUDE.md rule 8)."""
    return os.path.join(nrpic_home(), "harness", "bin", "nrpic-fetch-arxiv")


def default_brief():
    for base in (CHECKOUT, nrpic_home()):
        p = os.path.join(base, "einstein_vlasov_pic_cosmology_agent_brief.en.md")
        if os.path.exists(p):
            return p
    return None
