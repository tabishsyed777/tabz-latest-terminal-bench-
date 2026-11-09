import argparse
import json
import subprocess
import time
import uuid
from pathlib import Path

import yaml

from harness.agent_interface import OracleAgent, StubAgent


AGENTS = {"stub": StubAgent, "oracle": OracleAgent}


def run_task(task_dir, agent_name="stub", timeout=None):
    task_dir = Path(task_dir).resolve()
    config_path = task_dir / "task.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"task configuration not found: {config_path}")
    if agent_name not in AGENTS:
        raise ValueError(f"unknown agent {agent_name!r}; choose from {', '.join(AGENTS)}")

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    timeout = timeout or config.get("time_limit_seconds", 1800)
    image = f"mtb-{task_dir.name}".lower()
    container = f"mtb-{task_dir.name}-{uuid.uuid4().hex[:8]}".lower()
    started = time.time()
    container_started = False
    result = {
        "task": task_dir.name,
        "agent": agent_name,
        "passed": False,
        "return_code": None,
        "stdout": "",
        "stderr": "",
        "transcript": [],
        "duration_seconds": None,
        "error": None,
    }

    try:
        print(f"[1/5] Building {image}")
        subprocess.run(["docker", "build", "-t", image, str(task_dir)], check=True)

        print(f"[2/5] Starting {container}")
        subprocess.run(
            ["docker", "run", "-d", "--network=none", "--name", container, "--workdir", "/workspace", image, "sleep", "infinity"],
            check=True,
            capture_output=True,
            text=True,
        )
        container_started = True

        print("[3/5] Running agent")
        agent = AGENTS[agent_name](task_dir, container, config)
        result["transcript"] = agent.solve(config["instruction"], timeout)

        # Tests are mounted only after the agent's workspace is finalized.
        print("[4/5] Running hidden tests")
        tests_dir = task_dir / "tests"
        if not tests_dir.is_dir():
            raise FileNotFoundError(f"task test directory not found: {tests_dir}")
        subprocess.run(
            ["docker", "cp", str(tests_dir), f"{container}:/workspace/tests"],
            check=True,
            capture_output=True,
            text=True,
        )
        test = subprocess.run(
            ["docker", "exec", container, "bash", "-lc", config["test_command"]],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        result.update(
            passed=test.returncode == 0,
            return_code=test.returncode,
            stdout=test.stdout,
            stderr=test.stderr,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
        result["error"] = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            result["return_code"] = exc.returncode
            result["stdout"] = exc.stdout or ""
            result["stderr"] = exc.stderr or ""
        elif isinstance(exc, subprocess.TimeoutExpired):
            result["stderr"] = f"Timed out after {exc.timeout} seconds"
    finally:
        if container_started:
            print("[5/5] Cleaning up")
            subprocess.run(["docker", "rm", "-f", container], capture_output=True, text=True)

    result["duration_seconds"] = round(time.time() - started, 2)
    output_dir = Path(__file__).resolve().parents[1] / "results"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{task_dir.name}-{int(time.time())}.json"
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("task", "agent", "passed", "duration_seconds", "error")}, indent=2))
    print(f"Result saved: {output_path}")
    return 0 if result["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description="Run one local Docker task with the no-op or oracle agent.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--agent", choices=sorted(AGENTS), default="stub")
    parser.add_argument("--timeout", type=int)
    args = parser.parse_args()
    raise SystemExit(run_task(args.task, args.agent, args.timeout))


if __name__ == "__main__":
    main()
