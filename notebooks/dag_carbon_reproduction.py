import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Carbon-aware scheduling for DAG workloads

    **An evidence-first tutorial reproducing the central claim of
    [arXiv:2512.07799](https://www.alphaxiv.org/abs/2512.07799).**
    """)
    return


@app.cell
def _(mo):
    mo.image(
        "https://raw.githubusercontent.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/main/reports/dag-carbon-reproduction/images/headline_result.png",
        width=900,
        rounded=True,
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What the figure says

    A makespan-only scheduler answers: *How soon can all jobs finish?* A
    carbon-aware scheduler asks a second question: *Among schedules that
    finish within the allowed makespan, which one runs work in the cleanest
    grid periods?*

    In this downscaled reproduction, carbon-aware scheduling saved **20.93%**
    at the same optimal makespan on homogeneous servers, compared with the
    paper's **25%**. On heterogeneous servers it saved **20.60%**, compared
    with **18%**. Allowing twice the makespan and scaling solver time with
    search complexity produced **54.52%**, compared with **54%**.
    """)
    return


@app.cell
def _(mo):
    summary = [
        {
            "Claim": "Homogeneous S=1",
            "Paper (%)": 25.0,
            "Observed (%)": 20.93,
            "n": 24,
            "Assessment": "Aligned",
        },
        {
            "Claim": "Heterogeneous S=1",
            "Paper (%)": 18.0,
            "Observed (%)": 20.60,
            "n": 16,
            "Assessment": "Aligned",
        },
        {
            "Claim": "Homogeneous S=2",
            "Paper (%)": 54.0,
            "Observed (%)": 54.52,
            "n": 8,
            "Assessment": "Aligned under proportional timeouts",
        },
    ]
    mo.ui.table(summary, selection=None, label="Paper and observed results")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## The scheduling model in plain language

    Each job is a directed acyclic graph (DAG): a task may start only after
    its parent finishes. Each task can run on one of five servers, and no
    server can run overlapping tasks. Time is divided into 15-minute epochs,
    each carrying the AU-SA grid's carbon intensity.

    The experiment solves every sampled instance twice:

    1. Minimize makespan to obtain $C_{OPT}$.
    2. Constrain makespan to $S \times C_{OPT}$, then minimize
       $\sum_{task}\sum_{epoch} power \times carbon\ intensity$.

    Savings are paired within an instance:

    $$
    100\times\frac{carbon_{makespan}-carbon_{aware}}{carbon_{makespan}}.
    $$
    """)
    return


@app.cell
def _():
    proportional_records = [
        {"instance": 0, "stretch": 1.0, "savings_pct": 58.3308},
        {"instance": 0, "stretch": 1.5, "savings_pct": 66.5144},
        {"instance": 0, "stretch": 2.0, "savings_pct": 65.8021},
        {"instance": 1, "stretch": 1.0, "savings_pct": 24.1854},
        {"instance": 1, "stretch": 1.5, "savings_pct": 43.7262},
        {"instance": 1, "stretch": 2.0, "savings_pct": 57.4515},
        {"instance": 2, "stretch": 1.0, "savings_pct": 12.6364},
        {"instance": 2, "stretch": 1.5, "savings_pct": 27.3743},
        {"instance": 2, "stretch": 2.0, "savings_pct": 29.5414},
        {"instance": 3, "stretch": 1.0, "savings_pct": 70.0489},
        {"instance": 3, "stretch": 1.5, "savings_pct": 76.3817},
        {"instance": 3, "stretch": 2.0, "savings_pct": 76.3001},
        {"instance": 4, "stretch": 1.0, "savings_pct": 3.1349},
        {"instance": 4, "stretch": 1.5, "savings_pct": 50.9284},
        {"instance": 4, "stretch": 2.0, "savings_pct": 77.8757},
        {"instance": 5, "stretch": 1.0, "savings_pct": 42.6921},
        {"instance": 5, "stretch": 1.5, "savings_pct": 41.0744},
        {"instance": 5, "stretch": 2.0, "savings_pct": 46.1737},
        {"instance": 6, "stretch": 1.0, "savings_pct": 9.2953},
        {"instance": 6, "stretch": 1.5, "savings_pct": 8.5442},
        {"instance": 6, "stretch": 2.0, "savings_pct": 8.7369},
        {"instance": 7, "stretch": 1.0, "savings_pct": 28.9859},
        {"instance": 7, "stretch": 1.5, "savings_pct": 68.6367},
        {"instance": 7, "stretch": 2.0, "savings_pct": 74.2439},
    ]
    return (proportional_records,)


@app.cell
def _(mo):
    instance = mo.ui.slider(0, 7, value=0, step=1, label="Inspect paired instance")
    instance
    return (instance,)


@app.cell
def _(instance, mo, proportional_records):
    selected = [
        {
            "Stretch S": row["stretch"],
            "Carbon savings (%)": row["savings_pct"],
            "Solver cap (s)": {1.0: 10, 1.5: 30, 2.0: 50}[row["stretch"]],
        }
        for row in proportional_records
        if row["instance"] == instance.value
    ]
    mo.vstack(
        [
            mo.md(
                f"### Instance {instance.value}: the effect is heterogeneous, not guaranteed per case"
            ),
            mo.ui.table(selected, selection=None),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why timeout policy matters

    A larger stretch factor expands the feasible set, so the true optimum
    cannot become worse. But it also expands CP-SAT's search space. With a
    fixed 10-second cap, only 11 of 16 homogeneous $S=2$ searches returned
    a feasible schedule and their mean savings were 7.54%. With the paper's
    proportional 1×/3×/5× policy, scaled to 10/30/50 seconds, all eight
    focused cases returned schedules and mean savings rose monotonically:
    **31.16% → 47.90% → 54.52%**.

    This distinction is a useful reproduction lesson: solver budget is part
    of the experimental treatment when problem complexity changes.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What this evidence does—and does not—establish

    **Supported here:** carbon-aware reordering can cut operational emissions
    without extending the optimal makespan; proportional search time recovers
    the reported $S=2$ endpoint; higher utilization is descriptively
    associated with lower savings.

    **Still open:** the paper's energy-vs-carbon objective comparison, server
    count and task count sweeps, regional carbon traces, and a full 1,000-case
    run with 60/180/300-second limits. The observed confidence intervals are
    descriptive: samples use one seed and multi-threaded CP-SAT searches.

    See the [full illustrated report](https://github.com/S-Discipline/30-quantifying-the-carbon-reduction-of-dag-workl/blob/main/reports/dag-carbon-reproduction/report.md)
    for implementation details, provenance, and every claim assessment.
    """)
    return


if __name__ == "__main__":
    app.run()
