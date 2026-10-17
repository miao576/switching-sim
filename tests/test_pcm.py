# tests/test_pcm.py
"""Step 1 验收测试：PCM30/32 帧结构。"""
from core.pcm_frame import (
    make_multiframe, verify_fas, FAS_CODE,
    VOICE_TS, TS_PER_FRAME, FRAMES_PER_MULTIFRAME,
)


def test_multiframe_size():
    mf = make_multiframe()
    assert len(mf) == FRAMES_PER_MULTIFRAME
    for f in mf:
        assert len(f.slots) == TS_PER_FRAME


def test_fas_in_even_frames():
    mf = make_multiframe()
    assert verify_fas(mf)
    assert mf[0].get_slot(0)[1:] == FAS_CODE
    assert mf[0].get_slot(0)[0] == "1"
    # 奇数帧第 2 位固定为 1
    for fno in (1, 3, 5, 7, 9, 11, 13, 15):
        assert mf[fno].get_slot(0)[1] == "1"


def test_multiframe_sync_in_f0_ts16():
    mf = make_multiframe()
    assert mf[0].get_slot(16).startswith("1101")     # F0 复帧同步码


def test_voice_slots_isolation():
    mf = make_multiframe({2: "11110000", 31: "00001111"})
    for f in mf:
        assert f.get_slot(2) == "11110000"
        assert f.get_slot(31) == "00001111"
        # 未填写的话路仍为全 0
        assert f.get_slot(1) == "00000000"


def test_voice_slot_list_excludes_ts0_ts16():
    assert 0 not in VOICE_TS
    assert 16 not in VOICE_TS
    assert len(VOICE_TS) == 30


def test_invalid_ts_raises():
    mf = make_multiframe()
    try:
        mf[0].set_slot(32, "00000000")
        assert False, "应当抛出 AssertionError"
    except AssertionError:
        pass


if __name__ == "__main__":
    # 不装 pytest 也能直接运行
    test_multiframe_size()
    test_fas_in_even_frames()
    test_multiframe_sync_in_f0_ts16()
    test_voice_slots_isolation()
    test_voice_slot_list_excludes_ts0_ts16()
    test_invalid_ts_raises()
    print("Step 1 全部测试通过 ✅")