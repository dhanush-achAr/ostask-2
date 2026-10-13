
import threading
import time
import random
import html
from datetime import datetime
from pathlib import Path

TOTAL = 4
MEALS = 3
REPORT = "dining_philosophers_semaphore.html"


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
<title>Dining Philosophers - Semaphore</title>
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
<h1>Dining Philosophers - Semaphore Solution</h1>
<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<div class="success">
All philosophers finished their assigned meals.
The room semaphore allows at most three philosophers to compete
for forks at a time, preventing circular waiting.
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


def philosopher_work(number, forks, room, log, meals):
    left_fork = number
    right_fork = (number + 1) % TOTAL
    name = f"Philosopher {number}"

    for meal in range(MEALS):
        log.add(name, f"Thinking before meal {meal + 1}")
        time.sleep(random.uniform(0.1, 0.4))

        log.add(name, "Hungry and waiting to enter")
        room.acquire()

        log.add(name, "Entered the room")
        forks[left_fork].acquire()
        log.add(name, f"Picked up fork {left_fork}")

        forks[right_fork].acquire()
        log.add(name, f"Picked up fork {right_fork}")

        log.add(name, f"Started eating meal {meal + 1}")
        time.sleep(random.uniform(0.1, 0.3))

        meals[number] += 1
        log.add(name, f"Finished eating meal {meal + 1}")

        forks[right_fork].release()
        log.add(name, f"Put down fork {right_fork}")

        forks[left_fork].release()
        log.add(name, f"Put down fork {left_fork}")

        room.release()
        log.add(name, "Left the room")

    log.add(name, "Completed all meals")


def main():
    print("=" * 55)
    print("DINING PHILOSOPHERS - SEMAPHORE SOLUTION")
    print("=" * 55)

    log = ActivityLog()
    meals = [0] * TOTAL

    # Each fork can be held by only one philosopher at a time.
    forks = [threading.Semaphore(1) for _ in range(TOTAL)]

    # Allow at most three philosophers to compete for forks.
    room = threading.Semaphore(TOTAL - 1)

    threads = []

    for number in range(TOTAL):
        thread = threading.Thread(
            target=philosopher_work,
            args=(number, forks, room, log, meals)
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
