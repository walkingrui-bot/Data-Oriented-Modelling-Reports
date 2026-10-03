# EXP047 真实多站时序来源门

UCI [北京多站点官方原件](https://archive.ics.uci.edu/dataset/501/beijing%2Bmulti%2Bsite%2Bair%2Bquality%2Bdata)仅在内存读取一次。按原件 CSV 成员 basename 与 `station` 列精确核对，12/12独立站一致；每站35,064个合法唯一小时、0重复、起止 2013-03-01 00:00 至2017-02-28 23:00，12站共同原始小时网格35,064。每站PM2.5非负有限小时34,111–34,682，`TEMP/PRES/WSPM`三者同时有限小时35,009–35,045。逐站派生表 (source asset outside this public snapshot)与总门 (source asset outside this public snapshot)留档。

原门≥10站、各≥30,000唯一小时/25,000 PM2.5/25,000气象、共同≥20,000小时，全部通过：**`REAL_MULTISITE_SOURCE_READY`**。原始缺失仍是缺失。本站时序资格不等于24小时预测模型有效，也不证明不同站点残差有可共享信息。EXP046的工程失败保持原样；本次才是有效数值裁定。
