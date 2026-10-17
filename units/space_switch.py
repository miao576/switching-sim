class SpaceSwitch:
    """
    每个交叉点 (in_line, out_line) 可闭合/断开。
    单播约束：一条输入线同一时隙只能连一个输出线。
    """

    def __init__(self, n_lines: int):
        self.n = n_lines
        self.CrossPoint = [[False] * n_lines for _ in range(n_lines)]

    def connect(self, in_line: int, out_line: int):
        assert 0 <= in_line < self.n, f"输入线号 {in_line} 超出范围 [0, {self.n})"
        assert 0 <= out_line < self.n, f"输出线号 {out_line} 超出范围 [0, {self.n})"
        # 单播约束：一条输入线同一时隙只能连一个输出线
        for j in range(self.n):
            if j != out_line and self.CrossPoint[in_line][j]:
                raise ValueError(
                    f"输入线 {in_line} 已连接到输出线 {j}，无法连接到输出线 {out_line}"
                )
            self.CrossPoint[in_line][out_line] = True

    def disconnect(self, in_line: int, out_line: int):
        assert 0 <= in_line < self.n, f"输入线号 {in_line} 超出范围 [0, {self.n})"
        assert 0 <= out_line < self.n, f"输出线号 {out_line} 超出范围 [0, {self.n})"
        self.CrossPoint[in_line][out_line] = False

    def route(self, in_line: int, payload):
        assert 0 <= in_line < self.n, f"输入线号 {in_line} 超出范围 [0, {self.n})"
        for out_line in range(self.n):
            if self.CrossPoint[in_line][out_line]:
                return out_line,payload

        return None, None  # 没有连接的输出线

    def connected_pairs(self):
        """返回当前所有闭合的 (in_line, out_line) 列表。"""
        return [
            (i, j)
            for i in range(self.n)
            for j in range(self.n)
            if self.CrossPoint[i][j]
        ]
