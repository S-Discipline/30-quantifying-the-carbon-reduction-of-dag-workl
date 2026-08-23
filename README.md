# Reproduction: carbon-aware DAG scheduling at fixed makespan

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/blob/main/notebooks/dag_carbon_reproduction.py)

We tested the headline claims of **[Quantifying the Carbon Reduction of DAG Workloads: A Job Shop Scheduling Perspective](https://www.alphaxiv.org/abs/2512.07799)**. Using the authors' pinned AU-SA 2024 trace and DAG pool, an OR-Tools CP-SAT reimplementation found **20.93% carbon savings at the same optimal makespan** on homogeneous servers (paper: **25%**) and **20.60%** on heterogeneous servers (paper: **18%**). With paper-proportional solver limits and $S=2$, homogeneous savings were **54.52%** (paper: **54%**).

**Assessment: aligned at downscaled scale.** The $S=1$ differences were −4.07 and +2.60 percentage points; the $S=2$ difference was +0.52 points. The main substitutions were 8–24 rather than 1,000 instances per condition, 10/30/50-second rather than 60/180/300-second CP-SAT limits, seeded random trace dates, and an equivalent start-time carbon lookup. Runs executed on the user-provided Vast.ai SSH host alias `paper2607-rtx3090`; constraint solving was CPU-bound.

- [Read the illustrated technical report](reports/dag-carbon-reproduction/report.md)
- [Explore the self-contained marimo tutorial](notebooks/dag_carbon_reproduction.py)
- [Inspect the published result CSVs](reports/dag-carbon-reproduction/data/)

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `main` | Public README, report, figures, data, notebook, and final implementation | Not run as an experiment (publication surface) | Presentation only | None |
| [Headline AU-SA baseline](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/headline-au-sa-reproduction-formal-baseline) | 24 homogeneous instances at $S=1$ | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | Aligned: 20.93% vs 25% | Vast.ai SSH; 4m27s |
| [Stretch and heterogeneity sweep](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/stretch-and-heterogeneity-sweep) | 16 instances; homogeneous/heterogeneous; $S=1,1.5,2$; equal 10s cap | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | $S=1$ aligned; equal-budget $S=2$ inconclusive. First attempt exposed and motivated the horizon repair; final run completed. | Vast.ai SSH; 16m41s successful run |
| [Proportional timeout stretch check](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/tree/orx/proportional-timeout-stretch-check) | Eight homogeneous instances; 10/30/50s limits at $S=1/1.5/2$ | `python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt && .venv/bin/python reproduce.py` | Aligned: $S=2$ 54.52% vs 54% | Vast.ai SSH; 12m26s |

The three successful evidence runs used 33m34s total wall-clock time. Monetary cost is unavailable from the captured run evidence.

## Local notebook

```bash
marimo edit notebooks/dag_carbon_reproduction.py
marimo run notebooks/dag_carbon_reproduction.py
```
