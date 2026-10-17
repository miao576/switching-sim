# tests/test_clos.py
"""Step 5 验收测试：CLOS 无阻塞条件。"""
from analysis.clos import (
    clos_nonblocking_type, total_crosspoints, check_clos,
)


def test_strict_nonblocking_boundary():
    n = 4
    assert clos_nonblocking_type(2 * n - 1, n) == "strict_nonblocking"
    assert clos_nonblocking_type(2 * n, n) == "strict_nonblocking"
    assert clos_nonblocking_type(2 * n - 2, n) == "rearrangeably_nonblocking"


def test_rearrangeable_boundary():
    n = 4
    assert clos_nonblocking_type(n, n) == "rearrangeably_nonblocking"
    assert clos_nonblocking_type(n - 1, n) == "blocking"


def test_typical_cases():
    assert clos_nonblocking_type(7, 4) == "strict_nonblocking"
    assert clos_nonblocking_type(4, 4) == "rearrangeably_nonblocking"
    assert clos_nonblocking_type(3, 4) == "blocking"


def test_total_crosspoints_formula():
    m, n, r = 4, 4, 4
    assert total_crosspoints(m, n, r) == r * n * m + r * m * r + r * n * m
    assert total_crosspoints(4, 4, 4) == 64 + 64 + 64


def test_check_clos_output():
    info = check_clos(7, 4, 4)
    assert info["name"] == "C(7,4,4)"
    assert info["type"] == "strict_nonblocking"
    assert info["total_crosspoints"] == 4 * 4 * 7 + 4 * 7 * 4 + 4 * 4 * 7


def test_invalid_args_raise():
    try:
        clos_nonblocking_type(0, 4)
        assert False
    except AssertionError:
        pass


if __name__ == "__main__":
    test_strict_nonblocking_boundary()
    test_rearrangeable_boundary()
    test_typical_cases()
    test_total_crosspoints_formula()
    test_check_clos_output()
    test_invalid_args_raise()
    print("Step 5 全部测试通过 ✅")