"""Symbols (kbtool.code_symbols): C++ through tree-sitter with Kokkos macros, Python, Fortran."""
import pytest

from kbtool import code_symbols as S

CPP = '''#define MY_MACRO 1
namespace nrpic {
//! \\brief weights of the cubic Hermite reconstruction
KOKKOS_INLINE_FUNCTION
void HermiteWeights(const Real s, Real w[4]) {
  w[0] = s;
}
template <class MetricT>
KOKKOS_INLINE_FUNCTION
int PushMidpoint(const MetricT &met, Real x[3]) {
  par_for("k", DevExeSpace(), 0, 1, KOKKOS_LAMBDA(const int i) { x[i] = 0; });
  return 0;
}
struct MeshMetric {
  int m;
  void Gather(const Real x[3]) const { (void)x; }
  void Declared(int);
};
}  // namespace nrpic
namespace particles {
void Particles::NrpicPush(Driver *pdriver, int stage) {
  return;
}
enum class ParticlesPusher {drift, leap_frog, midpoint};
}  // namespace particles
'''


@pytest.mark.skipif(not S.tree_sitter_available(), reason="tree-sitter not in this environment")
def test_cpp_symbols():
    syms, nerr = S.cpp_symbols(CPP)
    got = {(s["kind"], s["qualname"], s["line_start"], s["line_end"]) for s in syms}
    # a blanked attribute macro moves the start to the line of the return type (5, 10)
    assert got == {("macro", "MY_MACRO", 1, 1), ("namespace", "nrpic", 2, 19),
                   ("function", "nrpic::HermiteWeights", 5, 7), ("function", "nrpic::PushMidpoint", 10, 13),
                   ("struct", "nrpic::MeshMetric", 14, 18), ("method", "nrpic::MeshMetric::Gather", 16, 16),
                   ("prototype", "nrpic::MeshMetric::Declared", 17, 17), ("namespace", "particles", 20, 25),
                   ("method", "particles::Particles::NrpicPush", 21, 23),
                   ("enum", "particles::ParticlesPusher", 24, 24)}
    assert nerr == 0
    doc = [s for s in syms if s["name"] == "HermiteWeights"][0]["doc"]
    assert doc and "Hermite" in doc


def test_macro_neutralisation_keeps_offsets():
    t = "KOKKOS_INLINE_FUNCTION void f() { g(KOKKOS_LAMBDA(int i) {}); }"
    n = S.neutralize_macros(t)
    assert len(n) == len(t) and "KOKKOS" not in n and "[=]" in n


def test_python_symbols():
    src = 'class A(B):\n    """doc A"""\n    @dec\n    def m(self, x=1):\n        def inner():\n            pass\n' \
          '\nasync def f(*a, **k):\n    return 1\n'
    syms, err = S.python_symbols(src)
    assert err is None
    got = {(s["kind"], s["qualname"], s["line_start"], s["line_end"]) for s in syms}
    assert got == {("class", "A", 1, 6), ("method", "A.m", 3, 6), ("function", "A.m.inner", 5, 6),
                   ("function", "f", 8, 9)}
    assert [s for s in syms if s["name"] == "A"][0]["doc"] == "doc A"


def test_python_syntax_error_is_reported():
    syms, err = S.python_symbols("print 'python 2'\n")
    assert syms == [] and err.startswith("SyntaxError")


def test_fortran_symbols():
    src = ("module amr\ncontains\n  recursive subroutine refine(n)\n    integer :: n\n  end subroutine refine\n"
           "  real(dp) function rho(x)\n    rho = x\n  end function\nend module amr\nprogram main\nend program main\n")
    got = {(s["kind"], s["qualname"], s["line_start"], s["line_end"]) for s in S.fortran_symbols(src)}
    assert got == {("module", "amr", 1, 9), ("subroutine", "amr::refine", 3, 5), ("function", "amr::rho", 6, 8),
                   ("program", "main", 10, 11)}
