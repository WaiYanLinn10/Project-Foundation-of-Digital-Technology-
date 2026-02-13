This project is a Python-based Pomodoro Task Management and Scheduling Optimizer developed as part of a Fundamental Digital Technologies coursework.

The system combines structured time management with algorithmic scheduling techniques to help users:

Track tasks

Manage Pomodoro sessions

Automatically prioritize workload

Generate optimized daily and weekly schedules

Analyse productivity patterns using charts

The project demonstrates the practical application of algorithms, object-oriented programming, data persistence, and descriptive analytics.


Requirement 
-Operating System- Windows or Mac 
-Python version 3.10 or higher 
-Python package installer (pip)
 
Installation Instructions 
-git clone https://github.com/WaiYanLinn10/Project-Foundation-of-Digital-Technology-.git 
-pip install pandas matplotlib (Windows) 
-pip3 install pandas matplotlib (Mac) 

Run: python main.py

main.py              # CLI controller
task.py              # Task and TaskManager logic
timer.py             # PomodoroTimer implementation
visualization.py     # Charts and availability input
verify_refactor.py   # Backend testing
tasks.csv            # Task database
count_pomodoro.csv   # Pomodoro log storage


Features

Task Management

-Add and delete tasks

-Categorize tasks (study, exam, assignment, reading, other)

-Set due dates

-Add task dependencies

-Track completed Pomodoros

-Persistent storage using CSV

Pomodoro Timer

-25-minute work session

-5-minute break session

-Automatic session logging


Intelligent Scheduling

-Daily optimized schedule

-Weekly 7-day timetable generation

-Priority-based greedy algorithm

-Dependency constraint enforcement

-Priority decay for fair weekly distribution

-Non-overlapping time allocation


Productivity Analytics

-Daily Pomodoro summary

-Weekly summary

-Pomodoros per day

-Pomodoros by category

-Focus time calculation

-Chart visualization (matplotlib)


Algorithms & Concepts Used

-Object-Oriented Programming (OOP)

-Greedy Scheduling Algorithm

-Weighted Linear Priority Scoring

-Constraint Satisfaction

-Dependency Graph (DAG concept)

-Finite State Machine (Timer states)

-Descriptive Statistics

-Data Persistence (CSV)

Author - Wai Yam Lin

