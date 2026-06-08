from time import perf_counter
import psutil
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class Profiler:
    def __init__(self):
        self.process = psutil.Process(os.getpid())

        self.start_time = perf_counter()
        self.start_ram = self.process.memory_info().rss / 1024 / 1024

        self.steps = []

        # Prime CPU measurement
        self.process.cpu_percent()

    def step(self, name):
        current = perf_counter()

        if len(self.steps) == 0:
            elapsed = current - self.start_time
        else:
            elapsed = current - self.steps[-1]["timestamp"]

        ram = self.process.memory_info().rss / 1024 / 1024

        self.steps.append(
            {
                "name": name,
                "time": elapsed,
                "ram": ram,
                "timestamp": current,
            }
        )

    def finish(self):
        total_time = perf_counter() - self.start_time

        end_ram = self.process.memory_info().rss / 1024 / 1024
        ram_used = end_ram - self.start_ram

        cpu_percent = self.process.cpu_percent(interval=0.1)

        table = Table(
            title="󰔟 Step Performance",
            show_lines=True
        )

        table.add_column("󰈙 Step")
        table.add_column("⏱ Time")
        table.add_column("🧠 RAM")

        for step in self.steps:
            table.add_row(
                step["name"],
                f"{step['time']:.6f}s",
                f"{step['ram']:.2f} MB",
            )

        console.print()
        console.print(table)

        summary = Table(show_header=False)

        summary.add_row(
            "⏱ Total Runtime",
            f"{total_time:.6f}s"
        )

        summary.add_row(
            "🧠 RAM Delta",
            f"{ram_used:+.2f} MB"
        )

        summary.add_row(
            "🔥 CPU Usage",
            f"{cpu_percent:.1f}%"
        )

        console.print()
        console.print(
            Panel(
                summary,
                title="󰅐 Final Statistics",
                border_style="green",
            )
        )