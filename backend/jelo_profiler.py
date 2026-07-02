import os
from datetime import datetime
from io import StringIO
from time import perf_counter

import psutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Profiler:
    def __init__(self, log_file="performance_result.txt"):
        self.process = psutil.Process(os.getpid())
        self.start_time = perf_counter()
        self.start_ram = self.process.memory_info().rss / 1024 / 1024
        self.steps = []

        self.log_file = log_file
        self.session_start = datetime.now()

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
                "marker": False,
            }
        )

    def iteration(self, label):
        """
        Drops a labeled divider into the step list — use it to tag
        the start of a new loop iteration (e.g. with the user's input),
        so the report shows which steps belong to which run.
        """
        current = perf_counter()

        self.steps.append(
            {
                "name": label,
                "time": None,
                "ram": None,
                "timestamp": current,
                "marker": True,
            }
        )

    def finish(self):
        total_time = perf_counter() - self.start_time
        end_ram = self.process.memory_info().rss / 1024 / 1024
        ram_used = end_ram - self.start_ram
        cpu_percent = self.process.cpu_percent(interval=0.1)

        table = self._build_table()
        panel = self._build_summary_panel(total_time, ram_used, cpu_percent)

        console.print()
        console.print(table)
        console.print()
        console.print(panel)

        self._save_to_file(table, panel)

    def _build_table(self):
        table = Table(title="󰔟 Step Performance", show_lines=True)
        table.add_column("󰈙 Step")
        table.add_column("⏱ Time")
        table.add_column("🧠 RAM")

        for step in self.steps:
            if step["marker"]:
                table.add_row(
                    f"[bold yellow]▶ {step['name']}[/bold yellow]",
                    "",
                    "",
                )
            else:
                table.add_row(
                    step["name"],
                    f"{step['time']:.6f}s",
                    f"{step['ram']:.2f} MB",
                )

        return table

    def _build_summary_panel(self, total_time, ram_used, cpu_percent):
        summary = Table(show_header=False)
        summary.add_row("⏱ Total Runtime", f"{total_time:.6f}s")
        summary.add_row("🧠 RAM Delta", f"{ram_used:+.2f} MB")
        summary.add_row("🔥 CPU Usage", f"{cpu_percent:.1f}%")

        return Panel(
            summary,
            title="󰅐 Final Statistics",
            border_style="green",
        )

    def _save_to_file(self, table, panel):
        # ye console jodagane misazim ke faghat too file benevise
        # hamoon table o panel ro reuse mikonim, pas shekle txt ham
        # hamoon zibayi console ro dare
        buffer = Console(record=True, width=100, file=StringIO())

        buffer.print(
            f"[bold]Performance Log — {self.session_start:%Y-%m-%d %H:%M:%S}[/bold]"
        )
        buffer.print()
        buffer.print(table)
        buffer.print()
        buffer.print(panel)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(buffer.export_text())
            f.write("\n")
