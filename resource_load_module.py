import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def plot_resource_load(task_df, workdays_per_week):
    task_df["Длительность"] = task_df["Длительность"].astype(int)
    holidays = [datetime(2026, 1, 1), datetime(2026, 5, 1), datetime(2026, 12, 25)]
    schedule = {}
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    def calc_end_date(start, dur):
        cur = start
        days = 0
        while days < dur:
            cur += timedelta(days=1)
            if (workdays_per_week == 6 and cur.weekday() < 6) or \
               (workdays_per_week == 5 and cur.weekday() < 5):
                if cur not in holidays:
                    days += 1
        return cur

    for _, row in task_df.iterrows():
        task = int(row["Задача"])
        dur = int(row["Длительность"])
        preds = row.get("Предшественники", "")
        preds = list(map(int, str(preds).replace(",", " ").split())) if preds else []

        if not preds:
            s = start_date
        else:
            s = max(schedule[p]["end"] for p in preds)

        e = calc_end_date(s, dur)
        schedule[task] = {"start": s, "end": e, "resources": row["Ресурсы"]}

    roles = sorted(set(r.strip() for res in task_df["Ресурсы"] for r in str(res).split(",")))
    date_range = pd.date_range(
        start=min(x["start"] for x in schedule.values()),
        end=max(x["end"] for x in schedule.values())
    )
    load_data = []
    for date in date_range:
        row = {"Дата": date}
        for role in roles:
            row[role] = 0
        for task, info in schedule.items():
            if info["start"] <= date < info["end"]:
                for r in str(info["resources"]).replace(" ", "").split(","):
                    if r in row:
                        row[r] += 100
        load_data.append(row)

    df = pd.DataFrame(load_data)

    figures = []
    for role in roles:
        fig, ax = plt.subplots(figsize=(4, 2))

        ax.plot(df["Дата"], df[role], label=role, marker='o', markersize=3, linewidth=1)
        ax.axhline(y=100, color="red", linestyle="--", label="Макс.")

        ax.set_title(f"Загрузка: {role}", fontsize=8)
        ax.set_xlabel("Дата", fontsize=6)
        ax.set_ylabel("Загрузка (%)", fontsize=6)

        ax.tick_params(axis='x', labelsize=4)
        ax.tick_params(axis='y', labelsize=4)

        # Установим метки на оси X и повернем их на 45 градусов
        ax.set_xticklabels([date.strftime("%d-%m-%Y") for date in df["Дата"]], rotation=45, fontsize=6)

        ax.grid(True)

        figures.append(fig)

    return figures
