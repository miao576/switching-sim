# networks/tst.py
"""TST 三级交换网络：前 T → S → 后 T，支持动态选路与释放。"""
from units.time_switch import TimeSwitch
from units.space_switch import SpaceSwitch


class TSTNetwork:
    def __init__(self, n_in_lines=4, n_slots=64,
                 first_mode="seq_w_ctrl_r", last_mode="ctrl_w_seq_r"):
        self.n_in = n_in_lines
        self.n = n_slots
        self.first_stage = [TimeSwitch(n_slots, first_mode) for _ in range(n_in_lines)]
        self.space_stage = SpaceSwitch(n_in_lines, n_slots)
        self.last_stage = [TimeSwitch(n_slots, last_mode) for _ in range(n_in_lines)]
        self._routes = []

    def connect(self, in_line, in_ts, out_line, out_ts, internal_ts):
        self.first_stage[in_line].connect(in_ts, internal_ts)
        self.space_stage.connect(in_line, out_line, internal_ts)
        self.last_stage[out_line].connect(internal_ts, out_ts)
        self._routes.append((in_line, in_ts, out_line, out_ts, internal_ts))

    def find_path_and_connect(self, in_line, in_ts, out_line, out_ts):
        """单向动态选路与阻塞控制"""
        if self.last_stage[out_line].CM[out_ts] is not None:
            return False, None

        for internal_ts in range(self.n):
            if self.first_stage[in_line].CM[internal_ts] is not None:
                continue
            if self.last_stage[out_line].CM[internal_ts] is not None:
                continue
            if not self.space_stage.connect(in_line, out_line, internal_ts):
                continue
            self.connect(in_line, in_ts, out_line, out_ts, internal_ts)
            return True, internal_ts
        return False, None

    def find_path_and_connect_bidirectional(self, line_a, ts_a, line_b, ts_b):
        """
        双向连接：先分配正向，再自动用反相法分配反向。
        返回: (True, 正向内部时隙, 反向内部时隙) 或 (False, None, None)
        """
        # 1. 建立正向
        success, fwd_internal = self.find_path_and_connect(line_a, ts_a, line_b, ts_b)
        if not success:
            return False, None, None

        # 2. 反相法计算反向内部时隙
        rev_internal = (fwd_internal + self.n // 2) % self.n

        # 3. 检查反向内部时隙是否被占用，如果冲突则回滚正向建立
        if self.first_stage[line_b].CM[rev_internal] is not None or self.last_stage[line_a].CM[rev_internal] is not None:
            self.disconnect(line_a, ts_a, line_b, ts_b)
            return False, None, None

        # 4. 建立反向
        if not self.space_stage.connect(line_b, line_a, rev_internal):
            self.disconnect(line_a, ts_a, line_b, ts_b)
            return False, None, None

        self.connect(line_b, ts_b, line_a, ts_a, rev_internal)
        return True, fwd_internal, rev_internal

    def disconnect(self, in_line, in_ts, out_line, out_ts):
        for route in self._routes:
            if (route[0] == in_line and route[1] == in_ts and 
                route[2] == out_line and route[3] == out_ts):
                internal_ts = route[4]
                self.first_stage[in_line].disconnect(in_ts, internal_ts)
                self.space_stage.disconnect(in_line, out_line, internal_ts)
                self.last_stage[out_line].disconnect(internal_ts, out_ts)
                self._routes.remove(route)
                return True
        return False

    def switch_all(self, in_lines):
        assert len(in_lines) == self.n_in
        first_out = [self.first_stage[i].switch(in_lines[i]) for i in range(self.n_in)]
        s_out = [[None] * self.n for _ in range(self.n_in)]
        for ts in range(self.n):
            for in_line in range(self.n_in):
                payload = first_out[in_line][ts]
                if payload is not None:
                    out_line, p = self.space_stage.route(in_line, ts, payload)
                    if out_line is not None:
                        s_out[out_line][ts] = p
        return [self.last_stage[j].switch(s_out[j]) for j in range(self.n_in)]