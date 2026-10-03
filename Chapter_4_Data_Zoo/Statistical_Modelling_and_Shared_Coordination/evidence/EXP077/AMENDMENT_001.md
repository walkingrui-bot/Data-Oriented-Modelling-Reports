# EXP077 修订 001：日期宽度解析错误

- 发现于`EXP077-SOURCE-001`之后，看到的内容仅为**无效解析**产生的来源行计数：1,716,480行被固定10字符假设拒绝、每年仅约65日；未训练或查看模型成绩。
- 原稿/代码差异：计划以dd/mm/yyyy表示日/月/年，但代码额外假定必须`len(date)==10`，排除了单数字日/月。官方页面只规定日期的日/月/年语义，没有规定前置零固定宽度。
- 新实现：使用`/`分隔三个整数作day/month/year，`:`分隔三个整数作hour/minute/second，再构造源日历datetime；年月日含义、缺失政策、按目标年分段、+60分钟真配对及所有冻结门**不改**。
- 旧结果资格：首次派生来源矩阵 (source asset outside this public snapshot)和原输出 (source asset outside this public snapshot)保留、标`INVALID_PARSER`，其中失败门不构成数据失败。第二次尝试新run_id与新输出文件，不覆盖首轮。
- 预算：修复需再下载一次≤30MiB原ZIP、流式解析≤10分钟CPU；原始文件依然不落地。无test性能接触。
- 第二次有效运行后更正一个纯元数据字段：有效`SOURCE_MATRIX.json`最初由同一脚本误写`attempt_id=EXP077-SOURCE-001`，与新的`RUN_OUTPUT_002.txt`及工作日志不符；现就地改为`EXP077-SOURCE-002`并同步脚本常量。其所有行数、指标、门值均未改；首轮无效矩阵仍原样保留。
