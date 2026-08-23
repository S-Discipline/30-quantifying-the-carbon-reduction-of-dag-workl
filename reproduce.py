#!/usr/bin/env python3
"""Targeted reproduction of arXiv:2512.07799's carbon-scheduling claim.

The script follows the released CP-SAT formulation while making the scale and
solver budget explicit in config.json.  All evidence is emitted to stdout so an
ephemeral OpenResearch runner preserves it.
"""

from __future__ import annotations

import csv
import io
import json
import math
import random
import statistics
import time
import urllib.request
from dataclasses import dataclass

from ortools.sat.python import cp_model


UPSTREAM_COMMIT = "cc312ef7d238d56d7114053dcdd04685b8a6a4d7"
RAW_ROOT = f"https://raw.githubusercontent.com/rbostandoust/GreenSys26-DAG/{UPSTREAM_COMMIT}"
TRACE_URL = f"{RAW_ROOT}/CarbonTrace/AU-SA_2024.csv"
JOBS_URL = f"{RAW_ROOT}/Data/JobPool/JobPool_4Ops_MeanOpDur=7_Epoch=15_DAG.json"
EPOCH_HOURS = 0.25


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def load_trace() -> list[int]:
    rows = csv.DictReader(io.StringIO(fetch(TRACE_URL).decode()))
    hourly = [
        int(round(float(row["Carbon intensity gCO₂eq/kWh (Life cycle)"])))
        for row in rows
    ]
    return [value for value in hourly for _ in range(4)]


def load_jobs() -> dict[str, dict]:
    return json.loads(fetch(JOBS_URL))


@dataclass
class Solution:
    status: str
    objective: float | None = None
    makespan: int | None = None
    carbon_g: float | None = None
    energy_kwh: float | None = None
    utilization: float | None = None


def solve(
    durations: list[list[int]],
    parents: list[dict[int, int]],
    arrivals: list[int],
    carbon: list[int],
    powers: list[float],
    duration_coeffs: list[float],
    objective: str,
    timeout_s: float,
    seed: int,
    makespan_limit: int | None = None,
) -> Solution:
    model = cp_model.CpModel()
    horizon = makespan_limit or 7 * 24 * 4
    machine_intervals: list[list] = [[] for _ in powers]
    tasks: dict[tuple[int, int], tuple] = {}
    presences: dict[tuple[int, int, int], object] = {}
    task_costs = []

    for j, job in enumerate(durations):
        for t, base_duration in enumerate(job):
            start = model.new_int_var(0, horizon, f"start_{j}_{t}")
            end = model.new_int_var(0, horizon, f"end_{j}_{t}")
            tasks[(j, t)] = (start, end)
            choices = []
            for m, (power, coeff) in enumerate(zip(powers, duration_coeffs)):
                duration = int(math.ceil(coeff * base_duration))
                present = model.new_bool_var(f"present_{j}_{t}_{m}")
                interval = model.new_optional_interval_var(
                    start, duration, end, present, f"interval_{j}_{t}_{m}"
                )
                machine_intervals[m].append(interval)
                choices.append(present)
                presences[(j, t, m)] = present

                # A slow heterogeneous alternative can exceed a tight S=1
                # horizon. It is simply unavailable for that constrained solve.
                if duration > horizon:
                    model.add(present == 0)
                    continue

                if objective == "carbon":
                    latest = horizon - duration
                    prefix = [0]
                    for value in carbon[: horizon + duration]:
                        prefix.append(prefix[-1] + value)
                    costs = [
                        int(round((prefix[s + duration] - prefix[s]) * power * 100))
                        for s in range(latest + 1)
                    ]
                    safe_start = model.new_int_var(0, latest, f"safe_start_{j}_{t}_{m}")
                    model.add(safe_start == start).only_enforce_if(present)
                    model.add(safe_start == 0).only_enforce_if(present.negated())
                    raw_cost = model.new_int_var(min(costs), max(costs), f"raw_cost_{j}_{t}_{m}")
                    model.add_element(safe_start, costs, raw_cost)
                    active_cost = model.new_int_var(min(0, min(costs)), max(0, max(costs)), f"cost_{j}_{t}_{m}")
                    model.add(active_cost == raw_cost).only_enforce_if(present)
                    model.add(active_cost == 0).only_enforce_if(present.negated())
                    task_costs.append(active_cost)
            model.add_exactly_one(choices)

            if t == 0:
                model.add(start >= arrivals[j])
            else:
                model.add(start >= tasks[(j, parents[j][t])][1])

    for intervals in machine_intervals:
        model.add_no_overlap(intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [end for _, end in tasks.values()])
    if makespan_limit is not None:
        model.add(makespan <= makespan_limit)
    if objective == "makespan":
        model.minimize(makespan)
    elif objective == "carbon":
        model.minimize(sum(task_costs))
    else:
        raise ValueError(objective)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_s
    solver.parameters.random_seed = seed
    solver.parameters.num_search_workers = 8
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return Solution(status=solver.status_name(status))

    carbon_g = 0.0
    energy_kwh = 0.0
    busy_epochs = 0
    for (j, t, m), present in presences.items():
        if solver.value(present):
            start = solver.value(tasks[(j, t)][0])
            duration = int(math.ceil(duration_coeffs[m] * durations[j][t]))
            carbon_g += sum(carbon[start : start + duration]) * powers[m] * EPOCH_HOURS
            energy_kwh += duration * powers[m] * EPOCH_HOURS
            busy_epochs += duration
    span = solver.value(makespan)
    utilization = busy_epochs / (len(powers) * span) if span else 0.0
    return Solution(
        status=solver.status_name(status),
        objective=solver.objective_value,
        makespan=span,
        carbon_g=carbon_g,
        energy_kwh=energy_kwh,
        utilization=utilization,
    )


def main() -> None:
    with open("config.json", encoding="utf-8") as handle:
        cfg = json.load(handle)
    started = time.monotonic()
    trace = load_trace()
    pool = load_jobs()
    job_ids = list(pool)
    arrival_rng = random.Random(cfg["seed"])
    arrivals_all = [
        sorted(arrival_rng.randrange(0, 96) for _ in range(cfg["jobs_per_instance"]))
        for _ in range(cfg["instances"])
    ]
    date_rng = random.Random(cfg["seed"] + 991)
    day_offsets = [date_rng.randrange(0, 334) for _ in range(cfg["instances"])]
    records = []

    print("REPRO_CONFIG=" + json.dumps({**cfg, "upstream_commit": UPSTREAM_COMMIT}, sort_keys=True))
    for mode in cfg["server_modes"]:
        if mode == "homogeneous":
            powers, coeffs = [1.0] * 5, [1.0] * 5
        elif mode == "heterogeneous":
            powers, coeffs = [0.25, 0.5, 1.0, 1.5, 2.0], [3.0, 2.0, 1.0, 0.75, 0.5]
        else:
            raise ValueError(mode)

        for instance in range(cfg["instances"]):
            sample_rng = random.Random(cfg["seed"] + instance)
            selected = sample_rng.sample(job_ids, cfg["jobs_per_instance"])
            durations = [pool[job]["operations_duration"] for job in selected]
            parents = [
                {int(k): int(v) for k, v in pool[job]["operations_dependency"].items()}
                for job in selected
            ]
            offset = day_offsets[instance] * 96
            carbon = trace[offset : offset + 30 * 96]
            baseline = solve(
                durations, parents, arrivals_all[instance], carbon, powers, coeffs,
                "makespan", cfg["solver_timeout_s"], cfg["seed"] + instance,
            )
            if baseline.carbon_g is None:
                print(f"INSTANCE_SKIPPED mode={mode} instance={instance} baseline={baseline.status}")
                continue

            for stretch in cfg["stretch_factors"]:
                limit = int(math.ceil(stretch * baseline.makespan))
                aware = solve(
                    durations, parents, arrivals_all[instance], carbon, powers, coeffs,
                    "carbon", cfg["solver_timeout_s"], cfg["seed"] + instance,
                    makespan_limit=limit,
                )
                if aware.carbon_g is None:
                    print(f"INSTANCE_SKIPPED mode={mode} instance={instance} stretch={stretch} aware={aware.status}")
                    continue
                record = {
                    "mode": mode,
                    "instance": instance,
                    "day_offset": day_offsets[instance],
                    "stretch": stretch,
                    "baseline_status": baseline.status,
                    "aware_status": aware.status,
                    "baseline_makespan": baseline.makespan,
                    "aware_makespan": aware.makespan,
                    "baseline_carbon_g": round(baseline.carbon_g, 4),
                    "aware_carbon_g": round(aware.carbon_g, 4),
                    "carbon_savings_pct": round(100 * (baseline.carbon_g - aware.carbon_g) / baseline.carbon_g, 4),
                    "baseline_energy_kwh": round(baseline.energy_kwh, 4),
                    "aware_energy_kwh": round(aware.energy_kwh, 4),
                    "baseline_utilization": round(baseline.utilization, 6),
                }
                records.append(record)
                print("INSTANCE_RESULT=" + json.dumps(record, sort_keys=True))

    summaries = []
    for mode in cfg["server_modes"]:
        for stretch in cfg["stretch_factors"]:
            subset = [r for r in records if r["mode"] == mode and r["stretch"] == stretch]
            values = [r["carbon_savings_pct"] for r in subset]
            if not values:
                continue
            summary = {
                "mode": mode,
                "stretch": stretch,
                "n": len(values),
                "mean_carbon_savings_pct": round(statistics.mean(values), 4),
                "median_carbon_savings_pct": round(statistics.median(values), 4),
                "stdev_carbon_savings_pct": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
                "mean_baseline_makespan": round(statistics.mean(r["baseline_makespan"] for r in subset), 4),
                "mean_baseline_utilization_pct": round(100 * statistics.mean(r["baseline_utilization"] for r in subset), 4),
                "paper_mean_carbon_savings_pct": cfg["paper_targets"][mode].get(str(stretch)),
            }
            summaries.append(summary)
            print("SUMMARY=" + json.dumps(summary, sort_keys=True))
    print("FINAL_RESULT=" + json.dumps({
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "records": len(records),
        "summaries": summaries,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
