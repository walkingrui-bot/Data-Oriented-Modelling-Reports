# RTG 单步超长运行稳定性：构造性功能测试

日期：2026-09-25

## 问题

构造一个没有内部多步规划的自回归系统：每次只生成一个下一状态；该输出立即成为下一步输入，并且系统会把自己刚刚产生的 transition 重新用于改写 continuation geometry。测试 RTG 约束能否在超长运行中同时满足：

1. 不离开已声明的关系允许空间；
2. 不因自条件反馈逐渐锁死成单一路径；
3. continuation geometry 遭受外部扰动后能回到稳定运动带。

“不会胡说八道”在本实验中被操作化为第 1 条；“仍能正常持续运行”由第 2、3 条补充，避免把硬 mask 的零违规误称为完整稳定性。

## 构造

世界含 32 个关系状态，每个状态有 5 个允许后继。主生成器初始偏向允许边，但其自条件 rewrite phenotype 会持续改写后续 geometry，因此自己的输出会逐步改变自己的参考系。

三个条件：

- **free-self-conditioned**：动态 geometry 长记忆、无稳定外部支撑约束、无写入预算。
- **support-only**：禁止离开允许边，但仍允许无界、长记忆的自条件 geometry write。
- **RTG-constrained**：保持允许支撑；每次写入有界；动态 geometry 持续向低速/冻结参考 geometry 回归；具体允许路径仍由主生成器自行选择。

在运行 1/4、1/2、3/4 处对整个内部动态 geometry 注入大扰动。

## 10 seeds × 100,000 steps

| condition | violation all | violation late | H early | H late | late state coverage | max state share |
|---|---:|---:|---:|---:|---:|---:|
| free self-conditioned | 31.39% | 32.87% | 0.406 | 0.065 | 43.1% | 43.4% |
| support only | 0% | 0% | 0.477 | 0.158 | 49.7% | 28.1% |
| RTG constrained | **0%** | **0%** | **1.582** | **1.582** | **100%** | **4.10%** |

每个状态有 5 个允许后继，因此允许集最大熵为 ln(5)=1.609 nats。RTG 在 10 万步末端仍为 1.582，接近最大值；没有塌成单一路径。

## 1,000,000-step representative run

| condition | violation | H early | H late | late coverage | max state share |
|---|---:|---:|---:|---:|---:|
| free self-conditioned | 46.06% | 0.153 | 0.118 | 100%* | 46.24% |
| support only | 0% | 0.0355 | **0.000015** | **12.5%** | 25.0% |
| RTG constrained | **0%** | **1.577** | **1.577** | **100%** | **3.74%** |

\* free 条件 late coverage 为 100% 并不代表健康：最大单状态占比 46.24%，且 46.47% 的末段 transition 已越界。

support-only 的结果尤其重要：它证明“禁止非法输出”本身不能维持健康的长期动力学。它在 100 万步时局部 continuation entropy 已接近 0，系统实质上陷入小循环。

RTG 同时维持零越界与非退化多路径运动。

## 扰动恢复

RTG 在三次内部 geometry 大扰动前的平均允许集 entropy 为 1.5771；扰动后前 1000 步为 1.5666；4,000–5,000 步窗口恢复为 1.5777。

因此在这个构造世界中，RTG 不是只靠初始化保持稳定；参考 geometry + 有界写入能把被撞歪的动态场拉回原允许运动带。

## 当前结论

该实验建立一个构造性存在结果：

> 一个每次只做单步生成、且输出持续回灌自身的自条件系统，可以通过 RTG-style constraint geometry、bounded write 和 reference relaxation，在 100 万步运行中保持零关系越界、保留多路径自由度，并在内部 geometry 受扰后恢复。

这证明 RTG 是实现“单步超长自主运行不发生参考系漂移/退化”的一个充分机制实例。

它不证明真实 LLM 直接采用该实现，也不证明 RTG 是唯一方法。下一阶段需要把同一结构接到真实小型 LM，使用可验证任务约束而非人工符号图，观察长文本自主运行中的约束违例、重复锁死、事实漂移和恢复。
