import subprocess
from pathlib import Path


class StubAgent:
    """No-op baseline used to confirm that task tests reject an empty solution."""

    def __init__(self, task_dir, container, config=None):
        self.task_dir = Path(task_dir)
        self.container = container

    def solve(self, instruction, timeout):
        return [{"role": "assistant", "content": "Stub agent made no changes."}]


class OracleAgent:
    """Runs the task's hidden reference script for deterministic harness checks."""

    def __init__(self, task_dir, container, config):
        self.task_dir = Path(task_dir)
        self.container = container
        self.config = config

    def solve(self, instruction, timeout):
        solution = self.task_dir / self.config["solution_script"]
        if not solution.is_file():
            raise FileNotFoundError(f"reference solution not found: {solution}")

        destination = f"{self.container}:/tmp/mtb-reference-solution.sh"
        subprocess.run(["docker", "cp", str(solution), destination], check=True, capture_output=True, text=True)
        result = subprocess.run(
            ["docker", "exec", self.container, "bash", "/tmp/mtb-reference-solution.sh"],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return [
            {"role": "user", "content": instruction},
            {"role": "assistant", "content": result.stdout.strip() or "Reference solution applied."},
        ]
