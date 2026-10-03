# EXP026 Amendment 001 — M0 验证集先验的来源

记录于 2026-10-02，EXP026-SOURCE-001 下载中，**任何 EXP026 特征/模型成绩未查看，模型尚未拟合**。原 [PLAN.md](PLAN.md) 中「M0 用 train+validation 类别先验」只适用于最终 test；若把 validation 的标签计入 validation 预测，将构成泄漏。修正为：M0 在 validation 只用 train 类别先验；在 test 用 train+validation 类别先验。M1–M3 的 validation 只用 train 拟合/缩放，选定 λ 后 train+validation 重拟合测试。其它样本、特征、指标、门槛、预算均不改。此修订发生在结果观察前，不回写原句。
