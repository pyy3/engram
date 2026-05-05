#!/bin/bash
# Run all engram tests.
set -e

cd "$(dirname "$0")/.."

echo "=== Engram Test Suite ==="
echo ""

PASS=0
FAIL=0

for test in tests/test_*.py; do
  echo "--- $(basename "$test") ---"
  if python3 "$test"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAILED: $test"
  fi
  echo ""
done

echo "=== Results: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] || exit 1
