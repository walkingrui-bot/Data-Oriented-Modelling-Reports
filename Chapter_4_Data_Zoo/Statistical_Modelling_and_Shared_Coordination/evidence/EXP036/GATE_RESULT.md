# EXP036 MyGait 来源门

研究 ID `STAT-PSYMOE-EXP036-20261002-001`；2026-10-02。事前 [计划](PLAN.md) 的两级门先要明确许可，后以 ZIP 中央目录证明 `10mSlow` 中 PD/健康各≥30个不同人、每人左右足文件可辨且各组≥80%配对。不读取原始CSV内容来替代已冻结的**文件路径门**。

| 门 | 实际 | 判定 |
| --- | --- | --- |
| Zenodo 许可 | 官方 [API](https://zenodo.org/api/records/15672744) `license.id=cc-by-4.0`，单一 ZIP 497,749,531字节 | 通过 |
| ZIP 中央目录 | 206 Range 仅读尾部4 MiB，1517成员/1482文件，未下载/保存 ZIP | 有效读取 |
| `10mSlow` 参与者人数 | 初版路径解析漏10名带连字符的PD，已保留失败输出；更正后 **PD44、健康45**，各人一个 CSV | 人数通过 |
| 左右足文件配对 | 路径为每人一个CSV，没有侧别字段；官方描述称内部有 `foot` 列，但文件名不能证明该列在每人均含左右 | `STOP_FILE_INTERSECTION_UNKNOWN` |

本轮未读取 CSV 数值，不能说两足原始流已配对或有效，也不能把压力列当可信力。停止属于**存储语义可识别性**，不代表实际缺一足。新问题须另立 ID，在明确许可下核一个 CSV 内的两足记录；本实验的人数/路径门不改写成通过。详细 元数据 (source asset outside this public snapshot)、路径诊断 (source asset outside this public snapshot)、[修订](AMENDMENT_001.md)。
