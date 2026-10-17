# tests/test_space_switch.py
"""Step 3 验收测试：S 接线器。"""
from units.space_switch import SpaceSwitch


def test_single_connection():
    sw = SpaceSwitch(8)
    sw.connect(0, 3)
    out, payload = sw.route(0, "voice")
    assert out == 3
    assert payload == "voice"


def test_unconnected_returns_none():
    sw = SpaceSwitch(8)
    out, payload = sw.route(5, "voice")
    assert out is None
    assert payload is None


def test_disconnect():
    sw = SpaceSwitch(8)
    sw.connect(2, 6)
    sw.disconnect(2, 6)
    out, _ = sw.route(2, "voice")
    assert out is None


def test_multiple_independent_connections():
    sw = SpaceSwitch(8)
    sw.connect(0, 3)
    sw.connect(1, 5)
    sw.connect(7, 2)
    assert sw.route(0, "a") == (3, "a")
    assert sw.route(1, "b") == (5, "b")
    assert sw.route(7, "c") == (2, "c")


def test_unicaast_conflict_raises():
    sw = SpaceSwitch(8)
    sw.connect(0, 3)
    try:
        sw.connect(0, 4)          # 同一条输入线连第二个输出，应报错
        assert False, "应当抛出 ValueError"
    except ValueError:
        pass


def test_connected_pairs():
    sw = SpaceSwitch(4)
    sw.connect(0, 1)
    sw.connect(2, 3)
    pairs = set(sw.connected_pairs())
    assert pairs == {(0, 1), (2, 3)}


if __name__ == "__main__":
    test_single_connection()
    test_unconnected_returns_none()
    test_disconnect()
    test_multiple_independent_connections()
    test_unicaast_conflict_raises()
    test_connected_pairs()
    print("Step 3 全部测试通过 ✅")