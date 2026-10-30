from control.time_table_scheduler import TimeTableScheduler

def test_scheduler():
    sched = TimeTableScheduler()
    log = []
    
    # 定义三个程序：A每2ms执行，B每4ms执行，C每8ms执行
    programs = [
        ("A", 2, lambda: log.append("A")),
        ("B", 4, lambda: log.append("B")),
        ("C", 8, lambda: log.append("C"))
    ]
    
    sched.design_time_table(programs)
    assert sched.base_period == 2
    assert len(sched.schedule_table) == 4 # LCM(2,4,8) / 2 = 4
    
    # 模拟 8ms
    for _ in range(4):
        sched.tick()
        
    # 预期：t=0(A,B,C), t=2(A), t=4(A,B), t=6(A)
    expected = ["A", "B", "C", "A", "A", "B", "A"]
    assert log == expected, f"实际输出: {log}"
    print("时间表调度测试通过 ✅")

if __name__ == "__main__":
    test_scheduler()