# tests/test_call_state_machine.py
"""Phase 3 验收测试：本局呼叫全流程（状态机）"""
from interfaces.user_circuit import AnalogUserCircuit
from networks.tst import TSTNetwork
from control.call_state_machine import CallStateMachine

def test_full_local_call():
    caller = AnalogUserCircuit(101) # 号码 101
    callee = AnalogUserCircuit(102) # 号码 102
    network = TSTNetwork(n_in_lines=2, n_slots=32)
    
    # 明确传入：号码 101 对应物理线 0，号码 102 对应物理线 1
    fsm = CallStateMachine(caller, callee, network, 
                           caller_line=0, caller_ts=2, 
                           callee_line=1, callee_ts=10)
    
    # --- 动作1：主叫摘机 ---
    caller.set_hardware_state('off_hook')
    fsm.handle_event(caller.detect_hook_change())
    assert fsm.state == 'DIALING'
    
    # --- 动作2：主叫拨号 (102) ---
    fsm.handle_event('digit_1')
    fsm.handle_event('digit_0')
    fsm.handle_event('digit_2')
    assert fsm.state == 'RINGING'
    assert callee.state == 'ringing'
    
    # --- 动作3：被叫摘机应答 ---
    callee.set_hardware_state('off_hook')
    fsm.handle_event('answer')
    assert fsm.state == 'TALKING'
    assert len(network._routes) == 2 
    
    # --- 动作4：主叫挂机 ---
    caller.set_hardware_state('on_hook')
    fsm.handle_event(caller.detect_hook_change())
    assert fsm.state == 'IDLE'
    assert len(network._routes) == 0 

if __name__ == "__main__":
    test_full_local_call()
    print("\nPhase 3 呼叫状态机全流程测试通过 ✅")