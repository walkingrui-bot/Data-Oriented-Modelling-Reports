# EXP084 实现更正 001（2026-10-02 BST）

- 原冻结计划的时间门为“时刻单调”，意指允许同一记录时间相等、禁止回退；没有要求严格递增。
- `EXP084-SOURCE-001` 脚本错误使用`stamp <= last`，把所有180试验标为非单调；原派生矩阵 (source asset outside this public snapshot)及原输出 (source asset outside this public snapshot)保留，不能当有效来源失败。
- 本次实现改为`stamp < last`才判回退，同时记录相等与回退步数。数值支持门、标签、样本、预算及科学问题不改；新尝试`EXP084-SOURCE-002`用同一原件重做来源审计。未看任何模型/分类效果，0拟合。
