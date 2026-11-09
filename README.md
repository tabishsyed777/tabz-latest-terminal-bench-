# My Terminal Bench

A small, self-contained Docker benchmark for terminal task agents. It includes two tasks, a no-op baseline, and a deterministic oracle runner.

> This is a custom local benchmark harness. It is not an official Terminal-Bench 3 / Harbor repository or task format.

## Repository layout

```text
harness/                    Local Docker runner and agent interface
tasks/
  001-fix-broken-script/    Shell repair task
  002-repair-etl-pipeline/  Multi-file Python ETL task
```

## Setup

Requirements: Python 3.10+ and Docker.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
docker info
```

## Run a task

The `stub` agent makes no changes and should fail. The `oracle` agent applies the included reference solution and should pass. Both modes are for local sanity checks; connect your own terminal agent through `harness/agent_interface.py` to evaluate it.

```bash
mtb --task tasks/001-fix-broken-script --agent oracle
mtb --task tasks/001-fix-broken-script --agent stub

mtb --task tasks/002-repair-etl-pipeline --agent oracle
mtb --task tasks/002-repair-etl-pipeline --agent stub
```

Results are written to `results/` as JSON. Task images run with networking disabled. The Docker build context excludes verifier and reference-solution files, and the runner copies verifier files into the container after solving.

## Task summaries

### `001-fix-broken-script`

Repair a deployment script so dry-run, help, and invalid-argument behavior is safe and tested.

### `002-repair-etl-pipeline`

Repair validation, last-record deduplication, configurable USD-to-INR conversion, rejected-row reporting, and UTC timestamp output in a sales pipeline.

## Benchmark integrity

This repository is public and includes the tests, expected output, and reference solutions for reproducibility. Therefore the tasks are not secret and should not be used as a blind or adversarial evaluation set. For that use, keep verifier and reference files in a private grader repository and publish only task instructions and starter files.

## Known limits

- No model API or external agent integration is included yet.
- The oracle validates task solvability; it does not measure agent capability.
- A passing stub/oracle pair is a harness sanity check, not a difficulty calibration.
- Docker task execution must be run locally; package installation does not run it automatically.
