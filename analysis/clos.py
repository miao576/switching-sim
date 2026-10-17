# analysis/clos.py
"""CLOS 网络无阻塞条件验证。"""


def clos_nonblocking_type(m: int, n: int) -> str:
    """
    C(m, n, r) 的无阻塞类型：
      m >= 2n-1 -> strict_nonblocking
      m >= n    -> rearrangeably_nonblocking
      否则       -> blocking
    """
    assert m > 0 and n > 0
    if m >= 2 * n - 1:
        return "strict_nonblocking"
    if m >= n:
        return "rearrangeably_nonblocking"
    return "blocking"


def total_crosspoints(m: int, n: int, r: int) -> int:
    """三级 CLOS 交叉点总数：输入级 + 中间级 + 输出级。"""
    assert m > 0 and n > 0 and r > 0
    input_stage = r * n * m
    middle_stage = r * m * r
    output_stage = r * n * m
    return input_stage + middle_stage + output_stage


def check_clos(m: int, n: int, r: int) -> dict:
    return {
        "name": f"C({m},{n},{r})",
        "total_crosspoints": total_crosspoints(m, n, r),
        "type": clos_nonblocking_type(m, n),
    }