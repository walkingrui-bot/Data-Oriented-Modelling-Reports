# EXP024 近年当次 Label 来源门判定

冻结依据 [PLAN.md](PLAN.md)、[SAMPLE_FREEZE.md](SAMPLE_FREEZE.md)。样本为 ORIG NDA15/BLA5、efficacy SUPPL NDA15/BLA5，共 40 个不同 application，2010–2024 已批准 action。四层均 100% 有同-key FDA `Label` 元数据 URL；40/40 URL 可下载 PDF，合计首次读取 46,300,976 bytes。**URL 和 PDF 可达不等于正文类别及本门通过。**

定向人工核了足以裁决冻结门的两个 ORIG NDA 文件：

| 样本 | 官方 PDF 内容 | 本门 I&U 判定 |
| --- | --- | --- |
| `ORIG_NDA-04`，NDA 205434 | [2014 FLONASE Allergy Relief 原件](https://www.accessdata.fda.gov/drugsatfda_docs/label/2014/205434Orig1s000lbl.pdf) 是 OTC 外包装及消费者问答资料；可视首页和全文可检索页未见处方标签完整 `INDICATIONS AND USAGE`。 | `FAIL_REQUIRED_PI_IU` |
| `ORIG_NDA-06`，NDA 205352 | [2014 Aleve PM corrected label 原件](https://www.accessdata.fda.gov/drugsatfda_docs/label/2014/205352Orig1s000lbl_corrected.pdf) 七页视觉全核为 OTC 纸盒/Drug Facts 图版，不含处方标签完整 I&U；metadata document date 比 action 日晚 11 天，也不能倒用。 | `FAIL_REQUIRED_PI_IU` |

ORIG NDA 子层冻结门为 **≥14/15** 可读的同-key、完整处方 I&U。两条已确定不符合，剩余十三条即使全符合，上限也仅 **13/15**，故 `STOP_DOCUMENT_TYPE_GATE`。ORIG 总层的理论上限可为 18/20，不会拯救 NDA 子层门。其余 38 份保留 `DOCUMENT_AUDIT.csv` 原始 HTTP/解析结果，`DOCUMENT_ADJUDICATION.csv` 明确标 `NOT_ADJUDICATED_AFTER_FROZEN_GATE_FAILURE`，不把机器找到的标题自动称人工通过，也不补抽、排除 OTC 后重算旧分母。

这个停止说明该近年 NDA cohort 混入了官方 `Label` 类型但不同文书语义的真实产品，先前仅凭 metadata 不能形成统一处方 I&U 门；**不证明所有 FDA 当次标签不可用，也未检验 efficacy supplement 的新增适应症**。没有训练模型、形成 indication event 或建立历史 first-public。EXP022 的 regulator event layer 和 EXP023 旧停止保持独立。
