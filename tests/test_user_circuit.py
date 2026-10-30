# tests/test_user_circuit.py
"""Phase 1 验收测试：用户电路与信号音"""
from interfaces.user_circuit import AnalogUserCircuit
from core.signal_tones import SignalTone

def test_hook_detection_flow():
    circuit = AnalogUserCircuit(101)
    
    # 初始状态：挂机
    assert circuit.detect_hook_change() is None
    assert circuit.scan_line() == 1
    
    # 物理动作：用户摘机
    circuit.set_hardware_state('off_hook')
    
    # 控制层扫描：检测到摘机
    event = circuit.detect_hook_change()
    assert event == 'off_hook'
    assert circuit.state == 'off_hook'
    
    # 下一次扫描：状态未变，不应重复触发
    assert circuit.detect_hook_change() is None
    
    # 物理动作：用户挂机
    circuit.set_hardware_state('on_hook')
    
    # 控制层扫描：检测到挂机
    event = circuit.detect_hook_change()
    assert event == 'on_hook'
    assert circuit.state == 'on_hook'

def test_ringing_and_tone():
    # 测试振铃
    circuit = AnalogUserCircuit(102)
    circuit.apply_ringing()
    assert circuit.state == 'ringing'
    circuit.stop_ringing()
    assert circuit.state != 'ringing'

    # 测试信号音
    tone_info = SignalTone.get_tone_frequency(SignalTone.DIAL_TONE)
    assert "450Hz" in tone_info

if __name__ == "__main__":
    test_hook_detection_flow()
    test_ringing_and_tone()
    print("Phase 1 全部测试通过 ✅")