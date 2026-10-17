# tests/test_main_smoke.py
"""Step 8 验收测试：main.py 全部演示可运行且无异常。"""
import io
import contextlib


def test_run_all_no_exception():
    from main import run_all
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_all()
    out = buf.getvalue()
    assert "[FAIL]" not in out, f"有演示失败:\n{out}"
    for key in ("PCM30/32", "T 接线器", "S 接线器", "TST 三级网络",
                "CLOS 无阻塞条件", "Lee 阻塞率", "DSN 两级自选路由"):
        assert key in out, f"缺少演示输出: {key}"
    assert out.count("[7/7]") == 1


def test_each_demo_individually():
    import main as m
    for name, fn in m.DEMOS:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fn()
        assert buf.getvalue().strip() != "", f"{name} 无输出"


if __name__ == "__main__":
    test_run_all_no_exception()
    test_each_demo_individually()
    print("Step 8 全部测试通过 ✅")