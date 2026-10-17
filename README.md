# 交换网络仿真平台

基于 Python 标准库实现的交换网络教学仿真平台，覆盖 PCM30/32 帧结构、T/S 接线器、TST 三级网络、CLOS 无阻塞条件、Lee 阻塞率模型与 DSN 两级自选路由。

## 模块与知识点

| 模块 | 文件 | 对应知识点 |
| :--- | :--- | :--- |
| PCM30/32 帧 | `core/pcm_frame.py` | G.704 基本帧、16 帧复帧、FAS、TS0/TS16 |
| T 接线器 | `units/time_switch.py` | 共享存储器型交换单元、顺序写/控制读、控制写/顺序读 |
| S 接线器 | `units/space_switch.py` | 空间交换、N×N 交叉矩阵、单播约束 |
| TST 网络 | `networks/tst.py` | 三级网络、反相法双向通路 |
| CLOS 条件 | `analysis/clos.py` | 严格无阻塞 m≥2n−1、可重排 m≥n |
| Lee 模型 | `analysis/blocking.py` | 三级网络阻塞概率近似 |
| DSN | `networks/dsn.py` | 两级自选路由、选择/数据/置闲信道字 |

## 运行

```bash
python main.py          # 交互式菜单
python main.py all      # 一次性跑全部演示
python main.py 4        # 单独跑第 4 项（TST）