# main.py —— 综合仿真平台最终版
import sys


def demo_pcm():
    from core.pcm_frame import make_multiframe, verify_fas, VOICE_TS
    mf = make_multiframe({2: "10101010", 31: "01010101"})
    print(f"  复帧帧数: {len(mf)}")
    print(f"  话路时隙数: {len(VOICE_TS)}")
    print(f"  FAS 校验: {verify_fas(mf)}")
    print(f"  偶帧 TS0: {mf[0].get_slot(0)}")
    print(f"  奇帧 TS0: {mf[1].get_slot(0)}")
    print(f"  F0 TS16:  {mf[0].get_slot(16)}")


def demo_time_switch():
    from units.time_switch import TimeSwitch
    for mode in ("seq_w_ctrl_r", "ctrl_w_seq_r"):
        ts = TimeSwitch(32, mode)
        ts.connect(2, 15)
        ts.connect(12, 27)
        ts.connect(27, 12)
        ins = [None] * 32
        ins[2], ins[12], ins[27] = "A", "B->A", "A->B"
        outs = ts.switch(ins)
        print(f"  [{mode}] TS2->TS15={outs[15]}, "
              f"TS12->TS27={outs[27]}, TS27->TS12={outs[12]}")


def demo_space_switch():
    from units.space_switch import SpaceSwitch
    sw = SpaceSwitch(n_lines=8, n_slots=32)
    sw.connect(in_line=0, out_line=3, ts=5)
    sw.connect(in_line=1, out_line=5, ts=5)
    sw.connect(in_line=0, out_line=4, ts=6)
    
    print(f"  时隙5的连接对: {sw.connected_pairs(ts=5)}")
    print(f"  ts=5, route(0): {sw.route(in_line=0, ts=5, payload='voice')}")
    print(f"  ts=5, route(1): {sw.route(in_line=1, ts=5, payload='data')}")
    print(f"  ts=6, route(0): {sw.route(in_line=0, ts=6, payload='ctrl')}")


def demo_tst():
    from networks.tst import TSTNetwork
    net = TSTNetwork(4, 64)
    success, fwd, rev = net.find_path_and_connect_bidirectional(0, 2, 2, 51)
    
    if success:
        print(f"  建立成功! 正向内部时隙={fwd}, 反向内部时隙={rev}")
        ins = [[None] * 64 for _ in range(4)]
        ins[0][2] = "A->B"
        ins[2][51] = "B->A"
        outs = net.switch_all(ins)
        print(f"  PCM0-TS2 -> PCM2-TS51 = {outs[2][51]}")
        print(f"  PCM2-TS51 -> PCM0-TS2 = {outs[0][2]}")
    else:
        print("  建立失败（发生阻塞）")


def demo_clos():
    from analysis.clos import check_clos
    for m, n, r in [(7, 4, 4), (4, 4, 4), (3, 4, 4)]:
        info = check_clos(m, n, r)
        print(f"  {info['name']}: type={info['type']}, "
              f"crosspoints={info['total_crosspoints']}")


def demo_blocking():
    from analysis.blocking import sweep_load
    for n, m in [(8, 8), (8, 16)]:
        print(f"  n={n}, m={m}:")
        for ld, pb in sweep_load(n, m):
            print(f"    load={ld:.1f}  P_block={pb:.6f}")


def demo_dsn():
    from networks.dsn import DSNSimple
    dsn = DSNSimple(8, 32)
    dsn.establish(0, 10, (3, 6), 6, 20)
    dsn.establish(1, 11, (4, 7), 7, 21)
    o = dsn.send(0, 10, "voice_a")
    print(f"  send(0,10) -> out_port={o[0]}, out_slot={o[1]}, type={o[2]['type']}")
    o = dsn.send(2, 12, "voice_c")
    print(f"  send(2,12) -> type={o[2]['type']} (未建路由)")


def demo_user_circuit():
    from interfaces.user_circuit import AnalogUserCircuit
    from core.signal_tones import SignalTone
    
    print("  --- 模拟用户电路 BORSCHT 功能 ---")
    user = AnalogUserCircuit(101)
    print(f"  用户 101 初始状态: {user.state}")
    
    user.set_hardware_state('off_hook')
    event = user.detect_hook_change()
    print(f"  模拟摘机动作 -> 触发事件: {event}, 内部状态更新为: {user.state}")
    
    user.apply_ringing()
    SignalTone.play(SignalTone.DIAL_TONE)


def demo_call_state_machine():
    from interfaces.user_circuit import AnalogUserCircuit
    from networks.tst import TSTNetwork
    from control.call_state_machine import CallStateMachine
    
    print("  --- 模拟一次完整本局呼叫全流程 ---")
    caller = AnalogUserCircuit(101)
    callee = AnalogUserCircuit(102)
    network = TSTNetwork(n_in_lines=2, n_slots=32) 
    
    # 号码 101 接在物理端口 0 (TS2)；号码 102 接在物理端口 1 (TS10)
    fsm = CallStateMachine(caller, callee, network, 
                           caller_line=0, caller_ts=2, 
                           callee_line=1, callee_ts=10)
    
    # 1. 摘机
    print("\n  [动作] 主叫 101 摘机")
    caller.set_hardware_state('off_hook')
    fsm.handle_event(caller.detect_hook_change())
    
    # 2. 拨号 "102"
    print("\n  [动作] 主叫拨号 1-0-2")
    fsm.handle_event('digit_1')
    fsm.handle_event('digit_0')
    fsm.handle_event('digit_2')
    
    # 3. 被叫应答
    print("\n  [动作] 被叫 102 摘机应答")
    callee.set_hardware_state('off_hook')
    fsm.handle_event('answer')
    
    # 4. 主叫挂机拆线
    print("\n  [动作] 主叫 101 挂机")
    caller.set_hardware_state('on_hook')
    fsm.handle_event(caller.detect_hook_change())
    print("-" * 40)


DEMOS = [
    ("PCM30/32 帧结构", demo_pcm),
    ("T 接线器 (两种模式)", demo_time_switch),
    ("S 接线器 (支持时隙)", demo_space_switch),
    ("TST 三级网络 (动态寻路/反相法)", demo_tst),
    ("CLOS 无阻塞条件", demo_clos),
    ("Lee 阻塞率分析", demo_blocking),
    ("DSN 两级自选路由", demo_dsn),
    ("用户电路状态与信号音", demo_user_circuit),
    ("完整呼叫全流程 (状态机)", demo_call_state_machine),
]


def run_all():
    for i, (name, fn) in enumerate(DEMOS, 1):
        print(f"\n[{i}/{len(DEMOS)}] {name}")
        print("-" * 40)
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {e}")


def menu():
    while True:
        print("\n===== 综合交换网络仿真平台 =====")
        for i, (name, _) in enumerate(DEMOS, 1):
            print(f"  {i}. {name}")
        print("  0. 全部运行")
        print("  q. 退出")
        cmd = input("请选择: ").strip().lower()
        if cmd == "q":
            break
        elif cmd == "0":
            run_all()
        elif cmd.isdigit() and 1 <= int(cmd) <= len(DEMOS):
            name, fn = DEMOS[int(cmd) - 1]
            print(f"\n>>> {name}")
            print("-" * 40)
            fn()
        else:
            print("无效输入")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "all":
            run_all()
        elif arg.isdigit() and 1 <= int(arg) <= len(DEMOS):
            DEMOS[int(arg) - 1][1]()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python main.py [all|1..9|无参进菜单]")
            sys.exit(1)
    else:
        menu()