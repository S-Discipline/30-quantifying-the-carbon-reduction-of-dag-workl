#!/usr/bin/env python3
"""Build the public evidence CSVs and figures from immutable orx run logs."""

from __future__ import annotations

import csv
import json
import math
import statistics
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
IMAGES = HERE / "images"
RUNS = {
    "baseline": "8cc15cd1-1a31-46f0-8f08-3ee49053fef9",
    "equal_budget": "0b4de799-65f7-4af5-954d-63bc618e44a8",
    "proportional": "eafa1f70-7e0d-4ea3-87cf-f761df508e37",
}
PAPER = {
    ("homogeneous", 1.0): 25.0,
    ("heterogeneous", 1.0): 18.0,
    ("homogeneous", 2.0): 54.0,
}
BLUE = "#2563EB"
GOLD = "#D79B00"
INK = "#20242A"
GREY = "#9AA3AF"
LIGHT = "#E8EEF8"


def read_run(run_id: str) -> list[dict]:
    text = subprocess.run(
        ["orx", "logs", run_id, "--bytes", "200000"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [
        json.loads(line.split("=", 1)[1])
        for line in text.splitlines()
        if line.startswith("INSTANCE_RESULT=")
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def style(ax, ylabel="Carbon savings (%)"):
    ax.set_facecolor("white")
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(INK)
    ax.tick_params(colors=INK)
    ax.set_ylabel(ylabel, color=INK)


def chart_title(ax, main: str, subtitle: str) -> None:
    ax.set_title(main, loc="left", color=INK, fontsize=16, fontweight="bold", pad=34)
    ax.text(0, 1.01, subtitle, transform=ax.transAxes, color="#5F6875", fontsize=10)


def save(fig, name: str):
    fig.savefig(IMAGES / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def mean_ci(values: list[float]) -> tuple[float, float]:
    mean = statistics.mean(values)
    ci = 1.96 * statistics.stdev(values) / math.sqrt(len(values))
    return mean, ci


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    records = {name: read_run(run_id) for name, run_id in RUNS.items()}
    for name, rows in records.items():
        write_csv(DATA / f"{name}_records.csv", rows)

    baseline_h1 = [
        row for row in records["baseline"]
        if row["mode"] == "homogeneous" and row["stretch"] == 1.0
    ]
    hetero_h1 = [
        row for row in records["equal_budget"]
        if row["mode"] == "heterogeneous" and row["stretch"] == 1.0
    ]
    prop_h2 = [
        row for row in records["proportional"]
        if row["mode"] == "homogeneous" and row["stretch"] == 2.0
    ]
    groups = [baseline_h1, hetero_h1, prop_h2]
    labels = ["Homogeneous\nS=1", "Heterogeneous\nS=1", "Homogeneous\nS=2"]
    keys = [("homogeneous", 1.0), ("heterogeneous", 1.0), ("homogeneous", 2.0)]
    observed_ci = [mean_ci([row["carbon_savings_pct"] for row in group]) for group in groups]
    summary_rows = []
    for label, key, group, (observed, ci) in zip(labels, keys, groups, observed_ci):
        summary_rows.append({
            "claim": label.replace("\n", " "),
            "paper_pct": PAPER[key],
            "observed_pct": round(observed, 4),
            "normal_95ci_halfwidth_pct": round(ci, 4),
            "n": len(group),
        })
    write_csv(DATA / "headline_summary.csv", summary_rows)

    # Figure 1: the immediate paper-vs-observed comparison.
    x = np.arange(3)
    width = 0.34
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    paper_values = [PAPER[key] for key in keys]
    observed_values = [item[0] for item in observed_ci]
    observed_err = [item[1] for item in observed_ci]
    bars1 = ax.bar(x - width / 2, paper_values, width, color="white", edgecolor=INK,
                   linewidth=1.5, label="Paper")
    bars2 = ax.bar(x + width / 2, observed_values, width, color=BLUE, edgecolor=INK,
                   linewidth=1.0, yerr=observed_err, capsize=4, label="Observed")
    ax.bar_label(bars1, fmt="%.0f%%", padding=4, color=INK, fontsize=10)
    ax.bar_label(bars2, fmt="%.1f%%", padding=7, color=INK, fontsize=10)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 78)
    chart_title(ax, "Paper and observed carbon savings",
                "Paper reports no CI; observed error bars describe this small sample and do not establish numeric agreement")
    style(ax)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "headline_result.png")

    # Figure 2: distribution, with all points visible.
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    values = [[row["carbon_savings_pct"] for row in group] for group in groups]
    bp = ax.boxplot(values, patch_artist=True, widths=0.5, showfliers=False,
                    medianprops={"color": INK, "linewidth": 2})
    for box in bp["boxes"]:
        box.set(facecolor=LIGHT, edgecolor=BLUE, linewidth=1.4)
    rng = np.random.default_rng(42)
    for i, vals in enumerate(values, 1):
        jitter = rng.uniform(-0.14, 0.14, len(vals))
        ax.scatter(np.full(len(vals), i) + jitter, vals, s=28, color=BLUE,
                   edgecolor="white", linewidth=0.6, alpha=0.85, zorder=3)
    ax.axhline(0, color=INK, linewidth=1.0)
    ax.set_xticks([1, 2, 3], [f"{label}\nn={len(vals)}" for label, vals in zip(labels, values)])
    chart_title(ax, "Savings vary widely across workload–date pairs",
                "Each point is one paired makespan-only vs carbon-aware schedule")
    style(ax)
    save(fig, "instance_distributions.png")

    # Figure 3: the solver-budget diagnostic.
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    stretches = [1.0, 1.5, 2.0]
    equal_means, equal_ns, prop_means = [], [], []
    for stretch in stretches:
        equal_vals = [
            row["carbon_savings_pct"] for row in records["equal_budget"]
            if row["mode"] == "homogeneous" and row["stretch"] == stretch
        ]
        prop_vals = [
            row["carbon_savings_pct"] for row in records["proportional"]
            if row["mode"] == "homogeneous" and row["stretch"] == stretch
        ]
        equal_means.append(statistics.mean(equal_vals))
        equal_ns.append(len(equal_vals))
        prop_means.append(statistics.mean(prop_vals))
    ax.plot(stretches, equal_means, color=GREY, marker="o", markersize=7,
            linewidth=2, linestyle="--", label="Equal 10 s cap")
    ax.plot(stretches, prop_means, color=BLUE, marker="o", markersize=8,
            linewidth=2.5, label="Proportional 10/30/50 s")
    ax.scatter([2.0], [54.0], marker="D", s=75, facecolor="white", edgecolor=INK,
               linewidth=1.5, label="Paper S=2")
    for x0, y0, n in zip(stretches, equal_means, equal_ns):
        ax.annotate(f"{y0:.1f}% (n={n})", (x0, y0), xytext=(0, -18),
                    textcoords="offset points", ha="center", color="#657080", fontsize=9)
    for x0, y0 in zip(stretches, prop_means):
        ax.annotate(f"{y0:.1f}%", (x0, y0), xytext=(0, 10),
                    textcoords="offset points", ha="center", color=INK, fontsize=9)
    ax.set_xticks(stretches)
    ax.set_xlim(0.88, 2.10)
    ax.set_xlabel("Makespan stretch factor S", color=INK)
    ax.set_ylim(-2, 66)
    chart_title(ax, "Search time determines whether extra stretch is useful",
                "Homogeneous servers; means over returned feasible schedules")
    style(ax)
    ax.legend(frameon=False, loc="upper left")
    save(fig, "timeout_sensitivity.png")

    # Figure 4: utilization mechanism diagnostic at S=1.
    util = np.array([100 * row["baseline_utilization"] for row in baseline_h1])
    saving = np.array([row["carbon_savings_pct"] for row in baseline_h1])
    corr = float(np.corrcoef(util, saving)[0, 1])
    slope, intercept = np.polyfit(util, saving, 1)
    xx = np.linspace(util.min(), util.max(), 100)
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.scatter(util, saving, s=48, facecolor=LIGHT, edgecolor=BLUE, linewidth=1.3)
    ax.plot(xx, slope * xx + intercept, color=GOLD, linewidth=2.2,
            label=f"Linear fit (r={corr:.2f})")
    ax.axhline(0, color=INK, linewidth=0.9)
    ax.set_xlabel("Baseline server utilization (%)", color=INK)
    chart_title(ax, "Higher utilization leaves less room to shift work",
                "Homogeneous S=1 baseline; n=24 paired instances; descriptive association")
    style(ax)
    ax.legend(frameon=False, loc="upper right")
    save(fig, "utilization_vs_savings.png")

    print(json.dumps({"summary": summary_rows, "utilization_correlation": round(corr, 4)}, indent=2))


if __name__ == "__main__":
    main()
