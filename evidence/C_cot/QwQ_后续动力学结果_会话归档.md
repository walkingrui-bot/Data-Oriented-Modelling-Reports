# QwQ 后续动力学结果｜会话归档

本文件记录在初始 `REPORT(20260925-005446).md` 之后、通过连续实验获得但没有形成独立原始代码包的 QwQ-32B-Preview Putnam 结果。数值来自当时保存的实验汇报；因此本文件属于“结果归档”，不是独立复现实验包。公开数据来源为 ChainScope 的 QwQ-32B-Preview Putnam correct-response 数据。

## 1. 大样本状态与运动

- 公开 correct reasoning traces：115 条。
- 其中一次分析使用 99 条足够长的轨迹，100-content-word 非重叠窗口共 958 个状态。
- 绝对 early/middle/late 阶段分类：31.0%，低于 38.8% majority baseline。
- 生成进度回归：R² = -0.30。

定义 `z_t` 为关系几何，`v_t=z_t-z_{t-1}`，`a_t=v_t-v_{t-1}`。

不同窗口下未来运动预测 MSE：

| 窗口 | z | z+v | z+v+a |
|---|---:|---:|---:|
| 80 content words | 0.759 | 0.714 | 0.708 |
| 100 content words | 0.791 | 0.743 | 0.737 |
| 120 content words | 0.830 | 0.796 | 0.775 |
| 100 all words | 0.674 | 0.656 | 0.642 |

纯惯性 `v_{t+1}=v_t` 的 MSE 约 2.945，说明轨迹存在动力学信息，但不表现为简单弹道惯性。

## 2. Diffuse / Concentrated 状态

一次无监督分析中：

- K=2 silhouette = 0.216
- K=3 = 0.135
- K=4 = 0.128
- K=5 = 0.117

两态平均生成进度接近：diffuse 0.553，concentrated 0.563，支持它们是运动状态而非绝对生成阶段。

典型形态：
- diffuse：recurrence/local/bridge/n-gram 较低，long/horizon entropy 较高；
- concentrated：recurrence/local/bridge/n-gram 较高，long/horizon entropy 较低。

原分析的 100-word 条件：speed 3.71→4.30；conditional motion entropy 0.996→0.836。该“集中态低二态转移熵”结论后来在独立重写实现中没有复现，因此只保留为定义/实现敏感现象；“D/C 两态 + concentrated 更快”获得独立方向复现。

## 3. 终态形成与 path matters

以最后两窗平均关系几何为 observed terminal geometry：

- 全局平均终态 baseline MSE：1.760
- 假定当前状态就是终态：2.085
- 当前 z 学终态：1.716
- z+v：1.694

只有约 50.76% 的连续步骤向终态几何靠近；速度与“本步是否更接近终态”的相关约 r=0.08。终态不是沿静态距离单调逼近形成。

## 4. 严格 trace-level 5-fold 留出

| 模型 | 一步预测 MSE | 自由 rollout 后半段 MSE | 终态 MSE |
|---|---:|---:|---:|
| 只看 z_t | 0.889 | 1.254 | 1.008 |
| z_t+v_t+a_t | 0.835 | 1.194 | 0.956 |
| 运动量随机错配 | 0.909 | 1.260 | 1.011 |
| 两态 switching dynamics | 0.875 | 1.195 | 0.938 |
| nonlinear random-feature field | 0.875 | 1.216 | 0.992 |

真实 v/a 的优势在随机错配后消失，支持真实时间顺序提供静态 z 以外的预测信息。switching dynamics 对终态最好，提示 coarse movement regime 对长程形成有额外约束。

自由 rollout 的 D/C 统计：
- state-only：concentrated 占比误差 0.284；运动熵误差 0.453；逐步状态准确率 69.8%。
- z+v+a：0.266；0.408；71.5%。
- switching：占比误差 0.245；运动熵误差 0.404；逐步状态准确率 69.3%。

## 5. 历史状态负结果

48维 recurrent reservoir 曾在表面上改善未来预测；把训练轨迹时间顺序打乱后，优势没有选择性消失，部分结果甚至略好。因此它没有获得“真实历史记忆”资格。后续历史状态必须通过时间顺序破坏门。

## 6. 独立重写复现

使用重新实现的 content-token 几何、90 条较长 trace、100-token 非重叠窗：
- total windows = 2590；[z,v] states = 2500。
- centroid-silhouette：K2=0.346，K3=0.259，K4=0.245，K5=0.241。
- diffuse speed = 0.454；concentrated speed = 0.498。
- 简单二态 conditional entropy：D=0.9988 bits，C=0.9994 bits。

因此独立实现支持 D/C 两态及 concentrated 更快；不支持把“C 必然降低二态 transition entropy”当作当前稳健机制结论。
