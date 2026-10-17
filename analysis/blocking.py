# analysis/blocking.py
"""Lee 模型阻塞率计算。"""


def lee_blocking_clos(load: float, n: int, m: int) -> float:
    """
    load: 归一化负载 0~1，表示每条输入级链路上的平均占用率。
    n: 输入级模块入线数。
    m: 中间级模块数。
    返回 Lee 模型近似阻塞概率。
    """
    assert 0.0 <= load <= 1.0, f"load 越界: {load}"
    assert n > 0 and m > 0
    p = load * n / m
    p = min(max(p, 0.0), 1.0)
    q = 1 - p
    return (1 - q ** 2) ** m


def sweep_load(n: int, m: int, loads=(0.1, 0.3, 0.5, 0.7, 0.9)):
    """对一组负载返回 [(load, blocking_prob), ...]。"""
    return [(ld, lee_blocking_clos(ld, n, m)) for ld in loads]