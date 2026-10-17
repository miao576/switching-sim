# networks/dsn.py
"""DSN 简化模型：两级 DSE + 自选路由 + 选择/数据/置闲字。"""


class DSESwitch:
    """
    单个 DSE：n_ports 个端口，每端口 n_slots 个时隙。
    routing[out_port][out_slot][in_port] = in_slot 表示建立过的路由。
    """

    def __init__(self, n_ports=8, n_slots=32):
        self.n_ports = n_ports
        self.n_slots = n_slots
        self.routing = [[{} for _ in range(n_slots)] for _ in range(n_ports)]

    def select(self, in_port, in_slot, out_port, out_slot):
        """选择字：建立 in_port/in_slot -> out_port/out_slot 路由。"""
        assert 0 <= in_port < self.n_ports
        assert 0 <= out_port < self.n_ports
        assert 0 <= in_slot < self.n_slots
        assert 0 <= out_slot < self.n_slots
        self.routing[out_port][out_slot][in_port] = in_slot
        return {
            "type": "select",
            "in_port": in_port, "in_slot": in_slot,
            "out_port": out_port, "out_slot": out_slot,
        }

    def idle(self, in_port, in_slot, out_port, out_slot):
        """置闲字：拆除路由。"""
        assert 0 <= out_port < self.n_ports
        assert 0 <= out_slot < self.n_slots
        self.routing[out_port][out_slot].pop(in_port, None)
        return {"type": "idle", "in_port": in_port,
                "in_slot": in_slot, "out_port": out_port, "out_slot": out_slot}

    def forward(self, in_port, in_slot, payload):
        """
        按已建立路由转发数据。返回 (out_port, out_slot, word)。
        未建立路由时返回 (None, None, {"type": "idle"})。
        """
        assert 0 <= in_port < self.n_ports
        assert 0 <= in_slot < self.n_slots
        for out_port in range(self.n_ports):
            for out_slot in range(self.n_slots):
                entry = self.routing[out_port][out_slot]
                if entry.get(in_port) == in_slot:
                    return out_port, out_slot, {
                        "type": "data",
                        "in_port": in_port, "in_slot": in_slot,
                        "out_port": out_port, "out_slot": out_slot,
                        "payload": payload,
                    }
        return None, None, {"type": "idle"}


class DSNSimple:
    """
    两级 DSN：stage1 + stage2 级联。
    地址两段 (A, B)：A 用于第 1 级选路，B 用于第 2 级选路。
    """

    def __init__(self, n_ports=8, n_slots=32):
        self.stage1 = DSESwitch(n_ports, n_slots)
        self.stage2 = DSESwitch(n_ports, n_slots)

    def establish(self, in_port, in_slot, addr, out_port, out_slot):
        """
        按地址建立跨两级的路由。
        addr: 二元组 (a1, a2)，a1/a2 分别作为两级中间端口选择依据。
        返回 (select_word_stage1, select_word_stage2)。
        """
        a1, a2 = addr
        w1 = self.stage1.select(in_port, in_slot, a1, out_slot)
        w2 = self.stage2.select(a1, out_slot, out_port, out_slot)
        return w1, w2

    def release(self, in_port, in_slot, addr, out_port, out_slot):
        a1, _ = addr
        self.stage1.idle(in_port, in_slot, a1, out_slot)
        self.stage2.idle(a1, out_slot, out_port, out_slot)

    def send(self, in_port, in_slot, payload):
        """
        自选路由转发：
          1) stage1 按 in_port/in_slot 找到中间端口 a1；
          2) stage2 按 a1/中间时隙找到最终 out_port。
        返回 (out_port, out_slot, word) 或 (None, None, idle_word)。
        """
        mid_port, mid_slot, w1 = self.stage1.forward(in_port, in_slot, payload)
        if w1["type"] != "data":
            return None, None, w1
        out_port, out_slot, w2 = self.stage2.forward(mid_port, mid_slot, payload)
        if w2["type"] != "data":
            return None, None, w2
        return out_port, out_slot, w2