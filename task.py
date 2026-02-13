import csv
from datetime import date, datetime, timedelta
import os

class Task:
    def __init__(self, name, category, estimated_pomodoros, due_date, completed_pomodoros=0, status="not started", start_date=None, end_date="", dependencies=None):
        self.name = name
        self.category = category
        self.estimated_pomodoros = int(estimated_pomodoros)
        self.completed_pomodoros = int(completed_pomodoros)
        self.due_date = due_date
        self.status = status
        self.start_date = start_date if start_date else date.today().isoformat()
        self.end_date = end_date
        self.dependencies = dependencies or []
        self.priority_score = 0 

    def mark_completed(self):
        self.status = "completed"
        self.end_date = date.today().isoformat()

    def add_pomodoro(self):
        self.completed_pomodoros += 1
        self.status = "in progress"
        if self.completed_pomodoros >= self.estimated_pomodoros:
            self.mark_completed()

    def is_completed(self):
        return self.status == "completed"

    def to_dict(self):
        return {
            "task_name": self.name,
            "category": self.category,
            "estimated_pomodoros": self.estimated_pomodoros,
            "completed_pomodoros": self.completed_pomodoros,
            "status": self.status,
            "start_date": self.start_date,
            "due_date": self.due_date,
            "end_date": self.end_date,
            "dependencies": ",".join(self.dependencies)
        }

    @classmethod
    def from_dict(cls, data):
        deps = data.get("dependencies") or ""
        dependencies = [d.strip() for d in deps.split(",") if d.strip()]

        return cls(
            name=data["task_name"],
            category=data["category"],
            estimated_pomodoros=data["estimated_pomodoros"],
            due_date=data["due_date"],
            completed_pomodoros=data["completed_pomodoros"],
            status=data["status"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date", ""),
            dependencies=dependencies
        
        )


class TaskManager:
    TASK_FILE = "tasks.csv"
    POMODORO_FILE = "count_pomodoro.csv"

    def __init__(self):
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        if not os.path.exists(self.TASK_FILE):
            return
        
        with open(self.TASK_FILE, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.tasks.append(Task.from_dict(row))

    def save_tasks(self):
        if not self.tasks:
            return

        with open(self.TASK_FILE, "w", newline="") as file:
            fieldnames = self.tasks[0].to_dict().keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in self.tasks:
                writer.writerow(task.to_dict())

    def add_task(self, name, category, estimated, due_date, dependencies=None):
        try:
            due = date.fromisoformat(due_date)
            today = date.today()

            if due < today:
                return False, "Due date must be today or later."
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."

        if self.get_task_by_name(name):
            return False, f"Task '{name}' already exists!"

        new_task = Task(name, category, estimated, due_date, dependencies=dependencies or [])
        self.tasks.append(new_task)
        self.save_tasks()

        return True, "Task added successfully."

    
    def delete_task(self, task_name):
        task = self.get_task_by_name(task_name)

        if not task:
            return False, f"Task '{task_name}' not found."

        self.tasks.remove(task)

        if not self.tasks:
            with open(self.TASK_FILE, "w", newline="") as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=task.to_dict().keys()
                )
                writer.writeheader()
            return True, f"Task '{task_name}' deleted. No tasks remaining."

        self.save_tasks()
        return True, f"Task '{task_name}' deleted successfully."

    def get_task_by_name(self, name):
        for task in self.tasks:
            if task.name.lower() == name.lower():
                return task
        return None

    def get_all_tasks(self):
        return self.tasks

    def get_todays_pomodoro_count(self):
        today = date.today().isoformat()
        if not os.path.exists(self.POMODORO_FILE):
            return 0

        total = 0
        with open(self.POMODORO_FILE, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row.get("date") or "").strip() == today:
                    try:
                        total += int(row.get("pomodoros", 0))
                    except ValueError:
                        pass
        return total


    def log_pomodoro(self, task_name):
        task = self.get_task_by_name(task_name)
        if not task:
            return False, "Task not found."

        task.add_pomodoro()
        self.save_tasks()

        file_exists = os.path.exists(self.POMODORO_FILE)

        with open(self.POMODORO_FILE, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "category", "pomodoros"])
            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "date": date.today().isoformat(),
                "category": task.category.lower(),
                "pomodoros": 1
            })

        return True, "Pomodoro recorded successfully."


    def priority_level(self, task):
        """
        Convert numeric priority_score into High / Medium / Low
        """
        if task.priority_score >= 7:
            return "High"
        elif task.priority_score >= 4:
            return "Medium"
        else:
            return "Low"


    def calculate_priorities(self, weights=None):
        weights = weights or {"urgency": 0.4, "importance": 0.4, "effort": 0.2}
        today = date.today()

        for task in self.tasks:

            if task.due_date:
                days_until_due = (datetime.fromisoformat(task   .due_date).date() - today).days
                urgency_score = max(0, 10 - days_until_due)
            else:
                urgency_score = 0

            importance_mapping = {"exam": 10, "assignment": 8, "reading": 4, "other": 2}
            importance_score = importance_mapping.get(task.category.lower(), 5)

            effort_score = task.estimated_pomodoros

            task.priority_score = (
                weights["urgency"] * urgency_score +
                weights["importance"] * importance_score +
                weights["effort"] * effort_score
            )

    def can_schedule(self, task):
        """Return True if all dependencies are completed."""
        for dep_name in task.dependencies:
            dep_task = self.get_task_by_name(dep_name)
            if dep_task is None or not dep_task.is_completed():
                return False
        return True
    
    def generate_daily_schedule(self, available_hours):
        """
        Non-overlapping daily schedule.
        Each pomodoro block = 0.5 hours (30 mins) in schedule view.
        """
        self.calculate_priorities()

        schedule = []
        tasks = sorted(self.tasks, key=lambda t: t.priority_score, reverse=True)

        timeline = []
        for start, end in available_hours:
            hour = float(start)
            while hour + 0.5 <= float(end):
                timeline.append((hour, hour + 0.5))
                hour += 0.5

        slot_index = 0 

        for task in tasks:
            if task.is_completed():
                continue
            if not self.can_schedule(task):
                continue

            remaining = task.estimated_pomodoros - task.completed_pomodoros
            if remaining <= 0:
                continue

            while remaining > 0 and slot_index < len(timeline):
                start, end = timeline[slot_index]
                schedule.append({
                    "task": task.name,
                    "start": start,
                    "end": end,
                    "priority": self.priority_level(task),
                    "category": task.category.lower()
                })
                slot_index += 1
                remaining -= 1

            if slot_index >= len(timeline):
                break

        return schedule

    def generate_weekly_schedule(self, days_available, decay_per_day=0.1):
        weekly_schedule = {}
        today = date.today()
        end_day = today + timedelta(days=6)

        self.calculate_priorities()
        base_scores = {t.name: t.priority_score for t in self.tasks}

        window_days = {}
        for i in range(7):
            d = today + timedelta(days=i)
            key = d.isoformat()
            window_days[key] = days_available.get(key, []) 


        for idx, day_str in enumerate(sorted(window_days.keys())):
            current_day = date.fromisoformat(day_str)

            if current_day < today or current_day > end_day:
                weekly_schedule[day_str] = []
                continue

            for t in self.tasks:
                t.priority_score = max(0, base_scores.get(t.name, 0) * (1 - decay_per_day * idx))

            timeline = []
            for start, end in window_days[day_str]:
                hour = float(start)
                while hour + 0.5 <= float(end):
                    timeline.append((hour, hour + 0.5))
                    hour += 0.5

            slot_index = 0
            day_schedule = []
            tasks = sorted(self.tasks, key=lambda t: t.priority_score, reverse=True)

            for task in tasks:
                try:
                    due = date.fromisoformat(task.due_date)
                    if due < today:
                        continue
                except Exception:
                    pass

                if task.is_completed():
                    continue
                if not self.can_schedule(task):
                    continue

                remaining = task.estimated_pomodoros - task.completed_pomodoros
                if remaining <= 0:
                    continue

                while remaining > 0 and slot_index < len(timeline):
                    start, end = timeline[slot_index]
                    day_schedule.append({
                        "task": task.name,
                        "start": start,
                        "end": end,
                        "priority": self.priority_level(task),
                        "category": task.category.lower()
                    })
                    slot_index += 1
                    remaining -= 1

                if slot_index >= len(timeline):
                    break

            weekly_schedule[day_str] = day_schedule

        for t in self.tasks:
            t.priority_score = base_scores.get(t.name, t.priority_score)

        return weekly_schedule


    def weekly_summary(self):
        end_date = date.today()
        start_date = end_date - timedelta(days=6)

        per_day = {(start_date + timedelta(days=i)).isoformat(): 0 for i in range(7)}

        by_category = {
            "study": 0,
            "exam": 0,
            "assignment": 0,
            "reading": 0,
            "other": 0
        }

        try:
            with open("count_pomodoro.csv", "r", newline="") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        log_date = date.fromisoformat(row["date"])
                    except Exception:
                        continue

                    if log_date > end_date:
                        continue

                    if log_date < start_date:
                        continue

                    category = row.get("category", "other").strip().lower()

                    try:
                        pomodoros = int(row.get("pomodoros", 0))
                    except ValueError:
                        pomodoros = 0

                    if category not in by_category:
                        category = "other"

                    per_day[log_date.isoformat()] += pomodoros
                    by_category[category] += pomodoros

        except FileNotFoundError:
            pass

        total = sum(per_day.values())

        return {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "total": total,
            "focus_minutes": total * 25,
            "per_day": per_day,
            "by_category": by_category
        }