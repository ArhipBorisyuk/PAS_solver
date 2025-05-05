# gantt_module.py
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def plot_gantt_diagram(task_df, start_date, workdays_per_week):
    holidays = [datetime(2025, 1, 1), datetime(2025, 5, 1), datetime(2025, 12, 25)]
    task_schedule = {}

    def calculate_end_date(start, duration):
        current_date = start
        days_count = 0
        while days_count < duration:
            current_date += timedelta(days=1)
            if (workdays_per_week == 6 and current_date.weekday() < 6) or \
               (workdays_per_week == 5 and current_date.weekday() < 5):
                if current_date not in holidays:  # Учитываем праздники
                    days_count += 1
        return current_date

    task_executors = {}
    task_dependencies = {}

    for _, row in task_df.dropna().iterrows():
        task = int(float(row["Задача"]))
        dur = int(float(row["Длительность"]))
        deps = str(row["Предшественники"]).replace(",", " ").split()
        deps = list(map(int, deps)) if deps else []
        res = str(row["Ресурсы"])

        task_dependencies[task] = deps
        task_executors[task] = res.split(',') if res else []

    for task in sorted(task_dependencies.keys()):
        deps = task_dependencies.get(task, [])
        ready_deps = [task_schedule[dep]["end"] for dep in deps if dep in task_schedule]

        if ready_deps:
            s = max(ready_deps)
        else:
            s = pd.to_datetime(start_date)

        e = calculate_end_date(s, int(float(task_df.loc[task_df["Задача"] == str(task), "Длительность"].values[0])))
        task_schedule[task] = {"start": s, "end": e}

    fig, ax = plt.subplots(figsize=(12, 6))
    task_list = sorted(task_schedule.keys())

    for task in task_list:
        start = task_schedule[task]["start"]
        end = task_schedule[task]["end"]
        ax.hlines(y=task, xmin=start, xmax=end, color="black", linewidth=2)

        if task in task_executors and task_executors[task]:
            ax.text(start, task, ", ".join(task_executors[task]), va='bottom', fontsize=9, color="black")

    for task, dependencies in task_dependencies.items():
        for dep in dependencies:
            if dep in task_schedule and task in task_schedule:
                dep_end = task_schedule[dep]["end"]
                task_start = task_schedule[task]["start"]

                if dep_end < task_start:
                    arrow_offset = timedelta(days=0.5)
                    ax.hlines(y=dep, xmin=dep_end, xmax=task_start, color="gray", linestyle="dotted", linewidth=1.5)
                    ax.arrow(dep_end + arrow_offset, dep, -0.2, 0, head_width=0.3, head_length=0.5, fc="gray", ec="gray")
                    ax.arrow(task_start - arrow_offset, dep, 0.2, 0, head_width=0.3, head_length=0.5, fc="gray", ec="gray")

                ax.vlines(x=task_start, ymin=dep, ymax=task, color="gray", linestyle="dashed", linewidth=1.5)

    important_dates = sorted(set(date for t in task_schedule.values() for date in [t["start"], t["end"]]))
    ax.set_xticks(important_dates)
    ax.set_xticklabels([date.strftime("%d-%m-%Y") for date in important_dates], rotation=45)
    ax.set_yticks(task_list)
    ax.set_yticklabels(task_list)

    plt.xlabel("Дата")
    plt.ylabel("№ работы")
    plt.title("Календарный план (Диаграмма Ганта)")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.gca().invert_yaxis()
    return fig
