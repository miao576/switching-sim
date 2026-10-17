# tests/test_blocking.py
"""Step 6 验收测试：Lee 阻塞率模型。"""
import math
from analysis.blocking import lee_blocking_clos, sweep_load


def test_single_formula_exact_value():
    # load=0.5, n=4, m=8 -> p=0.25, q=0.75, P=(1-0.5625)^8
    expected = (1 - 0.75 ** 2) ** 8
    got = lee_blocking_clos(0.5, 4, 8)
    assert math.isclose(got, expected, rel_tol=1e-12)


def test_zero_load_gives_zero_blocking():
    assert lee_blocking_clos(0.0, 4, 8) == 0.0


def test_full_load_unity_when_m_less_than_n():
    # m < n 时 p > 1，被截到 1，q=0，P=1
    assert lee_blocking_clos(1.0, 8, 4) == 1.0


def test_blocking_increases_with_load():
    vals = [lee_blocking_clos(ld, 8, 8) for ld in (0.1, 0.5, 0.9)]
    assert vals[0] < vals[1] < vals[2]


def test_blocking_decreases_with_m():
    b_small = lee_blocking_clos(0.9, 8, 8)
    b_large = lee_blocking_clos(0.9, 8, 20)
    assert b_large < b_small


def test_sweep_load_returns_sorted_pairs():
    pairs = sweep_load(8, 8)
    assert len(pairs) == 5
    loads = [p[0] for p in pairs]
    probs = [p[1] for p in pairs]
    assert loads == sorted(loads)
    for i in range(1, len(probs)):
        assert probs[i] >= probs[i - 1]


def test_invalid_load_raises():
    try:
        lee_blocking_clos(1.5, 4, 8)
        assert False
    except AssertionError:
        pass


if __name__ == "__main__":
    test_single_formula_exact_value()
    test_zero_load_gives_zero_blocking()
    test_full_load_unity_when_m_less_than_n()
    test_blocking_increases_with_load()
    test_blocking_decreases_with_m()
    test_sweep_load_returns_sorted_pairs()
    test_invalid_load_raises()
    print("Step 6 全部测试通过 ✅")