"""K7 module descriptions and task-list order (kbtool.code_modules, `kb code modules`):
comment and header extraction, block and call parsing on synthetic C++ text, and the whole
command end to end on a synthetic upstream clone and a synthetic `local/nrpic` git tree,
indexed by `kb ingest repo` first."""
import json
import os
import subprocess

import pytest

from kbtool import code_fetch, code_index, code_modules as M, code_symbols, db, paths

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@example.invalid", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

BANNER = """//========================================================================================
// AthenaXXX astrophysical plasma code
// Copyright(C) 2020 James M. Stone <jmstone@ias.edu> and the Athena code team
// Licensed under the 3-clause BSD License (the "LICENSE")
//========================================================================================
"""

TASKS = BANNER + """//! \\file particles_tasks.cpp
//! \\brief functions that control Particles tasks. Second sentence here. Third one.

#include "particles.hpp"

namespace particles {
//----------------------------------------------------------------------------------------
//! \\fn  void Particles::AssembleTasks
//! \\brief Adds particle tasks to the task lists. Called by AddPhysics.

void Particles::AssembleTasks(std::map<std::string, std::shared_ptr<TaskList>> tl) {
  TaskID none(0);
  // nrpic: push after the stages
  if (is_nrpic) {
    id.savemet = tl["before_timeintegrator"]->AddTask(&Particles::SaveMetric, this, none);
    id.push    = tl["after_timeintegrator"]->AddTask(&Particles::Push2, this, none);
    TaskID before = id.push;
    if (coll.on) {
      id.coll = tl["after_timeintegrator"]->AddTask(&Particles::Collide, this, id.push);
      before = id.coll;
    }
    id.deposit = tl["after_timeintegrator"]->AddTask(&Particles::Deposit, this, before);
    return;
  }
  // id.x = tl["stagen"]->AddTask(&Particles::Commented, this, none);
  id.push   = tl["before_timeintegrator"]->AddTask(&Particles::Push, this, none);
  /* id.y = tl["stagen"]->AddTask(&Particles::AlsoCommented, this, none); */
  return;
}

//! \\brief writes the sources
TaskStatus Particles::Deposit(Driver *pdriver, int stage) {
  DepositSources();
  return TaskStatus::complete;
}

void Particles::DepositSources() {
  auto tm = pmy_pack->ptmunu->u_tmunu;   // the sources
}

TaskStatus Particles::Push2(Driver *pdriver, int stage) {
  printf("// not a comment; tmunu in a string does not count\\n");
  return TaskStatus::complete;
}
}  // namespace particles
"""

Z4C_TASKS = BANNER + """//! \\file z4c_tasks.cpp
//! \\brief functions that control z4c tasks

namespace z4c {
void Z4c::QueueZ4cTasks() {
  NumericalRelativity *pnr = pmy_pack->pnr;
  pnr->QueueTask(&Z4c::InitRecv, this, Z4c_Recv, "Z4c_Recv", Task_Start);
  pnr->QueueTask(&Z4c::CopyU, this, Z4c_CopyU, "Z4c_CopyU", Task_Run);
  switch (indcs.ng) {
    case 2:
      pnr->QueueTask(&Z4c::CalcRHS<2>, this, Z4c_CalcRHS, "Z4c_CalcRHS",
                     Task_Run, {Z4c_CopyU}, {MHD_SetTmunu, SF_SetTmunu});
      break;
  }
  pnr->QueueTask(&Z4c::ADMConstraints_, this, Z4c_ADMC, "Z4c_ADMC", Task_End,
  //               {Z4c_Z4c2ADM});
                 {Z4c_ClearR});
  pnr->QueueTask(&DynPS<EOS, Err>::ConToPrim, pmhd, MHD_C2P, "MHD_C2P", Task_Run, {MHD_BCS});
}
template <int NGHOST>
TaskStatus Z4c::CalcRHS(Driver *pdrive, int stage) {
  auto &tmunu = pmy_pack->ptmunu->tmunu;
  return TaskStatus::complete;
}
}  // namespace z4c
"""

DRIVER_CPP = BANNER + """//! \\file driver.cpp
//  \\brief implementation of functions in class Driver

void Driver::Execute(Mesh *pmesh, ParameterInput *pin, Outputs *pout, bool wdflag) {
  if (time_evolution == TimeEvolution::tstatic) {
    std::cout << "static {" << std::endl;
  } else {
    while ((pmesh->time < tlim) && (pmesh->ncycle < nlim || nlim < 0)) {
      ExecuteTaskList(pmesh, "before_timeintegrator", 0);
      for (int stage=1; stage<=(nexp_stages); ++stage) {
        ExecuteTaskList(pmesh, "before_stagen", stage);
        if (pmesh->pmb_pack->pgrav != nullptr) {pmesh->pmb_pack->pgrav->pmgd->Solve(this, stage);}
        ExecuteTaskList(pmesh, "stagen", stage);
        ExecuteTaskList(pmesh, "after_stagen", stage);
      }
      ExecuteTaskList(pmesh, "after_timeintegrator", 1);
    }
  }
}
"""

NUMREL_CPP = """namespace numrel {
std::vector<QueuedTask>& NumericalRelativity::SelectQueue(TaskLocation loc) {
  switch(loc) {
    case Task_Start:
      return start_queue;
    case Task_Run:
      return run_queue;
    case Task_End:
      return end_queue;
  }
  return end_queue;
}
void NumericalRelativity::AssembleNumericalRelativityTasks(
       std::map<std::string, std::shared_ptr<TaskList>>& tl) {
  bool success = AssembleNumericalRelativityTasks(tl["before_stagen"], start_queue);
  success = AssembleNumericalRelativityTasks(tl["stagen"], run_queue);
  success = AssembleNumericalRelativityTasks(tl["after_stagen"], end_queue);
}
}
"""

PACK_CPP = """void MeshBlockPack::AddPhysics(ParameterInput *pin) {
  if (pin->DoesBlockExist("z4c")) {
    pz4c = new z4c::Z4c(this, pin);
  }
  if (pz4c != nullptr || padm != nullptr) {
    pnr->AssembleNumericalRelativityTasks(tl_map);
  }
  if (pin->DoesBlockExist("particles")) {
    ppart->AssembleTasks(tl_map);
  }
}
"""

HPP = """#ifndef PARTICLES_PARTICLES_HPP_
#define PARTICLES_PARTICLES_HPP_
""" + BANNER + """//! \\file particles.hpp
//! \\brief definitions for Particles class

namespace particles {
//----------------------------------------------------------------------------------------
//! \\class Particles
//! \\brief the particles of a MeshBlockPack
class Particles {
 public:
  void AssembleTasks();
};
}  // namespace particles
#endif
"""


# ---------------------------------------------------------------- text helpers
def test_blank_comments_keeps_offsets_and_strings():
    t = 'a = "//x"; // c\nb /* d\ne */ = 1; s = "/*y*/";\n'
    out = M.blank_comments(t)
    assert len(out) == len(t) and out.count("\n") == t.count("\n")
    assert '"//x"' in out and '"/*y*/"' in out and " c" not in out and "d" not in out
    out2 = M.blank_comments(t, blank_strings=True)
    assert "x" not in out2 and "y" not in out2 and len(out2) == len(t)


def test_header_comment_athenak_style():
    h = M.header_comment(TASKS)
    assert h["file_tag"] == "particles_tasks.cpp"
    assert h["first_sentences"] == "functions that control Particles tasks. Second sentence here."
    assert h["banner_lines"] == 5
    h2 = M.header_comment(HPP)                            # include guard before the banner
    assert h2["file_tag"] == "particles.hpp" and h2["first_sentences"] == "definitions for Particles class"
    h3 = M.header_comment(BANNER + "//! \\file x.cpp\n//  \\brief\n\n#include <a>\n")
    assert h3["first_sentences"] == "" and h3["banner_lines"] == 5
    h4 = M.header_comment("/* Problem generator\n * for a test. More. */\nint x;\n")
    assert h4["first_sentences"] == "Problem generator for a test. More."
    assert M.header_comment("#include <a>\n// late comment\n")["first_sentences"] == ""


def test_first_sentences_numbering_and_abbreviations():
    s = M.first_sentences("One cycle: 1. push the particles. 2. deposit. Then more. Last.", n=2)
    assert s == "One cycle: 1. push the particles. 2. deposit."
    assert M.first_sentences("See e.g. Smith for this. Second. Third.") == "See e.g. Smith for this. Second."
    assert M.first_sentences("x" * 500, cap=50).endswith("...")


def test_comment_above():
    lines = TASKS.splitlines()
    ln = next(i for i, x in enumerate(lines, 1) if x.startswith("void Particles::AssembleTasks"))
    assert M.comment_above(lines, ln) == "Adds particle tasks to the task lists."
    ln = next(i for i, x in enumerate(lines, 1) if x.startswith("TaskStatus Particles::Deposit"))
    assert M.comment_above(lines, ln) == "writes the sources"
    ln = next(i for i, x in enumerate(lines, 1) if x.startswith("void Particles::DepositSources"))
    assert M.comment_above(lines, ln) is None             # the line above is code
    zl = Z4C_TASKS.splitlines()
    ln = next(i for i, x in enumerate(zl, 1) if x.startswith("TaskStatus Z4c::CalcRHS"))
    assert M.comment_above(zl, ln) is None                # template line skipped, then code
    hl = HPP.splitlines()
    ln = next(i for i, x in enumerate(hl, 1) if x.startswith("class Particles"))
    assert M.comment_above(hl, ln) == "the particles of a MeshBlockPack"


def test_blocks_for_header_and_else():
    code = "void f() {\n  if (a) { x(); } else { y(); }\n  for (int i=0; i<3; ++i) { z(); }\n}\n"
    blk = M.blocks(M.blank_comments(code, True), code)
    heads = [h for _, _, h in blk]
    assert "for (int i=0; i<3; ++i)" in heads
    assert "else (of if (a))" in heads
    off = code.index("z();")
    assert M.enclosing(blk, off) == ["void f()", "for (int i=0; i<3; ++i)"]


def test_split_args_template_and_braces():
    a = M.split_args('&DynPS<EOS, Err>::ConToPrim, pmhd, MHD_C2P, "MHD_C2P", Task_Run, {MHD_BCS, X}')
    assert a == ["&DynPS<EOS, Err>::ConToPrim", "pmhd", "MHD_C2P", '"MHD_C2P"', "Task_Run", "{MHD_BCS, X}"]


# ---------------------------------------------------------------- task lists
def test_registrations_addtask_and_returning_block():
    regs = M.registrations("src/particles/particles_tasks.cpp", TASKS, [])
    fns = [r["task_function"] for r in regs]
    assert fns == ["Particles::SaveMetric", "Particles::Push2", "Particles::Collide", "Particles::Deposit",
                   "Particles::Push"]                    # the two commented calls are not found
    by = {r["task_function"]: r for r in regs}
    assert by["Particles::SaveMetric"]["list"] == "before_timeintegrator"
    assert by["Particles::Collide"]["conditions"] == ["if (is_nrpic)", "if (coll.on)"]
    assert by["Particles::Collide"]["dependencies"] == ["id.push"] and by["Particles::Collide"]["id"] == "id.coll"
    assert by["Particles::Deposit"]["dependencies"] == ["before"]
    assert by["Particles::Push"]["conditions"] == [] and by["Particles::Push"]["after_returning_blocks"] == \
        ["if (is_nrpic)"]
    assert by["Particles::Deposit"]["after_returning_blocks"] == []


def test_registrations_queuetask():
    regs = M.registrations("src/z4c/z4c_tasks.cpp", Z4C_TASKS, [])
    by = {r["name"]: r for r in regs}
    assert set(by) == {"Z4c_Recv", "Z4c_CopyU", "Z4c_CalcRHS", "Z4c_ADMC", "MHD_C2P"}
    rhs = by["Z4c_CalcRHS"]
    assert rhs["task_function"] == "Z4c::CalcRHS<2>" and rhs["location"] == "Task_Run"
    assert rhs["dependencies"] == ["Z4c_CopyU"] and rhs["optional_dependencies"] == ["MHD_SetTmunu", "SF_SetTmunu"]
    assert rhs["conditions"] == ["switch (indcs.ng)"]
    assert by["Z4c_ADMC"]["dependencies"] == ["Z4c_ClearR"]            # the commented alternative is ignored
    c2p = by["MHD_C2P"]
    assert c2p["task_function"] == "DynPS<EOS, Err>::ConToPrim" and c2p["name_string"] == "MHD_C2P"


def test_driver_schedule_and_queue_map():
    d = M.driver_schedule(DRIVER_CPP)
    assert d["found"]
    assert [(c["list"], c["when"]) for c in d["calls"]] == [
        ("before_timeintegrator", "once per cycle"), ("before_stagen", "each explicit stage"),
        ("stagen", "each explicit stage"), ("after_stagen", "each explicit stage"),
        ("after_timeintegrator", "once per cycle")]
    assert d["calls"][1]["stage_arg"] == "stage"
    assert any("pmgd->Solve(this, stage)" in x for x in d["other_statements_in_stage_loop"])
    assert M.nr_queue_map(NUMREL_CPP) == {"Task_Start": "before_stagen", "Task_Run": "stagen",
                                          "Task_End": "after_stagen"}
    pa = M.physics_assembly(PACK_CPP)
    assert [c["call"] for c in pa] == ["pnr->AssembleNumericalRelativityTasks(tl_map)", "ppart->AssembleTasks(tl_map)"]
    assert pa[1]["conditions"] == ['if (pin->DoesBlockExist("particles"))']


def test_tmunu_mentions():
    lines = TASKS.splitlines()
    syms = []
    for name in ("Deposit", "DepositSources", "Push2"):
        a = next(i for i, x in enumerate(lines, 1) if f"Particles::{name}(" in x and not x.strip().startswith("//"))
        b = next(i for i in range(a, len(lines) + 1) if lines[i - 1].startswith("}"))
        syms.append({"kind": "method", "qualname": f"particles::Particles::{name}", "line_start": a, "line_end": b})
    bodies = M.function_bodies(TASKS, syms)
    assert M.tmunu_mentions("Particles::DepositSources", bodies) == "direct"
    assert M.tmunu_mentions("Particles::Deposit", bodies) == "via Particles::DepositSources"
    assert M.tmunu_mentions("Particles::Push2", bodies) is None      # only inside a string literal ... and code
    assert M.tmunu_mentions("Particles::Missing", bodies) is None


# ---------------------------------------------------------------- end to end
def git(args, cwd):
    subprocess.run(["git"] + args, cwd=cwd, env=ENV, check=True, capture_output=True)


def write_tree(root, prefix):
    files = {"particles/particles_tasks.cpp": TASKS, "particles/particles.hpp": HPP, "z4c/z4c_tasks.cpp": Z4C_TASKS,
             "driver/driver.cpp": DRIVER_CPP, "tasklist/numerical_relativity.cpp": NUMREL_CPP,
             "mesh/meshblock_pack.cpp": PACK_CPP, "pgen/notes.txt": "plain text\n",
             "parameter_input.hpp": "class ParameterInput {\n public:\n  int GetInteger();\n};\n"}
    for rel, text in files.items():
        p = root / prefix / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


@pytest.fixture
def env(tmp_path, monkeypatch):
    if not code_symbols.tree_sitter_available():
        pytest.skip("tree-sitter is not installed (kb[code])")
    # upstream: a bare remote served as file://, cloned by kb fetch-repos
    work = tmp_path / "upstream"
    work.mkdir()
    (work / "LICENSE").write_text("Copyright (c) X\nRedistribution and use in source and binary forms, with or "
                                  "without modification... Neither the name of the copyright holder\n")
    write_tree(work, "src")
    git(["init", "-q", "-b", "main"], work)
    git(["add", "-A"], work)
    git(["commit", "-q", "-m", "initial"], work)
    remote = tmp_path / "remote" / "IAS-Astrophysics"
    remote.mkdir(parents=True)
    git(["clone", "-q", "--bare", str(work), str(remote / "athenak")], tmp_path)
    # this repository: a git tree with athenak/src at lay.home; the local tree differs: no
    # particles in before_timeintegrator except SaveMetric
    home = tmp_path / "home"
    home.mkdir()
    write_tree(home, "athenak/src")
    (home / "athenak" / "LICENSE").write_text("Redistribution and use in source and binary forms\n")
    git(["init", "-q", "-b", "main"], home)
    git(["add", "-A"], home)
    git(["commit", "-q", "-m", "local"], home)
    monkeypatch.setenv("KB_GITHUB_BASE", "file://" + str(tmp_path / "remote"))
    monkeypatch.setenv("KB_DATA_ROOT", str(tmp_path / "kb-data"))
    monkeypatch.setenv("KB_LOCK", str(tmp_path / "kb-writer.lock"))
    monkeypatch.setenv("NRPIC_HOME", str(home))
    paths.nrpic_home.cache_clear()
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    (mdir / "github.tsv").write_text("IAS-Astrophysics/athenak\tcore\tall\tAthenaK\n")
    lay = paths.layout()
    for d in lay.dirs():
        os.makedirs(d, exist_ok=True)
    db.init_db(lay)
    monkeypatch.setattr(code_index, "kb_manifest_dir", lambda: str(mdir))
    code_fetch.fetch_repos(lay, str(tmp_path / "w"), manifest_dir=str(mdir), log=lambda s: None)
    res = code_index.ingest(lay, repos=["IAS-Astrophysics/athenak"], this=True, ref="main", log=lambda s: None)
    assert [r["status"] for r in res] == ["ok", "ok"]
    yield {"lay": lay, "tmp": tmp_path, "home": home}
    paths.nrpic_home.cache_clear()


def test_modules_end_to_end(env):
    lay, tmp = env["lay"], env["tmp"]
    rep = tmp / "out" / "code_modules.md"
    descs = M.build(lay, db=lay.db_work, report=str(rep), log=lambda s: None)
    assert [d["repo_id"] for d in descs] == ["local/nrpic", "IAS-Astrophysics/athenak"]
    for d in descs:
        p = os.path.join(lay.build, "code", d["repo_id"].replace("/", "__"), "modules.json")
        assert d["modules_json"] == p and json.load(open(p))["commit_sha"] == d["commit_sha"]
        files = {f["path"]: f for f in d["files"]}
        assert set(files) == {"particles/particles_tasks.cpp", "particles/particles.hpp", "z4c/z4c_tasks.cpp",
                              "mesh/meshblock_pack.cpp", "pgen/notes.txt"}
        f = files["particles/particles_tasks.cpp"]
        assert f["header"]["file_tag"] == "particles_tasks.cpp"
        defs = {x["name"]: x for x in f["definitions"]}
        assert defs["AssembleTasks"]["brief"] == "Adds particle tasks to the task lists."
        assert defs["Deposit"]["kind"] == "method" and defs["Deposit"]["brief"] == "writes the sources"
        assert files["particles/particles.hpp"]["definitions"][0]["name"] == "Particles"
        assert files["pgen/notes.txt"]["note"] == "not a C/C++ source file"
        sched = M.schedule(d)
        assert [(lst, when) for _, lst, when, _ in sched] == [
            ("before_timeintegrator", "once per cycle"), ("before_stagen", "each explicit stage"),
            ("stagen", "each explicit stage"), ("after_stagen", "each explicit stage"),
            ("after_timeintegrator", "once per cycle")]
        lists = {lst: [(m, [t["task_function"] for t in ts]) for m, ts in mods] for _, lst, _, mods in sched}
        assert lists["after_timeintegrator"] == [("particles", ["Particles::Push2", "Particles::Collide",
                                                                "Particles::Deposit"])]
        assert lists["stagen"] == [("z4c", ["Z4c::CopyU", "Z4c::CalcRHS<2>", "DynPS<EOS, Err>::ConToPrim"])]
        sw = {t["task_function"]: t["tmunu"] for t in M.source_writers(d)}
        assert sw == {"Particles::Deposit": "via Particles::DepositSources", "Z4c::CalcRHS<2>": "direct"}
    text = rep.read_text()
    assert "## local/nrpic at" in text and "## IAS-Astrophysics/athenak at" in text
    assert "| 5 | `after_timeintegrator` | once per cycle | particles | 3 |" in text
    assert "`after if (is_nrpic) returns`" in text
    assert "functions that control Particles tasks. Second sentence here." in text
    # a second run with --no-write leaves modules.json alone and gives the same description
    again = M.build(lay, db=lay.db_work, write=False, repos=["this"], log=lambda s: None)
    assert again[0]["tasks"] == descs[0]["tasks"] and "modules_json" not in again[0]


def test_modules_refuses_moved_clone(env):
    lay = env["lay"]
    con = db.connect_rw(lay.db_work)
    con.execute("UPDATE repos SET commit_sha = ? WHERE repo_id = ?", ("0" * 40, "IAS-Astrophysics/athenak"))
    con.commit()
    con.close()
    with pytest.raises(SystemExit, match="index records"):
        M.build(lay, db=lay.db_work, repos=["athenak"], write=False, log=lambda s: None)
    with pytest.raises(SystemExit, match="covers"):
        M.build(lay, db=lay.db_work, repos=["someone/else"], write=False, log=lambda s: None)
