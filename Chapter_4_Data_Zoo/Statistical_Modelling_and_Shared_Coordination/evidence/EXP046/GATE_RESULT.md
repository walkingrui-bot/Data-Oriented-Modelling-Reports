# EXP046 来源与数值门

[UCI官方页面](https://archive.ics.uci.edu/dataset/501/beijing%2Bmulti%2Bsite%2Bair%2Bquality%2Bdata)明确CC BY4.0、12站真实空气/气象观测、小时范围及 NA 缺失，来源门通过。原始数值尝试 (source asset outside this public snapshot)确实在一次8,192,212字节原件响应中读到12 CSV/420,768行，但本站名解析有[实现错误](AMENDMENT_001.md)：把ZIP父目录误当站名，导致原派生0合格站的 `STOP_NUMERIC_SOURCE_SUPPORT` **无效**。冻结的≥10站和共同小时交集门未可靠裁定，不称来源失败或通过；实际行/缺失诊断只作已看证据保留。没有训练。
