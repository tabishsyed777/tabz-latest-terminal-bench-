#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/deploy.sh <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: deploy.sh --dry-run | --help"
}

if [[ $# -eq 1 && "$1" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -ne 1 || "$1" != "--dry-run" ]]; then
    usage >&2
    exit 2
fi

echo "Dry run complete."
SCRIPT
chmod +x /workspace/deploy.sh
