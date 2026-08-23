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
    mo.Html(r"""
    <svg viewBox="0 0 900 350" role="img"
         aria-label="Paper and observed carbon savings for three claims"
         style="width:100%;max-width:900px;font-family:system-ui,sans-serif;background:#f8fafc;border-radius:14px">
      <text x="28" y="38" font-size="22" font-weight="700" fill="#17202a">Carbon savings: paper vs. reproduction</text>
      <rect x="610" y="20" width="18" height="12" rx="2" fill="#aab4c3"/><text x="636" y="31" font-size="13" fill="#46515f">Paper</text>
      <rect x="700" y="20" width="18" height="12" rx="2" fill="#087f8c"/><text x="726" y="31" font-size="13" fill="#46515f">Observed</text>

      <text x="28" y="92" font-size="15" fill="#273444">Homogeneous, S=1</text>
      <rect x="218" y="69" width="375" height="20" rx="4" fill="#aab4c3"/><text x="603" y="84" font-size="14" fill="#273444">25.0%</text>
      <rect x="218" y="95" width="314" height="20" rx="4" fill="#087f8c"/><text x="542" y="110" font-size="14" font-weight="700" fill="#087f8c">20.93%</text>

      <text x="28" y="175" font-size="15" fill="#273444">Heterogeneous, S=1</text>
      <rect x="218" y="152" width="270" height="20" rx="4" fill="#aab4c3"/><text x="498" y="167" font-size="14" fill="#273444">18.0%</text>
      <rect x="218" y="178" width="309" height="20" rx="4" fill="#087f8c"/><text x="537" y="193" font-size="14" font-weight="700" fill="#087f8c">20.60%</text>

      <text x="28" y="258" font-size="15" fill="#273444">Homogeneous, S=2</text>
      <rect x="218" y="235" width="540" height="20" rx="4" fill="#aab4c3"/><text x="768" y="250" font-size="14" fill="#273444">54.0%</text>
      <rect x="218" y="261" width="545" height="20" rx="4" fill="#087f8c"/><text x="773" y="276" font-size="14" font-weight="700" fill="#087f8c">54.52%</text>

      <line x1="218" y1="307" x2="818" y2="307" stroke="#b8c2cc"/>
      <text x="218" y="329" text-anchor="middle" font-size="12" fill="#65717f">0%</text>
      <text x="518" y="329" text-anchor="middle" font-size="12" fill="#65717f">30%</text>
      <text x="818" y="329" text-anchor="middle" font-size="12" fill="#65717f">60%</text>
    </svg>
    """)
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
            "Assessment": "Direction supported; numeric gap 16.3%",
        },
        {
            "Claim": "Heterogeneous S=1",
            "Paper (%)": 18.0,
            "Observed (%)": 20.60,
            "n": 16,
            "Assessment": "Direction supported; numeric gap 14.4%",
        },
        {
            "Claim": "Homogeneous S=2",
            "Paper (%)": 54.0,
            "Observed (%)": 54.52,
            "n": 8,
            "Assessment": "Supported; numeric gap 1.0%",
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

    **Overall grade: C — partial reproduction success (medium confidence).**
    Carbon-aware reordering reduced operational emissions without extending
    the optimal makespan, and proportional search time recovered the reported
    homogeneous $S=2$ endpoint. However, the two $S=1$ means differ from the
    paper by 16.3% and 14.4%, beyond the 10% reference used when the paper gives
    no uncertainty interval. The heterogeneous $S=2$ endpoint and several core
    ablations were not supported or not attempted.

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
