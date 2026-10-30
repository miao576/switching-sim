from control.fsm_implementation import FSMArrayImpl, FSMMultiTableImpl

def test_fsm():
    log = []
    def action_1(): log.append("Action1")
    def action_2(): log.append("Action2")
    
    # 测试二维数组
    fsm = FSMArrayImpl(["idle", "busy"], ["ev1", "ev2"])
    fsm.register_transition("idle", "ev1", "busy", action_1)
    fsm.register_transition("busy", "ev2", "idle", action_2)
    
    s = fsm.handle_event("idle", "ev1")
    assert s == "busy" and log[-1] == "Action1"
    
    s = fsm.handle_event("busy", "ev2")
    assert s == "idle" and log[-1] == "Action2"
    
    # 测试多级表
    fsm2 = FSMMultiTableImpl()
    fsm2.register("idle", "ev1", "busy", action_1)
    assert fsm2.handle_event("idle", "ev1") == "busy"
    
    print("FSM 测试通过 ✅")

if __name__ == "__main__":
    test_fsm()