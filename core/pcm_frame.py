"""PCM30/32 帧结构 —— G.704 基本帧 + 16 帧复帧。"""
from dataclasses import dataclass, field
from typing import List

FAS_CODE  = "0011011"  # 帧同步码
TS_PER_FRAME = 32  # 每帧时隙数
BITS_PER_TS = 8  # 每时隙位数
FRAMES_PER_MULTIFRAME = 16  # 每复帧时帧数
VOICE_TS = list(range(1, 16)) + list(range(17, 32))  # 语音时隙列表

@dataclass
class PCMFrame:
    """PCM30/32 帧结构"""
    frame_no: int  # 帧号
    slots: list[int] = field(default_factory=lambda: ["00000000"] * TS_PER_FRAME)  # 时隙数据列表

    def set_slot(self, ts: int, bits: str):
        assert 0 <= ts < TS_PER_FRAME, f"时隙号 {ts} 超出范围 [0, {TS_PER_FRAME})"
        assert len(bits) == BITS_PER_TS, f"位数 {len(bits)} 不等于 {BITS_PER_TS}"
        self.slots[ts] = bits

    def get_slot(self, ts: int) -> str:
        assert 0 <= ts < TS_PER_FRAME, f"时隙号 {ts} 超出范围 [0, {TS_PER_FRAME})"
        return self.slots[ts]

    def build_ts0(self):
        """偶帧填 FAS；奇帧第 2 位固定 1，A1=0 表示帧同步。"""
        if self.frame_no % 2 == 0:
            self.slots[0] = "1" + FAS_CODE  # 偶数帧
        else:
            self.slots[0] = "11011111"  # 奇数帧

    def build_ts16(self):
        """F0 填复帧同步码 1101，其余帧作信令占位。"""
        if self.frame_no == 0:
            self.slots[16] = "11010000"  # 复帧起始帧
        else:
            self.slots[16] = "00000000"  # 复帧非起始帧

def make_multiframe(voice_payloads: dict[int, str]|None = None) -> List[PCMFrame]:
    """
    生成一个完整复帧（16 个基本帧）。
    voice_payloads: {ts: 8bit 串}，会填入每一帧的对应话路时隙。
    """
    frame = []
    for fno in range(FRAMES_PER_MULTIFRAME):
        f = PCMFrame(frame_no=fno)
        f.build_ts0()
        f.build_ts16()
        if voice_payloads:
            for ts, bits in voice_payloads.items():
                f.set_slot(ts, bits)
        frame.append(f)
    return frame

def verify_fas(frame: PCMFrame) -> bool:
    """验证帧同步码"""
    for f in frame:
        if f.frame_no % 2 == 0:
            if f.get_slot(0)[1:] != FAS_CODE:
                return False
    return True
