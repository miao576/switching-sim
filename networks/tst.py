# networks/tst.py
"""TST 三级交换网络：前 T → S → 后 T，含反相法双向建立。"""
from units.time_switch import TimeSwitch
from units.space_switch import SpaceSwitch


class TSTNetwork:
    def __init__(self, n_in_lines=4, n_slots=64,
                 first_mode="seq_w_ctrl_r", last_mode="ctrl_w_seq_r"):
        self.n_in = n_in_lines
        self.n = n_slots
        self.first_stage = [TimeSwitch(n_slots, first_mode) for _ in range(n_in_lines)]
        self.space_stage = SpaceSwitch(n_in_lines)
        self.last_stage = [TimeSwitch(n_slots, last_mode) for _ in range(n_in_lines)]
        self._routes = []

    def connect(self, in_line, in_ts, out_line, out_ts, internal_ts):
        """建立单向连接：in_line/in_ts → out_line/out_ts，经 internal_ts。"""
        self.first_stage[in_line].connect(in_ts, internal_ts)
        self.space_stage.connect(in_line, out_line)
        self.last_stage[out_line].connect(internal_ts, out_ts)
        self._routes.append((in_line, in_ts, out_line, out_ts, internal_ts))

    def connect_bidirectional(self, line_a, ts_a, line_b, ts_b, internal_ts=None):
        """
        双向连接。正向内部时隙 internal_ts，反向自动取 (internal_ts + N/2) % N。
        返回 (正向内部时隙, 反向内部时隙)。
        """
        if internal_ts is None:
            internal_ts = ts_b % self.n
        reverse_internal = (internal_ts + self.n // 2) % self.n
        self.connect(line_a, ts_a, line_b, ts_b, internal_ts)
        self.connect(line_b, ts_b, line_a, ts_a, reverse_internal)
        return internal_ts, reverse_internal

    def switch_all(self, in_lines):
        """
        in_lines[i][ts] -> 前 T -> S -> 后 T -> out_lines[out_line][out_ts]
        """
        assert len(in_lines) == self.n_in
        for row in in_lines:
            assert len(row) == self.n

        # 1) 前 T：每条输入母线各自做时隙交换
        first_out = [self.first_stage[i].switch(in_lines[i]) for i in range(self.n_in)]

        # 2) S 级：按内部时隙逐个搬运
        s_out = [[None] * self.n for _ in range(self.n_in)]
        for ts in range(self.n):
            for in_line in range(self.n_in):
                payload = first_out[in_line][ts]
                if payload is not None:
                    out_line, p = self.space_stage.route(in_line, payload)
                    if out_line is not None:
                        s_out[out_line][ts] = p

        # 3) 后 T：每条输出母线各自做时隙交换
        return [self.last_stage[j].switch(s_out[j]) for j in range(self.n_in)]