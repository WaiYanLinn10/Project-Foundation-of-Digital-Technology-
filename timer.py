import time

class PomodoroTimer:
    WORK_TIME = 1 * 60
    BREAK_TIME = 1 * 60

    def __init__(self):
        self.running = False
        self.remaining_time = 0

    def countdown(self, seconds):
        while seconds > 0 and self.running:
            minutes, secs = divmod(seconds, 60)
            print(f"{minutes:02d}:{secs:02d}", end="\r")
            time.sleep(1)
            seconds -= 30

    def start(self):
        self.running = True
        print("Pomodoro started (25 minutes)")
        self.countdown(self.WORK_TIME)

    def pause(self):
        self.running = False
        print("Pomodoro paused")

    def reset(self):
        self.running = False
        self.remaining_time = 0
        print("Pomodoro reset")

    def complete(self):
        print("Pomodoro completed")
        print("Break time (5 minutes)")
        self.countdown(self.BREAK_TIME)
        print("Break done, Go for the next Pomodoro?")

    