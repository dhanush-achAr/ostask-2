
import threading
import time
import random
import html
from datetime import datetime
from pathlib import Path

TOTAL = 4
MEALS = 3
REPORT = "dining_philosophers_monitor.html"

THINKING = 0
HUNGRY = 1
EATING = 2


class ActivityLog:
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()
        self.sequence = 0

    def add(self, philosopher, action):
        with self.lock:
            self.sequence += 1
            timestamp = datetime.now().strftime("%H:%M:%S")

            event = {
                "sequence": self.sequence,
                "time": timestamp,
                "philosopher": philosopher,
                "action": action
            }
            self.events.append(event)

            # Print every activity in the terminal
            print(
                f"[{self.sequence:03d}] {timestamp} | "
                f"{philosopher} | {action}",
                flush=True
            )


class DiningMonitor:
    def __init__(self, log):
        self.log = log
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.states = [THINKING] * TOTAL

    def can_eat(self, number):
        left = (number - 1) % TOTAL
        right = (number + 1) % TOTAL

        return (
            self.states[left] != EATING
            and self.states[right] != EATING
        )

    def take_forks(self, number):
        name = f"Philosopher {number}"

        with self.condition:
            self.states[number] = HUNGRY
            self.log.add(name, "Hungry and waiting for forks")

            while not self.can_eat(number):
                self.condition.wait()

            self.states[number] = EATING
            self.log.add(name, "Picked up both forks")
            self.log.add(name, "Entered eating state")

    def put_forks(self, number):
        name = f"Philosopher {number}"

        with self.condition:
            self.states[number] = THINKING
            self.log.add(name, "Put down both forks")
            self.log.add(name, "Returned to thinking state")

            # Wake waiting philosophers so they can check again.
            self.condition.notify_all()


def create_html_report(log, meals):
    rows = ""

    for event in log.events:
        rows += (
            "<tr>"
            f"<td>{event['sequence']}</td>"
            f"<td>{html.escape(event['time'])}</td>"
            f"<td>{html.escape(event['philosopher'])}</td>"
            f"<td>{html.escape(event['action'])}</td>"
            "</tr>\n"
        )

    meal_rows = ""
    for philosopher in range(TOTAL):
        meal_rows += (
            f"<tr><td>Philosopher {philosopher}</td>"
            f"<td>{meals[philosopher]}</td></tr>\n"
        )

    report_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dining Philosophers - Monitor</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 25px;
    background: #f4f6f8;
}}
h1, h2 {{ color: #243b53; }}
table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    margin-bottom: 25px;
}}
th, td {{
    padding: 10px;
    border: 1px solid #ccc;
    text-align: left;
}}
th {{ background: #d9e8f5; }}
tr:nth-child(even) {{ background: #f8fafc; }}
.success {{
    padding: 12px;
    background: #d9f5df;
    border-radius: 6px;
}}
</style>
</head>
<body>
<h1>Dining Philosophers - Monitor Solution</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<div class="success">
All philosophers finished their assigned meals.
The monitor protects philosopher states and allows a philosopher
to eat only when neither neighbor is eating.
</div>

<h2>Meal Summary</h2>
<table>
<tr><th>Philosopher</th><th>Meals completed</th></tr>
{meal_rows}
</table>

<h2>Activity Log</h2>
<table>
<tr><th>No.</th><th>Time</th><th>Philosopher</th><th>Action</th></tr>
{rows}
</table>
</body>
</html>
"""

    Path(REPORT).write_text(report_html, encoding="utf-8")
    print(f"\nHTML report saved: {Path(REPORT).resolve()}")


def philosopher_work(number, monitor, log, meals):
    name = f"Philosopher {number}"

    for meal in range(MEALS):
        log.add(name, f"Thinking before meal {meal + 1}")
        time.sleep(random.uniform(0.1, 0.4))

        monitor.take_forks(number)

        log.add(name, f"Started eating meal {meal + 1}")
        time.sleep(random.uniform(0.1, 0.3))

        meals[number] += 1
        log.add(name, f"Finished eating meal {meal + 1}")

        monitor.put_forks(number)

    log.add(name, "Completed all meals")


def main():
    print("=" * 55)
    print("DINING PHILOSOPHERS - MONITOR SOLUTION")
    print("=" * 55)

    log = ActivityLog()
    meals = [0] * TOTAL
    monitor = DiningMonitor(log)
    threads = []

    for number in range(TOTAL):
        thread = threading.Thread(
            target=philosopher_work,
            args=(number, monitor, log, meals)
        )
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("\n" + "=" * 55)
    print("FINAL RESULT")
    print("=" * 55)

    for number, count in enumerate(meals):
        print(f"Philosopher {number}: {count}/{MEALS} meals completed")

    successful = all(count == MEALS for count in meals)
    print("Status:", "SUCCESS" if successful else "INCOMPLETE")

    create_html_report(log, meals)


if __name__ == "__main__":
    main()
