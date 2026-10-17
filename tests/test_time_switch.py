# tests/test_time_switch.py
"""Step 2 验收测试：T 接线器两种模式。"""
from units.time_switch import TimeSwitch


def test_seq_w_ctrl_r_single_connection():
    ts = TimeSwitch(32, "seq_w_ctrl_r")
    ts.connect(2, 15)
    ins = [None] * 32
    ins[2] = "A"
    outs = ts.switch(ins)
    assert outs[15] == "A"
    assert outs[2] is None


def test_ctrl_w_seq_r_bidirectional():
    ts = TimeSwitch(32, "ctrl_w_seq_r")
    ts.connect(12, 27)
    ts.connect(27, 12)
    ins = [None] * 32
    ins[12] = "from_a"
    ins[27] = "from_b"
    outs = ts.switch(ins)
    assert outs[27] == "from_a"
    assert outs[12] == "from_b"


def test_both_modes_equivalent_for_same_connections():
    ins = [None] * 32
    ins[2] = "X"
    ins[5] = "Y"
    ins[9] = "Z"

    a = TimeSwitch(32, "seq_w_ctrl_r")
    a.connect(2, 20); a.connect(5, 21); a.connect(9, 22)
    outs_a = a.switch(ins)

    b = TimeSwitch(32, "ctrl_w_seq_r")
    b.connect(2, 20); b.connect(5, 21); b.connect(9, 22)
    outs_b = b.switch(ins)

    for ts in (20, 21, 22):
        assert outs_a[ts] == outs_b[ts]
    assert outs_a[20] == "X"
    assert outs_a[21] == "Y"
    assert outs_a[22] == "Z"


def test_unconnected_output_is_none():
    ts = TimeSwitch(32)
    outs = ts.switch([None] * 32)
    assert all(o is None for o in outs)


def test_disconnect():
    ts = TimeSwitch(32, "seq_w_ctrl_r")
    ts.connect(2, 15)
    ts.disconnect(2, 15)
    ins = [None] * 32
    ins[2] = "X"
    outs = ts.switch(ins)
    assert outs[15] is None


def test_invalid_mode_raises():
    try:
        TimeSwitch(32, "bogus")
        assert False, "应当抛出 AssertionError"
    except AssertionError:
        pass


if __name__ == "__main__":
    test_seq_w_ctrl_r_single_connection()
    test_ctrl_w_seq_r_bidirectional()
    test_both_modes_equivalent_for_same_connections()
    test_unconnected_output_is_none()
    test_disconnect()
    test_invalid_mode_raises()
    print("Step 2 全部测试通过 ✅")