class AnalogUserCircuit:
    def __init__(self, line_number):
        self.line_number = line_number
        self.state = 'on_hook'
        self.last_scan_result = 1
        self.current_scan_result = 1

    def scan_line(self):
        return self.current_scan_result

    def set_hardware_state(self, hook_state):
        """模拟物理动作：用户拿起或放下话筒"""
        self.current_scan_result = 0 if hook_state == 'off_hook' else 1

    def detect_hook_change(self):
        event = None
        if self.last_scan_result == 1 and self.current_scan_result == 0:
            event = 'off_hook'
            self.state = 'off_hook'
        elif self.last_scan_result == 0 and self.current_scan_result == 1:
            self.state = 'on_hook'
            event = 'on_hook'

        self.last_scan_result = self.current_scan_result
        return event

    # --- B (Battery) 馈电 & R (Ringing) 振铃 ---
    def feed_current(self, enable=True):
        """B-馈电：向用户线提供 -48V"""
        action = "开启" if enable else "关闭"
        # print(f"    [用户电路 {self.line_number}] {action} -48V 馈电")

    def apply_ringing(self):
        """R-振铃：向被叫发送铃流"""
        self.state = 'ringing'
        print(f"    [用户电路 {self.line_number}] 🔔 启动 25Hz/90V 振铃")
        
    def stop_ringing(self):
        """停止振铃"""
        if self.state == 'ringing':
            self.state = 'off_hook' # 振铃停止通常因为被叫摘机
            print(f"    [用户电路 {self.line_number}] 停止振铃")