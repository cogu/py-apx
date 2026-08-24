#!/usr/bin/env python3
"""
Example Scripts Validator

Discovers and executes all example scripts under doc/examples/ and examples/
to verify they run successfully (exit code 0).
"""
import argparse
import os
import subprocess
import sys
from typing import List


def discover_example_scripts(search_dirs: List[str]) -> List[str]:
    """
    Discovers all runnable example scripts under the given search directories.
    """
    scripts = []
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        for root, _, files in os.walk(search_dir):
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    scripts.append(os.path.join(root, f))
    scripts.sort()
    return scripts


def run_example(script_path: str, repo_root: str, verbose: bool = True, show_output: bool = False) -> bool:
    """
    Runs a single example script and returns True if execution succeeded (returncode == 0).
    """
    rel_path = os.path.relpath(script_path, repo_root)
    script_dir = os.path.dirname(script_path)
    env = os.environ.copy()
    src_dir = os.path.join(repo_root, "src")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else src_dir

    res = subprocess.run([sys.executable, script_path],
                         cwd=script_dir,
                         capture_output=True,
                         text=True,
                         env=env,
                         check=False)

    stdout = res.stdout.strip()
    stderr = res.stderr.strip()

    if res.returncode != 0:
        print(f"FAILED: {rel_path} (exit code {res.returncode})", file=sys.stderr)
        if stdout:
            print("STDOUT:\n" + stdout, file=sys.stderr)
        if stderr:
            print("STDERR:\n" + stderr, file=sys.stderr)
        return False

    if verbose:
        print(f"PASSED: {rel_path}")
        if show_output and stdout:
            print("  Output: " + stdout)

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate APX example scripts.")
    parser.add_argument("scripts", nargs="*", help="Optional specific script(s) to validate")
    parser.add_argument("-s", "--silent", action="store_true", help="Run silently (only report failures)")
    parser.add_argument("-v", "--verbose-output", action="store_true", help="Show stdout output of passed examples")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    search_dirs = [
        os.path.join(repo_root, "doc", "examples"),
        os.path.join(repo_root, "examples"),
    ]

    if args.scripts:
        target_scripts = [os.path.abspath(s) for s in args.scripts]
    else:
        target_scripts = discover_example_scripts(search_dirs)

    if not target_scripts:
        print("No example scripts found.")
        sys.exit(0)

    verbose = not args.silent
    failed = 0
    for script in target_scripts:
        if not run_example(script, repo_root, verbose=verbose, show_output=args.verbose_output):
            failed += 1

    if failed > 0:
        if verbose:
            print(f"\n{failed} out of {len(target_scripts)} example(s) failed.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"\nAll {len(target_scripts)} example(s) passed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
