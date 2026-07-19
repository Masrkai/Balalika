#!/usr/bin/env bash
# Gate script for the active plan: reports ALL PHASES COMPLETE when both
# the pytest unit suite and the behave integration specs pass (offline).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY="${PY:-.venv/bin/python}"

echo "== Running pytest unit suite =="
if "$PY" -m pytest tests/ -q -p no:cacheprovider 2>&1; then
  pytest_ok=1
else
  pytest_ok=0
fi

echo "== Running behave integration specs (offline) =="
if "$PY" -m behave tests/features --no-skipped 2>&1; then
  behave_ok=1
else
  behave_ok=0
fi

if [ "$pytest_ok" = "1" ] && [ "$behave_ok" = "1" ]; then
  echo "ALL PHASES COMPLETE"
  exit 0
else
  echo "PHASES INCOMPLETE (pytest=$pytest_ok behave=$behave_ok)"
  exit 1
fi
