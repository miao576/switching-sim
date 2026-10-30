from control.group_processing import GroupProcessor

def test_group_scan():
    gp = GroupProcessor(16)
    last = 0b1111111111111111  # 全挂机
    current = 0b1111111111111100 # 0号和1号摘机
    
    off, on = gp.scan_group(current, last)
    assert off == 0b0000000000000011  # 检测到0、1号摘机
    assert on == 0
    print("群处理测试通过 ✅")

if __name__ == "__main__":
    test_group_scan()