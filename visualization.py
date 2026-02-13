import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import date, timedelta

def get_daily_availability():
    WORK_START, WORK_END = 9, 22
    raw = input("Unavailable (e.g. 9-12, 15-20): ").strip()

    unavailable = []
    if raw:
        for part in [p.strip() for p in raw.split(",") if p.strip()]:
            if "-" not in part:
                print(f" Invalid format '{part}' (use 9-12)")
                continue

            try:
                a, b = part.split("-", 1)
                start = int(a.strip())
                end = int(b.strip())

                start = max(WORK_START, start)
                end = min(WORK_END, end)

                if start < end:
                    unavailable.append((start, end))
            except ValueError:
                print(f" Invalid numbers in '{part}'")


    unavailable.sort()

    available = []
    current = WORK_START
    for s, e in unavailable:
        if current < s:
            available.append((current, s))
        current = max(current, e)

    if current < WORK_END:
        available.append((current, WORK_END))

    return available

from datetime import date, timedelta

def get_weekly_availability():
    WORK_START, WORK_END = 9, 22
    today = date.today()

    print("\n📅 Weekly Availability (09:00–22:00 fixed)")
    print("Enter unavailable hours like: 13-15, 18-19 (Enter = free all day)\n")

    weekly = {}

    for i in range(7):
        day_date = today + timedelta(days=i)
        day_key = day_date.isoformat()
        day_name = day_date.strftime("%A")

        raw = input(f"{day_name} ({day_key}) unavailable: ").strip()

        unavailable = []
        if raw:
            for part in [x.strip() for x in raw.split(",") if x.strip()]:
                if "-" not in part:
                    print(f"Skipped invalid slot '{part}' (use 13-15)")
                    continue
                try:
                    a, b = part.split("-", 1)
                    start, end = int(a.strip()), int(b.strip())
                    start = max(WORK_START, start)
                    end = min(WORK_END, end)
                    if start < end:
                        unavailable.append((start, end))
                except ValueError:
                    print(f"Skipped invalid slot '{part}'")

        unavailable.sort()

        available = []
        current = WORK_START
        for start, end in unavailable:
            if current < start:
                available.append((current, start))
            current = max(current, end)

        if current < WORK_END:
            available.append((current, WORK_END))

        weekly[day_key] = available

    return weekly


def weekly_charts_paged(summary):
    """
    Shows 4 charts + 1 pie across 3 pages.
    Uses TaskManager.weekly_summary() output (passed from main.py).
    """

    per_day = summary.get("per_day", {})
    by_cat = summary.get("by_category", {})

    all_categories = ["study", "exam", "assignment", "reading", "other"]
    by_cat_ordered = {c: int(by_cat.get(c, 0)) for c in all_categories}

    days = list(per_day.keys())
    values = [int(per_day[d]) for d in days]

    cumulative = []
    running = 0
    for v in values:
        running += v
        cumulative.append(running)

    avg = (sum(values) / len(values)) if values else 0

    if len(values) >= 2:
        slope = (values[-1] - values[0]) / (len(values) - 1)
        trend = [values[0] + slope * i for i in range(len(values))]
    else:
        trend = values

    plt.ion()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    pages = 3
    page = 0

    def render_page(p):
        for ax in axes:
            ax.clear()

        if p == 0:

            axes[0].bar(days, values)
            axes[0].set_title("Pomodoros Per Day")
            axes[0].set_ylabel("Pomodoros")
            axes[0].tick_params(axis="x", rotation=45)


            axes[1].plot(days, cumulative)
            axes[1].set_title("Cumulative Productivity")
            axes[1].set_ylabel("Total Pomodoros")
            axes[1].tick_params(axis="x", rotation=45)

            fig.suptitle("Weekly Dashboard — Page 1/3 (N=Next, P=Prev, Q=Quit)")

        elif p == 1:
  
            axes[0].bar(list(by_cat_ordered.keys()), list(by_cat_ordered.values()))
            axes[0].set_title("Pomodoros by Category (Bar)")
            axes[0].set_ylabel("Pomodoros")
            axes[0].tick_params(axis="x", rotation=20)


            axes[1].plot(days, values)
            axes[1].axhline(avg)
            axes[1].set_title("Daily Productivity vs Average")
            axes[1].set_ylabel("Pomodoros")
            axes[1].tick_params(axis="x", rotation=45)

            fig.suptitle("Weekly Dashboard — Page 2/3 (N=Next, P=Prev, Q=Quit)")

        else:
 
            axes[0].plot(days, values)
            axes[0].plot(days, trend)
            axes[0].set_title("Weekly Trend (Simple Fit)")
            axes[0].set_ylabel("Pomodoros")
            axes[0].tick_params(axis="x", rotation=45)

            if sum(by_cat_ordered.values()) > 0:
                axes[1].pie(
                    list(by_cat_ordered.values()),
                    labels=list(by_cat_ordered.keys()),
                    autopct="%1.1f%%"
                )
                axes[1].set_title("Category Share (Pie)")
            else:
                axes[1].text(0.5, 0.5, "No category data", ha="center", va="center")
                axes[1].set_title("Category Share (Pie)")

            fig.suptitle("Weekly Dashboard — Page 3/3 (N=Next, P=Prev, Q=Quit)")

        fig.canvas.draw()
        fig.canvas.flush_events()

    render_page(page)

    while True:
        cmd = input("\nCharts UI: [N]ext  [P]revious  [Q]uit : ").strip().lower()
        if cmd == "n":
            page = (page + 1) % pages
            render_page(page)
        elif cmd == "p":
            page = (page - 1) % pages
            render_page(page)
        elif cmd == "q":
            break
        else:
            print("Invalid input. Use N, P, or Q.")

    plt.ioff()
    plt.close(fig)

def plot_schedule(schedule):

    if not schedule:
        print("No schedule to plot.")
        return

    CATEGORY_COLORS = {
        "study": "#4C72B0",
        "exam": "#DD8452",
        "assignment": "#55A868",
        "reading": "#C44E52",
        "other": "#8172B3"
    }

    fig, ax = plt.subplots(figsize=(14, 4))

    for entry in schedule:
        start = entry["start"]
        duration = entry["end"] - entry["start"]
        category = entry.get("category", "other")
        color = CATEGORY_COLORS.get(category, "#999999")

        ax.barh(
            0,   
            duration,
            left=start,
            height=0.6,
            color=color,
            edgecolor="black"
        )

        if duration > 0.5:
            ax.text(
                start + duration / 2,
                0,
                entry["task"],
                ha="center",
                va="center",
                color="white",
                fontsize=9
            )

    ax.set_xlim(9, 22)
    ax.set_yticks([]) 
    ax.set_xlabel("Time")
    ax.set_title("Daily Timetable")

    ax.set_xticks(range(9, 23))
    ax.grid(axis="x", linestyle="--", alpha=0.4)


    legend_patches = [
        mpatches.Patch(color=color, label=cat.capitalize())
        for cat, color in CATEGORY_COLORS.items()
    ]
    ax.legend(handles=legend_patches, loc="upper right")

    plt.tight_layout()
    plt.show()

def plot_weekly_schedule(weekly_schedule):

    if not weekly_schedule:
        print("No weekly schedule to plot.")
        return

    CATEGORY_COLORS = {
        "study": "#4C72B0",
        "exam": "#DD8452",
        "assignment": "#55A868",
        "reading": "#C44E52",
        "other": "#8172B3"
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    days = sorted(weekly_schedule.keys())
    y_positions = range(len(days))

    for i, day in enumerate(days):
        for entry in weekly_schedule[day]:
            start = entry["start"]
            duration = entry["end"] - entry["start"]
            category = entry.get("category", "other")

            color = CATEGORY_COLORS.get(category, "#999999")

            ax.barh(
                i,
                duration,
                left=start,
                height=0.6,
                color=color,
                edgecolor="black"
            )


            if duration > 0.5:
                ax.text(
                    start + duration / 2,
                    i,
                    entry["task"],
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8
                )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(days)
    ax.set_xlim(9, 22)

    ax.set_xlabel("Time")
    ax.set_title("Weekly Timetable (Optimized Schedule)")

    ax.set_xticks(range(9, 23))
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    legend_patches = [
        mpatches.Patch(color=color, label=cat.capitalize())
        for cat, color in CATEGORY_COLORS.items()
    ]
    ax.legend(handles=legend_patches, loc="upper right")

    plt.tight_layout()
    plt.show()