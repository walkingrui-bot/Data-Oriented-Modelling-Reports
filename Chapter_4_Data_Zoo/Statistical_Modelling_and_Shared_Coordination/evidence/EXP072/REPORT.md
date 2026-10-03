# EXP072 报告：1629重复时间键是同值重复行

对 [WISDM官方原件](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)只读受试者1629的手机acc/gyro两文件，预定A/D/E六组与先前来源行数、21,424折叠量、每组一次倒序全一致。每个重复时间键恰有两行，两行的三轴**数值完全相同**，冲突键0、最大轴差0。[门](GATE_RESULT.md) · 六组证据摘要 (source asset outside this public snapshot)。

因此EXP071按预定规则对同时间戳取均值不会改变1629的这些数值；此前JOINT开发门失败仍有效，不需也不允许据此删人重训。这个裁决仅排除了“重复键包含冲突三轴值”这一解释；不能推出同一人的录制协议之外没有其他问题，也不是模型容量诊断。实际运行只涉及原件两文件、六组审计和局部派生7/7；无新训练、测试评分或全仓检查。[关账](CLOSEOUT.md)。
