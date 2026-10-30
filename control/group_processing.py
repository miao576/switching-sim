# control/group_processing.py
class GroupProcessor:
    def __init__(self, word_size=16):
        self.word_size = word_size
        self.mask = (1 << word_size) - 1  # 0xFFFF

    def scan_group(self, current_status: int, last_status: int):
        """
        群处理摘挂机检测（对应 PPT 图3.50）
        current_status / last_status: 16位整数，每位对应一个用户状态（0=摘机，1=挂机）
        返回: (摘机掩码, 挂机掩码)
        """
        # 摘机：上次=1 且 本次=0
        hook_off_mask = last_status & (~current_status & self.mask)
        # 挂机：上次=0 且 本次=1
        hook_on_mask = (~last_status & self.mask) & current_status
        return hook_off_mask, hook_on_mask