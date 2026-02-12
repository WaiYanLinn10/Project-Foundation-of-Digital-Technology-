import os
from datetime import date, timedelta
from task import TaskManager


def test_backend():
    print("Testing Backend Logic...")

    # Clean test files
    if os.path.exists("tasks.csv"):
        os.remove("tasks.csv")
    if os.path.exists("count_pomodoro.csv"):
        os.remove("count_pomodoro.csv")

    manager = TaskManager()

    today = date.today()
    today_str = today.isoformat()

    # Add Multiple Tasks
    manager.add_task("Math Revision", "exam", 3, (today + timedelta(days=3)).isoformat())
    manager.add_task("Essay Draft", "assignment", 2, (today + timedelta(days=2)).isoformat())
    manager.add_task("Research Reading", "reading", 4, (today + timedelta(days=5)).isoformat())
    manager.add_task("General Study", "study", 1, (today + timedelta(days=1)).isoformat())
    manager.add_task("Random Task", "other", 2, (today + timedelta(days=4)).isoformat())

    print("✓ Multiple tasks added")

    # Add Overdue Task (result = rejected)

    past_date = (today - timedelta(days=1)).isoformat()
    success, _ = manager.add_task("Overdue Task", "study", 1, past_date)
    assert not success
    print("✓ Overdue task rejected")

    # Log Pomodoros

    # Today
    manager.log_pomodoro("Math Revision")
    manager.log_pomodoro("Essay Draft")

    # Previous days
    with open("count_pomodoro.csv", "a") as f:
        for i in range(1, 6):
            d = (today - timedelta(days=i)).isoformat()
            f.write(f"{d},study,2\n")
            f.write(f"{d},exam,1\n")

    print("✓ Weekly pomodoro data simulated")

    # Reload Manager (Persistence Check)

    new_manager = TaskManager()
    tasks = new_manager.get_all_tasks()
    assert len(tasks) == 5
    print("✓ Task persistence verified")

    # Test Weekly Summary

    summary = new_manager.weekly_summary()
    print("Weekly Summary:", summary)

    assert summary["total"] > 0
    assert len(summary["per_day"]) == 7
    print("✓ Weekly summary verified")

    # Test Daily Schedule

    available_hours = [(9, 12)]
    schedule = new_manager.generate_daily_schedule(available_hours)
    assert isinstance(schedule, list)
    print("✓ Daily schedule generated")

    # Test Weekly Schedule

    weekly_availability = {
        (today + timedelta(days=i)).isoformat(): [(9, 11)]
        for i in range(7)
    }

    weekly_schedule = new_manager.generate_weekly_schedule(weekly_availability)
    assert isinstance(weekly_schedule, dict)
    print("✓ Weekly schedule generated")

    # Delete Task

    success, _ = new_manager.delete_task("Random Task")
    assert success
    print("✓ Task deletion verified")

    print("\nALL EXTENDED BACKEND TESTS PASSED!")
