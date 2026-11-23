"""Compare generator output with the checked-in snapshots.

Run example_node1.py through example_node3.py from examples/generator first.
Then run ./validate_examples.sh from the repository root to check the derived
directories without changing them.
"""

from difflib import unified_diff
from pathlib import Path


def validate_directory(expected: Path, generated: Path) -> bool:
    for directory in (expected, generated):
        if not directory.is_dir():
            print(f"Missing directory: {directory}")
            return False

    expected_files = {path.relative_to(expected) for path in expected.rglob("*") if path.is_file()}
    generated_files = {path.relative_to(generated) for path in generated.rglob("*") if path.is_file()}
    matches = expected_files == generated_files

    for path in sorted(expected_files - generated_files):
        print(f"Missing output: {generated / path}")
    for path in sorted(generated_files - expected_files):
        print(f"Unexpected output: {generated / path}")
    for path in sorted(expected_files & generated_files):
        snapshot = (expected / path).read_bytes()
        output = (generated / path).read_bytes()
        if snapshot != output:
            matches = False
            print(f"Output differs: {generated / path}")
            diff = unified_diff(
                snapshot.decode("utf-8", errors="backslashreplace").split("\n"),
                output.decode("utf-8", errors="backslashreplace").split("\n"),
                fromfile=str(expected / path),
                tofile=str(generated / path),
                lineterm="",
            )
            for line in diff:
                print(line)

    if matches:
        print(f"{expected.name}: {len(expected_files)} files match")
    return matches


def main() -> int:
    expected_dir = Path(__file__).resolve().parent
    generator_dir = expected_dir.parent
    matches = True
    for number in range(1, 4):
        if not validate_directory(expected_dir / f"example_node{number}", generator_dir / f"derived{number}"):
            matches = False
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())