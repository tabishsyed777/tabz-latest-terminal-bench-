#!/usr/bin/env bash
# Broken starter script: does not validate arguments or implement dry-run mode.
if [ "$1" = "--dry-run" ]; then
    echo "Deploying for real..."
    exit 1
fi
exit 0
