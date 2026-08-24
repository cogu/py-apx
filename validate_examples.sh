#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    "$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/dev_utils/validate_examples.py" "$@"
else
    python3 "$SCRIPT_DIR/dev_utils/validate_examples.py" "$@"
fi
