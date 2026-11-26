#!/usr/bin/env bash
set -e

CDPATH= cd -- "$(dirname -- "$0")/examples/generator"

for example in example_node*.py; do
    [[ "$example" =~ ^example_node[0-9]+\.py$ ]] || continue
    python3 "$example"
done

exec python3 expected/validate_expected.py
