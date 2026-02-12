from datetime import datetime, date, timedelta
from timer import PomodoroTimer
from task import TaskManager
from visualization import get_daily_availability, get_weekly_availability

def select_task_ui(manager):
    tasks = manager.get_all_tasks()
    if not tasks:
        print("No tasks available.")
        return None

    print("\nSelect a task:")
    for idx, task in enumerate(tasks, 1):
        print(f"{idx}. {task.name} (Category: {task.category}, Estimated: {task.estimated_pomodoros} Pomodoros)")

    while True:
        choice = input("Enter task number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(tasks):
            return tasks[int(choice) - 1].name
        print("Invalid choice. Please enter a valid task number.")

def show_tasks_ui(manager):
    tasks = manager.get_all_tasks()
    if not tasks:
        print("No tasks available.")
        return

    print("\n Current Tasks")

    for task in tasks:
        if task.completed_pomodoros == 0:
            status = "Not Started"
        elif task.completed_pomodoros < task.estimated_pomodoros:
            status = "In Progress"
        else:
            status = "Completed"

        remaining = max(0, task.estimated_pomodoros - task.completed_pomodoros)

        print(
            f"- {task.name}\n"
            f"   Category : {task.category}\n"
            f"   Status   : {status}\n"
            f"   Sessions : {task.completed_pomodoros}/{task.estimated_pomodoros}\n"
            f"   Remaining: {remaining}\n"
        )


CATEGORIES = {
    "1": "study",
    "2": "exam",
    "3": "assignment",
    "4": "reading",
    "5": "other"
}

def main():
    timer = PomodoroTimer()
    manager = TaskManager()

    while True:
        print("\n--- Pomodoro Task Manager ---")
        print("1. Add new task")
        print("2. Start Pomodoro")
        print("3. Complete Pomodoro for a task")
        print("4. Show tasks")
        print("5. Delete task")
        print("6. Daily summary")
        print("7. Weekly summary With Charts")
        print("8. Generate daily schedule")
        print("9. Generate weekly schedule")
        print("10. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            name = input("Task name: ")
            print("\nSelect category:")
            for key, value in CATEGORIES.items():
                print(f"{key}. {value.capitalize()}")

            while True:
                choice_cat = input("Enter category number: ").strip()
                if choice_cat in CATEGORIES:
                    category = CATEGORIES[choice_cat]
                    break
                print("Invalid category. Please choose a number from the list.")

            while True:
                estimated = input("Estimated Pomodoros (>= 1): ").strip()
                if estimated.isdigit() and int(estimated) >= 1:
                    estimated = int(estimated)
                    break
                print("Please enter a whole number (1 or more).")

            while True:
                due_date = input("Due date (YYYY-MM-DD): ").strip()

                try:
                    parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()

                    if parsed_date < date.today():
                        print("Due date must be today or later.")
                        continue

                    break 

                except ValueError:
                    print("Invalid format. Please use YYYY-MM-DD.")

            print("Task added")

            deps_raw = input("Dependencies (comma-separated task names, or blank): ").strip()
            dependencies = [d.strip() for d in deps_raw.split(",") if d.strip()]

            success, message = manager.add_task(name, category, estimated, due_date, dependencies=dependencies)
            print(message)

        elif choice == "2":
            timer.start()

        elif choice == "3":
            task_name = select_task_ui(manager)

            if task_name:
                while True:
                    task = manager.get_task_by_name(task_name)
                    if task.is_completed():
                        print(f"Task '{task_name}' is already completed.")
                        break

                    timer.start()
                    timer.complete()
                    manager.log_pomodoro(task_name)
                    print(f"Pomodoro for '{task_name}' completed and recorded")

                    study_again = input(
                        "Start another Pomodoro for this task? (y/n): "
                    ).lower()
                    if study_again != "y":
                        break

        elif choice == "4":
            show_tasks_ui(manager)

        elif choice == "5":
            task_name = select_task_ui(manager)
            if task_name:
                confirm = input(
                    f"Are you sure you want to delete '{task_name}'? (y/n): "
                ).lower()
                if confirm == "y":
                    success, message = manager.delete_task(task_name)
                    print(message)
                else:
                    print("Delete cancelled.")

        elif choice == "6":
            today_pomodoros_count = manager.get_todays_pomodoro_count()
            print(f"Pomodoros completed today: {today_pomodoros_count}")
            print(f"Focus time today: {today_pomodoros_count * 25} minutes")

        elif choice == "7":
            summary = manager.weekly_summary()

            print(f"\n📊 Weekly Summary ({summary['start']} to {summary['end']})")
            print(f"Total Pomodoros: {summary['total']}")
            print(f"Total Focus Time: {summary['focus_minutes']} minutes")

            print("\nPomodoros per day:")
            for day_str, count in summary["per_day"].items():
                print(f"  {day_str}: {count}")

            print("\nPomodoros by category:")
            for cat, count in summary["by_category"].items():
                print(f"  {cat}: {count}")

            try:
                from visualization import weekly_charts_paged
                weekly_charts_paged(summary)  
            except Exception as e:
                print("Chart error:", e)


        elif choice == "8":
            available_hours = get_daily_availability() 

            schedule = manager.generate_daily_schedule(available_hours)

            if not schedule:
                print("No tasks scheduled.")
            else:
                print("\nOptimized Daily Schedule:")
                for entry in schedule:
                    print(f"{entry['start']:.2f}-{entry['end']:.2f} : {entry['task']} ({entry.get('category','other')})")

            try:
                from visualization import plot_schedule
                plot_schedule(schedule)
            except Exception as e:
                print("Daily schedule chart error:", e)

        elif choice == "9":
            weekly_availability = get_weekly_availability() 

            weekly_schedule = manager.generate_weekly_schedule(
                weekly_availability,
                decay_per_day=0.1
            )

            for day in sorted(weekly_schedule.keys()):
                schedule = weekly_schedule[day]
                print(f"\n📅 {day}")
                if not schedule:
                    print("  No tasks scheduled.")
                else:
                    for entry in schedule:
                        print(f"  {entry['start']:.2f}-{entry['end']:.2f} : {entry['task']} ({entry.get('category','other')})")

            try:
                from visualization import plot_weekly_schedule
                plot_weekly_schedule(weekly_schedule)
            except Exception as e:
                print("Weekly schedule chart error:", e)

        elif choice == "10":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice, try again")


if __name__ == "__main__":
    main()
