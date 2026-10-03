# EXP086 — 14路气敏与真实腔室CO浓度的按日原件结构门

研究ID `STAT-PSYMOE-EXP086-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_SENSOR_CONCENTRATION_SOURCE_SCHEMA_AUDIT`；父=[EXP085](../EXP085/CLOSEOUT.md)。新科学问题：官方[UCI487](https://archive.ics.uci.edu/dataset/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation)原件是否真的提供13个可按日期分开的独立实验日、同期14路气敏与连续CO施加浓度记录，足以在后续新ID研究“连续校准/概率质量”而非复用EXP085已看试验留出？本ID只做来源结构及缺失审计，**0模型、0性能**。官方描述为13工作日/17自然日、每天100个15分钟施加设定（10浓度×10重复）、14路传感器与温湿度/加热电压，约410万采样行，CC BY 4.0；CO浓度由流量控制器生成并有相对不确定度，不冒充独立化学分析仪逐秒真值。

## 旧结果与信息增益

EXP085八路模型在同风洞新试验的logloss改善保持，但留出平衡准确率没有改善；该冻结整体门失败。继续看同24次test或调阈值不能产生新的确认。UCI487有不同的CO连续目标、14路传感器、按实验日文件组织和明确许可，若原件可复核，能回答“当前框架是否适合校准类真实输出”的来源前提；若按日或参考数值不可用，就停止而不建模。它与EXP085不同装置/任务，不能称直接外部复现。

## 冻结源门和预算

仅内存读取官方ZIP `https://archive.ics.uci.edu/static/public/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation.zip`及其内原文件；不保存ZIP/txt副本。审包装成员、13个按文件名`yyyymmdd_HHMMSS`可解析且不同日期的原实验文件；各文件须能解为20数值列（时间、CO、湿度、温度、流量、加热电压、14传感器）。原件数值以流式处理：全部非空数据行有效比例≥99%、每文件有效行≥280,000、合计≥4,000,000，时间单调不回退且跨度≥24小时；每文件CO浓度至少5个有限不同水平且取值落在[0,20]ppm、14路各有限比例≥99%，温湿度/流量/电压与CO同时有限≥99%。不把缺失设零；原件自带文本头可跳过但须记录。正式实验单元/15分钟段能否重建是**下一个ID的问题**，本ID不据行数声称样本支持，也不评价任何模型。若源包装与官方页面命名不同，可在保留原失败后修正纯路径解析，不调整上述数值门。

全门通过为`DATED_REAL_CO_SENSOR_SOURCE_READY_FOR_EPISODE_AUDIT`，否则写触发门及未知并停止；不能因为下载成功或文件计数就报告来源通过。网络≤210MiB、内存≤850MiB、CPU≤8分钟。预登记`EXP086-SOURCE-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python audit_co_source.py`；原stdout/stderr`RUN_OUTPUT_001.txt`、派生`SOURCE_MATRIX.json`、门/报告/关账。局部仅核本ID日数、计数、门和0模型；不运行全仓测试、哈希或其它实验。
