# tests/test_dsn.py
"""Step 7 验收测试：DSN 两级自选路由 + 信道字序列。"""
from networks.dsn import DSESwitch, DSNSimple


def test_dse_select_forward_idle_sequence():
    dse = DSESwitch(8, 32)
    w_sel = dse.select(0, 10, 3, 20)
    assert w_sel["type"] == "select"

    out_port, out_slot, w_data = dse.forward(0, 10, "voice")
    assert (out_port, out_slot) == (3, 20)
    assert w_data["type"] == "data"
    assert w_data["payload"] == "voice"

    dse.idle(0, 10, 3, 20)
    out_port2, out_slot2, w_idle = dse.forward(0, 10, "voice")
    assert (out_port2, out_slot2) == (None, None)
    assert w_idle["type"] == "idle"


def test_dse_unconnected_forward_returns_idle():
    dse = DSESwitch(8, 32)
    out_port, out_slot, w = dse.forward(1, 5, "voice")
    assert (out_port, out_slot) == (None, None)
    assert w["type"] == "idle"


def test_dsn_two_stage_forward():
    dsn = DSNSimple(8, 32)
    dsn.establish(in_port=0, in_slot=10, addr=(3, 6), out_port=6, out_slot=20)

    out_port, out_slot, w = dsn.send(0, 10, "voice")
    assert (out_port, out_slot) == (6, 20)
    assert w["type"] == "data"
    assert w["payload"] == "voice"


def test_dsn_unconnected_send_returns_idle():
    dsn = DSNSimple(8, 32)
    out_port, out_slot, w = dsn.send(2, 7, "voice")
    assert (out_port, out_slot) == (None, None)
    assert w["type"] == "idle"


def test_dsn_release_tears_down_route():
    dsn = DSNSimple(8, 32)
    dsn.establish(0, 10, (3, 6), 6, 20)
    dsn.release(0, 10, (3, 6), 6, 20)
    out_port, out_slot, w = dsn.send(0, 10, "voice")
    assert (out_port, out_slot) == (None, None)
    assert w["type"] == "idle"


def test_dsn_multiple_routes():
    dsn = DSNSimple(8, 32)
    dsn.establish(0, 10, (3, 6), 6, 20)
    dsn.establish(1, 11, (4, 7), 7, 21)

    o1 = dsn.send(0, 10, "a")
    o2 = dsn.send(1, 11, "b")
    assert (o1[0], o1[1], o1[2]["payload"]) == (6, 20, "a")
    assert (o2[0], o2[1], o2[2]["payload"]) == (7, 21, "b")


if __name__ == "__main__":
    test_dse_select_forward_idle_sequence()
    test_dse_unconnected_forward_returns_idle()
    test_dsn_two_stage_forward()
    test_dsn_unconnected_send_returns_idle()
    test_dsn_release_tears_down_route()
    test_dsn_multiple_routes()
    print("Step 7 全部测试通过 ✅")