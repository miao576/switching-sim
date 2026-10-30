# tests/test_tst.py
"""验收测试：TST 动态并发、选路与阻塞"""
from networks.tst import TSTNetwork


def test_dynamic_path_and_concurrency():
    net = TSTNetwork(4, 64)
    
    # 1. 用户 A (line 0 TS2) 打给 用户 B (line 2 TS51)
    success1, ts1 = net.find_path_and_connect(in_line=0, in_ts=2, out_line=2, out_ts=51)
    assert success1 == True, "第一通电话建立失败"
    
    # 2. 用户 C (line 1 TS5) 打给 用户 D (line 3 TS10)，并发进行
    success2, ts2 = net.find_path_and_connect(in_line=1, in_ts=5, out_line=3, out_ts=10)
    assert success2 == True, "第二通电话并发建立失败"
    
    # 3. 数据双向通行测试
    ins = [[None]*64 for _ in range(4)]
    ins[0][2] = "A2B"
    ins[1][5] = "C2D"
    outs = net.switch_all(ins)
    
    assert outs[2][51] == "A2B"
    assert outs[3][10] == "C2D"
    
    # 4. 挂机释放
    released = net.disconnect(0, 2, 2, 51)
    assert released == True, "连接释放失败"
    
    # 5. 资源复用测试：释放后，新呼叫应该可以重新占用刚刚释放的内部时隙
    success3, ts3 = net.find_path_and_connect(in_line=0, in_ts=8, out_line=2, out_ts=20)
    assert success3 == True, "释放后重新建立连接失败"
    assert ts3 == ts1, "内部时隙没有被成功回收复用"

def test_blocking_when_capacity_exhausted():
    # 用一个极小的网络（只有2个内部时隙）来测试阻塞
    net = TSTNetwork(n_in_lines=2, n_slots=2)
    
    # 占满所有的内部时隙
    s1, _ = net.find_path_and_connect(0, 0, 1, 0)
    s2, _ = net.find_path_and_connect(0, 1, 1, 1)
    assert s1 and s2
    
    # 此时再来第三个呼叫，必然阻塞（无内部时隙可用）
    s3, _ = net.find_path_and_connect(0, 0, 1, 0)
    assert s3 == False, "网络已满，应当发生阻塞"
    print("阻塞控制验证成功（无可用内部时隙）")

if __name__ == "__main__":
    test_dynamic_path_and_concurrency()
    test_blocking_when_capacity_exhausted()
    print("TST 完整并发与阻塞测试通过 ✅")