# EXP080 修订001：原CSV列名内部空格格式

- 修改前已看：`EXP080-SOURCE-001`仅见官方504；`EXP080-SOURCE-002`仅见ZIP成员名、52,416行和九列原表头，未解析日期或任何数值/模型结果。源表头`Zone 2  Power Consumption`、`Zone 3  Power Consumption`使用双空格；代码错误要求与官方页面中的单空格逐字匹配。
- 旧约定与问题：计划冻结**九列语义**、要求保留原表头及审出实际格式；实现只`strip()`首尾空白，额外引入无科学意义的内部空格要求，导致旧派生矩阵 (source asset outside this public snapshot)误判。旧输出`STOP_SOURCE_COLUMNS_MISMATCH`无来源裁决资格。
- 新实现：只对列名使用`" ".join(name.split())`规范化连续空白再匹配同九个列名；原始header仍原样存入有效矩阵。列顺序、数值、时间、缺失、样本/目标及全部来源门不改。
- 重试为`EXP080-SOURCE-003`，原`RUN_OUTPUT_001/002.txt`与旧矩阵保留，第三次新输出不覆盖；网络/CPU同原小预算。无test性能接触。
