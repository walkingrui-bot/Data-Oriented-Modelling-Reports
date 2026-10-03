# EXP063 评分前运行环境明确

2026-10-02。原计划命令写 `python3 score_frozen_n1.py`；工作区系统 `python3` 不含 NumPy，EXP060 原 N1 特征计算使用 NumPy 的线性百分位算法。为逐项复现原特征定义，实际命令固定为 `/Users/rui/.cache/stat_psymoe_exp017_env/bin/python score_frozen_n1.py`；该既有本地环境具备 NumPy 2.5.3、pandas 3.0.6。此补充在任何伦敦模型误差计算前，只明确实现环境，不改样本、参数、预测或门。模型状态仍指向原件，不复制。
