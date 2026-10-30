# control/call_state_machine.py
from core.signal_tones import SignalTone
from interfaces.user_circuit import AnalogUserCircuit

class CallStateMachine:
    # 注意：新增了 caller_line 和 callee_line 参数代表物理端口，和电话号码区分开
    def __init__(self, caller_circuit: AnalogUserCircuit, callee_circuit: AnalogUserCircuit, 
                 tst_network, caller_line, caller_ts, callee_line, callee_ts):
        self.caller = caller_circuit
        self.callee = callee_circuit
        self.network = tst_network
        
        self.caller_line = caller_line  # 主叫物理端口（如 0 号线）
        self.caller_ts = caller_ts
        self.callee_line = callee_line  # 被叫物理端口（如 1 号线）
        self.callee_ts = callee_ts
        
        self.state = 'IDLE' 
        self.digits = []
        self.internal_ts = None

    def handle_event(self, event):
        if self.state == 'IDLE' and event == 'off_hook':
            print(f"  [状态机] 主叫 {self.caller.line_number} 摘机，进入收号状态")
            self.state = 'DIALING'
            SignalTone.play(SignalTone.DIAL_TONE)
            
        elif self.state == 'DIALING' and event.startswith('digit_'):
            digit = event.split('_')[1]
            self.digits.append(digit)
            print(f"  [状态机] 收到号码: {digit} (当前号码: {''.join(self.digits)})")
            
            if len(self.digits) == 3:
                self._on_dialing_complete()

        elif self.state == 'RINGING' and event == 'answer':
            print(f"  [状态机] 被叫 {self.callee.line_number} 摘机应答")
            self.callee.stop_ringing()
            
            # 这里使用物理线号 (0 和 1) 进行路由分配，不再使用电话号码
            success, fwd_ts, rev_ts = self.network.find_path_and_connect_bidirectional(
                self.caller_line, self.caller_ts,
                self.callee_line, self.callee_ts
            )
            if success:
                self.state = 'TALKING'
                self.internal_ts = (fwd_ts, rev_ts)
                print(f"  [状态机] 🎉 双方进入通话状态 (内部时隙: {fwd_ts}, {rev_ts})")
            else:
                print("  [状态机] ❌ 发生阻塞，无法建立连接！")
                SignalTone.play(SignalTone.BUSY_TONE)
                self._release_resources()

        elif self.state in ['TALKING', 'RINGING'] and event == 'on_hook':
            print(f"  [状态机] 收到挂机信号，拆线")
            self._release_resources()

    def _on_dialing_complete(self):
        called_number = int("".join(self.digits))
        print(f"  [状态机] 号码分析完成，呼叫目标: {called_number}")
        
        if called_number == self.callee.line_number:
            if self.callee.state == 'on_hook':
                self.state = 'RINGING'
                print(f"  [状态机] 被叫空闲，开始振铃")
                self.callee.apply_ringing()
                SignalTone.play(SignalTone.RING_BACK_TONE)
            else:
                print(f"  [状态机] 被叫 {called_number} 忙，播放忙音")
                SignalTone.play(SignalTone.BUSY_TONE)
                self.state = 'IDLE'
        else:
            print(f"  [状态机] 找不到号码 {called_number}")
            SignalTone.play(SignalTone.BUSY_TONE)
            self.state = 'IDLE'

    def _release_resources(self):
        """释放底层网络资源，状态归零"""
        if self.state == 'TALKING':
            # 1. 拆除正向路由 (主叫 -> 被叫)
            self.network.disconnect(
                self.caller_line, self.caller_ts,
                self.callee_line, self.callee_ts
            )
            # 2. 拆除反向路由 (被叫 -> 主叫)
            self.network.disconnect(
                self.callee_line, self.callee_ts,
                self.caller_line, self.caller_ts
            )
            print("  [状态机] 已释放双向 TST 网络资源")
        
        self.state = 'IDLE'
        self.digits = []
        self.internal_ts = None