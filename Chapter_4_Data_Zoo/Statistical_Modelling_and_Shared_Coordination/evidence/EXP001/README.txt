INTERNAL COORDINATION 001
Living experiment version 0.1 | 1 October 2026

中文说明

本轮把“同一体系下的不同境界”操作化为同一合成体系的七种状态。
七个小模型各自学习三个参数；它们学成的局部函数成为上层共同的学习目标。
上层通过一套共享参数和七个内部状态生成这七个局部模型的参数。

无噪声、按局部参数的统计结构初始化、80 次内部更新的条件下：
直线上层的目标 RMSE 下限为 0.122899；曲线上层配合耦合更新，30/30 次
同时满足七个局部目标的 RMSE <= 0.01。随机初始化的曲线上层为 11/30。
记录的 seed 0 轨迹中，共享弯曲项在第一次内部更新从零开始出现。
延长训练后，普通联合梯度也在统计结构初始化的 10/10 次补充实验中达标。
这轮分别定位了表示容量、初始化与更新方法的作用。

曲线形式是本轮明确提供的候选结构。隐藏状态标签仅供拟合后的审计。
本轮检验的是对已学成局部函数的共同拟合；训练先后顺序是下一轮可测的变量。
完整英文报告位于 report/，原始数据和全部数值结果位于 data/ 与 results/。

EXPERIMENT DESIGN

Seven local models, each with three trainable weights and fixed features 1, x, x^2,
learn 17 observations. Their coefficient vectors come from one quadratic family
at seven equally spaced simulator states. Observation-noise SD is 0 or 0.03.
Each local model receives 500 gradient updates. Its fitted function is then frozen.

The higher layer learns all seven local functions simultaneously. It infers one
internal coordinate per local target and shared weights for a line or a curve.
The curve stores 9 shared weights and 7 states, with 14 effective continuous
variables after fixing two coordinate freedoms. Hidden simulator states and
clean outputs are withheld from this fit. Every update uses all 119 target values.

The main experiment crosses 30 seeds, two noise levels, two initializations,
two model families, and two update rules, for 480 higher-layer fits at 80 updates.
Noiseless observations repeat across seeds; initialization varies. In noisy runs,
observation noise and initialization both vary. A run passes when ALL seven
local target RMSEs are <= 0.01.

The coupled update solves a damped linearized least-squares system with an
analytical Jacobian. The ordinary joint-gradient control uses the same variables,
targets, and starting point. Update counts are not matched wall-clock costs.
Geometry initialization uses the first principal coordinate of learned local
coefficients with seeded perturbations. It already provides a useful organization.

Post-run follow-ups compute the exact best line, audit initialization, and extend
the update budget for the first ten noiseless seeds. These add 40 higher-layer fits.
They are follow-up diagnostics, not additional independent confirmatory datasets.

REPRODUCTION

Tested with Python 3.12.14 on CPU. Exact dependency versions are in requirements.txt.
From the extracted coordination_001 directory, run:

    python -m pip install -r requirements.txt
    python code/experiment.py
    python code/controls.py
    python code/analyze.py
    python code/make_report.py

The commands replace generated data, summaries, figures, and the DOCX report.
They use local numerical computation and require no model download or API key.
Floating-point round-off and elapsed runtime can vary with the numerical platform.
The full report contains methods, results, parameter trajectories, and scope.

FILE GUIDE

protocol.json
    Recorded fixed settings for the main experiment.
code/experiment.py
    Simulator, local gradient training, coordinator, Jacobian checks, main runs.
code/controls.py
    Post-run exact-line, initialization, and extended-budget diagnostics.
code/analyze.py
    Aggregation, Wilson intervals, paired bootstrap, and four scientific figures.
code/make_report.py
    English Word living report with editable native math and result tables.
code/package.py
    Rebuilds manifest.json and the evidence ZIP, then verifies archive hashes.
data/all_experiment_arrays.npz
    Observations, learned target coefficients, final higher-layer weights/states,
    and simulator audit arrays. Simulator-only names include audit_only.
results/run_metrics.csv
    All 480 main fits, including aggregate and worst-source errors and diagnostics.
results/coordination_traces.csv
    Every recorded update for seed 0 in all 16 main conditions.
results/local_parameter_trajectories.npz
    Local training coefficient trajectories for seed 0 at both noise levels.
results/teacher_metrics.csv
    Metrics for all 60 seven-model training configurations.
results/extended_budget_controls.csv
    The 40 longer-budget fits.
results/exact_representation_controls.csv
    Exact rank-one function-space residual floor for every training configuration.
results/initial_state_audit.csv
    Geometry/random initialization metrics, including hidden-state audit.
results/group_summary.csv and results/summary.json
    Complete grouped results and quantitative findings used by the report.
results/runtime_and_checks.json
    Actual main-run runtime, environment, and derivative/normalization checks.
figures/
    Four PNG figures used in the report; Figure 3 locates internal changes.
report/
    Eight-page English Word report.
manifest.json
    SHA256 and byte count for every packaged file except the manifest itself.

EVIDENCE CHECK

The archive was checked for ZIP integrity and every member was compared with its
manifest digest. Rendered report pages were visually inspected before packaging.
Reproducing the experiment may change file bytes while preserving the numerical
findings; the manifest identifies the exact delivered evidence snapshot.

NEXT MEASUREMENT

Hold the seven learned targets fixed, vary when their constraints become available,
and record per-source contributions to the shared-parameter update. This separates
training history from the initialization and representation effects measured here.
