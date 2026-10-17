"""T 接线器 —— 共享存储器型时分交换单元。"""

class TimeSwitch:
    """
    mode:
      - "seq_w_ctrl_r": 顺序写入、控制读出
      - "ctrl_w_seq_r": 控制写入、顺序读出
    """
    Modes = ["seq_w_ctrl_r", "ctrl_w_seq_r"]
    def __init__(self, n_slots: int = 32, mode: str = "seq_w_ctrl_r"):
        assert mode in self.Modes, f"mode 必须是 {self.Modes} 之一"
        self.n = n_slots
        self.mode = mode
        self.CM = [None] * n_slots
        self.SM = [None] * n_slots

    def connect(self, input_ts: int, output_ts: int):
        """连接控制器时隙"""
        assert 0 <= input_ts < self.n, f"输入时隙号 {input_ts} 超出范围 [0, {self.n})"
        assert 0 <= output_ts < self.n, f"输出时隙号 {output_ts} 超出范围 [0, {self.n})"
        if self.mode == "seq_w_ctrl_r":
            self.CM[output_ts] = input_ts
        else:
            self.CM[input_ts] = output_ts

    def disconnect(self, input_ts: int, output_ts: int):
        """断开控制器时隙"""
        assert 0 <= input_ts < self.n, f"输入时隙号 {input_ts} 超出范围 [0, {self.n})"
        assert 0 <= output_ts < self.n, f"输出时隙号 {output_ts} 超出范围 [0, {self.n})"
        if self.mode == "seq_w_ctrl_r":
            if self.CM[output_ts] == input_ts:
                self.CM[output_ts] = None
        else:
            if self.CM[input_ts] == output_ts:
                self.CM[input_ts] = None

    def switch(self,in_slots):
        """交换时隙数据"""
        assert len(in_slots) == self.n, f"输入时隙数 {len(in_slots)} 不等于 {self.n}"
        out_slots = [None] * self.n
        if self.mode == "seq_w_ctrl_r":
            for ts in range(self.n):
                self.SM[ts] = in_slots[ts]
            for ts in range(self.n):
                src = self.CM[ts]
                out_slots[ts] = self.SM[src] if src is not None else None
        else:
            for ts in range(self.n):
                dst = self.CM[ts]
                if dst is not None:
                    self.SM[dst] = in_slots[ts]
            for ts in range(self.n):
                out_slots[ts] = self.SM[ts]
        return out_slots