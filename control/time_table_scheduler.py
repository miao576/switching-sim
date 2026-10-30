# control/time_table_scheduler.py
import math

class TimeTableScheduler:
    def __init__(self):
        self.base_period = 1
        self.time_counter = 0
        self.schedule_table = []
        self.program_table = []

    def design_time_table(self, programs):
        """
        programs: [(name, period_ms, func), ...]
        """
        periods = [p[1] for p in programs]
        # 计算最大公约数作为时基
        self.base_period = math.gcd(*periods)
        # 计算最小公倍数作为总循环周期
        lcm = math.lcm(*periods)
        rows = lcm // self.base_period

        self.program_table = [p[2] for p in programs]
        self.schedule_table = [[0] * len(programs) for _ in range(rows)]

        for i, (name, period, func) in enumerate(programs):
            step = period // self.base_period
            for row in range(0, rows, step):
                self.schedule_table[row][i] = 1

    def tick(self):
        """每个时基脉冲到来时调用"""
        if self.time_counter >= len(self.schedule_table):
            self.time_counter = 0

        row = self.schedule_table[self.time_counter]
        for i, flag in enumerate(row):
            if flag == 1:
                self.program_table[i]()

        self.time_counter += 1