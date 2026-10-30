class SignalTone:
    DIAL_TONE = "dial_tone"          # 拨号音
    BUSY_TONE = "busy_tone"          # 忙音
    RING_BACK_TONE = "ring_back_tone" # 回铃音
    RINGING = "ringing"              # 铃流 (25Hz/90V)
    
    @staticmethod
    def get_tone_frequency(tone_type:str) -> str:
        tones = {
            SignalTone.DIAL_TONE: "450Hz 连续",
            SignalTone.BUSY_TONE: "450Hz 0.35s通/0.35s断",
            SignalTone.RING_BACK_TONE: "450Hz 1s通/4s断",
            SignalTone.RINGING: "25Hz 90V 铃流"
        }
        return tones.get(tone_type, "无信号")

    @staticmethod
    def play(tone_type: str):
        """模拟向PCM时隙插入信号音"""
        if tone_type:
            print(f"[信号音] 播放: {tone_type} ({SignalTone.get_tone_frequency(tone_type)})")