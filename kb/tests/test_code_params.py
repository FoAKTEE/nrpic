"""Parameter index (kbtool.code_params): synthetic C++ with the cases that break a naive grep."""
import pytest

from kbtool import code_params as P

SRC = r'''
// pin->GetReal("comment", "not_a_call");
/* pin->GetInteger("block_comment", "no") */
int a = pin->GetInteger("mesh", "nx1");
Real b = pin->GetOrAddReal("z4c", "kappa1",
                           0.02);   // multi-line call
std::string s = "pin->GetString(\"string\", \"no\")";
auto raw = R"x(pin->GetReal("raw", "no"))x";
int sep = 1'000'000; char q = '"';
Real c = pinput->GetOrAddReal(block, "cfl_number", std::min(0.3, f(1, 2)));
bool d = pin->GetOrAddBoolean("particles", "deposit", (x > 0) ? true : false);
if (pin->DoesParameterExist("z4c", "lapse_oplog")) {}
if (pin->DoesBlockExist("adm")) {}
pin->SetReal(op.block_name, "last_time", t);
std::string e = pin->GetOrAddString("job", "basename", "run");
'''


def test_calls_found_exactly():
    calls = P.extract_calls(SRC)
    got = [(c["method"], c["block"], c["name"], c["default"], c["line"]) for c in calls]
    assert got == [
        ("GetInteger", "mesh", "nx1", None, 4),
        ("GetOrAddReal", "z4c", "kappa1", "0.02", 5),
        ("GetOrAddReal", "block", "cfl_number", "std::min(0.3, f(1, 2))", 10),
        ("GetOrAddBoolean", "particles", "deposit", "(x > 0) ? true : false", 11),
        ("DoesParameterExist", "z4c", "lapse_oplog", None, 12),
        ("DoesBlockExist", "adm", None, None, 13),
        ("SetReal", "op.block_name", "last_time", "t", 14),
        ("GetOrAddString", "job", "basename", '"run"', 15),
    ]
    by = {c["name"]: c for c in calls}
    assert by["kappa1"]["end_line"] == 6 and by["kappa1"]["access"] == "get_or_add"
    assert by["cfl_number"]["block_literal"] is False and by["nx1"]["block_literal"] is True
    assert all(c["args_ok"] for c in calls)


def test_mask_keeps_length_and_lines():
    m = P.mask_cpp(SRC)
    assert len(m) == len(SRC) and m.count("\n") == SRC.count("\n")
    assert "not_a_call" not in m and "raw" not in m.split("R\"")[1][:30]


def test_unbalanced_call_is_reported_not_guessed():
    calls = P.extract_calls('x = pin->GetReal("a", "b"\n')
    assert len(calls) == 1 and calls[0]["args_ok"] is False


def test_athinput_and_comparison():
    text = "# c\n<job>\nbasename = run   # name\n<output1>\nfile_type = hst\n<z4c>\nkappa1 = 0.02\nbogus = 1\n" \
           "<mesh>\nnx1=16\n"
    ins = P.parse_athinput(text)
    assert ins == [(3, "job", "basename", "run"), (5, "output1", "file_type", "hst"), (7, "z4c", "kappa1", "0.02"),
                   (8, "z4c", "bogus", "1"), (10, "mesh", "nx1", "16")]
    code = [{"block": "job", "block_literal": True, "name": "basename", "name_literal": True},
            {"block": "op.block_name", "block_literal": False, "name": "file_type", "name_literal": True},
            {"block": "z4c", "block_literal": True, "name": "kappa1", "name_literal": True},
            {"block": "hydro", "block_literal": True, "name": "nx1", "name_literal": True}]
    rows = P.compare_inputs([("f",) + x for x in ins], code)
    assert [r["status"] for r in rows] == ["literal", "computed", "literal", "unmatched", "other_block"]


@pytest.mark.parametrize("path,yes", [("inputs/z4c/athinput.bbh", True), ("problems/os/os.athinput", True),
                                      ("src/athinput.cpp", True), ("README.md", False)])
def test_is_athinput(path, yes):
    assert P.is_athinput(path) == yes
