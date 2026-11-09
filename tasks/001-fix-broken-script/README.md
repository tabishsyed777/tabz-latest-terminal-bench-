# Fix the broken deployment script

A small shell-debugging task. The starter script is copied into the task container as `/workspace/deploy.sh`; the agent must make dry-run and argument handling safe and predictable.

The test suite is copied into the container only after the agent finishes. `solution.sh` is the hidden reference solution used by the local harness's `oracle` agent.
