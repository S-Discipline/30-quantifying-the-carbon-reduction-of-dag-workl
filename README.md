# Reproduction: carbon-aware DAG scheduling at fixed makespan

We tested the headline claims of **[Quantifying the Carbon Reduction of DAG Workloads: A Job Shop Scheduling Perspective](https://www.alphaxiv.org/abs/2512.07799)**. Using the authors' pinned AU-SA 2024 trace and DAG pool, an OR-Tools CP-SAT reimplementation found **20.93% carbon savings at the same optimal makespan** on homogeneous servers (paper: **25%**) and **20.60%** on heterogeneous servers (paper: **18%**). With paper-proportional solver limits and $S=2$, homogeneous savings were **54.52%** (paper: **54%**).

**统一判定：C（部分复现成功），可信度：中。** 实验数字来自本次实例级运行日志，而非论文或 README。方向上，同构/异构 $S=1$ 都显示正碳节省，同构 $S=2$ 的伸缩趋势也一致；数值上，同构和异构 $S=1$ 的相对差异分别为 **16.26%** 和 **14.44%**，超过论文无误差范围时采用的 10% 参考，只有同构 $S=2$ 的 **0.96%** 相对差异满足该参考。异构 $S=2$ 相差 **51.08%**，能耗、服务器数、任务数和地区消融未运行，因此不能称为完整或缩小规模复现成功。

主要替代是每条件 8–24 而非 1,000 个实例、10/30/50 秒而非 60/180/300 秒 CP-SAT 时限、单个生成种子、确定性 trace 日期抽样和等价的开始时间碳成本查表。运行位于用户提供的 Vast.ai SSH 主机别名 `paper2607-rtx3090`；约束求解为 CPU 密集型。

- [Read the illustrated technical report](reports/dag-carbon-reproduction/report.md)
- [Explore the self-contained marimo tutorial](notebooks/dag_carbon_reproduction.py)
- [Inspect the published result CSVs](reports/dag-carbon-reproduction/data/)

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `main` | Reader-facing README, report, figures, data, notebook, and final implementation | Not run as an experiment (publication surface) | Presentation only | None |
| [Headline AU-SA baseline](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/headline-au-sa-reproduction-formal-baseline) | 24 homogeneous instances at $S=1$ | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | 部分支持：方向一致；20.93% vs 25%，相对差异 16.26% | Vast.ai SSH; 4m27s |
| [Stretch and heterogeneity sweep](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/stretch-and-heterogeneity-sweep) | 16 instances; homogeneous/heterogeneous; $S=1,1.5,2$; equal 10s cap | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | 异构 $S=1$ 部分支持；异构 $S=2$ 与利用率机制在本设置下不支持；统一预算伸缩结果证据不足 | Vast.ai SSH; 16m41s successful run |
| [Proportional timeout stretch check](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/proportional-timeout-stretch-check) | Eight homogeneous instances; 10/30/50s limits at $S=1/1.5/2$ | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | 同构 $S=2$ 端点支持：54.52% vs 54%；“近乎翻倍”仅部分支持 | Vast.ai SSH; 12m26s |

The three successful evidence runs used 33m34s total wall-clock time. Monetary cost is unavailable from the captured run evidence.

## Local notebook

```bash
marimo edit notebooks/dag_carbon_reproduction.py
marimo run notebooks/dag_carbon_reproduction.py
```
