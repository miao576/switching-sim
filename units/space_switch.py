# units/space_switch.py
"""S 接线器 —— 支持时隙复用的空间交换单元。"""

class SpaceSwitch:
    def __init__(self, n_lines: int, n_slots: int = 32):
        self.n = n_lines
        self.n_slots = n_slots
        # 三维矩阵：[时隙][入线][出线]
        self.crosspoints = [[[False for _ in range(n_lines)] for _ in range(n_lines)] for _ in range(n_slots)]

    def connect(self, in_line: int, out_line: int, ts: int) -> bool:
        """在指定时隙建立连接。如果有单播冲突返回 False。"""
        assert 0 <= ts < self.n_slots
        assert 0 <= in_line < self.n
        assert 0 <= out_line < self.n
        
        # 检查单播冲突：在同一个 ts 下，该入线是否已连到别的出线
        for j in range(self.n):
            if j != out_line and self.crosspoints[ts][in_line][j]:
                return False
                
        self.crosspoints[ts][in_line][out_line] = True
        return True

    def disconnect(self, in_line: int, out_line: int, ts: int):
        """在指定时隙断开连接"""
        assert 0 <= ts < self.n_slots
        assert 0 <= in_line < self.n
        assert 0 <= out_line < self.n
        self.crosspoints[ts][in_line][out_line] = False

    def route(self, in_line: int, ts: int, payload):
        """在指定时隙查表转发"""
        assert 0 <= ts < self.n_slots
        assert 0 <= in_line < self.n
        for out_line in range(self.n):
            if self.crosspoints[ts][in_line][out_line]:
                return out_line, payload
        return None, None

    def connected_pairs(self, ts: int = None):
        """返回当前闭合的交叉点 (in_line, out_line)。如果不传ts，返回所有时隙的。"""
        pairs = []
        if ts is not None:
            for i in range(self.n):
                for j in range(self.n):
                    if self.crosspoints[ts][i][j]:
                        pairs.append((i, j))
        else:
            for t in range(self.n_slots):
                for i in range(self.n):
                    for j in range(self.n):
                        if self.crosspoints[t][i][j]:
                            pairs.append((t, i, j))
        return pairs