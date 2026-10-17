# tests/test_tst.py
"""Step 4 验收测试：TST 三级网络 + 反相法。"""
from networks.tst import TSTNetwork


def test_single_connection_pcm0_ts2_to_pcm2_ts51():
    net = TSTNetwork(4, 64)
    net.connect(0, 2, 2, 51, internal_ts=51)
    ins = [[None] * 64 for _ in range(4)]
    ins[0][2] = "hello"
    outs = net.switch_all(ins)
    assert outs[2][51] == "hello"
    assert outs[0][2] is None       # 未连接输入不会凭空出数据
    assert outs[2][2] is None        # 同母线的相邻时隙不受影响


def test_bidirectional_uses_reverse_internal():
    net = TSTNetwork(4, 64)
    fwd, rev = net.connect_bidirectional(0, 2, 2, 51, internal_ts=51)
    assert fwd == 51
    assert rev == (51 + 32) % 64    # 64 槽时半帧 = 32，反相 = 19


def test_bidirectional_forward_and_reverse_data():
    net = TSTNetwork(4, 64)
    net.connect_bidirectional(0, 2, 2, 51, internal_ts=51)
    ins = [[None] * 64 for _ in range(4)]
    ins[0][2] = "A->B"
    ins[2][51] = "B->A"
    outs = net.switch_all(ins)
    assert outs[2][51] == "A->B"
    assert outs[0][2] == "B->A"


def test_multiple_independent_connections():
    net = TSTNetwork(4, 64)
    net.connect(0, 2, 1, 10, internal_ts=10)
    net.connect(1, 3, 2, 20, internal_ts=20)
    net.connect(2, 4, 3, 30, internal_ts=30)
    ins = [[None] * 64 for _ in range(4)]
    ins[0][2] = "a"
    ins[1][3] = "b"
    ins[2][4] = "c"
    outs = net.switch_all(ins)
    assert outs[1][10] == "a"
    assert outs[2][20] == "b"
    assert outs[3][30] == "c"


def test_no_data_no_output():
    net = TSTNetwork(4, 64)
    net.connect(0, 2, 2, 51, internal_ts=51)
    ins = [[None] * 64 for _ in range(4)]
    outs = net.switch_all(ins)
    assert outs[2][51] is None


def test_unicast_conflict_raises():
    net = TSTNetwork(4, 64)
    net.connect(0, 2, 2, 51, internal_ts=51)
    try:
        net.connect(0, 3, 3, 52, internal_ts=52)  # in_line=0 已连到 out_line=2
        assert False, "应当抛出 ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_single_connection_pcm0_ts2_to_pcm2_ts51()
    test_bidirectional_uses_reverse_internal()
    test_bidirectional_forward_and_reverse_data()
    test_multiple_independent_connections()
    test_no_data_no_output()
    test_unicast_conflict_raises()
    print("Step 4 全部测试通过 ✅")